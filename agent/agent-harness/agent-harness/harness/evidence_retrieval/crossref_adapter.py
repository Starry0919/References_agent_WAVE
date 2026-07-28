"""Real, live `EvidenceRetrievalAdapter` backed by the Crossref REST API
(`api.crossref.org`) - confirmed reachable from this environment during
Phase C's audit (`GET /works?query=... -> 200` in ~2s). Crossref indexes
DOI-registered scholarly metadata (title/authors/year/journal/DOI) for
essentially the entire DOI corpus; it does NOT return full text or
structured biological claims, so `extract_claims()` here can only ever
produce `extraction_method="api_metadata_only"`,
`extraction_status="partial"` claim drafts (title/abstract-derived at
best) - never a fabricated organism/strain/condition value.

This adapter's most load-bearing use in Phase C is NOT search - it is DOI
verification (`resolve_doi`): a DOI Crossref cannot resolve is a real,
checkable signal that a DOI is fabricated (prompt invariant #10: "DOI 不得
补造"), independent of whatever an LLM claims about it.
"""
from __future__ import annotations

import math
import re
import time
from typing import Any

from harness.evidence_retrieval.contracts import AdapterHealth, EvidenceClaimDraft, EvidenceDocument, EvidenceSearchResult

try:
    import httpx
except ImportError:  # pragma: no cover - already a hard repo dependency
    httpx = None

_BASE_URL = "https://api.crossref.org"
_TIMEOUT_S = 10.0

# One deliberately narrow, project-facing policy.  Impact factors change
# annually and Crossref does not publish them, so callers may inject a
# licensed/current ``impact_factors`` mapping.  Preferred-journal membership
# is still useful when no metric snapshot is available, but is never labelled
# as an IF value.
DEFAULT_LITERATURE_POLICY: dict[str, Any] = {
    "organism_required": [],
    "organism_acceptable": [],
    "from_year": 2020,
    "until_year": 2026,
    "article_types": ["journal-article"],
    "preferred_journals": [
        "Nature", "Science", "Cell", "Nature Biotechnology",
        "Nature Chemical Biology", "Proceedings of the National Academy of Sciences",
        "Science Advances", "Nature Communications", "ACS Synthetic Biology",
        "Metabolic Engineering",
    ],
    "engineering_terms": [
        "genome engineering", "gene knockout", "knockout", "gene overexpression",
        "overexpression", "metabolic engineering", "synthetic regulation",
        "protein engineering", "crispr", "promoter engineering",
    ],
    "must_have_groups": [
        ["engineer", "knockout", "overexpression", "crispr", "mutation", "deletion"],
        ["experiment", "validation", "validated", "fermentation", "assay", "culture"],
        ["mechanism", "pathway", "flux", "regulation", "causal"],
        ["design", "construct", "strain", "workflow", "strategy"],
    ],
    "prefer_terms": [
        "omics", "transcriptom", "proteom", "metabolom", "multi-omics",
        "iteration", "iterative", "failure analysis", "failed", "dbtl",
        "design-build-test-learn",
    ],
    "weights": {
        "relevance": 0.45,
        "organism": 0.20,
        "journal_impact": 0.15,
        "recency": 0.10,
        "design_quality": 0.10,
    },
    "candidate_pool": 40,
    "max_results": 8,
}


