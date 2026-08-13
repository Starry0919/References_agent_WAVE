"""Multi-objective and Portfolio Decision (doc04 §4.5, §2.5): hard
constraints filter first; objective values are kept as an explicit vector
with each entry's own unit, direction, basis and evidence tier - never
collapsed into a single unweighted or arbitrarily-weighted composite score.
Pareto dominance is computed only over dimensions that are actually
comparable (ordinal trade-off dimensions, plus any real numeric result a
Phase 3 counterfactual run supplies) - a primary economic metric whose
magnitude is `not_computed` never silently drops out of the vector, it just
cannot support a dominance claim on its own.
"""
from __future__ import annotations

from typing import Any

from harness.engineering_design.evaluators import evidence as evidence_mod
from harness.engineering_design.evaluators.tradeoff import build_tradeoff_profile
from harness.engineering_design.models import EVIDENCE_TIERS
from harness.workflow.gene_registry import essential_genes

_ORDINAL_SCALES: dict[str, dict[str, int]] = {
    "build_complexity": {"low": 0, "medium": 1, "high": 2},  # higher = worse
    "growth_burden_risk": {"none": 0, "low": 1, "moderate": 2, "elevated": 3},  # higher = worse
    # Module 2 (Engineering Decision Intelligence Layer prompt §13,
    # "Complexity-aware Design Ranking": performance + evidence strength +
    # risk + implementation complexity, not performance-only) - `EVIDENCE_
    # TIERS` is already ordered best-to-worst (experimental_evidence first),
    # so its index doubles directly as the "higher = worse" ordinal this
    # scale convention requires. "unknown" is deliberately left OUT of the
    # scale: `_dominates` already skips any dimension whose value isn't in
    # the scale, so a candidate with no evidence at all simply doesn't
    # support a dominance claim on this dimension, rather than being
    # silently scored as maximally bad or good.
    "evidence_strength": {tier: i for i, tier in enumerate(EVIDENCE_TIERS) if tier != "unknown"},
}


