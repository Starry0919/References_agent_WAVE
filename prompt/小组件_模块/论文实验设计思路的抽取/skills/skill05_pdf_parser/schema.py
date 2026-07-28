import hashlib
import json
from pathlib import Path
from typing import Any

SKILL_ID = "skill05_pdf_parser"
SKILL_VERSION = "0.2.0"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def artifact_ref(path: Path, source: str, version: str = "1"):
    checksum = sha256_file(path)
    suffix = path.suffix.casefold()
    media = {
        ".md": "text/markdown", ".json": "application/json",
        ".pdf": "application/pdf", ".png": "image/png",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg"
    }.get(suffix, "application/octet-stream")
    return {
        "artifact_id": "artifact:" + checksum[:24], "media_type": media,
        "sha256": checksum, "version": version,
        "source": source, "uri": str(path.resolve())
    }

