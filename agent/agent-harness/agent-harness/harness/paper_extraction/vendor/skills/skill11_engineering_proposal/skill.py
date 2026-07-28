from __future__ import annotations
import time
from typing import Any, Mapping
try:
    from .schema import SKILL_ID, SKILL_VERSION, POLICY, sha256_json
    from .error_codes import error
    from .logger import JsonlSkillLogger
    from .planner import build_objective, map_steps, details_for
    from .step import reported_steps, combination_steps
    from .reasoning import reported as reported_rationale, combination as combination_rationale
    from .validation import build as build_validation
    from .risk import build as build_risks
    from .approval import route
    from .validator import validate
except ImportError:
    from schema import SKILL_ID, SKILL_VERSION, POLICY, sha256_json
    from error_codes import error
    from logger import JsonlSkillLogger
    from planner import build_objective, map_steps, details_for
    from step import reported_steps, combination_steps
    from reasoning import reported as reported_rationale, combination as combination_rationale
    from validation import build as build_validation
    from risk import build as build_risks
    from approval import route
    from validator import validate

class EngineeringPlanEngine:
    def __init__(self, logger=None):
        self.logger = logger if logger is not None else JsonlSkillLogger()

    def execute(self, request: Mapping[str, Any]):
        started = time.perf_counter(); input_hash = sha256_json(request)
        space = request.get("k12_design_space") if isinstance(request, Mapping) else None
        if not isinstance(space, Mapping) or "candidate_design_space" not in space:
            return self._finish(self._failure(error("PLAN001"), input_hash), started)
        user_target = request.get("user_target") if isinstance(request, Mapping) else None
        candidates = space.get("candidate_design_space", [])
        clusters = space.get("objective_clusters", [])
        rows = {x.get("paper_id"): x for x in space.get("comparison_matrix", [])}
        supported, removed = [], []
        for candidate in candidates:
            if candidate.get("literature_support", {}).get("evidence_ids"):
                supported.append(candidate)
            else:
                removed.append(candidate.get("candidate_id", "unknown"))
        plans = []
        for candidate in supported:
            paper_id = candidate["literature_support"]["paper_id"]
            details = details_for(candidate, rows.get(paper_id, {}))
            steps = reported_steps(candidate, details)
            plans.append({"plan_id": f"plan:{paper_id}", "track": "A", "source_type": "reported_in_literature",
                          "objective": build_objective(candidate, clusters, user_target=user_target),
                          "design_rationale": reported_rationale(candidate),
                          "experimental_details": details, "dbtl_plan": map_steps(steps),
                          "validation_plan": build_validation(details, candidate),
                          "risks": build_risks(candidate), "alternatives": [],
                          "approval_status": {"approval_required": False, "status": "auto_eligible_reported_only"}})
        ai = self._combinations(supported, clusters, user_target)
        approval = route(plans, ai)
        for plan in ai: plan["approval_status"] = approval
        unified = self._unified(plans, ai, removed)
        output = {"engineering_plans": plans, "ai_combination_proposals": ai,
                  "ai_engineering_proposal": unified, "approval_status": approval,
                  "removed_unsupported_candidates": removed}
        checks = validate(output)
        warnings, reviews = [], []
        if removed:
            warnings.append(error("PLAN002", {"candidate_ids": removed}))
            reviews.append({"reason": "unsupported_candidates_removed", "candidate_ids": removed})
        if not plans:
            warnings.append(error("PLAN001", {"reason": "no evidence-supported candidates"}))
            reviews.append({"reason": "incomplete_plan"})
        if ai:
            reviews.append({"reason": "ai_level_2", "proposal_ids": [x["plan_id"] for x in ai]})
        if approval["approval_required"]:
            reviews.append({"reason": "human_approval_required", "details": approval["reason"]})
        if not all(x["passed"] for x in checks):
            warnings.append(error("PLAN004", [x["name"] for x in checks if not x["passed"]]))
            reviews.append({"reason": "incomplete_plan"})
        reported_count = sum(len(v) for p in plans for v in p["dbtl_plan"].values())
        ai_count = sum(len(v) for p in ai for v in p["dbtl_plan"].values())
        evidence_coverage = 1.0 if reported_count else 0.0
        result = {"status": "needs_review" if reviews else "succeeded", "output": output, "artifacts": [],
                  "self_check": {"passed": all(x["passed"] for x in checks), "checks": checks,
                                 "score": sum(x["passed"] for x in checks) / len(checks)},
                  "warnings": warnings, "errors": [],
                  "metrics": {"reported_steps": reported_count, "ai_steps": ai_count,
                              "evidence_coverage": evidence_coverage, "approval_required": approval["approval_required"]},
                  "provenance": {"skill_id": SKILL_ID, "skill_version": SKILL_VERSION, "input_hash": input_hash,
                                 "output_hash": sha256_json(output), "planning_policy_version": POLICY},
                  "review_requests": reviews}
        return self._finish(result, started)

    @staticmethod
    def _combinations(candidates, clusters, user_target=None):
        proposals = []
        for group in clusters:
            members = [c for c in candidates if c["objective_cluster"] == group["objective_cluster"]]
            distinct = []
            seen = set()
            for c in members:
                key = str(c["candidate_strategy"])
                if key not in seen: distinct.append(c); seen.add(key)
            if len(distinct) < 2: continue
            steps = combination_steps(distinct)
            rationale = combination_rationale(distinct)
            literature_objective = group.get("representative_objective")
            if literature_objective and literature_objective != "unknown":
                phenotype, source = literature_objective, "reported_in_literature"
            elif user_target:
                phenotype, source = user_target, "user_specified_not_literature_verified"
            else:
                phenotype, source = "unknown", "unknown"
            proposals.append({"plan_id": f"ai-combination:{group['objective_cluster']}", "track": "B",
                              "source_type": "ai_generated_proposal", "objective": {
                                  "target_phenotype": phenotype, "target_phenotype_source": source,
                                  "organism": "Escherichia coli", "strain": "K-12",
                                  "statement": f"{phenotype} in Escherichia coli K-12"},
                              "design_rationale": rationale, "experimental_details": {"parameters": "unknown; human definition required"},
                              "dbtl_plan": map_steps(steps),
                              "validation_plan": {"strategy": "staged single-candidate controls before combination", "checkpoints": ["human approval", "single-strategy baselines", "combination comparison"]},
                              "risks": {"biological": ["Combined phenotype is unknown."], "technical": ["Combined construction complexity is unknown."],
                                        "interpretation": ["Interaction effects may prevent attribution."]},
                              "alternatives": [{"candidate_id": x["candidate_id"], "strategy": x["candidate_strategy"]} for x in distinct]})
        return proposals

    @staticmethod
    def _unified(plans, ai, removed):
        primary = plans[0] if plans else None
        objective = primary["objective"]["statement"] if primary else "unknown — no evidence-supported candidate"
        steps = [s for phase in ("design", "build", "test", "learn") for s in primary["dbtl_plan"][phase]] if primary else []
        risks = ([x for values in primary["risks"].values() for x in values] if primary else ["No evidence-supported plan could be generated."])
        alternatives = [p["plan_id"] for p in plans[1:]] + [p["plan_id"] for p in ai]
        return {"proposal_label": "ai_engineering_proposal", "objective": objective, "steps": steps,
                "assumptions": ["Execution requires Skill12 human governance.", "Unknown parameters must be completed without inventing literature facts."],
                "risks": risks, "alternatives": alternatives + [f"removed:{x}" for x in removed]}

    def _finish(self, result, started):
        result["metrics"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        event = {"skill_name": SKILL_ID, "reported_steps": result["metrics"].get("reported_steps", 0),
                 "ai_steps": result["metrics"].get("ai_steps", 0), "evidence_coverage": result["metrics"].get("evidence_coverage", 0),
                 "approval_required": result["metrics"].get("approval_required", False), "errors": result["errors"], "status": result["status"]}
        try: self.logger(event)
        except Exception: pass
        return result

    @staticmethod
    def _failure(err, input_hash):
        return {"status": "terminal_failure", "output": None, "artifacts": [], "self_check": {"passed": False, "checks": [], "score": 0.0},
                "warnings": [], "errors": [err], "metrics": {}, "provenance": {"skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": None}, "review_requests": []}

def execute(request: Mapping[str, Any], **kwargs):
    return EngineeringPlanEngine(**kwargs).execute(request)