def check_hard_constraints(candidate: dict[str, Any], hard_constraints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each `hard_constraints` entry is `{"constraint": str, "type": str, ...}`.
    Recognized `type`s are checked automatically; anything else returns
    `satisfied: None` (not silently assumed to pass) with an explicit note
    that it requires human/manual review."""
    results = []
    mods = candidate.get("genetic_modifications", [])
    essential = essential_genes()
    for hc in hard_constraints:
        ctype = hc.get("type", "manual_review")
        label = hc.get("constraint", ctype)
        if ctype == "no_essential_gene_knockout":
            violators = [m["target_identifier"] for m in mods if m.get("operation") == "knockout" and m.get("target_identifier") in essential]
            results.append({"constraint": label, "satisfied": not violators, "detail": f"violating modifications: {violators}" if violators else "no essential-gene knockout present"})
        elif ctype == "max_modifications":
            limit = hc.get("value")
            results.append({"constraint": label, "satisfied": limit is None or len(mods) <= limit, "detail": f"{len(mods)} modification(s), limit={limit}"})
        else:
            results.append({"constraint": label, "satisfied": None, "detail": f"constraint type {ctype!r} is not automatically checkable - requires manual/human review"})
    return results


def compute_objective_vector(
    candidate: dict[str, Any], *, primary_metrics: list[dict[str, Any]], counterfactual_results: list[dict[str, Any]] | None = None
) -> list[dict[str, Any]]:
    profile = build_tradeoff_profile(candidate)
    counterfactual_results = counterfactual_results or []
    entries: list[dict[str, Any]] = []

    for m in primary_metrics:
        metric_name = str(m.get("metric", m.get("name", "unknown")))
        # A real Phase-3 counterfactual result whose output names this
        # metric (or an FBA objective_value standing in for "growth"/
        # "productivity") supplies an actual numeric magnitude; absent
        # that, the direction is a qualitative, non-numeric estimate only.
        matched = next((r for r in counterfactual_results if r.get("runtime_status") == "optimal" and metric_name.lower() in str(r.get("outputs", {})).lower()), None)
        if matched is not None:
            entries.append({
                "metric": metric_name, "direction_estimate": "computed", "magnitude": matched["outputs"].get("objective_value", "not_computed"),
                "unit": m.get("unit", "unspecified"), "basis": f"model_computation via {matched.get('adapter_name', 'unknown adapter')}",
                "evidence_tier": "model_computation",
            })
        else:
            has_mods = bool(candidate.get("genetic_modifications"))
            entries.append({
                "metric": metric_name,
                "direction_estimate": ("baseline" if candidate.get("portfolio_role") == "reference_or_control" else ("intended_increase" if has_mods else "unknown")),
                "magnitude": "not_computed", "unit": m.get("unit", "unspecified"),
                "basis": "qualitative: no real model computation available for this metric yet", "evidence_tier": "expert_or_llm_judgment",
            })

    entries.append({
        "metric": "build_complexity", "direction_estimate": profile["build_complexity"], "magnitude": "not_computed",
        "unit": "ordinal(low<medium<high)", "basis": profile["basis"], "evidence_tier": profile["evidence_tier"],
    })
    entries.append({
        "metric": "growth_burden_risk", "direction_estimate": profile["growth_burden_risk"], "magnitude": "not_computed",
        "unit": "ordinal(none<low<moderate<elevated)", "basis": profile["growth_burden_detail"], "evidence_tier": profile["evidence_tier"],
    })
    # Module 2 §13: evidence strength as its own Pareto-comparable dimension
    # (previously only build_complexity/growth_burden_risk were), sourced
    # from the same `evidence.strongest_tier` the EvidenceEvaluator and
    # ConfidenceEvaluator already use - never a second, independent
    # evidence-grading computation.
    strongest = evidence_mod.strongest_tier(candidate)
    entries.append({
        "metric": "evidence_strength", "direction_estimate": strongest, "magnitude": "not_computed",
        "unit": f"ordinal({'<'.join(reversed([t for t in EVIDENCE_TIERS if t != 'unknown']))}, lower=stronger)",
        "basis": "strongest evidence_links tier across this candidate's genetic_modifications" if strongest != "unknown" else "no evidence_links recorded",
        "evidence_tier": strongest,
    })
    return entries


def _dominates(a: list[dict[str, Any]], b: list[dict[str, Any]]) -> bool | None:
    """True if vector `a` Pareto-dominates `b` over the ordinal dimensions
    both vectors share (lower is better for these "risk" dimensions).
    Returns None (not computable) if neither vector has any comparable
    dimension - never guesses."""
    by_metric_a = {e["metric"]: e for e in a}
    by_metric_b = {e["metric"]: e for e in b}
    comparable = [m for m in _ORDINAL_SCALES if m in by_metric_a and m in by_metric_b]
    if not comparable:
        return None
    at_least_as_good = True
    strictly_better = False
    for m in comparable:
        scale = _ORDINAL_SCALES[m]
        va, vb = by_metric_a[m]["direction_estimate"], by_metric_b[m]["direction_estimate"]
        if va not in scale or vb not in scale:
            continue
        sa, sb = scale[va], scale[vb]
        if sa > sb:
            at_least_as_good = False
            break
        if sa < sb:
            strictly_better = True
    return at_least_as_good and strictly_better


def compute_pareto_status(vectors_by_design: dict[str, list[dict[str, Any]]]) -> dict[str, str]:
    """doc04 §2.5: dominance is preserved explicitly per candidate, never
    collapsed into a ranked list by a hidden weighted sum. Returns
    `{design_id: "dominated"|"nondominated"|"not_computed"}`."""
    ids = list(vectors_by_design)
    status: dict[str, str] = {}
    for i in ids:
        comparisons = [d is not None for j in ids if j != i for d in [_dominates(vectors_by_design[j], vectors_by_design[i])]]
        if not comparisons or not any(comparisons):
            status[i] = "not_computed"
            continue
        dominated_by_someone = any(
            _dominates(vectors_by_design[j], vectors_by_design[i]) for j in ids if j != i
        )
        status[i] = "dominated" if dominated_by_someone else "nondominated"
    return status


def recommend_portfolio(
    *,
    evaluations_by_design: dict[str, dict[str, Any]],  # design_id -> {"hard_constraint_results", "objective_vector", "blocking_findings", "portfolio_role"}
    preferences_or_weights: list[dict[str, Any]],
) -> dict[str, Any]:
    """doc04 §4.5: hard constraints filter first; Pareto trade-off is
    always preserved in the output. A recommendation is only produced when
    the user has stated explicit preferences - otherwise the function
    returns the nondominated set and says so, rather than forcing a single
    answer doc04 §2.5 forbids.

    `reference_or_control` is excluded from the selectable/dominance pool:
    it has zero modifications by construction, so on the risk-only ordinal
    dimensions available before a real model prediction exists it would
    trivially "dominate" every real candidate - selecting it would mean
    recommending doing nothing, which is a comparison baseline, not an
    engineering recommendation. It is still evaluated and reported."""
    baseline_ids = {did for did, ev in evaluations_by_design.items() if ev.get("portfolio_role") == "reference_or_control"}
    selectable = {did: ev for did, ev in evaluations_by_design.items() if did not in baseline_ids}

    eligible = {
        did: ev for did, ev in selectable.items()
        if all(r["satisfied"] is not False for r in ev["hard_constraint_results"]) and not ev.get("blocking_findings")
    }
    excluded = {did: ev for did, ev in selectable.items() if did not in eligible}

    if not eligible:
        return {
            "recommendation": "insufficient_evidence", "selected_design_ids": [], "alternatives": [],
            "rejected": {did: "failed a hard constraint or has an unresolved blocking evaluator finding" for did in excluded},
            "pareto_status": {did: "not_computed" for did in baseline_ids}, "note": "no candidate survives hard-constraint filtering",
        }

    vectors = {did: ev["objective_vector"] for did, ev in eligible.items()}
    pareto = compute_pareto_status(vectors)
    pareto.update({did: "baseline_excluded_from_selection" for did in baseline_ids})
    nondominated = [did for did, s in pareto.items() if s in ("nondominated", "not_computed") and did not in baseline_ids]

    nondominated = sorted(nondominated, key=lambda did: float(eligible[did].get("failure_recall", {}).get("penalty", 0.0)))

    if not preferences_or_weights:
        return {
            "recommendation": "ranked_nondominated_set" if len(nondominated) > 1 else "ranked_candidate",
            "selected_design_ids": nondominated, "alternatives": [d for d in eligible if d not in nondominated],
            "rejected": {did: "hard constraint or blocking finding" for did in excluded}, "pareto_status": pareto,
            "failure_recall": {did: eligible[did].get("failure_recall", {}) for did in eligible},
            "note": "no explicit preferences/weights recorded - returning the full nondominated set rather than forcing a single choice "
                    "(reference_or_control excluded from selection - it is a comparison baseline, not a recommendation)",
        }

    preferred_roles = [p.get("prefer_role") for p in preferences_or_weights if p.get("prefer_role")]
    ranked = sorted(nondominated, key=lambda did: (
        preferred_roles.index(eligible[did]["portfolio_role"]) if eligible[did]["portfolio_role"] in preferred_roles else len(preferred_roles),
        float(eligible[did].get("failure_recall", {}).get("penalty", 0.0)),
    ))
    return {
        "recommendation": "ranked_candidate", "selected_design_ids": ranked[:1], "alternatives": ranked[1:] + [d for d in eligible if d not in nondominated],
        "rejected": {did: "hard constraint or blocking finding" for did in excluded}, "pareto_status": pareto,
        "failure_recall": {did: eligible[did].get("failure_recall", {}) for did in eligible},
        "note": f"ranked by explicit preference order over portfolio_role: {preferred_roles}",
    }
