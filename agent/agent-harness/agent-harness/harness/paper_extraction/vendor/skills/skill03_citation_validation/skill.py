from __future__ import annotations

import copy
import time
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

try:
    from .adapters import CrossrefClient, PubMedClient, EuropePmcClient
    from .adapters.base import DatabaseUnavailable
    from .error_codes import error
    from .logger import JsonlSkillLogger
    from .schema import SKILL_ID, SKILL_VERSION, canonical_metadata, normalize_doi, sha256_json, valid_doi_format
    from .validator import MetadataMatcher, RetrySearcher
except ImportError:
    from adapters import CrossrefClient, PubMedClient, EuropePmcClient
    from adapters.base import DatabaseUnavailable
    from error_codes import error
    from logger import JsonlSkillLogger
    from schema import SKILL_ID, SKILL_VERSION, canonical_metadata, normalize_doi, sha256_json, valid_doi_format
    from validator import MetadataMatcher, RetrySearcher


class CitationValidationGate:
    def __init__(
        self,
        clients: Optional[Sequence[Any]] = None,
        logger: Optional[Callable[[Mapping[str, Any]], None]] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ):
        self.clients = list(clients or [CrossrefClient(), PubMedClient(), EuropePmcClient()])
        self.matcher = MetadataMatcher()
        self.retry_searcher = RetrySearcher()
        self.logger = logger if logger is not None else JsonlSkillLogger()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def execute(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        started = time.perf_counter()
        input_hash = sha256_json(request)
        candidates = request.get("candidates") if isinstance(request, Mapping) else None
        if not isinstance(candidates, list):
            result = self._failure(error("DOI001", {"field": "candidates"}), input_hash)
            return self._finish(result, started)

        validated, accepted, validation_results = [], [], []
        warnings, review_requests = [], []
        for candidate in candidates:
            result, updated = self._validate_candidate(candidate)
            validation_results.append(result)
            validated.append(updated)
            if result["final_decision"] == "accepted":
                accepted.append(updated)
            elif result["final_decision"] == "needs_review":
                review_requests.append({"reason": result["failure_reason"], "paper_id": candidate.get("paper_id")})
            else:
                warnings.append({"code": "DOI005", "paper_id": candidate.get("paper_id"), "message": result["failure_reason"]})

        output = {
            "validated_candidates": validated,
            "accepted_candidates": accepted,
            "validation_results": validation_results
        }
        checks = self._self_check(output)
        if not all(v["passed"] for v in checks):
            result = self._failure(error("DOI005", {"failed_checks": [v["name"] for v in checks if not v["passed"]]}), input_hash)
            return self._finish(result, started)

        status = "needs_review" if review_requests else ("succeeded_with_warnings" if warnings else "succeeded")
        result = {
            "status": status, "output": output, "artifacts": [],
            "self_check": {"passed": True, "checks": checks, "score": 1.0},
            "warnings": warnings, "errors": [],
            "metrics": {
                "papers_checked": len(candidates), "accepted": len(accepted),
                "rejected": sum(v["final_decision"] == "rejected" for v in validation_results)
            },
            "provenance": {
                "skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": sha256_json(output),
                "sources_checked": [client.name for client in self.clients]
            },
            "review_requests": review_requests
        }
        return self._finish(result, started)

    def _validate_candidate(self, candidate: Mapping[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        original_doi = normalize_doi(candidate.get("identifiers", {}).get("doi"))
        audit: List[Dict[str, Any]] = []
        best_metadata = None
        best_report = None
        best_score = -1.0
        any_database_response = False
        any_database_available = False
        sources_checked = []
        attempts_used = 0

        for strategy in self.retry_searcher.strategies(candidate):
            attempts_used = strategy["attempt"]
            query = strategy["query"]
            if strategy["mode"] == "doi" and not valid_doi_format(query):
                audit.append({
                    "attempt": strategy["attempt"], "mode": "doi", "query": query,
                    "source": None, "status": "invalid_format", "error_code": "DOI001"
                })
                continue
            for client in self.clients:
                sources_checked.append(client.name)
                retrieved_at = self.clock().isoformat()
                try:
                    if strategy["mode"] == "doi":
                        raw_items = [client.lookup_doi(query)]
                    else:
                        raw_items = client.search(query, 5)
                    any_database_available = True
                    raw_items = [item for item in raw_items if item]
                    if not raw_items:
                        audit.append({
                            "attempt": strategy["attempt"], "mode": strategy["mode"], "query": query,
                            "source": client.name, "status": "not_found", "retrieved_at": retrieved_at,
                            "error_code": "DOI002"
                        })
                        continue
                    any_database_response = True
                    for raw in raw_items:
                        metadata = canonical_metadata(raw, client.name)
                        report = self.matcher.compare(candidate, metadata)
                        score = (
                            report["title_similarity"] * 0.5
                            + report["author_overlap"] * 0.2
                            + report["journal_similarity"] * 0.2
                            + (1.0 if report["year_match"] else 0.0) * 0.1
                        )
                        audit.append({
                            "attempt": strategy["attempt"], "mode": strategy["mode"], "query": query,
                            "source": client.name, "status": "verified" if report["all_core_match"] else "mismatch",
                            "retrieved_at": retrieved_at, "metadata_hash": sha256_json(metadata),
                            "matching_report": report
                        })
                        if score > best_score:
                            best_metadata, best_report, best_score = metadata, report, score
                        if report["all_core_match"] and valid_doi_format(metadata["doi"]):
                            return self._decision(
                                candidate, original_doi, metadata, report, audit, attempts_used,
                                sources_checked, "verified", "accepted", None
                            )
                except DatabaseUnavailable as exc:
                    audit.append({
                        "attempt": strategy["attempt"], "mode": strategy["mode"], "query": query,
                        "source": client.name, "status": "database_unavailable",
                        "retrieved_at": retrieved_at, "error_code": "DOI004",
                        "error_type": type(exc).__name__
                    })

        if not any_database_available:
            validation_status, final_decision, reason = "failed", "needs_review", "all_databases_unavailable"
        elif best_report and best_report["has_unknown"] and best_report["title_match"]:
            validation_status, final_decision, reason = "mismatch", "needs_review", "partial_metadata_unconfirmed"
        elif any_database_response:
            validation_status, final_decision, reason = "failed", "rejected", "metadata_mismatch_after_3_attempts"
        else:
            validation_status, final_decision, reason = "not_found", "rejected", "doi_not_found_after_3_attempts"
        return self._decision(
            candidate, original_doi, best_metadata, best_report, audit, attempts_used,
            sources_checked, validation_status, final_decision, reason
        )

    def _decision(self, candidate, original_doi, metadata, report, audit, attempts, sources, validation_status, decision, reason):
        updated = copy.deepcopy(dict(candidate))
        schema_status = {
            "accepted": "valid", "rejected": "invalid", "needs_review": "conflict" if metadata else "unknown"
        }[decision]
        updated["citation_validation"] = {
            "status": schema_status, "attempts": min(attempts, 3),
            "checks": [{"source": v.get("source"), "status": v["status"], "attempt": v["attempt"]} for v in audit]
        }
        if decision == "accepted" and metadata:
            if metadata.get("doi"):
                updated.setdefault("identifiers", {})["doi"] = metadata["doi"]
            updated["title"] = metadata["title"]
            updated["authors"] = metadata["authors"]
            updated["journal"] = metadata["journal"]
            updated["year"] = metadata["year"]
        result = {
            "paper_id": candidate.get("paper_id"),
            "original_candidate": {
                "original_title": candidate.get("title"),
                "original_doi": original_doi,
                "original_source": candidate.get("retrieval_sources", [])
            },
            "doi_validation_status": validation_status,
            "doi_metadata": metadata,
            "matching_report": report,
            "final_decision": decision,
            "failure_reason": reason,
            "validation_attempts": min(attempts, 3),
            "sources_checked": list(dict.fromkeys(sources)),
            "audit_trail": audit,
            "skill04_eligible": decision == "accepted"
        }
        return result, updated

    @staticmethod
    def _self_check(output):
        results = output["validation_results"]
        source_check = all(
            r["final_decision"] != "accepted"
            or (r["doi_metadata"] and r["doi_metadata"].get("database_source"))
            for r in results
        )
        hallucination = all(r["final_decision"] != "accepted" or r["audit_trail"] for r in results)
        retry_limit = all(r["validation_attempts"] <= 3 for r in results)
        status_check = all(
            (r["final_decision"] != "accepted" or (r["matching_report"] and r["matching_report"]["all_core_match"]))
            and (r["final_decision"] != "rejected" or bool(r["failure_reason"]))
            for r in results
        )
        gate_check = all(c["citation_validation"]["status"] == "valid" for c in output["accepted_candidates"])
        return [
            {"name": "doi_database_source", "passed": source_check},
            {"name": "metadata_identity_consistency", "passed": status_check},
            {"name": "no_database_no_acceptance", "passed": hallucination},
            {"name": "retry_limit", "passed": retry_limit},
            {"name": "skill04_gate", "passed": gate_check}
        ]

    def _finish(self, result, started):
        result["metrics"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        validations = result.get("output", {}).get("validation_results", []) if result.get("output") else []
        event = {
            "skill_name": SKILL_ID, "timestamp": self.clock().isoformat(),
            "input_paper_id": [v.get("paper_id") for v in validations],
            "original_doi": [v.get("original_candidate", {}).get("original_doi") for v in validations],
            "validation_attempts": [v.get("validation_attempts") for v in validations],
            "sources_checked": result["provenance"].get("sources_checked", []),
            "final_status": [v.get("final_decision") for v in validations],
            "errors": result["errors"],
            "human_review_required": result["status"] == "needs_review",
            "input_hash": result["provenance"]["input_hash"],
            "output_hash": result["provenance"]["output_hash"]
        }
        try:
            self.logger(event)
        except Exception:
            pass
        return result

    @staticmethod
    def _failure(err, input_hash):
        return {
            "status": "terminal_failure", "output": None, "artifacts": [],
            "self_check": {"passed": False, "checks": [], "score": 0.0},
            "warnings": [], "errors": [err], "metrics": {},
            "provenance": {
                "skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": None, "sources_checked": []
            },
            "review_requests": []
        }


def execute(request: Mapping[str, Any], **kwargs: Any) -> Dict[str, Any]:
    return CitationValidationGate(**kwargs).execute(request)

