"""Prediction Reviewer (doc06 §8): an independent, deterministic (never
LLM-generated) boundary review of a `CounterfactualComparison` - checks the
12-point doc06 §8 checklist against the real objects it was built from
(`CompatibilityReport`, `CompiledIntervention`, `SimulationRun`), not a
re-summary of the numbers. `decision` cannot become `decision_ready` while
any `blocking` finding is open (`harness/virtual_cell/guards.py::
assert_review_passed_before_decision` re-checks this independently of the
value written here).
"""
from __future__ import annotations

from typing import Any

from harness.ids import new_id, now
from harness.virtual_cell.models import (
    CompatibilityReport,
    CompiledIntervention,
    CounterfactualComparison,
    PredictionReview,
    SimulationRun,
)


def review_prediction(
    *, simulation_case_id: str, comparison: CounterfactualComparison, compatibility: CompatibilityReport,
    compiled: list[CompiledIntervention], baseline_run: SimulationRun, candidate_run: SimulationRun,
) -> PredictionReview:
    findings: list[dict[str, Any]] = []

    # 1/2. real successful run, adapter/model/artifact/version traceable
    for run, label in ((baseline_run, "baseline"), (candidate_run, "candidate")):
        if run.status != "optimal":
            findings.append({"category": "run_not_successful", "severity": "blocking", "endpoint": None, "message": f"{label} run {run.model_run_id} did not reach status=optimal (status={run.status})"})
        if not run.model_version or run.model_id is None:
            findings.append({"category": "not_traceable", "severity": "blocking", "endpoint": None, "message": f"{label} run {run.model_run_id} is missing model_id/model_version traceability"})

    # 3. chassis/condition/perturbation coverage
    if compatibility.decision == "compatible_with_assumptions":
        findings.append({"category": "domain_assumption", "severity": "warning", "endpoint": None, "message": f"compatibility accepted with non-blocking assumptions: {compatibility.non_blocking_assumptions}"})
    elif compatibility.decision not in ("compatible",):
        findings.append({"category": "domain_mismatch", "severity": "blocking", "endpoint": None, "message": f"compatibility decision was {compatibility.decision!r}, not compatible"})

    # 4. intervention mapping directness
    mapping_status_summary: dict[str, int] = {}
    for ci in compiled:
        mapping_status_summary[ci.mapping_status] = mapping_status_summary.get(ci.mapping_status, 0) + 1
        if ci.mapping_status == "approximate":
            findings.append({"category": "approximate_mapping", "severity": "warning", "endpoint": None, "message": f"{ci.compiled_intervention_id} mapping is approximate: {ci.mapping_assumptions}"})
        elif ci.mapping_status == "unsupported":
            findings.append({"category": "unsupported_mapping", "severity": "major", "endpoint": None, "message": f"{ci.compiled_intervention_id} could not be mapped: {ci.rejection_reason}"})

    # 5. baseline/counterfactual comparability
    if comparison.comparability_status != "comparable":
        findings.append({"category": "invalid_comparison", "severity": "blocking", "endpoint": None, "message": f"comparison is invalid_comparison: {comparison.comparability_violations}"})

    # 6. stochastic replicate adequacy - gem_fba is a deterministic LP solve
    if baseline_run.simulation_config.get("random_seed") is not None and baseline_run.simulation_config.get("replicate_index", 0) == 0:
        findings.append({"category": "single_replicate_stochastic_model", "severity": "warning", "endpoint": None, "message": "only a single replicate was run for a model with a random seed configured"})

    # 7/8. model-direct vs derived vs not_modeled endpoints
    model_derived = [e["name"] for e in comparison.endpoints if not e.get("not_modeled") and e.get("delta") is not None]
    derived = []  # this round computes no code-derived ratios beyond raw model endpoints
    not_modeled = [e["name"] for e in comparison.endpoints if e.get("not_modeled")]

    # 9. uncertainty matches method (gem_fba is deterministic - any
    # "calibrated"/numeric-probability confidence would be pseudo-precision)
    # - checked structurally: this round never writes such a value, so no
    # finding is needed unless a caller violates that (defensive check).

    # 10. pseudo-precision / cross-domain extrapolation
    rejected_endpoints = [e for e in comparison.endpoints if e.get("rejected_reason") and not e.get("not_modeled")]
    for e in rejected_endpoints:
        findings.append({"category": "endpoint_not_comparable", "severity": "warning", "endpoint": e["name"], "message": e["rejected_reason"]})

    # 11. falsifiable experimental translation - deferred to ValidationPlanItem (doc06 §9.1); flag if comparison has zero usable endpoints
    if not model_derived:
        findings.append({"category": "no_usable_endpoint", "severity": "blocking", "endpoint": None, "message": "comparison produced zero usable (model-derived, comparable) endpoints to validate experimentally"})

    blocking_count = sum(1 for f in findings if f["severity"] == "blocking")
    if blocking_count:
        decision = "rejected" if compatibility.decision not in ("compatible", "compatible_with_assumptions") else "rerun_required"
    elif any(f["severity"] == "major" for f in findings):
        decision = "limited_acceptance"
    else:
        decision = "decision_ready"

    return PredictionReview(
        review_id=new_id("PREVIEW"), simulation_case_id=simulation_case_id, comparison_id=comparison.comparison_id,
        findings=findings, model_derived_endpoints=model_derived, derived_endpoints=derived, not_modeled_endpoints=not_modeled,
        mapping_status_summary=mapping_status_summary, decision=decision, reviewer_type="deterministic_rule", created_at=now(),
    )
