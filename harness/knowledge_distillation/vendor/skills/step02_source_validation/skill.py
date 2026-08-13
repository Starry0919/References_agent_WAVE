"""Step02 - identify and validate the knowledge source.

Deterministic keyword classification only - this step never invents an
ISBN/DOI/edition it wasn't given (SKILL.md 十一.13), and course notes are
never silently promoted to textbook authority (SKILL.md Step02 note 6).
"""
from __future__ import annotations

import re

VERSION = "0.1.0"

TYPE_KEYWORDS = {
    "textbook": ["textbook", "教材", "introduction to", "principles of"],
    "monograph": ["monograph", "专著"],
    "handbook": ["handbook", "手册"],
    "manual": ["lab manual", "experimental manual", "实验手册"],
    "guideline": ["guideline", "guidance", "指南"],
    "database_entry": ["database", "数据库条目", "ecocyc", "uniprot", "kegg", "ecosal"],
    "review_article": ["review", "综述"],
    "protocol": ["protocol", "sop", "方法规范"],
    "course_material": ["lecture notes", "课程讲义", "slides", "课件"],
    "primary_research": ["original research", "research article", "原创论文"],
}

AUTHORITY_LEVEL = {
    "textbook": "high", "monograph": "high", "guideline": "high",
    "handbook": "medium_high", "manual": "medium_high", "review_article": "medium_high",
    "database_entry": "medium", "protocol": "medium",
    "course_material": "low_medium", "primary_research": "context_dependent", "unknown": "low",
}

EDITION_SENSITIVE_TYPES = {"textbook", "monograph", "handbook"}

_CJK = re.compile(r"[一-鿿]")


def _classify(text):
    low = (text or "").lower()
    for source_type, keywords in TYPE_KEYWORDS.items():
        if any(kw in low or kw in (text or "") for kw in keywords):
            return source_type
    return "unknown"


def _detect_language(*texts):
    joined = "".join(t for t in texts if t)
    if not joined.strip():
        return "unknown"
    cjk = len(_CJK.findall(joined))
    return "zh" if cjk / max(len(joined), 1) > 0.15 else "en"


def execute(request, **kwargs):
    src = request["source_ref"]
    source_id = src.get("source_id", "unknown_source")
    biblio = src.get("bibliographic") or {}
    title = biblio.get("title", "")
    hint = biblio.get("source_type", "")
    source_type = _classify(hint) if _classify(hint) != "unknown" else _classify(title)

    isbn = biblio.get("isbn") or []
    doi = biblio.get("doi") or ""
    authors = biblio.get("authors_or_editors") or []
    publisher = biblio.get("publisher") or ""
    year = biblio.get("publication_year")
    edition = biblio.get("edition") or ""

    verification_evidence = []
    if isbn:
        verification_evidence.append("isbn")
    if doi:
        verification_evidence.append("doi")
    if authors and publisher and year:
        verification_evidence.append("authors_publisher_year")
    identity_verified = bool(title) and bool(verification_evidence)

    limitations = []
    unresolved_edition = False
    if not identity_verified:
        limitations.append("identity_unverified: insufficient bibliographic evidence (need isbn, doi, or authors+publisher+year).")
    if source_type in EDITION_SENSITIVE_TYPES and not edition:
        unresolved_edition = True
        limitations.append("unresolved_edition: edition not provided; do not silently merge with other editions of the same title.")
    if source_type == "course_material":
        limitations.append("course_material is not auto-promoted to textbook authority even if it resembles one.")
    if not src.get("raw_text") and src.get("source_ref_type") not in {"bibliographic", "intermediate_artifact"}:
        limitations.append("no raw_text supplied; downstream parsing/extraction will have nothing to work on.")

    language = _detect_language(title, src.get("raw_text", ""))

    validated = {
        "source_id": source_id,
        "source_type": source_type,
        "title": title,
        "title_zh": title if language == "zh" else "",
        "title_en": title if language == "en" else "",
        "authors_or_editors": authors,
        "edition": edition or "unresolved_edition",
        "publisher": publisher,
        "publication_year": year,
        "isbn": isbn,
        "doi": doi,
        "chapter": biblio.get("chapter", ""),
        "page_range": biblio.get("page_range", ""),
        "source_language": language,
        "access_type": src.get("source_ref_type", "unknown"),
        "identity_verified": identity_verified,
        "verification_evidence": verification_evidence,
        "authority_level": AUTHORITY_LEVEL.get(source_type, "low"),
        "scope": biblio.get("scope", ""),
        "limitations": limitations,
        "unresolved_edition": unresolved_edition,
    }

    errors = []
    if not identity_verified:
        errors.append({"code": "SOURCE_IDENTITY_ERROR", "message": f"{source_id}: could not verify source identity from supplied bibliographic data.", "retryable": True, "source_id": source_id})
    if unresolved_edition:
        errors.append({"code": "UNRESOLVED_EDITION", "message": f"{source_id}: edition not specified for an edition-sensitive source type ({source_type}).", "retryable": True, "source_id": source_id})

    status = "needs_review" if (not identity_verified or unresolved_edition) else "succeeded"
    return {
        "output": validated, "status": status, "errors": errors,
        "provenance": {"step_version": VERSION, "source_ids": [source_id]},
    }
