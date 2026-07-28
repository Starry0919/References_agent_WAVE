from __future__ import annotations
import time
from typing import Any, Mapping
try:
    from .schema import SKILL_ID, SKILL_VERSION, POLICY, get_fields, get_extensions, sha256_json
    from .error_codes import error
    from .logger import JsonlSkillLogger
    from .evaluators import completeness, evidence_quality, logic_quality, variable_quality, workflow_quality, reproducibility, method_quality
    from .scoring import calculate
    from .risk import detect
    from .validator import validate
except ImportError:
    from schema import SKILL_ID, SKILL_VERSION, POLICY, get_fields, get_extensions, sha256_json
    from error_codes import error
    from logger import JsonlSkillLogger
    from evaluators import completeness, evidence_quality, logic_quality, variable_quality, workflow_quality, reproducibility, method_quality
    from scoring import calculate
    from risk import detect
    from validator import validate

class QualityEvaluationEngine:
    def __init__(self, logger=None):
        self.logger = logger if logger is not None else JsonlSkillLogger()

    def execute(self, request: Mapping[str, Any]):
        started = time.perf_counter()
        input_hash = sha256_json(request)
        skill08 = request.get("skill08_output") if isinstance(request, Mapping) else None
        if not isinstance(skill08, Mapping):
            return self._finish(self._failure(error("EVAL001"), input_hash), started)
        fields = get_fields(skill08)
        if not isinstance(fields, Mapping) or not fields:
            return self._finish(self._failure(error("EVAL001"), input_hash), started)
        skill07 = request.get("skill07_output")
        extensions = get_extensions(skill08, skill07)
        conflicts = skill08.get("conflicts", [])
        missing = sorted(k for k, v in fields.items() if v.get("status") == "unknown")
        dimensions = {
            "field_completeness": completeness.evaluate(fields),
            "evidence_quality": evidence_quality.evaluate(fields, skill08),
            "experimental_logic": logic_quality.evaluate(fields, extensions),
            "variable_quality": variable_quality.evaluate(extensions),
            "workflow_quality": workflow_quality.evaluate(fields, extensions),
            "reproducibility": reproducibility.evaluate(fields),
            "method_quality": method_quality.evaluate(fields),
        }
        overall, score_details = calculate(dimensions)
        report = {
            "dimensions": dimensions,
            "missing_information": [{"field": k, "importance": "high" if k in {"strain", "engineering_method", "culture_conditions", "replicates", "assay"} else "medium"} for k in missing],
            "risks": detect(dimensions, missing, conflicts),
            "overall_score": overall,
            "confidence": self._confidence(dimensions["evidence_quality"], conflicts),
            "recommendation": self._recommendation(overall, dimensions["evidence_quality"]["grade"]),
        }
        checks = validate(report, fields)
        if not all(c["passed"] for c in checks):
            return self._finish(self._failure(error("EVAL003", [c["name"] for c in checks if not c["passed"]]), input_hash), started)
        quality = {
            "completeness": dimensions["field_completeness"]["score"] / 100,
            "reproducibility": dimensions["reproducibility"]["score"] / 100,
            "evidence_level": dimensions["evidence_quality"]["score"] / 100,
            "missing_information": missing,
            "extraction_confidence": dimensions["evidence_quality"]["score"] / 100,
        }
        output = {"quality_evaluation": quality, "evaluation_report": report, "score_details": score_details}
        warnings, reviews = [], []
        if not skill08.get("evidence_map"):
            warnings.append(error("EVAL002")); reviews.append({"reason": "missing_evidence", "fields": [k for k, v in fields.items() if v.get("status") == "reported"]})
        if conflicts:
            warnings.append(error("EVAL004", {"count": len(conflicts)})); reviews.append({"reason": "data_conflict", "fields": [v.get("field") for v in conflicts]})
        if overall < 50:
            reviews.append({"reason": "low_quality", "overall_score": overall})
        status = "needs_review" if reviews else "succeeded"
        result = {
            "status": status, "output": output, "artifacts": [],
            "self_check": {"passed": True, "checks": checks, "score": 1.0},
            "warnings": warnings, "errors": [],
            "metrics": {"fields_evaluated": len(fields), "evidence_coverage": dimensions["evidence_quality"]["coverage"],
                        "logic_score": dimensions["experimental_logic"]["score"], "workflow_score": dimensions["workflow_quality"]["score"],
                        "overall_score": overall},
            "provenance": {"skill_id": SKILL_ID, "skill_version": SKILL_VERSION, "input_hash": input_hash,
                           "output_hash": sha256_json(output), "paper_id": skill08.get("evidence_linked_design", {}).get("paper_id", "unknown"),
                           "scoring_policy_version": request.get("scoring_policy_version", POLICY),
                           "formula_ids": ["weighted-sum-v1", "evidence-grade-v1"]},
            "review_requests": reviews,
        }
        return self._finish(result, started)

    @staticmethod
    def _confidence(evidence, conflicts):
        if conflicts or evidence["grade"] == "D": return "low"
        if evidence["grade"] == "A": return "high"
        return "medium"

    @staticmethod
    def _recommendation(score, grade):
        if score >= 80 and grade in {"A", "B"}: return "Suitable for downstream engineering analysis with normal review."
        if score >= 50: return "Use downstream only after resolving listed missing information and evidence issues."
        return "Do not use as a standalone downstream input; human review and source completion are required."

    def _finish(self, result, started):
        result["metrics"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        event = {"skill_name": SKILL_ID, "paper_id": result["provenance"].get("paper_id"),
                 "fields_evaluated": result["metrics"].get("fields_evaluated", 0),
                 "evidence_coverage": result["metrics"].get("evidence_coverage", 0),
                 "logic_score": result["metrics"].get("logic_score", 0),
                 "workflow_score": result["metrics"].get("workflow_score", 0),
                 "overall_score": result["metrics"].get("overall_score", 0),
                 "errors": result["errors"], "status": result["status"]}
        try: self.logger(event)
        except Exception: pass
        return result

    @staticmethod
    def _failure(err, input_hash):
        return {"status": "terminal_failure", "output": None, "artifacts": [],
                "self_check": {"passed": False, "checks": [], "score": 0.0},
                "warnings": [], "errors": [err], "metrics": {},
                "provenance": {"skill_id": SKILL_ID, "skill_version": SKILL_VERSION, "input_hash": input_hash, "output_hash": None},
                "review_requests": []}

def execute(request: Mapping[str, Any], **kwargs):
    return QualityEvaluationEngine(**kwargs).execute(request)
