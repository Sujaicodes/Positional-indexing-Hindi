"""Command-line interface for the bilingual positional inverted index."""
import argparse
import json
from pathlib import Path
from dataset_loader import load_documents
from indexer import build_index
from query_processor import PositionalIndex

ROOT = Path(__file__).resolve().parents[1]


def json_dumps(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Hindi-English disk-based positional inverted index with BM25 ranking"
    )
    parser.add_argument("--docs", default=str(ROOT / "dataset" / "documents"))
    parser.add_argument("--index", default=str(ROOT / "index"))
    parser.add_argument("--block-limit", type=int, default=50000)
    parser.add_argument("--query", help="Look up one Hindi or English term")
    parser.add_argument("--phrase", help="Search an exact Hindi-English phrase")
    parser.add_argument("--rank", help="Rank documents for a multi-term query using BM25")
    parser.add_argument("--top-k", type=int, default=5, help="Number of ranked documents to display (default: 5)")
    parser.add_argument("--top-cf", action="store_true", help="Display the top five terms by collection frequency")
    parser.add_argument("--top-df", action="store_true", help="Display the top five terms by document frequency")
    parser.add_argument("--no-build", action="store_true", help="Query an existing index without rebuilding")
    args = parser.parse_args()

    if args.top_k < 1:
        parser.error("--top-k must be at least 1")

    if not args.no_build:
        docs = load_documents(args.docs)
        vocab = build_index(docs, args.index, args.block_limit)
        print(f"Indexed {len(docs)} documents; bilingual vocabulary size = {len(vocab)}")

    index = PositionalIndex(args.index)
    if args.query:
        result = index.lookup(args.query)
        print(json_dumps(result) if result else f"Term not found: {args.query}")
    if args.phrase:
        print(json_dumps(index.phrase_search(args.phrase)))
    if args.rank:
        print(json_dumps({"query": args.rank, "ranking_method": "BM25", "results": index.rank_documents(args.rank, args.top_k)}))
    if args.top_cf:
        print("TOP TERMS BY COLLECTION FREQUENCY (CF)")
        print(json_dumps(index.top_terms("cf", 5)))
    if args.top_df:
        print("TOP TERMS BY DOCUMENT FREQUENCY (DF)")
        print(json_dumps(index.top_terms("df", 5)))


if __name__ == "__main__":
    main()
