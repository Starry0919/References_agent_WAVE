import hashlib
import json
from pathlib import Path
from typing import Any

SKILL_ID = "skill06_markdown_cleaner"
SKILL_VERSION = "0.3.1"
RULE_SET_VERSION = "scientific-cleaning-rules/0.3.1"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def artifact_ref(path: Path, source: str):
    data = path.read_bytes()
    checksum = hashlib.sha256(data).hexdigest()
    media = "text/markdown" if path.suffix == ".md" else "application/json"
    return {
        "artifact_id": "artifact:" + checksum[:24], "media_type": media,
        "sha256": checksum, "version": "1", "source": source,
        "uri": str(path.resolve())
    }
