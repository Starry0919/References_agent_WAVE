from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Optional

SKILL_ID = "skill03_citation_validation"
SKILL_VERSION = "0.2.0"
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$", re.I)


def normalize_doi(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    cleaned = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", str(value).strip(), flags=re.I)
    return cleaned.lower() or None


def valid_doi_format(value: Optional[str]) -> bool:
    doi = normalize_doi(value)
    return bool(doi and DOI_PATTERN.fullmatch(doi))


def sha256_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def canonical_metadata(raw: Mapping[str, Any], source: str) -> dict:
    year = raw.get("year")
    try:
        year = int(year) if year not in (None, "") else None
    except (TypeError, ValueError):
        year = None
    return {
        "doi": normalize_doi(raw.get("doi")),
        "title": str(raw.get("title") or "").strip(),
        "authors": [str(v).strip() for v in raw.get("authors", []) if str(v).strip()],
        "journal": str(raw["journal"]).strip() if raw.get("journal") else None,
        "year": year,
        "database_source": source,
        "source_record_id": raw.get("source_record_id")
    }

