"""Multi-objective Candidate Comparator (doc05 §4.7/§3.8): builds one
`CandidateEvaluationVector` per candidate - every dimension is an explicit
`{mode, value_or_level, unit, basis, source}` dict, `mode` always one of
`computed`/`qualitative`/`not_computed` so an unscored dimension can never
silently read as zero or medium (doc05 §5.3) - then computes Pareto
dominance only over dimensions that are actually comparable, after hard
constraints and blocking critical findings have already eliminated
ineligible candidates. Never collapses to one composite score (doc05 §4.7's
own "禁止用未经校准的单一 overall_score 掩盖维度冲突").
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.engineering_design import decision as decision_mod
from harness.engineering_design.evaluators.tradeoff import build_tradeoff_profile
from harness.engineering_design.models import BuildTestPackage, CandidateDesign, EngineeringDesignProject
from harness.ids import new_id, now
from harness.scientific_evaluation.models import (
    SEVERITY_LEVELS,
    CandidateEvaluationVector,
    CriticFinding,
    EvaluationCase,
    EvidenceAssessment,
    ScientificReview,
)

# {dimension: (scale_low_to_high, higher_is_better)}
_ORDINAL_SCALES: dict[str, tuple[tuple[str, ...], bool]] = {
    "genetic_complexity": (("low", "medium", "high"), False),
    "growth_impact": (("none", "low", "moderate", "elevated"), False),
    "risk": (("informational", "minor", "moderate", "major", "critical", "none"), False),
    "uncertainty": (("low", "medium", "high"), False),
    "evidence_strength": (("unknown", "insufficient", "weak", "moderate", "strong"), True),
    "buildability": (("conceptual", "evaluated", "planning_ready", "build_ready"), True),
}


def _dim(mode: str, value: Any, unit: str, basis: str, source: str) -> dict[str, Any]:
    return {"mode": mode, "value_or_level": value, "unit": unit, "basis": basis, "source": source}


def _build_vector_dims(
    candidate: CandidateDesign, proj: EngineeringDesignProject, evidence: list[EvidenceAssessment],
    findings: list[CriticFinding], session: Session,
) -> dict[str, Any]:
    cd = {"genetic_modifications": candidate.genetic_modifications, "portfolio_role": candidate.portfolio_role}
    hard_results = decision_mod.check_hard_constraints(cd, proj.hard_constraints)
    if any(r["satisfied"] is False for r in hard_results):
        hard_status = "violated"
    elif any(r["satisfied"] is None for r in hard_results):
        hard_status = "unknown"
    else:
        hard_status = "satisfied"

    obj_vector = decision_mod.compute_objective_vector(cd, primary_metrics=proj.primary_metrics, counterfactual_results=candidate.counterfactual_results)
    primary = obj_vector[0] if obj_vector else None
    if primary is None:
        production_potential = _dim("not_computed", "unknown", "unspecified", "no primary_metrics declared on the design project", "none")
    elif primary["magnitude"] != "not_computed":
        production_potential = _dim("computed", primary["magnitude"], primary["unit"], primary["basis"], primary["evidence_tier"])
    else:
        production_potential = _dim("qualitative", primary["direction_estimate"], primary["unit"], primary["basis"], primary["evidence_tier"])

    profile = build_tradeoff_profile(cd)
    growth_impact = _dim("qualitative", profile["growth_burden_risk"], "ordinal(none<low<moderate<elevated)", profile["growth_burden_detail"], profile["evidence_tier"])

    n = len(candidate.genetic_modifications)
    genetic_complexity = _dim("computed", "low" if n <= 1 else ("medium" if n == 2 else "high"), "ordinal(low<medium<high)", f"{n} declared genetic modification(s)", "deterministic_rule")

    stability_findings = [f for f in findings if f.category == "buildability_or_stability"]
    if stability_findings:
        worst = max((f.severity for f in stability_findings), key=lambda s: SEVERITY_LEVELS.index(s))
        stability = _dim("qualitative", "at_risk" if worst in ("major", "critical") else "minor_concern", "categorical", f"{len(stability_findings)} buildability_or_stability finding(s), worst={worst}", "critic")
    else:
        stability = _dim("not_computed", "unknown", "categorical", "no stability assay or critic finding on record", "none")

    buildability = _dim("qualitative", candidate.readiness, "ordinal(conceptual<evaluated<planning_ready<build_ready)", "CandidateDesign.readiness", "deterministic_rule")

    pkg = session.get(BuildTestPackage, candidate.build_test_package_id) if candidate.build_test_package_id else None
    cost_info = pkg.estimated_time_cost_and_risk if pkg is not None else {}
    experimental_cost = _dim("qualitative", cost_info.get("cost", "unknown"), "unspecified", "BuildTestPackage.estimated_time_cost_and_risk", "human_or_agent_estimate") if cost_info else _dim("not_computed", "unknown", "unspecified", "no BuildTestPackage.estimated_time_cost_and_risk recorded", "none")
    time_to_result = _dim("qualitative", cost_info.get("time", "unknown"), "unspecified", "BuildTestPackage.estimated_time_cost_and_risk", "human_or_agent_estimate") if cost_info else _dim("not_computed", "unknown", "unspecified", "no BuildTestPackage.estimated_time_cost_and_risk recorded", "none")

    if evidence:
        strengths = [a.overall_strength for a in evidence]
        order = ("unknown", "insufficient", "weak", "moderate", "strong")
        worst_strength = min(strengths, key=lambda s: order.index(s) if s in order else 0)
        evidence_strength = _dim("qualitative", worst_strength, "ordinal(unknown<insufficient<weak<moderate<strong)", f"weakest overall_strength across {len(strengths)} EvidenceAssessment(s) - never averaged upward", "deterministic_rule")
    else:
        evidence_strength = _dim("not_computed", "unknown", "ordinal", "no EvidenceAssessment on record", "none")

    if findings:
        worst_sev = max((f.severity for f in findings), key=lambda s: SEVERITY_LEVELS.index(s))
        risk = _dim("qualitative", worst_sev, "ordinal(informational<minor<moderate<major<critical)", f"worst CriticFinding severity across {len(findings)} finding(s)", "critic")
    else:
        risk = _dim("qualitative", "none", "ordinal", "no CriticFinding raised", "critic")

    if candidate.portfolio_role == "information_gain":
        information_gain = _dim("qualitative", "high", "ordinal", "portfolio_role=information_gain", "deterministic_rule")
    elif candidate.portfolio_role == "reference_or_control":
        information_gain = _dim("qualitative", "not_applicable", "ordinal", "baseline/reference candidate", "deterministic_rule")
    else:
        information_gain = _dim("not_computed", "unknown", "ordinal", "no diagnostic information-value quantification available for this candidate", "none")

    total_dims = len(evidence) + (1 if primary is not None else 0)
    unknown_dims = sum(1 for a in evidence if a.overall_strength in ("unknown", "insufficient")) + (1 if primary is not None and primary["magnitude"] == "not_computed" else 0)
    if total_dims == 0:
        uncertainty = _dim("not_computed", "unknown", "ordinal(low<medium<high)", "no evidence or objective data to assess uncertainty from", "none")
    else:
        ratio = unknown_dims / total_dims
        level = "high" if ratio > 0.6 else ("medium" if ratio > 0.2 else "low")
        uncertainty = _dim("qualitative", level, "ordinal(low<medium<high)", f"{unknown_dims}/{total_dims} underlying data points are unknown/insufficient/not_computed", "deterministic_rule")

    return {
        "hard_constraint_status": hard_status, "production_potential": production_potential, "growth_impact": growth_impact,
        "stability": stability, "buildability": buildability, "genetic_complexity": genetic_complexity,
        "experimental_cost": experimental_cost, "time_to_result": time_to_result, "evidence_strength": evidence_strength,
        "risk": risk, "information_gain": information_gain, "uncertainty": uncertainty,
    }


def build_candidate_evaluation_vectors(
    session: Session, *, case: EvaluationCase, proj: EngineeringDesignProject, candidates: list[CandidateDesign],
    evidence_by_design: dict[str, list[EvidenceAssessment]], findings_by_design: dict[str, list[CriticFinding]],
) -> list[CandidateEvaluationVector]:
    ts = now()
    rows: list[CandidateEvaluationVector] = []
    for c in candidates:
        dims = _build_vector_dims(c, proj, evidence_by_design.get(c.design_id, []), findings_by_design.get(c.design_id, []), session)
        row = CandidateEvaluationVector(
            vector_id=new_id("CVEC"), evaluation_id=case.evaluation_id, candidate_id=c.design_id, design_version=c.design_version,
            hard_constraint_status=dims["hard_constraint_status"], production_potential=dims["production_potential"],
            growth_impact=dims["growth_impact"], stability=dims["stability"], buildability=dims["buildability"],
            genetic_complexity=dims["genetic_complexity"], experimental_cost=dims["experimental_cost"],
            time_to_result=dims["time_to_result"], evidence_strength=dims["evidence_strength"], risk=dims["risk"],
            information_gain=dims["information_gain"], uncertainty=dims["uncertainty"], pareto_status=None,
            dominates=[], dominated_by=[], excluded_reasons=[], created_at=ts,
        )
        session.add(row)
        rows.append(row)
    session.flush()

    eligible: dict[str, CandidateEvaluationVector] = {}
    for row, c in zip(rows, candidates):
        reasons = []
        if row.hard_constraint_status == "violated":
            reasons.append("hard_constraint_status=violated")
        blocking = [f for f in findings_by_design.get(c.design_id, []) if f.blocking and f.severity == "critical"]
        if blocking:
            reasons.append(f"{len(blocking)} unresolved blocking critical CriticFinding(s)")
        if c.portfolio_role == "reference_or_control":
            reasons.append("reference_or_control baseline - excluded from dominance selection, not from reporting")
        if reasons:
            row.excluded_reasons = reasons
        else:
            eligible[c.design_id] = row

    _compute_pareto(eligible)
    for row in rows:
        if row.pareto_status is None:
            row.pareto_status = "excluded" if row.excluded_reasons else "not_computed"
    session.flush()
    return rows


def _ordinal_dims(v: CandidateEvaluationVector) -> dict[str, Any]:
    return {
        "genetic_complexity": v.genetic_complexity, "growth_impact": v.growth_impact, "risk": v.risk,
        "uncertainty": v.uncertainty, "evidence_strength": v.evidence_strength, "buildability": v.buildability,
    }


def _dominates(a: CandidateEvaluationVector, b: CandidateEvaluationVector) -> bool | None:
    dims_a, dims_b = _ordinal_dims(a), _ordinal_dims(b)
    at_least_as_good, strictly_better, comparable = True, False, False
    for name, (scale, higher_better) in _ORDINAL_SCALES.items():
        da, db = dims_a[name], dims_b[name]
        if da["mode"] == "not_computed" or db["mode"] == "not_computed":
            continue
        va, vb = da["value_or_level"], db["value_or_level"]
        if va not in scale or vb not in scale:
            continue
        comparable = True
        sa, sb = scale.index(va), scale.index(vb)
        if not higher_better:
            sa, sb = -sa, -sb
        if sa < sb:
            at_least_as_good = False
            break
        if sa > sb:
            strictly_better = True
    if not comparable:
        return None
    return at_least_as_good and strictly_better


def _compute_pareto(eligible: dict[str, CandidateEvaluationVector]) -> None:
    ids = list(eligible)
    for i in ids:
        comparisons = [_dominates(eligible[j], eligible[i]) for j in ids if j != i]
        if not any(cmp is not None for cmp in comparisons):
            eligible[i].pareto_status = "not_computed"
            continue
        dominated_by = [j for j in ids if j != i and _dominates(eligible[j], eligible[i])]
        dominates = [j for j in ids if j != i and _dominates(eligible[i], eligible[j])]
        eligible[i].dominated_by = dominated_by
        eligible[i].dominates = dominates
        eligible[i].pareto_status = "dominated" if dominated_by else "nondominated"