class CrossrefEvidenceAdapter:
    source_name = "crossref"

    def health_check(self) -> AdapterHealth:
        if httpx is None:
            return AdapterHealth(available=False, source_name=self.source_name, reason="httpx is not installed")
        t0 = time.monotonic()
        try:
            r = httpx.get(f"{_BASE_URL}/works", params={"query": "escherichia coli", "rows": 1}, timeout=_TIMEOUT_S)
            r.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            return AdapterHealth(available=False, source_name=self.source_name, reason=f"{type(exc).__name__}: {exc}", latency=time.monotonic() - t0)
        return AdapterHealth(available=True, source_name=self.source_name, latency=time.monotonic() - t0)

    def search(self, query: str, filters: dict[str, Any] | None = None, pagination: dict[str, Any] | None = None) -> EvidenceSearchResult:
        filters = filters or {}
        pagination = pagination or {}
        policy = self._policy(filters)
        rows = min(int(pagination.get("rows", policy["candidate_pool"])), 100)
        if httpx is None:
            return EvidenceSearchResult(query=query, documents=[], source_name=self.source_name)
        focused_query = self._focused_query(query, filters.get("project_goal"))
        crossref_filters = [
            f"from-pub-date:{policy['from_year']}-01-01",
            f"until-pub-date:{policy['until_year']}-12-31",
            "type:journal-article",
        ]
        params: dict[str, Any] = {
            "query.bibliographic": focused_query,
            "rows": rows,
            "filter": ",".join(crossref_filters),
            "select": "DOI,title,author,published-print,published-online,issued,container-title,URL,abstract,type,subtype",
        }
        try:
            r = httpx.get(f"{_BASE_URL}/works", params=params, timeout=_TIMEOUT_S)
            r.raise_for_status()
            data = r.json()
        except Exception:  # noqa: BLE001 - a search failure is "no results", not a crash; health_check() is the availability signal
            return EvidenceSearchResult(query=query, documents=[], source_name=self.source_name)
        items = data.get("message", {}).get("items", [])
        ranked = []
        for item in items:
            score = self._score(item, focused_query, policy, filters.get("impact_factors", {}))
            if score["hard_filter_passed"]:
                enriched = dict(item)
                enriched["_ranking"] = score
                ranked.append((score["total_score"], self._to_document(enriched)))
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        docs = [doc for _, doc in ranked[: int(policy["max_results"])]]
        return EvidenceSearchResult(query=query, documents=docs, total_available=data.get("message", {}).get("total-results"), source_name=self.source_name)

    @staticmethod
    def _focused_query(query: str, project_goal: Any) -> str:
        goal = " ".join(str(v) for v in project_goal.values() if v) if isinstance(project_goal, dict) else str(project_goal or "")
        base = " ".join(f"{query} {goal}".split())
        return f"{base} experimental design mechanism"

    @staticmethod
    def _policy(filters: dict[str, Any]) -> dict[str, Any]:
        policy = {**DEFAULT_LITERATURE_POLICY}
        policy["weights"] = {**DEFAULT_LITERATURE_POLICY["weights"], **filters.get("weights", {})}
        for key in DEFAULT_LITERATURE_POLICY:
            if key in filters and key != "weights":
                policy[key] = filters[key]
        policy["max_results"] = max(1, min(int(policy["max_results"]), 12))
        return policy

    @staticmethod
    def _text(item: dict[str, Any]) -> str:
        return " ".join([
            " ".join(item.get("title") or []),
            item.get("abstract") or "",
            " ".join(item.get("subject") or []),
        ]).casefold()

    @classmethod
    def _score(
        cls, item: dict[str, Any], query: str, policy: dict[str, Any], impact_factors: dict[str, Any],
    ) -> dict[str, Any]:
        text = cls._text(item)
        journal = ((item.get("container-title") or [""])[0] or "").strip()
        year = cls._year(item)
        required = bool(policy["organism_required"]) and any(term in text for term in policy["organism_required"])
        acceptable = bool(policy["organism_acceptable"]) and any(term in text for term in policy["organism_acceptable"])
        engineering_hits = sorted({term for term in policy["engineering_terms"] if term in text})
        must_groups = [any(term in text for term in group) for group in policy["must_have_groups"]]
        prefer_hits = sorted({term for term in policy["prefer_terms"] if term in text})

        query_terms = {t for t in re.findall(r"[a-z0-9-]{3,}", query.casefold()) if t not in {"coli", "escherichia"}}
        relevance = len([t for t in query_terms if t in text]) / max(1, len(query_terms))
        organism_filter_active = bool(policy["organism_required"] or policy["organism_acceptable"])
        organism = 1.0 if required else (0.55 if acceptable else (0.5 if not organism_filter_active else 0.0))
        recency = max(0.0, min(1.0, ((year or policy["from_year"]) - policy["from_year"]) /
                               max(1, policy["until_year"] - policy["from_year"])))
        design_quality = min(1.0, (sum(must_groups) / len(must_groups)) * 0.8 + min(len(prefer_hits), 2) * 0.1)

        metric = impact_factors.get(journal)
        try:
            impact_factor = float(metric) if metric is not None else None
        except (TypeError, ValueError):
            impact_factor = None
        preferred = any(journal.casefold() == name.casefold() for name in policy["preferred_journals"])
        impact_score = min(1.0, math.log1p(max(impact_factor or 0.0, 0.0)) / math.log1p(20.0)) if impact_factor is not None else (0.75 if preferred else 0.0)
        weights = policy["weights"]
        total = (
            relevance * weights["relevance"] + organism * weights["organism"]
            + impact_score * weights["journal_impact"] + recency * weights["recency"]
            + design_quality * weights["design_quality"]
        )
        # Metadata-only screening cannot prove all must-haves.  Require the
        # target strain (or accepted B strain), a real engineering signal,
        # date/type, and at least two design-evidence groups; full-text
        # extraction will validate the remaining requirements.
        hard_pass = bool(
            (not organism_filter_active or required or acceptable) and engineering_hits and sum(must_groups) >= 2
            and year is not None and policy["from_year"] <= year <= policy["until_year"]
            and item.get("type") == "journal-article"
        )
        return {
            "total_score": round(total, 6),
            "components": {
                "relevance": round(relevance, 4), "organism": organism,
                "journal_impact": round(impact_score, 4), "recency": round(recency, 4),
                "design_quality": round(design_quality, 4),
            },
            "weights": weights,
            "hard_filter_passed": hard_pass,
            "organism_match": "required" if required else ("acceptable" if acceptable else "none"),
            "engineering_hits": engineering_hits,
            "must_have_metadata_hits": sum(must_groups),
            "prefer_hits": prefer_hits,
            "impact_factor": impact_factor,
            "impact_factor_status": "provided_snapshot" if impact_factor is not None else "journal_preference_proxy",
        }

    @staticmethod
    def _year(item: dict[str, Any]) -> int | None:
        for date_field in ("published-print", "published-online", "issued"):
            parts = item.get(date_field, {}).get("date-parts")
            if parts and parts[0]:
                return parts[0][0]
        return None

    def fetch(self, source_id: str) -> EvidenceDocument | None:
        """`source_id` is a DOI. Returns `None` (not a fabricated document)
        if Crossref cannot resolve it - the caller must treat `None` as
        "unresolved DOI", never silently skip the check."""
        if httpx is None:
            return None
        try:
            r = httpx.get(f"{_BASE_URL}/works/{source_id}", timeout=_TIMEOUT_S)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            item = r.json().get("message", {})
        except Exception:  # noqa: BLE001
            return None
        return self._to_document(item)

    def resolve_doi(self, doi: str) -> bool:
        """Real DOI-existence check via Crossref - the concrete mechanism
        behind invariant #10 ("hallucinated DOI 被拒绝")."""
        return self.fetch(doi) is not None

    def extract_claims(self, document: EvidenceDocument, schema_version: str) -> list[EvidenceClaimDraft]:
        # Crossref metadata has no biological content - only ever an
        # honestly-partial claim draft carrying the bibliographic facts.
        return [
            EvidenceClaimDraft(
                document=document, claim_summary=document.title or "(no title in Crossref metadata)",
                extraction_method="api_metadata_only", extraction_status="partial",
            )
        ]

    @staticmethod
    def _to_document(item: dict[str, Any]) -> EvidenceDocument:
        doi = item.get("DOI")
        title_list = item.get("title") or []
        authors = [
            " ".join(filter(None, [a.get("given"), a.get("family")]))
            for a in item.get("author", []) if isinstance(a, dict)
        ]
        year = CrossrefEvidenceAdapter._year(item)
        return EvidenceDocument(
            source_id=doi or item.get("URL", ""), source_type="literature",
            title=title_list[0] if title_list else None, authors=authors, publication_year=year,
            journal_or_repository=(item.get("container-title") or [None])[0], doi_or_accession=doi,
            url=item.get("URL"), abstract_or_summary=item.get("abstract", ""), raw_metadata=item,
        )
