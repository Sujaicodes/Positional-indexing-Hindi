"""SPIMI-style bilingual positional indexer with disk block flushing."""
from collections import defaultdict
from pathlib import Path
import heapq
import json
import math
import shutil
import tempfile
from preprocessing import tokenize_with_languages
from storage import DiskPostingsStore


def _flush_block(block, run_path):
    with run_path.open("w", encoding="utf-8", newline="\n") as out:
        for term in sorted(block):
            out.write(json.dumps([term, block[term]], ensure_ascii=False, separators=(",", ":")) + "\n")


def build_index(documents, index_dir, block_posting_limit=50000):
    """Build sorted runs and merge one term at a time into disk postings.

    The indexed vocabulary includes both Devanagari Hindi and Latin-script
    English words found in the input. Token positions count both scripts.
    """
    if block_posting_limit < 1:
        raise ValueError("block_posting_limit must be positive")
    index_dir = Path(index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)
    runs_dir = Path(tempfile.mkdtemp(prefix="spimi_", dir=str(index_dir)))
    runs = []
    block = defaultdict(list)
    block_size = 0
    doc_count = 0
    document_lengths = {}
    language_counts = {"hi": 0, "en": 0}
    try:
        for doc in documents:
            doc_count += 1
            per_doc = defaultdict(list)
            tokens = tokenize_with_languages(doc["text"])
            document_lengths[doc["doc_id"]] = len(tokens)
            for position, (term, language) in enumerate(tokens, start=1):
                per_doc[term].append(position)
                language_counts[language] = language_counts.get(language, 0) + 1
            for term, positions in per_doc.items():
                block[term].append({"doc_id": doc["doc_id"], "positions": positions})
                block_size += 1
                if block_size >= block_posting_limit:
                    run_path = runs_dir / f"run_{len(runs):06d}.jsonl"
                    _flush_block(block, run_path)
                    runs.append(run_path)
                    block = defaultdict(list)
                    block_size = 0
        if block:
            run_path = runs_dir / f"run_{len(runs):06d}.jsonl"
            _flush_block(block, run_path)
            runs.append(run_path)

        handles = [p.open("r", encoding="utf-8") for p in runs]
        heap = []
        for i, handle in enumerate(handles):
            line = handle.readline()
            if line:
                term, postings = json.loads(line)
                heapq.heappush(heap, (term, i, postings))
        vocabulary = {}
        store = DiskPostingsStore(index_dir / "postings.jsonl")
        with store.path.open("wb") as final_out:
            while heap:
                term = heap[0][0]
                merged = []
                while heap and heap[0][0] == term:
                    _, run_i, postings = heapq.heappop(heap)
                    merged.extend(postings)
                    line = handles[run_i].readline()
                    if line:
                        next_term, next_postings = json.loads(line)
                        heapq.heappush(heap, (next_term, run_i, next_postings))
                merged.sort(key=lambda p: p["doc_id"])
                compact = []
                for posting in merged:
                    if compact and compact[-1]["doc_id"] == posting["doc_id"]:
                        compact[-1]["positions"].extend(posting["positions"])
                        compact[-1]["positions"].sort()
                    else:
                        compact.append({"doc_id": posting["doc_id"], "positions": list(posting["positions"])})
                cf = sum(len(p["positions"]) for p in compact)
                df = len(compact)
                language = "hi" if any("DEVANAGARI" in __import__("unicodedata").name(c, "") for c in term) else "en"
                vocabulary[term] = {
                    "cf": cf, "df": df, "language": language,
                    "postings": store.write_record(final_out, compact)
                }
        for handle in handles:
            handle.close()
        vocab_path = index_dir / "vocabulary.json"
        vocab_path.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=2), encoding="utf-8")
        total_tokens = sum(document_lengths.values())
        metadata = {
            "documents": doc_count,
            "vocabulary_size": len(vocabulary),
            "total_tokens": total_tokens,
            "language_token_counts": language_counts,
            "document_lengths": document_lengths,
            "average_document_length": (total_tokens / doc_count) if doc_count else 0,
            "builder": "SPIMI-style sorted block runs with term-wise merge",
            "block_posting_limit": block_posting_limit,
            "tokenization": "NFC-normalized Hindi Devanagari and English Latin-script lexical tokens",
            "position_convention": "1-indexed positions over the complete Hindi-English lexical token stream"
        }
        (index_dir / "index_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        return vocabulary
    finally:
        shutil.rmtree(runs_dir, ignore_errors=True)
