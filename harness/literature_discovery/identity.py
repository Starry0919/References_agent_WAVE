from __future__ import annotations

import hashlib
import re
from difflib import SequenceMatcher

from .models import PaperCandidate


def normalized_title(title: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", title.casefold()))


def resolve_identities(candidates: list[PaperCandidate], fuzzy_threshold: float = 0.965):
    canonical: list[PaperCandidate] = []
    doi_index: dict[str, PaperCandidate] = {}
    id_index: dict[str, PaperCandidate] = {}
    conflicts=[]
    for item in candidates:
        target = doi_index.get(item.doi) if item.doi else None
        for identifier in (item.pmid, item.pmcid, item.openalex_id):
            if target is None and identifier:
                target = id_index.get(identifier)
        norm = normalized_title(item.canonical_title)
        if target is None:
            for existing in canonical:
                other = normalized_title(existing.canonical_title)
                similarity=SequenceMatcher(None,norm,other).ratio()
                author_overlap=bool(set(a.casefold() for a in item.authors)&set(a.casefold() for a in existing.authors))
                if norm == other or (len(norm)>=25 and similarity>=fuzzy_threshold and (item.year==existing.year or author_overlap)):
                    if item.year and existing.year and item.year!=existing.year:
                        conflicts.append({"type":"TITLE_MATCH_DIFFERENT_YEAR","left":existing.candidate_id,"right":item.candidate_id});continue
                    target = existing
                    break
        if target is not None:
            if item.doi and target.doi and item.doi!=target.doi:
                conflicts.append({"type":"IDENTIFIER_CONFLICT","left":target.candidate_id,"right":item.candidate_id});target=None
            elif item.doi and target.doi and item.doi==target.doi and normalized_title(item.canonical_title)!=normalized_title(target.canonical_title) and SequenceMatcher(None,norm,normalized_title(target.canonical_title)).ratio()<.75:
                conflicts.append({"type":"SAME_DOI_DIFFERENT_TITLE","left":target.candidate_id,"right":item.candidate_id});target=None
        if target is not None:
            _merge(target, item)
            continue
        item.candidate_id = "paper_" + hashlib.sha256((item.doi or norm).encode()).hexdigest()[:16]
        canonical.append(item)
        if item.doi:
            doi_index[item.doi] = item
        for identifier in (item.pmid, item.pmcid, item.openalex_id):
            if identifier:
                id_index[identifier] = item
    return canonical,conflicts

def deduplicate(candidates: list[PaperCandidate], fuzzy_threshold: float = 0.965) -> list[PaperCandidate]:
    return resolve_identities(candidates,fuzzy_threshold)[0]


def _merge(target: PaperCandidate, other: PaperCandidate) -> None:
    for field in ("doi", "pmid", "pmcid", "openalex_id", "year", "venue", "abstract", "publication_type"):
        if getattr(target, field) in (None, "", []):
            setattr(target, field, getattr(other, field))
    target.authors = list(dict.fromkeys([*target.authors, *other.authors]))
    target.oa_urls = list(dict.fromkeys([*target.oa_urls, *other.oa_urls]))
    target.source_records.extend(other.source_records)
    target.is_review = target.is_review or other.is_review
