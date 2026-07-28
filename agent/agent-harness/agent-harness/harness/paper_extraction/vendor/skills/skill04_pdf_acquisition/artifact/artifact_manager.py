from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

try:
    from ..schema import safe_paper_id, sha256_bytes, sha256_file
except ImportError:
    from schema import safe_paper_id, sha256_bytes, sha256_file


class ArtifactManager:
    def __init__(self, artifact_root: Path):
        self.root = artifact_root.resolve()
        self.papers_root = (self.root / "papers").resolve()
        self.papers_root.mkdir(parents=True, exist_ok=True)

    def store(self, paper_id, data, metadata):
        directory = (self.papers_root / safe_paper_id(paper_id)).resolve()
        if self.papers_root not in directory.parents:
            raise ValueError("Artifact target escapes configured root")
        directory.mkdir(parents=True, exist_ok=True)
        checksum = sha256_bytes(data)
        existing = sorted(directory.glob("original*.pdf"))
        for path in existing:
            if sha256_file(path) == checksum:
                version = self._version_from_name(path.name)
                return path, version, checksum, False
        version = len(existing) + 1
        name = "original.pdf" if version == 1 else f"original_v{version}.pdf"
        target = directory / name
        descriptor, temp_name = tempfile.mkstemp(prefix=".download-", suffix=".pdf", dir=str(directory))
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        stored_metadata = dict(metadata)
        stored_metadata["file_information"] = {
            "file_name": target.name, "path": str(target),
            "size_bytes": len(data), "mime_type": "application/pdf"
        }
        stored_metadata["integrity"] = {
            "checksum_algorithm": "sha256", "checksum_value": checksum
        }
        stored_metadata["artifact_version"] = str(version)
        metadata_path = directory / f"metadata_v{version}.json"
        metadata_path.write_text(json.dumps(stored_metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        (directory / f"checksum_v{version}.txt").write_text(checksum + "\n", encoding="ascii")
        return target, version, checksum, True

    @staticmethod
    def _version_from_name(name):
        if name == "original.pdf":
            return 1
        return int(name.removeprefix("original_v").removesuffix(".pdf"))
