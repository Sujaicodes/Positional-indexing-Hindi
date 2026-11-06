"""Byte-offset based random access to disk-resident postings."""
import json
from pathlib import Path

class DiskPostingsStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write_record(self, out, postings):
        payload = (json.dumps(postings, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        offset = out.tell()
        out.write(payload)
        return {"offset": offset, "length": len(payload)}

    def read(self, offset, length):
        with self.path.open("rb") as src:
            src.seek(offset)
            payload = src.read(length)
        if len(payload) != length:
            raise IOError(f"Short postings read at byte offset {offset}")
        return json.loads(payload.decode("utf-8"))
