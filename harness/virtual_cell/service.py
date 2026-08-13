"""Top-level Problem 06 orchestration: `Problem 4 DesignVersion -> Baseline
Cell State -> Perturbation Compilation -> Model Compatibility Check -> Real
Model Execution -> Counterfactual Comparison -> Prediction Review ->
Validation Plan` (doc06's mandated pipeline, §0). Every mutating step here
transitions `SimulationCase.status` through one of `SIMULATION_STATES`,
records a `SimulationTransition`, and appends a `ProjectEvent` - the same
governance shape every other problem package in this codebase uses.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.designs.models import DesignVersion
from harness.designs.service import get_design_version
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.virtual_cell import compatibility as compat_mod
from harness.virtual_cell import compiler as compiler_mod
from harness.virtual_cell import registry as registry_mod
from harness.virtual_cell import runner as runner_mod
from harness.virtual_cell.cell_state_service import cell_state_to_dict
from harness.virtual_cell.comparison import compare_runs
from harness.virtual_cell.compiler import merge_compiled_bounds
from harness.virtual_cell.guards import (
    SimulationGuardError,
    assert_baseline_succeeded_before_delta,
    assert_compatible_before_run,
    assert_design_version_formal,
    assert_evaluation_not_blocking,
)
from harness.virtual_cell.models import (
    CompatibilityReport,
    CompiledIntervention,
    CounterfactualComparison,
    PerturbationSpec,
    PredictionReview,
    SimulationCase,
    SimulationResult,
    SimulationRun,
    SimulationTransition,
    ValidationPlanItem,
)

_SUPPORTED_PERTURBATION_TYPES = {"knockout": "deletion", "deletion": "deletion", "knockdown": "knockdown", "attenuation": "knockdown", "overexpression": "overexpression"}


class SimulationCaseNotFound(ValueError):
    pass


def _transition(session: Session, case: SimulationCase, *, to_state: str, reason: str, actor_id: str) -> None:
    from harness.virtual_cell.models import SIMULATION_STATES

    if to_state not in SIMULATION_STATES:
        raise ValueError(f"unknown simulation state {to_state!r}")
    tr = SimulationTransition(
        transition_id=new_id("SIMTR"), simulation_case_id=case.simulation_case_id, from_state=case.status,
        to_state=to_state, reason=reason, actor_id=actor_id, created_at=now(),
    )
    session.add(tr)
    case.status = to_state
    case.updated_at = now()
    session.flush()
    append_event(
        session, project_id=case.project_id, event_type=et.VC_SIMULATION_STATE_CHANGED, entity_type="SimulationCase",
        entity_id=case.simulation_case_id, payload={"from_state": tr.from_state, "to_state": tr.to_state, "reason": reason},
        actor_type="agent", actor_id=actor_id,
    )


def open_simulation_case(
    session: Session, *, project_id: str, design_version_id: str, requested_by: str, evaluation_reference: str | None = None,
    human_override: dict[str, Any] | None = None,
) -> SimulationCase:
    design_version = get_design_version(session, design_version_id)
    assert_design_version_formal(design_version)

    if evaluation_reference:
        from harness.scientific_evaluation.intake import get_case as get_evaluation_case

        assert_evaluation_not_blocking(get_evaluation_case(session, evaluation_reference), human_override=human_override)

    case = SimulationCase(
        simulation_case_id=new_id("SIMCASE"), project_id=project_id, design_version_id=design_version_id,
        evaluation_reference=evaluation_reference, requested_by=requested_by, status="simulation_requested",
        created_at=now(), updated_at=now(),
    )
    session.add(case)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.VC_SIMULATION_CASE_OPENED, entity_type="SimulationCase",
        entity_id=case.simulation_case_id, payload={"design_version_id": design_version_id, "evaluation_reference": evaluation_reference},
        actor_type="agent" if requested_by == "system" else "human", actor_id=requested_by,
    )
    return case


def get_case(session: Session, simulation_case_id: str) -> SimulationCase | None:
    return session.get(SimulationCase, simulation_case_id)


def set_baseline_cell_state(session: Session, *, case: SimulationCase, cell_state_id: str, actor_id: str) -> SimulationCase:
    case.baseline_cell_state_id = cell_state_id
    session.flush()
    _transition(session, case, to_state="state_validated", reason=f"baseline cell state {cell_state_id} attached", actor_id=actor_id)
    return case


def select_model(session: Session, *, case: SimulationCase, model_id: str, rationale: dict[str, Any] | None = None, actor_id: str) -> SimulationCase:
    entry = registry_mod.get_registry_entry(session, model_id)
    if entry is None:
        raise ValueError(f"no such model registry entry: {model_id}")
    case.model_id = model_id
    case.router_rationale = rationale or {"reason": "single available real adapter this round (gem_fba)"}
    session.flush()
    _transition(session, case, to_state="model_selected", reason=f"selected model {model_id}", actor_id=actor_id)
    return case


def extract_perturbations(session: Session, *, case: SimulationCase, design_version: DesignVersion, actor_id: str) -> list[PerturbationSpec]:
    """doc06 §5: compiles `DesignVersion.genotype_manifest.modifications`
    (`{gene, operation, detail}` - see `harness.designs.adapters.
    genotype_manifest_from_p1_decisions`) into `PerturbationSpec` rows.
    Unsupported operation strings are still recorded (status=`pending`) so
    the compatibility check can reject them structurally rather than the
    extraction step silently dropping them."""
    modifications = design_version.genotype_manifest.get("modifications", [])
    specs: list[PerturbationSpec] = []
    for mod in modifications:
        gene = mod.get("gene") or mod.get("target")
        raw_op = (mod.get("operation") or "").strip().lower()
        ptype = _SUPPORTED_PERTURBATION_TYPES.get(raw_op, raw_op or "unknown")
        spec = PerturbationSpec(
            perturbation_id=new_id("PSPEC"), simulation_case_id=case.simulation_case_id, design_version_id=design_version.design_version_id,
            type=ptype, target=gene, target_namespace="gene_symbol", biological_intent=mod.get("detail", ""),
            operation=raw_op, strength=None, implementation=mod.get("detail", ""), timing=None, combination_group=None,
            environmental_changes=[], required_mappings=[], assumptions=[], status="pending", created_at=now(),
        )
        session.add(spec)
        specs.append(spec)
    session.flush()
    return specs


def compile_perturbations(session: Session, *, case: SimulationCase, perturbations: list[PerturbationSpec], model_id: str, actor_id: str) -> list[CompiledIntervention]:
    compiled: list[CompiledIntervention] = []
    for p in perturbations:
        ci = compiler_mod.compile_intervention(p, model_id=model_id)
        session.add(ci)
        p.status = "compiled" if ci.status == "compiled" else "rejected"
        compiled.append(ci)
    session.flush()
    if any(c.status == "compiled" for c in compiled):
        _transition(session, case, to_state="intervention_compiled", reason=f"compiled {sum(c.status=='compiled' for c in compiled)}/{len(compiled)} perturbation(s)", actor_id=actor_id)
    else:
        _transition(session, case, to_state="unsupported_intervention", reason="no perturbation could be compiled for this model", actor_id=actor_id)
    append_event(
        session, project_id=case.project_id, event_type=et.VC_PERTURBATIONS_COMPILED, entity_type="SimulationCase",
        entity_id=case.simulation_case_id,
        payload={"compiled": [{"id": c.compiled_intervention_id, "status": c.status, "target": c.resolved_gene_id, "mapping_status": c.mapping_status} for c in compiled]},
        actor_type="agent", actor_id=actor_id,
    )
    return compiled


def run_compatibility_check(
    session: Session, *, case: SimulationCase, model_id: str, cell_state_id: str, chassis: dict[str, Any], perturbations: list[PerturbationSpec], actor_id: str,
) -> CompatibilityReport:
    entry = registry_mod.get_registry_entry(session, model_id)
    if entry is None:
        raise ValueError(f"no such model registry entry: {model_id}")
    report = compat_mod.check_compatibility(
        simulation_case_id=case.simulation_case_id, registry_entry=entry, cell_state_id=cell_state_id, chassis=chassis, perturbations=perturbations,
    )
    session.add(report)
    session.flush()
    next_state = {
        "compatible": "compatibility_checked", "compatible_with_assumptions": "compatibility_checked",
        "out_of_domain": "out_of_domain", "unsupported": "unsupported_intervention", "unavailable": "no_compatible_model",
    }[report.decision]
    _transition(session, case, to_state=next_state, reason=f"compatibility decision={report.decision}", actor_id=actor_id)
    append_event(
        session, project_id=case.project_id, event_type=et.VC_COMPATIBILITY_CHECKED, entity_type="CompatibilityReport",
        entity_id=report.compatibility_id, payload={
            "decision": report.decision, "blocking_reasons": report.blocking_reasons, "non_blocking_assumptions": report.non_blocking_assumptions,
        }, actor_type="agent", actor_id=actor_id,
    )
    return report


def run_baseline_and_candidate(
    session: Session, *, case: SimulationCase, compiled: list[CompiledIntervention], baseline_cell_state_id: str, actor_id: str,
) -> dict[str, Any]:
    """Runs S0 (baseline, empty reaction_bounds) then S1 (candidate,
    merged compiled bounds) - doc06 §6.1's minimum two-scenario matrix.
    Both runs are persisted regardless of outcome. Dispatches to whichever
    adapter `case.model_id` actually selected (via its `ModelRegistryEntry.
    adapter_id`) - not hardcoded to `gem_fba`/e_coli_core, so a case that
    selected `MREG-gem_fba_iml1515` genuinely runs the larger model."""
    entry = registry_mod.get_registry_entry(session, case.model_id) if case.model_id else None
    adapter_name = entry.adapter_id if entry is not None else "gem_fba"

    baseline_run, baseline_result = runner_mod.run_gem_fba_scenario(
        session, simulation_case_id=case.simulation_case_id, scenario_label="S0_baseline", baseline_state_id=baseline_cell_state_id,
        perturbation_ids=[], compiled_intervention_ids=[], reaction_bounds={}, model_id=case.model_id or "MREG-gem_fba", adapter_name=adapter_name,
    )
    _transition(session, case, to_state="baseline_running", reason=f"baseline run {baseline_run.model_run_id} status={baseline_run.status}", actor_id=actor_id)
    append_event(
        session, project_id=case.project_id, event_type=et.VC_SIMULATION_RUN_RECORDED, entity_type="SimulationRun",
        entity_id=baseline_run.model_run_id, payload={"scenario_label": "S0_baseline", "status": baseline_run.status, "outputs": baseline_run.raw_output_ref},
        actor_type="agent", actor_id=actor_id,
    )

    try:
        assert_baseline_succeeded_before_delta(baseline_run)
    except SimulationGuardError as e:
        _transition(session, case, to_state="run_failed", reason=str(e), actor_id=actor_id)
        return {"baseline_run": baseline_run, "baseline_result": baseline_result, "candidate_run": None, "candidate_result": None}

    try:
        merged_bounds = merge_compiled_bounds(compiled)
    except ValueError as e:
        _transition(session, case, to_state="invalid_comparison", reason=f"conflicting compiled interventions: {e}", actor_id=actor_id)
        return {"baseline_run": baseline_run, "baseline_result": baseline_result, "candidate_run": None, "candidate_result": None}

    candidate_run, candidate_result = runner_mod.run_gem_fba_scenario(
        session, simulation_case_id=case.simulation_case_id, scenario_label="S1_intervention", baseline_state_id=baseline_cell_state_id,
        perturbation_ids=[c.perturbation_id for c in compiled if c.status == "compiled"],
        compiled_intervention_ids=[c.compiled_intervention_id for c in compiled if c.status == "compiled"], reaction_bounds=merged_bounds,
        model_id=case.model_id or "MREG-gem_fba", adapter_name=adapter_name,
    )
    _transition(session, case, to_state="intervention_running", reason=f"candidate run {candidate_run.model_run_id} status={candidate_run.status}", actor_id=actor_id)
    append_event(
        session, project_id=case.project_id, event_type=et.VC_SIMULATION_RUN_RECORDED, entity_type="SimulationRun",
        entity_id=candidate_run.model_run_id, payload={"scenario_label": "S1_intervention", "status": candidate_run.status, "outputs": candidate_run.raw_output_ref},
        actor_type="agent", actor_id=actor_id,
    )
    if candidate_run.status == "optimal":
        _transition(session, case, to_state="results_normalized", reason="both runs normalized", actor_id=actor_id)
    else:
        _transition(session, case, to_state="run_failed", reason=f"candidate run failed: {candidate_run.status}", actor_id=actor_id)
    return {"baseline_run": baseline_run, "baseline_result": baseline_result, "candidate_run": candidate_run, "candidate_result": candidate_result}


def build_comparison(session: Session, *, case: SimulationCase, baseline_run: SimulationRun, baseline_result: SimulationResult | None, candidate_run: SimulationRun, candidate_result: SimulationResult | None, actor_id: str) -> CounterfactualComparison:
    comparison = compare_runs(
        simulation_case_id=case.simulation_case_id, baseline_run=baseline_run, baseline_result=baseline_result,
        candidate_run=candidate_run, candidate_result=candidate_result,
    )
    session.add(comparison)
    session.flush()
    _transition(
        session, case, to_state="comparison_ready" if comparison.comparability_status == "comparable" else "invalid_comparison",
        reason=f"comparability_status={comparison.comparability_status}", actor_id=actor_id,
    )
    append_event(
        session, project_id=case.project_id, event_type=et.VC_COMPARISON_COMPUTED, entity_type="CounterfactualComparison",
        entity_id=comparison.comparison_id, payload={"comparability_status": comparison.comparability_status, "endpoints": comparison.endpoints, "violations": comparison.comparability_violations},
        actor_type="agent", actor_id=actor_id,
    )
    return comparison


def run_prediction_review(
    session: Session, *, case: SimulationCase, comparison: CounterfactualComparison, compatibility: CompatibilityReport,
    compiled: list[CompiledIntervention], baseline_run: SimulationRun, candidate_run: SimulationRun, actor_id: str,
) -> PredictionReview:
    from harness.virtual_cell.guards import assert_comparison_valid_before_review
    from harness.virtual_cell.reviewer import review_prediction

    assert_comparison_valid_before_review(comparison)
    review = review_prediction(
        simulation_case_id=case.simulation_case_id, comparison=comparison, compatibility=compatibility,
        compiled=compiled, baseline_run=baseline_run, candidate_run=candidate_run,
    )
    session.add(review)
    session.flush()
    _transition(session, case, to_state="prediction_under_review", reason=f"prediction review decision={review.decision}", actor_id=actor_id)
    if review.decision == "rejected":
        _transition(session, case, to_state="prediction_rejected", reason="prediction review rejected the comparison", actor_id=actor_id)
    append_event(
        session, project_id=case.project_id, event_type=et.VC_PREDICTION_REVIEWED, entity_type="PredictionReview",
        entity_id=review.review_id, payload={"decision": review.decision, "findings": review.findings}, actor_type="agent", actor_id=actor_id,
    )
    return review


def run_validation_planning(session: Session, *, case: SimulationCase, comparison: CounterfactualComparison, actor_id: str) -> list[ValidationPlanItem]:
    from harness.virtual_cell.validation_service import build_validation_plan

    items = build_validation_plan(simulation_case_id=case.simulation_case_id, comparison=comparison)
    for item in items:
        session.add(item)
    session.flush()
    _transition(session, case, to_state="validation_planned", reason=f"{len(items)} validation item(s) planned", actor_id=actor_id)
    append_event(
        session, project_id=case.project_id, event_type=et.VC_VALIDATION_PLANNED, entity_type="SimulationCase",
        entity_id=case.simulation_case_id, payload={"items": [{"endpoint": i.endpoint, "expected_direction": i.expected_direction} for i in items]},
        actor_type="agent", actor_id=actor_id,
    )
    if items:
        _transition(session, case, to_state="awaiting_observation", reason="awaiting experimental observation", actor_id=actor_id)
    return items


def run_prediction_pipeline(
    session: Session, *, project_id: str, design_version_id: str, chassis: dict[str, Any], environment: dict[str, Any],
    model_id: str = "MREG-gem_fba", actor_id: str, evaluation_reference: str | None = None, human_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convenience end-to-end driver for the doc06 §1.3 minimum vertical
    slice: one formal DesignVersion -> baseline cell state -> compiled
    single-gene perturbation -> gem_fba baseline+intervention runs ->
    normalized results -> counterfactual comparison. Returns every object
    created so a caller (API route, test) can inspect the full trail."""
    from harness.virtual_cell.cell_state_service import build_baseline_cell_state

    design_version = get_design_version(session, design_version_id)
    assert_design_version_formal(design_version)

    case = open_simulation_case(
        session, project_id=project_id, design_version_id=design_version_id, requested_by=actor_id,
        evaluation_reference=evaluation_reference, human_override=human_override,
    )

    baseline_state = build_baseline_cell_state(
        session, project_id=project_id, design_version=design_version, chassis=chassis, environment=environment, actor_id=actor_id,
    )
    append_event(
        session, project_id=project_id, event_type=et.VC_CELL_STATE_RECORDED, entity_type="BiologicalStateSnapshot",
        entity_id=baseline_state.snapshot_id, payload=cell_state_to_dict(baseline_state), actor_type="agent", actor_id=actor_id,
    )
    set_baseline_cell_state(session, case=case, cell_state_id=baseline_state.snapshot_id, actor_id=actor_id)
    select_model(session, case=case, model_id=model_id, actor_id=actor_id)

    perturbations = extract_perturbations(session, case=case, design_version=design_version, actor_id=actor_id)
    if not perturbations:
        _transition(session, case, to_state="needs_input", reason="DesignVersion has no genotype modifications to simulate", actor_id=actor_id)
        return {"case": case, "perturbations": [], "compatibility": None, "compiled": [], "baseline_run": None, "candidate_run": None, "comparison": None}

    compatibility = run_compatibility_check(
        session, case=case, model_id=model_id, cell_state_id=baseline_state.snapshot_id, chassis=chassis, perturbations=perturbations, actor_id=actor_id,
    )
    try:
        assert_compatible_before_run(compatibility)
    except SimulationGuardError:
        return {"case": case, "perturbations": perturbations, "compatibility": compatibility, "compiled": [], "baseline_run": None, "candidate_run": None, "comparison": None}

    compiled = compile_perturbations(session, case=case, perturbations=perturbations, model_id=model_id, actor_id=actor_id)
    if not any(c.status == "compiled" for c in compiled):
        return {"case": case, "perturbations": perturbations, "compatibility": compatibility, "compiled": compiled, "baseline_run": None, "candidate_run": None, "comparison": None}

    runs = run_baseline_and_candidate(session, case=case, compiled=compiled, baseline_cell_state_id=baseline_state.snapshot_id, actor_id=actor_id)
    comparison = None
    review = None
    validation_items: list[ValidationPlanItem] = []
    if runs["candidate_run"] is not None:
        comparison = build_comparison(
            session, case=case, baseline_run=runs["baseline_run"], baseline_result=runs["baseline_result"],
            candidate_run=runs["candidate_run"], candidate_result=runs["candidate_result"], actor_id=actor_id,
        )
        if comparison.comparability_status == "comparable":
            review = run_prediction_review(
                session, case=case, comparison=comparison, compatibility=compatibility, compiled=compiled,
                baseline_run=runs["baseline_run"], candidate_run=runs["candidate_run"], actor_id=actor_id,
            )
            if review.decision in ("decision_ready", "limited_acceptance"):
                validation_items = run_validation_planning(session, case=case, comparison=comparison, actor_id=actor_id)

    return {
        "case": case, "baseline_state": baseline_state, "perturbations": perturbations, "compatibility": compatibility,
        "compiled": compiled, "baseline_run": runs["baseline_run"], "baseline_result": runs["baseline_result"],
        "candidate_run": runs["candidate_run"], "candidate_result": runs["candidate_result"], "comparison": comparison,
        "review": review, "validation_items": validation_items,
    }


def list_transitions(session: Session, simulation_case_id: str) -> list[SimulationTransition]:
    return list(session.execute(select(SimulationTransition).where(SimulationTransition.simulation_case_id == simulation_case_id).order_by(SimulationTransition.created_at)).scalars())
