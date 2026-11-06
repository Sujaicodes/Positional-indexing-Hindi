"""Deterministic loader for UTF-8 text documents."""
from pathlib import Path

def load_documents(directory):
    root = Path(directory)
    if not root.exists():
        raise FileNotFoundError(f"Document directory does not exist: {root}")
    docs = []
    for path in sorted(root.rglob("*.txt"), key=lambda p: p.relative_to(root).as_posix()):
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError(f"Empty document found; refusing to silently discard it: {path}")
        rel = path.relative_to(root).with_suffix("").as_posix()
        docs.append({"doc_id": rel, "path": str(path), "text": text})
    return docs
