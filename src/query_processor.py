"""Term, phrase, frequency-ranking and BM25 document queries."""
import json
import math
from pathlib import Path
from preprocessing import tokenize
from storage import DiskPostingsStore


class PositionalIndex:
    def __init__(self, index_dir):
        root = Path(index_dir)
        self.vocabulary = json.loads((root / "vocabulary.json").read_text(encoding="utf-8"))
        self.metadata = json.loads((root / "index_metadata.json").read_text(encoding="utf-8"))
        self.store = DiskPostingsStore(root / "postings.jsonl")
        self.document_lengths = self.metadata.get("document_lengths", {})
        self.document_count = self.metadata.get("documents", len(self.document_lengths))
        self.average_document_length = self.metadata.get("average_document_length", 0.0)

    def lookup(self, term):
        terms = tokenize(term)
        if len(terms) != 1:
            raise ValueError("lookup() expects exactly one Hindi or English token")
        term = terms[0]
        entry = self.vocabulary.get(term)
        if entry is None:
            return None
        pointer = entry["postings"]
        return {"term": term, "language": entry.get("language", "unknown"),
                "cf": entry["cf"], "df": entry["df"],
                "postings": self.store.read(pointer["offset"], pointer["length"])}

    def phrase_search(self, phrase_tokens):
        """Return exact phrase matches and their starting positions."""
        if isinstance(phrase_tokens, str):
            phrase_tokens = tokenize(phrase_tokens)
        if not phrase_tokens:
            return []
        lists = []
        for term in phrase_tokens:
            result = self.lookup(term)
            if result is None:
                return []
            lists.append({p["doc_id"]: set(p["positions"]) for p in result["postings"]})
        common_docs = set(lists[0])
        for posting_map in lists[1:]:
            common_docs.intersection_update(posting_map)
        matches = []
        for doc_id in sorted(common_docs):
            starts = {p for p in lists[0][doc_id]
                      if all(p + offset in lists[offset][doc_id]
                             for offset in range(1, len(lists)))}
            if starts:
                matches.append({"doc_id": doc_id, "positions": sorted(starts)})
        return matches

    def top_terms(self, metric="cf", limit=5):
        """Return terms ranked by CF or DF, with deterministic tie-breaking."""
        if metric not in {"cf", "df"}:
            raise ValueError("metric must be 'cf' or 'df'")
        other = "df" if metric == "cf" else "cf"
        ranked = sorted(self.vocabulary.items(), key=lambda item: (-item[1][metric], -item[1][other], item[0]))
        return [{"rank": rank, "term": term, "language": entry.get("language", "unknown"),
                 "cf": entry["cf"], "df": entry["df"]}
                for rank, (term, entry) in enumerate(ranked[:limit], start=1)]

    def rank_documents(self, query, limit=5, k1=1.5, b=0.75):
        """Rank matching documents with BM25; positions provide term frequency."""
        query_terms = list(dict.fromkeys(tokenize(query)))
        if not query_terms:
            return []
        scores = {}
        matched = {}
        n_docs = max(self.document_count, 1)
        avgdl = self.average_document_length or 1.0
        for term in query_terms:
            result = self.lookup(term)
            if result is None:
                continue
            df = result["df"]
            idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
            for posting in result["postings"]:
                doc_id = posting["doc_id"]
                tf = len(posting["positions"])
                dl = self.document_lengths.get(doc_id, 0)
                denominator = tf + k1 * (1.0 - b + b * dl / avgdl)
                contribution = idf * (tf * (k1 + 1.0)) / denominator
                scores[doc_id] = scores.get(doc_id, 0.0) + contribution
                matched.setdefault(doc_id, []).append(term)
        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        return [{"rank": rank, "doc_id": doc_id, "score": round(score, 6),
                 "matched_terms": matched[doc_id],
                 "document_length": self.document_lengths.get(doc_id, 0)}
                for rank, (doc_id, score) in enumerate(ranked[:limit], start=1)]
