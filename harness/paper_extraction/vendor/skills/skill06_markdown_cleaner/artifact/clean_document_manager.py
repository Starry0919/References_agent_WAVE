import json
import os
import tempfile
from pathlib import Path

try:
    from ..schema import artifact_ref, sha256_text
except ImportError:
    from schema import artifact_ref, sha256_text


class CleanDocumentManager:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def store(self, paper_id, source_hash, markdown, document_json):
        safe_id = "".join(c if c.isalnum() or c in "._-" else "_" for c in str(paper_id)).strip("._") or "unknown"
        directory = (self.root / safe_id / source_hash[:16]).resolve()
        if self.root not in directory.parents:
            raise ValueError("Clean document path escapes configured root")
        directory.mkdir(parents=True, exist_ok=True)
        markdown_path = directory / "clean_document.md"
        json_path = directory / "clean_document.json"
        self._immutable_write(markdown_path, markdown.encode("utf-8"))
        self._immutable_write(
            json_path,
            json.dumps(document_json, ensure_ascii=False, indent=2).encode("utf-8")
        )
        return markdown_path, json_path, artifact_ref(markdown_path, "skill06_markdown_cleaner"), artifact_ref(json_path, "skill06_markdown_cleaner")

    @staticmethod
    def _immutable_write(path, data):
        if path.exists():
            if path.read_bytes() != data:
                raise ValueError(f"Immutable clean artifact conflict: {path}")
            return
        descriptor, temporary = tempfile.mkstemp(prefix=".clean-", dir=str(path.parent))
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

