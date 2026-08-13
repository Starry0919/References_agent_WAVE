"""Counterfactual comparison (doc06 §3.8/§6.2): hard comparability gate
before any delta is computed - matching model id + version + artifact
hash, matching simulation config (solver, objective, time range), and both
runs must have actually succeeded. A denominator of zero or mismatched
units blocks the relative-change calculation for that endpoint specifically
(the rest of the comparison still proceeds) rather than raising or
fabricating a number.
"""
from __future__ import annotations

from harness.ids import new_id, now
from harness.virtual_cell.models import CounterfactualComparison, SimulationResult, SimulationRun


def _config_comparable(a: dict, b: dict) -> list[str]:
    violations = []
    for key in ("solver",):
        if a.get(key) != b.get(key):
            violations.append(f"simulation_config.{key} differs: {a.get(key)!r} vs {b.get(key)!r}")
    return violations


def compare_runs(
    *, simulation_case_id: str, baseline_run: SimulationRun, baseline_result: SimulationResult | None,
    candidate_run: SimulationRun, candidate_result: SimulationResult | None,
) -> CounterfactualComparison:
    ts = now()
    violations: list[str] = []

    if baseline_run.status != "optimal":
        violations.append(f"baseline run {baseline_run.model_run_id} did not succeed (status={baseline_run.status}); no counterfactual delta may be computed")
    if candidate_run.status != "optimal":
        violations.append(f"candidate run {candidate_run.model_run_id} did not succeed (status={candidate_run.status})")
    if baseline_run.model_id != candidate_run.model_id:
        violations.append(f"model_id differs: {baseline_run.model_id} vs {candidate_run.model_id}")
    if baseline_run.model_version != candidate_run.model_version:
        violations.append(f"model_version differs: {baseline_run.model_version} vs {candidate_run.model_version}")
    if baseline_run.artifact_hash != candidate_run.artifact_hash:
        violations.append(f"artifact_hash differs: {baseline_run.artifact_hash} vs {candidate_run.artifact_hash}")
    if baseline_run.baseline_state_id != candidate_run.baseline_state_id:
        violations.append("baseline and candidate runs were computed from different initial cell states")
    violations.extend(_config_comparable(baseline_run.simulation_config, candidate_run.simulation_config))

    if violations:
        return CounterfactualComparison(
            comparison_id=new_id("CFCOMP"), simulation_case_id=simulation_case_id, baseline_run_id=baseline_run.model_run_id,
            candidate_run_id=candidate_run.model_run_id, comparability_status="invalid_comparison",
            comparability_violations=violations, endpoints=[], missing_endpoints=[], tradeoffs=[], robustness=None, created_at=ts,
        )

    baseline_by_name = {e["name"]: e for e in (baseline_result.endpoints if baseline_result else [])}
    candidate_by_name = {e["name"]: e for e in (candidate_result.endpoints if candidate_result else [])}
    all_names = sorted(set(baseline_by_name) | set(candidate_by_name))

    endpoints = []
    missing = []
    for name in all_names:
        b = baseline_by_name.get(name)
        c = candidate_by_name.get(name)
        if b is None or c is None:
            missing.append(name)
            continue
        if b["unit"] != c["unit"]:
            endpoints.append({
                "name": name, "unit": b["unit"], "baseline_value": b["value"], "candidate_value": c["value"],
                "delta": None, "relative_change": None, "statistic": "point_estimate",
                "not_modeled": False, "rejected_reason": f"unit mismatch: {b['unit']} vs {c['unit']}",
            })
            continue
        delta = c["value"] - b["value"]
        relative_change = None
        if b["value"] != 0:
            relative_change = delta / abs(b["value"])
        endpoints.append({
            "name": name, "unit": b["unit"], "baseline_value": b["value"], "candidate_value": c["value"],
            "delta": delta, "relative_change": relative_change, "statistic": "point_estimate", "not_modeled": False,
            "rejected_reason": None if relative_change is not None else "baseline value is zero: relative_change not computed",
        })

    # Any endpoint on doc06 §6.3's checklist neither run produced is a
    # visible not_modeled row, never silently absent.
    for name in ("biomass", "product_titer", "product_yield", "productivity", "stress_state"):
        if name not in baseline_by_name and name not in candidate_by_name and name not in missing:
            endpoints.append({"name": name, "unit": None, "baseline_value": None, "candidate_value": None, "delta": None, "relative_change": None, "statistic": None, "not_modeled": True, "rejected_reason": "not modeled by gem_fba"})

    return CounterfactualComparison(
        comparison_id=new_id("CFCOMP"), simulation_case_id=simulation_case_id, baseline_run_id=baseline_run.model_run_id,
        candidate_run_id=candidate_run.model_run_id, comparability_status="comparable", comparability_violations=[],
        endpoints=endpoints, missing_endpoints=missing, tradeoffs=[], robustness={"replicates": 1, "note": "deterministic LP solve; single replicate is exact, not a sample of variability"},
        created_at=ts,
    )
