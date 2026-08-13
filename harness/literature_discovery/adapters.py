from __future__ import annotations

import html
import re
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx

from .models import PaperCandidate, SearchQueryRecord, SourceRecord


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    doi = value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi.rstrip(" .") or None


def strip_markup(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(value))).strip() or None


class ScholarlyAdapter(ABC):
    name: str

    def __init__(self, timeout: float = 20, retries: int = 2, client: httpx.Client | None = None):
        self.timeout = timeout
        self.retries = retries
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=True, headers={"User-Agent": "WAVE-Literature/0.1 (research metadata client)"})

    def _get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        last: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = self.client.get(url, params=params)
                if response.status_code == 429 or response.status_code >= 500:
                    if attempt < self.retries:
                        wait = min(float(response.headers.get("Retry-After", 2**attempt)), 10)
                        time.sleep(wait)
                        continue
                response.raise_for_status()
                return response.json()
            except (httpx.TimeoutException, httpx.HTTPError, ValueError) as exc:
                last = exc
                if attempt < self.retries:
                    time.sleep(min(2**attempt, 5))
        raise RuntimeError(f"{self.name} request failed: {last}")

    @abstractmethod
    def search(self, query: SearchQueryRecord, limit: int, year_from: int | None = None, year_until: int | None = None) -> list[PaperCandidate]: ...


class OpenAlexAdapter(ScholarlyAdapter):
    name = "openalex"
    URL = "https://api.openalex.org/works"

    def search(self, query: SearchQueryRecord, limit: int, year_from: int | None = None, year_until: int | None = None) -> list[PaperCandidate]:
        filters = []
        if year_from:
            filters.append(f"from_publication_date:{year_from}-01-01")
        if year_until:
            filters.append(f"to_publication_date:{year_until}-12-31")
        params: dict[str, Any] = {"search": query.query_text, "per-page": min(limit, 100), "sort": "relevance_score:desc"}
        if filters:
            params["filter"] = ",".join(filters)
        data = self._get(self.URL, params)
        return [self._normalize(item, query) for item in data.get("results", [])]

    def _normalize(self, item: dict[str, Any], query: SearchQueryRecord) -> PaperCandidate:
        authors = [a.get("author", {}).get("display_name") for a in item.get("authorships", []) if a.get("author", {}).get("display_name")]
        locations = item.get("locations") or []
        oa_urls = []
        for loc in [item.get("best_oa_location") or {}, *locations]:
            url = loc.get("pdf_url")
            if url and url not in oa_urls:
                oa_urls.append(url)
        abstract = item.get("abstract_inverted_index")
        if isinstance(abstract, dict):
            words = sorted(((pos, word) for word, positions in abstract.items() for pos in positions), key=lambda x: x[0])
            abstract = " ".join(word for _, word in words)
        doi = normalize_doi(item.get("doi"))
        oid = item.get("id")
        cid = doi or str(oid or item.get("title") or "unknown")
        pub_type = item.get("type")
        return PaperCandidate(
            candidate_id=f"openalex:{cid}", canonical_title=strip_markup(item.get("title")) or "Untitled", doi=doi,
            openalex_id=oid, authors=authors, year=item.get("publication_year"),
            venue=((item.get("primary_location") or {}).get("source") or {}).get("display_name"),
            abstract=abstract, publication_type=pub_type, is_review=pub_type in {"review", "systematic-review"}, oa_urls=oa_urls,
            source_records=[SourceRecord(source=self.name, source_record_id=oid, query_id=query.query_id, raw={"id": oid, "doi": item.get("doi"), "type": pub_type, "is_oa": (item.get("open_access") or {}).get("is_oa")})],
        )


class CrossrefAdapter(ScholarlyAdapter):
    name = "crossref"
    URL = "https://api.crossref.org/works"

    def search(self, query: SearchQueryRecord, limit: int, year_from: int | None = None, year_until: int | None = None) -> list[PaperCandidate]:
        params: dict[str, Any] = {"query.bibliographic": query.query_text, "rows": min(limit, 100), "select": "DOI,title,author,published,container-title,abstract,type,link"}
        filters = ["type:journal-article"]
        if year_from:
            filters.append(f"from-pub-date:{year_from}-01-01")
        if year_until:
            filters.append(f"until-pub-date:{year_until}-12-31")
        params["filter"] = ",".join(filters)
        data = self._get(self.URL, params)
        return [self._normalize(item, query) for item in data.get("message", {}).get("items", [])]

    def _normalize(self, item: dict[str, Any], query: SearchQueryRecord) -> PaperCandidate:
        title = strip_markup((item.get("title") or ["Untitled"])[0]) or "Untitled"
        doi = normalize_doi(item.get("DOI"))
        authors = [" ".join(filter(None, (a.get("given"), a.get("family")))) for a in item.get("author", [])]
        parts = ((item.get("published") or {}).get("date-parts") or [[None]])[0]
        links = [x.get("URL") for x in item.get("link", []) if x.get("content-type") == "application/pdf" and x.get("URL")]
        typ = item.get("type")
        return PaperCandidate(
            candidate_id=f"crossref:{doi or title}", canonical_title=title, doi=doi, authors=authors,
            year=parts[0] if parts else None, venue=((item.get("container-title") or [None])[0]),
            abstract=strip_markup(item.get("abstract")), publication_type=typ,
            is_review="review" in title.casefold() or typ == "review", oa_urls=links,
            source_records=[SourceRecord(source=self.name, source_record_id=doi, query_id=query.query_id, raw={"doi": item.get("DOI"), "type": typ, "subtype": item.get("subtype")})],
        )
