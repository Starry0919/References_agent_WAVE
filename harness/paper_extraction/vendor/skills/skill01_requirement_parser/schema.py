"""Skill01-local contract helpers; the framework schema remains authoritative."""

from __future__ import annotations

import hashlib
import json
from typing import Any

SKILL_ID = "skill01_requirement_parser"
SKILL_VERSION = "0.4.0"
ALLOWED_FIELD_STATUSES = {
    "reported", "unknown", "inferred", "needs_clarification"
}
ERROR_ALIASES = {
    "REQ001": "EDX-VAL-001",
    "REQ002": "EDX-VAL-001",
    "REQ003": "EDX-VAL-002",
    "REQ004": "EDX-VAL-002",
    "REQ005": "EDX-EXT-002"
}


def sha256_json(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
