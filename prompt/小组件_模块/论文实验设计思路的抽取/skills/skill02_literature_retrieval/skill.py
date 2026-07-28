from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

try:
    from .adapters import PubMedAdapter, CrossrefAdapter, EuropePmcAdapter, ScholarAdapter, WebOfScienceAdapter, CnkiAdapter
    from .adapters.base import SourceError
    from .logger import JsonlSkillLogger
    from .query import QueryExpander, KimiK3Client
    from .ranking import RelevanceRanker
    from .schema import SKILL_ID, SKILL_VERSION, candidate_from_raw, normalize_doi, sha256_json
    from .validator import validate_input, validate_output
except ImportError:
    from adapters import PubMedAdapter, CrossrefAdapter, EuropePmcAdapter, ScholarAdapter, WebOfScienceAdapter, CnkiAdapter
    from adapters.base import SourceError
    from logger import JsonlSkillLogger
    from query import QueryExpander, KimiK3Client
    from ranking import RelevanceRanker
    from schema import SKILL_ID, SKILL_VERSION, candidate_from_raw, normalize_doi, sha256_json
    from validator import validate_input, validate_output


class LiteratureRetrievalEngine:
    def __init__(
        self,
        adapters: Optional[Mapping[str, Any]] = None,
        kimi_client: Any = None,
        logger: Optional[Callable[[Mapping[str, Any]], None]] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ):
        defaults = [
            PubMedAdapter(), CrossrefAdapter(), EuropePmcAdapter(),
            ScholarAdapter(), WebOfScienceAdapter(), CnkiAdapter()
        ]
        self.adapters = dict(adapters or {adapter.name: adapter for adapter in defaults})
        active_kimi = kimi_client if kimi_client is not None else KimiK3Client.from_environment()
        self.expander = QueryExpander(active_kimi)
        self.ranker = RelevanceRanker(active_kimi)
        self.logger = logger if logger is not None else JsonlSkillLogger()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def execute(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        started = time.perf_counter()
        input_hash = sha256_json(request)
        error = validate_input(request)
        if error:
            result = self._failure(error, input_hash)
            return self._finish(result, request, started)

        intent = request["research_intent"]
        strategy = request.get("retrieval_strategy") or {}
        expanded = self.expander.expand(intent, strategy)
        queries = expanded["queries"]
        if not queries or not any(str(q.get("query", "")).strip() for q in queries):
            error = self._error("EDX-VAL-001", "RET002", "Research request is too vague to create a query.", False)
            result = self._failure(error, input_hash, review_reason="query_needs_clarification")
            return self._finish(result, request, started)
        query_check = self._query_quality_check(queries, intent)
        if not query_check["passed"]:
            expanded = self.expander.__class__(None).expand(intent, {})
            queries = expanded["queries"]
            expanded["error"] = "query_coverage_failed"

        requested_sources = request.get("sources") or strategy.get("recommended_sources") or list(self.adapters)
        limit = max(1, int(request.get("limit", 20)))
        max_queries = max(1, int(request.get("max_queries", 3)))
        raw_records: List[Dict[str, Any]] = []
        source_statuses: Dict[str, Dict[str, Any]] = {}
        warnings: List[Dict[str, Any]] = []
        retrieved_at = self.clock().isoformat()

        for source in requested_sources:
            adapter = self.adapters.get(source)
            if adapter is None:
                source_statuses[source] = {"status": "not_configured", "papers_found": 0}
                warnings.append({"code": "RET002", "source": source, "message": "Adapter is not configured."})
                continue
            found_count = 0
            attempted = 0
            source_state = "available"
            for query_info in queries[:max_queries]:
                query = str(query_info.get("query", "")).strip()
                if not query:
                    continue
                attempted += 1
                try:
                    batch = adapter.search(query, limit)
                    for raw in batch.records:
                        record = dict(raw)
                        record["_query_used"] = query
                        record["_retrieved_at"] = retrieved_at
                        raw_records.append(record)
                    found_count += len(batch.records)
                except SourceError as exc:
                    source_state = exc.state
                    code = "RET003" if exc.rate_limited else "RET002"
                    warnings.append({"code": code, "source": source, "message": str(exc)})
                    break
                except Exception as exc:
                    source_state = "unavailable"
                    warnings.append({"code": "RET002", "source": source, "message": type(exc).__name__})
                    break
            source_statuses[source] = {"status": source_state, "papers_found": found_count, "queries_attempted": attempted}

        for raw in request.get("manual_candidates", []):
            record = dict(raw)
            record["source"] = "ManualUpload"
            record["_query_used"] = "manual_upload"
            record["_retrieved_at"] = retrieved_at
            raw_records.append(record)
        if request.get("manual_candidates"):
            source_statuses["ManualUpload"] = {"status": "available", "papers_found": len(request["manual_candidates"]), "queries_attempted": 0}

        candidates, annotations = self._normalize_deduplicate(raw_records, intent)
        candidates = sorted(candidates, key=lambda c: (-annotations[c["paper_id"]]["relevance_score"], -(c.get("year") or 0), c["title"].casefold()))[:limit]
        annotations = {c["paper_id"]: annotations[c["paper_id"]] for c in candidates}
        result_state = "results" if candidates else "empty_result"

        output = {
            "candidates": candidates,
            "candidate_annotations": annotations,
            "queries": queries,
            "source_statuses": source_statuses,
            "result_state": result_state,
        }
        checks = validate_output(output) + [self._query_quality_check(queries, intent)]
        if not all(check["passed"] for check in checks):
            result = self._failure(self._error("EDX-VAL-002", "RET004", "Output self-check failed.", False), input_hash)
            return self._finish(result, request, started)

        configured_attempted = [v for v in source_statuses.values() if v.get("queries_attempted", 0) > 0]
        all_failed = bool(configured_attempted) and all(v["status"] != "available" for v in configured_attempted)
        if all_failed and not candidates:
            status = "needs_review"
            review_requests = [{"reason": "all_sources_failed", "field_path": "source_statuses"}]
        else:
            status = "succeeded_with_warnings" if warnings or expanded["error"] else "succeeded"
            review_requests = []
        if not candidates and not all_failed:
            warnings.append({"code": "RET004", "message": "No database returned a candidate; no paper was generated."})
        if expanded["error"]:
            warnings.append({"code": "RET005", "message": "Kimi-K3 query expansion failed; original query fallback used."})

        result = {
            "status": status,
            "output": output,
            "artifacts": [],
            "self_check": {"passed": True, "checks": checks, "score": 1.0},
            "warnings": warnings,
            "errors": [],
            "metrics": {"papers_found": len(candidates), "raw_records": len(raw_records)},
            "provenance": {
                "skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": sha256_json(output),
                "query_hash": sha256_json(queries), "retrieved_at": retrieved_at,
                "model_used": expanded["model_used"]
            },
            "review_requests": review_requests
        }
        return self._finish(result, request, started)

    def _normalize_deduplicate(self, raw_records: Sequence[Mapping[str, Any]], intent: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        candidates: List[Dict[str, Any]] = []
        annotations: Dict[str, Dict[str, Any]] = {}
        for raw in raw_records:
            if not raw.get("source") or not str(raw.get("title") or "").strip():
                continue
            candidate = candidate_from_raw(raw)
            existing = self._find_duplicate(candidates, candidate)
            if existing is None:
                candidates.append(candidate)
                score = self.ranker.score(candidate, intent)
                annotations[candidate["paper_id"]] = {
                    **score,
                    "retrieval_sources": [{
                        "source": raw["source"], "retrieval_time": raw["_retrieved_at"],
                        "query_used": raw["_query_used"], "source_record_id": raw.get("source_record_id")
                    }],
                    "citation_validation_status": "pending"
                }
            else:
                existing["retrieval_sources"] = list(dict.fromkeys(existing["retrieval_sources"] + [str(raw["source"])]))
                existing["identifiers"].update(candidate["identifiers"])
                if not existing["authors"] and candidate["authors"]:
                    existing["authors"] = candidate["authors"]
                if not existing["journal"] and candidate["journal"]:
                    existing["journal"] = candidate["journal"]
                if not existing["year"] and candidate["year"]:
                    existing["year"] = candidate["year"]
                annotations[existing["paper_id"]]["retrieval_sources"].append({
                    "source": raw["source"], "retrieval_time": raw["_retrieved_at"],
                    "query_used": raw["_query_used"], "source_record_id": raw.get("source_record_id")
                })
        return candidates, annotations

    @staticmethod
    def _find_duplicate(candidates: Sequence[Mapping[str, Any]], candidate: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        doi = normalize_doi(candidate.get("identifiers", {}).get("doi"))
        pmid = candidate.get("identifiers", {}).get("pmid")
        normalized_title = re.sub(r"\W+", " ", candidate["title"].casefold()).strip()
        for existing in candidates:
            if doi and doi == normalize_doi(existing.get("identifiers", {}).get("doi")):
                return existing  # type: ignore[return-value]
            if pmid and pmid == existing.get("identifiers", {}).get("pmid"):
                return existing  # type: ignore[return-value]
            other_title = re.sub(r"\W+", " ", existing["title"].casefold()).strip()
            if normalized_title and SequenceMatcher(None, normalized_title, other_title).ratio() >= 0.94:
                return existing  # type: ignore[return-value]
        return None

    @staticmethod
    def _query_quality_check(queries: Sequence[Mapping[str, Any]], intent: Mapping[str, Any]) -> Dict[str, Any]:
        query_text = " ".join(str(q.get("query", "")) for q in queries).casefold()
        required = [
            str(intent[name]).casefold()
            for name in ("organism", "phenotype", "engineering_objective")
            if intent.get(name)
        ]
        covered = all(
            value in query_text or any(token in query_text for token in re.findall(r"[a-z0-9-]+|[\u4e00-\u9fff]{2,}", value))
            for value in required
        )
        return {"name": "query_quality_coverage", "passed": covered}

    def _finish(self, result: Dict[str, Any], request: Mapping[str, Any], started: float) -> Dict[str, Any]:
        result["metrics"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        event = {
            "skill_name": SKILL_ID, "timestamp": self.clock().isoformat(),
            "input_reference": "skill01_output", "search_sources": list(request.get("sources") or []),
            "queries_used": result.get("output", {}).get("queries", []) if result.get("output") else [],
            "papers_found": result["metrics"].get("papers_found", 0),
            "errors": result["errors"], "model_used": result["provenance"].get("model_used"),
            "status": result["status"], "input_hash": result["provenance"]["input_hash"],
            "output_hash": result["provenance"]["output_hash"]
        }
        try:
            self.logger(event)
        except Exception:
            pass
        return result

    @staticmethod
    def _error(code: str, local_code: str, message: str, retryable: bool) -> Dict[str, Any]:
        return {
            "code": code, "local_code": local_code, "category": "retrieval",
            "message": message, "retryable": retryable, "severity": "error",
            "context": {}, "suggested_action": "Inspect source status and retry policy."
        }

    def _failure(self, error: Dict[str, Any], input_hash: str, review_reason: Optional[str] = None) -> Dict[str, Any]:
        return {
            "status": "needs_review" if review_reason else ("retryable_failure" if error["retryable"] else "terminal_failure"),
            "output": None, "artifacts": [],
            "self_check": {"passed": False, "checks": [], "score": 0.0},
            "warnings": [], "errors": [error], "metrics": {},
            "provenance": {
                "skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": None, "model_used": None
            },
            "review_requests": [{"reason": review_reason, "field_path": "research_intent"}] if review_reason else []
        }


def execute(request: Mapping[str, Any], **kwargs: Any) -> Dict[str, Any]:
    return LiteratureRetrievalEngine(**kwargs).execute(request)
