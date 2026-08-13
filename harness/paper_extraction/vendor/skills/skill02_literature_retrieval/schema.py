from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Mapping, Optional

SKILL_ID = "skill02_literature_retrieval"
SKILL_VERSION = "0.2.0"


def sha256_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def normalize_doi(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I)
    return doi.lower() or None


def candidate_from_raw(raw: Mapping[str, Any]) -> Dict[str, Any]:
    title = str(raw.get("title") or "").strip()
    source = str(raw.get("source") or "").strip()
    identifiers = {str(k).lower(): str(v) for k, v in dict(raw.get("identifiers") or {}).items() if v}
    doi = normalize_doi(raw.get("doi") or identifiers.get("doi"))
    if doi:
        identifiers["doi"] = doi
    year = raw.get("year")
    try:
        year = int(year) if year not in (None, "") else None
    except (TypeError, ValueError):
        year = None
    paper_key = doi or identifiers.get("pmid") or re.sub(r"\W+", "-", title.casefold()).strip("-")
    return {
        "paper_id": "paper:" + hashlib.sha256(paper_key.encode("utf-8")).hexdigest()[:20],
        "title": title,
        "authors": [str(v).strip() for v in raw.get("authors", []) if str(v).strip()],
        "journal": str(raw["journal"]).strip() if raw.get("journal") else None,
        "year": year,
        "identifiers": identifiers,
        "retrieval_sources": [source],
        "citation_validation": {"status": "unknown", "attempts": 0, "checks": []}
    }

