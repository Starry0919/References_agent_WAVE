import hashlib
import json
from typing import Any

SKILL_ID = "skill08_evidence_binding"
SKILL_VERSION = "0.2.0"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def unknown_field(notes="Evidence was not found in the supplied clean document."):
    return {
        "value": None, "status": "unknown", "confidence": 1.0,
        "extraction_method": "not_applicable", "evidence_ids": [],
        "notes": notes
    }

