"""Experiment Outcome Ingestion (doc04 §4.7, §9): expected-vs-observed
residuals, failure classification (never collapsed to a bare
`success=false`), and the resulting next-iteration / diagnosis-reopen /
stop decision. Technical (construction/measurement) failures are checked
FIRST and are never usable as biological evidence against the grounding
diagnosis - same discipline as `harness.learning.outcome_classifier.
classify_outcome`, whose taxonomy this reuses conceptually while adding
doc04's richer, build/test-specific classes.

A non-`success` classification also writes a real, cross-linked
`harness.learning.models.FailureCase` via `harness.learning.service.
classify_failure` - so Problem 04 failures land in the SAME failure-history
table Problem 02's own DBTL loop already reads, not a second, disconnected
one.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.engineering_design.evaluators.runner import latest_evaluation
from harness.engineering_design.loop import EngineeringDesignLoopController
from harness.engineering_design.models import CandidateDesign, DesignOutcomeRecord, EngineeringDesignProject
from harness.ids import new_id, now
from harness.learning import service as learning_svc
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

OUTCOME_SNAPSHOT_FIELDS = (
    "outcome_id", "design_id", "design_version", "experiment_run_id", "expected_observations", "observed_results",
    "residuals", "failure_classification", "failure_case_id", "outcome_update", "next_iteration_reason",
    "decided_next_action", "actor_id", "created_at",
)

_loop = EngineeringDesignLoopController()

_DESIGN_TO_LEARNING_FAILURE_CLASS = {
    "assembly_failed": "construction", "transformation_failed": "construction",
    "assay_failed": "measurement", "measurement_invalid": "measurement",
    "biological_underperformance": "biological_null", "unexpected_tradeoff": "tradeoff", "inconclusive": "inconclusive",
}

_NEXT_ACTION_MAP: dict[str, tuple[str, str]] = {
    "success": ("stop", "primary objective direction was met by this candidate"),
    "assembly_failed": ("next_iteration", "construction failed - a technical failure, not biological evidence against the diagnosis; retry with a revised build approach"),
    "transformation_failed": ("next_iteration", "transformation failed - a technical failure, not biological evidence against the diagnosis"),
    "assay_failed": ("next_iteration", "assay failed - a measurement failure, not biological evidence against the diagnosis"),
    "measurement_invalid": ("next_iteration", "measurement QC failed - not biological evidence against the diagnosis"),
    "biological_underperformance": ("diagnosis_reopened", "construction and measurement were verified, but the expected direction was not observed - the grounding diagnosis hypothesis may need reassessment"),
    "unexpected_tradeoff": ("next_iteration", "target metric improved but a hard constraint or side effect was violated - revise under the same diagnosis"),
    "inconclusive": ("next_iteration", "result is inconclusive - insufficient signal to accept or reject the grounding hypothesis"),
}


def _classify(*, construction_verified: bool, assay_qc_passed: bool, constraint_violations: list[str], residuals: list[dict[str, Any]]) -> str:
    if not construction_verified:
        return "assembly_failed"
    if not assay_qc_passed:
        return "measurement_invalid"
    if constraint_violations:
        return "unexpected_tradeoff"
    met = [r for r in residuals if r.get("direction_met") is True]
    unmet = [r for r in residuals if r.get("direction_met") is False]
    if unmet and not met:
        return "biological_underperformance"
    if met and not unmet:
        return "success"
    return "inconclusive"


def _compute_residuals(observed_results: list[dict[str, Any]], objective_vector: list[dict[str, Any]]) -> list[dict[str, Any]]:
    residuals = []
    for entry in objective_vector:
        metric = entry["metric"]
        obs = next((o for o in observed_results if o.get("metric") == metric), None)
        if obs is None:
            residuals.append({"metric": metric, "expected_direction": entry["direction_estimate"], "observed": None, "baseline": None, "direction_met": None})
            continue
        expected_dir = entry["direction_estimate"]
        observed_value, baseline_value = obs.get("value"), obs.get("baseline_value")
        direction_met = None
        if observed_value is not None and baseline_value is not None and expected_dir in ("intended_increase", "increase"):
            direction_met = observed_value > baseline_value
        residuals.append({"metric": metric, "expected_direction": expected_dir, "observed": observed_value, "baseline": baseline_value, "direction_met": direction_met})
    return residuals


def ingest_outcome(
    session: Session,
    *,
    design_id: str,
    actor_id: str,
    observed_results: list[dict[str, Any]],
    construction_verified: bool,
    assay_qc_passed: bool,
    experiment_run_id: str | None = None,
    constraint_violations: list[str] | None = None,
    outcome_update: str = "",
) -> DesignOutcomeRecord:
    candidate = session.get(CandidateDesign, design_id)
    if candidate is None:
        raise ValueError(f"no such candidate design: {design_id}")
    proj = session.get(EngineeringDesignProject, candidate.design_project_id)
    constraint_violations = constraint_violations or []

    eval_row = latest_evaluation(session, design_id)
    objective_vector = eval_row.objective_vector if eval_row else []
    residuals = _compute_residuals(observed_results, objective_vector)
    classification = _classify(
        construction_verified=construction_verified, assay_qc_passed=assay_qc_passed,
        constraint_violations=constraint_violations, residuals=residuals,
    )
    decided_next_action, next_iteration_reason = _NEXT_ACTION_MAP[classification]

    failure_case_id: str | None = None
    if classification != "success":
        learning_class = _DESIGN_TO_LEARNING_FAILURE_CLASS[classification]
        fc = learning_svc.classify_failure(
            session, project_id=proj.project_id, failure_class=learning_class, actor_id=actor_id,
            design_version_id=candidate.build_test_package_id, experiment_run_id=experiment_run_id,
            observed_outcome_ids=[], data_qc_status="passed" if assay_qc_passed else "failed",
            candidate_causes=[r["metric"] for r in residuals if r.get("direction_met") is False],
            causal_confidence="medium" if construction_verified and assay_qc_passed else "low",
            applicability_scope=dict(proj.temporal_and_environmental_context),
        )
        failure_case_id = fc.failure_case_id

    outcome = DesignOutcomeRecord(
        outcome_id=new_id("OUTCOME"), design_id=design_id, design_version=candidate.design_version,
        experiment_run_id=experiment_run_id, expected_observations=[str(e) for e in objective_vector],
        observed_results=observed_results, residuals=residuals, failure_classification=classification,
        failure_case_id=failure_case_id, outcome_update=outcome_update or f"classified as {classification}",
        next_iteration_reason=next_iteration_reason, decided_next_action=decided_next_action, actor_id=actor_id, created_at=now(),
    )
    session.add(outcome)
    from harness.engineering_design.decision_state import set_execution_status
    set_execution_status(session, design_id=candidate.design_id, status="tested")
    session.flush()
    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_OUTCOME_INGESTED, entity_type="DesignOutcomeRecord",
        entity_id=outcome.outcome_id, payload=snapshot(outcome, OUTCOME_SNAPSHOT_FIELDS), actor_type="human", actor_id=actor_id,
    )

    _loop.ingest_test_outcome(session, proj, actor_id=actor_id)
    _loop.complete_learning_update(session, proj, actor_id=actor_id)
    if decided_next_action == "stop":
        _loop.complete(session, proj, actor_id=actor_id)
        event_type = et.DESIGN_LOOP_STOPPED
    elif decided_next_action == "diagnosis_reopened":
        _loop.reopen_diagnosis(session, proj, actor_id=actor_id)
        event_type = et.DESIGN_DIAGNOSIS_REOPEN_REQUESTED
    else:
        _loop.start_next_iteration(session, proj, actor_id=actor_id)
        event_type = et.DESIGN_NEXT_ITERATION_STARTED
    append_event(
        session, project_id=proj.project_id, event_type=event_type, entity_type="EngineeringDesignProject",
        entity_id=proj.design_project_id, payload={"design_project_id": proj.design_project_id, "reason": next_iteration_reason, "outcome_id": outcome.outcome_id},
        actor_type="agent", actor_id=actor_id,
    )
    return outcome
