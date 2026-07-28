from __future__ import annotations
import time
from typing import Any, Mapping
try:
    from .schema import SKILL_ID, SKILL_VERSION, POLICY, sha256_json, inferred, unknown
    from .error_codes import error
    from .logger import JsonlSkillLogger
    from .objective import cluster
    from .comparison import normalize, build as build_matrix
    from .adaptation import analyze, assess_transferability
    from .risk import assess as assess_risk
    from .candidate import build as build_candidate
    from .validator import validate
except ImportError:
    from schema import SKILL_ID, SKILL_VERSION, POLICY, sha256_json, inferred, unknown
    from error_codes import error
    from logger import JsonlSkillLogger
    from objective import cluster
    from comparison import normalize, build as build_matrix
    from adaptation import analyze, assess_transferability
    from risk import assess as assess_risk
    from candidate import build as build_candidate
    from validator import validate

class K12AdaptationEngine:
    def __init__(self, logger=None):
        self.logger = logger if logger is not None else JsonlSkillLogger()

    def execute(self, request: Mapping[str, Any]):
        started = time.perf_counter()
        input_hash = sha256_json(request)
        target = request.get("target_system") if isinstance(request, Mapping) else None
        if not isinstance(target, Mapping) or not target.get("organism") or not target.get("strain_family"):
            return self._finish(self._failure(error("K12_001"), input_hash), started)
        designs = request.get("experimental_designs", [])
        evidences = request.get("evidence_objects", [])
        qualities = request.get("quality_reports", [])
        if not designs or not (len(designs) == len(evidences) == len(qualities)):
            return self._finish(self._failure(error("K12_004", {"reason": "input arrays must be non-empty and aligned"}), input_hash), started)
        normalized = [normalize(d, e, q, i) for i, (d, e, q) in enumerate(zip(designs, evidences, qualities))]
        objective_items = [{"paper_id": x["paper_id"], "objective": x["objective"]} for x in normalized]
        clusters = cluster(objective_items)
        membership = {pid: c["objective_cluster"] for c in clusters for pid in c["paper_ids"]}
        matrix = build_matrix(normalized, clusters)
        analyses, transfers, risks, candidates, unified = [], [], [], [], []
        warnings, reviews = [], []
        for item in normalized:
            analysis = analyze(item, target)
            transfer = assess_transferability(analysis)
            risk = assess_risk(item, analysis)
            analysis["transferability"] = transfer
            analyses.append(analysis); transfers.append(transfer); risks.append(risk)
            candidates.append(build_candidate(item, analysis, transfer, risk, membership[item["paper_id"]]))
            unified.append(self._unified(item, analysis, transfer, risk, target))
            if analysis["compatibility"] == "unknown":
                warnings.append(error("K12_004", {"paper_id": item["paper_id"]}))
                reviews.append({"reason": "unknown_compatibility", "paper_id": item["paper_id"]})
            if item["literature_facts"]["biological_system"]["organism_strain"] is None:
                warnings.append(error("K12_002", {"paper_id": item["paper_id"]}))
            if item["quality"]["evidence_grade"] in {"C", "D", "unknown"}:
                reviews.append({"reason": "low_evidence", "paper_id": item["paper_id"]})
            if risk["risk_level"] == "high":
                reviews.append({"reason": "migration_risk", "paper_id": item["paper_id"]})
        if len(clusters) > 1:
            warnings.append(error("K12_003", {"clusters": len(clusters)}))
            reviews.append({"reason": "objective_exclusion", "objective_clusters": [c["objective_cluster"] for c in clusters]})
        output = {"objective_clusters": clusters, "comparison_matrix": matrix, "k12_analysis": analyses,
                  "risk_assessment": risks, "candidate_design_space": candidates, "k12_transfer_analyses": unified,
                  "analysis_notice": "Candidate design space only; no ranking, best-strategy selection, or final proposal is produced."}
        checks = validate(output, normalized)
        if not all(x["passed"] for x in checks):
            return self._finish(self._failure(error("K12_004", [x["name"] for x in checks if not x["passed"]]), input_hash), started)
        result = {"status": "needs_review" if reviews else "succeeded", "output": output, "artifacts": [],
                  "self_check": {"passed": True, "checks": checks, "score": 1.0},
                  "warnings": warnings, "errors": [],
                  "metrics": {"papers_processed": len(normalized), "objective_clusters": len(clusters),
                              "comparisons_generated": len(matrix), "k12_assessments": len(analyses),
                              "risks_identified": sum(len(x["risks"]) for x in risks)},
                  "provenance": {"skill_id": SKILL_ID, "skill_version": SKILL_VERSION, "input_hash": input_hash,
                                 "output_hash": sha256_json(output), "analysis_policy_version": POLICY},
                  "review_requests": reviews}
        return self._finish(result, started)

    @staticmethod
    def _unified(item, analysis, transfer, risk, target):
        ids, confidence = item["evidence_ids"], analysis["confidence"]
        strain = item["literature_facts"]["biological_system"]["organism_strain"]
        strategy = item["literature_facts"]["engineering_strategy"]["modification"]
        outcome = item["literature_facts"]["outcome"]
        rationale = "AI K-12 compatibility analysis derived from evidence-bound literature fields and Skill09 quality."
        return {
            "target_context": f"{target['organism']} {target['strain_family']}",
            "strain_difference": inferred({"source_strain": strain, "compatibility": analysis["basis"]["strain_similarity"]}, ids, rationale, confidence) if strain else unknown("Source strain was not reported."),
            "engineering_strategy": inferred({"literature_strategy": strategy, "transferability": transfer["transferability"]}, ids, rationale, confidence) if strategy else unknown("Engineering strategy was not reported."),
            "advantages": inferred(["Literature-supported outcome is available."], ids, rationale, confidence) if outcome else unknown("No literature-supported outcome was available."),
            "limitations": inferred([x["detail"] for x in risk["risks"]], ids, rationale, confidence) if ids else unknown("Evidence-bound limitations could not be produced."),
            "transferability_risk": inferred({"level": risk["risk_level"], "validation_needed": transfer["validation_needed"]}, ids, rationale, confidence) if ids else unknown("Transferability could not be evidence-bound."),
        }

    def _finish(self, result, started):
        result["metrics"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        event = {"skill_name": SKILL_ID, **{k: result["metrics"].get(k, 0) for k in
                 ("papers_processed", "objective_clusters", "comparisons_generated", "k12_assessments", "risks_identified")},
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
    return K12AdaptationEngine(**kwargs).execute(request)
