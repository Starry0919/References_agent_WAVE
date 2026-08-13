from __future__ import annotations

import json
from pathlib import Path

from .adapters import CrossrefAdapter, OpenAlexAdapter, ScholarlyAdapter
from .identity import deduplicate
from .models import DiscoveryResult, ScientificLiteratureRequest, SourceRun
from .query import generate_queries
from .relevance import assess
from .classification import classify
from .routing import ranking_score, route


class LiteratureDiscoveryService:
    """Small, synchronous orchestration boundary suitable for a workflow node.

    Source failures are isolated. A JSON cache makes repeated benchmark and
    development runs deterministic and avoids unnecessary scholarly API load.
    """

    def __init__(self, adapters: list[ScholarlyAdapter] | None = None, cache_dir: Path | None = None):
        self.adapters = adapters or [OpenAlexAdapter(), CrossrefAdapter()]
        self.cache_dir = cache_dir

    def discover(self, request: ScientificLiteratureRequest, use_cache: bool = True) -> DiscoveryResult:
        sources = [a.name for a in self.adapters]
        queries = generate_queries(request, sources)
        cache_path = self._cache_path(request, queries)
        if use_cache and cache_path and cache_path.is_file():
            cached = DiscoveryResult.model_validate_json(cache_path.read_text(encoding="utf-8"))
            self._classify_rank(cached.candidates, request)
            return cached
        candidates = []
        runs: dict[str, SourceRun] = {name: SourceRun(source=name) for name in sources}
        adapter_map = {a.name: a for a in self.adapters}
        for query in queries:
            run = runs[query.target_source]
            run.query_count += 1
            try:
                found = adapter_map[query.target_source].search(query, request.max_results_per_query, request.year_from, request.year_until)
                run.raw_hits += len(found)
                candidates.extend(found)
            except Exception as exc:  # source isolation is an explicit contract
                run.errors.append(f"{query.query_id}: {type(exc).__name__}: {exc}")
        canonical = deduplicate(candidates)
        self._classify_rank(canonical, request)
        if not any((request.desired_publication_forms, request.desired_research_designs, request.desired_engineering_modes,
                    request.desired_evidence_modalities, request.desired_knowledge_contributions,
                    request.desired_evidence_strengths, request.desired_routes)):
            canonical = self._diversify(canonical)
        result = DiscoveryResult(request=request, queries=queries, candidates=canonical, source_runs=list(runs.values()))
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = cache_path.with_suffix(".tmp")
            tmp.write_text(result.model_dump_json(indent=2), encoding="utf-8")
            tmp.replace(cache_path)
        return result

    @staticmethod
    def _classify_rank(canonical, request):
        for candidate in canonical:
            candidate.relevance = assess(candidate, request)
            classified = classify(candidate)
            candidate.metadata_classification = classified.model_dump()
            candidate.final_classification = classified.model_dump()
            candidate.classification_conflicts = classified.conflict_fields
            candidate.route = route(classified)
            candidate.route_confidence = candidate.route["confidence"]
            desired = {
                "publication_form": request.desired_publication_forms,
                "research_design": request.desired_research_designs,
                "engineering_modes": request.desired_engineering_modes,
                "evidence_modalities": request.desired_evidence_modalities,
                "knowledge_contributions": request.desired_knowledge_contributions,
                "evidence_strength": request.desired_evidence_strengths,
            }
            candidate.ranking_score_v2 = ranking_score(candidate, desired)
        if request.sort_mode == "RECENT": key = lambda c: (c.year or 0, c.ranking_score_v2 or 0)
        elif request.sort_mode == "DIRECT_ENGINEERING": key = lambda c: ((c.route or {}).get("value") == "PRIMARY_EXPERIMENTAL_ROUTE", c.ranking_score_v2 or 0)
        elif request.sort_mode == "REVIEW_SYNTHESIS": key = lambda c: ((c.route or {}).get("value") == "REVIEW_SYNTHESIS_ROUTE", c.ranking_score_v2 or 0)
        elif request.sort_mode == "EVIDENCE_STRENGTH": key = lambda c: ("DIRECT_PRIMARY_EVIDENCE" in str(c.final_classification), c.ranking_score_v2 or 0)
        else: key = lambda c: (c.ranking_score_v2 or 0, len(c.source_records))
        canonical.sort(key=key, reverse=True)

    @staticmethod
    def _diversify(candidates):
        """Keep direct relevance first while reserving bounded scientific-route diversity."""
        buckets = {}
        for candidate in candidates: buckets.setdefault((candidate.route or {}).get("value", "BACKGROUND_ROUTE"), []).append(candidate)
        selected, used = [], set()
        quotas = {"PRIMARY_EXPERIMENTAL_ROUTE": 15, "REVIEW_SYNTHESIS_ROUTE": 4, "MODEL_ROUTE": 3,
                  "METHOD_ROUTE": 2, "RESOURCE_ROUTE": 2, "BENCHMARK_ROUTE": 2, "BACKGROUND_ROUTE": 2}
        for route_name, quota in quotas.items():
            for candidate in buckets.get(route_name, [])[:quota]: selected.append(candidate); used.add(candidate.candidate_id)
        selected.extend(x for x in candidates if x.candidate_id not in used)
        return selected

    def _cache_path(self, request, queries) -> Path | None:
        if self.cache_dir is None:
            return None
        import hashlib
        key = json.dumps({"request": request.model_dump(mode="json"), "queries": [q.model_dump(mode="json", exclude={"created_at"}) for q in queries], "contract": "1.0"}, sort_keys=True)
        return self.cache_dir / f"{hashlib.sha256(key.encode()).hexdigest()}.json"

    @staticmethod
    def refine_with_fulltext(candidate: PaperCandidate, canonical_document: dict) -> PaperCandidate:
        """Add full-text refinement without erasing metadata-stage provenance."""
        previous = candidate.metadata_classification
        refined = classify(candidate, canonical_document.get("text", ""), previous)
        candidate.fulltext_classification = refined.model_dump()
        candidate.final_classification = refined.model_dump()
        candidate.classification_conflicts = refined.conflict_fields
        candidate.route = route(refined)
        candidate.route_confidence = candidate.route["confidence"]
        candidate.ranking_score_v2 = ranking_score(candidate)
        return candidate

    @staticmethod
    def filter_candidates(candidates, **filters):
        """Service-level v2 filters; unknown filters fail closed."""
        out = []
        for candidate in candidates:
            classification = candidate.final_classification or candidate.metadata_classification
            if not classification: continue
            axes = {name: {x["value"] for x in classification[name]["labels"]} for name in
                    ("publication_form", "research_design", "engineering_modes", "evidence_modalities", "knowledge_contributions", "evidence_strength")}
            ok = True
            for key, wanted in filters.items():
                wanted = {wanted} if isinstance(wanted, str) else set(wanted)
                if key == "route": ok &= (candidate.route or {}).get("value") in wanted
                elif key == "fulltext_status": ok &= candidate.acquisition.state.value in wanted
                elif key == "host_relation": ok &= bool(candidate.relevance and candidate.relevance.host_relation.value in wanted)
                elif key in axes: ok &= bool(axes[key] & wanted)
                elif key == "year": ok &= candidate.year in wanted
                else: ok = False
            if ok: out.append(candidate)
        return out
