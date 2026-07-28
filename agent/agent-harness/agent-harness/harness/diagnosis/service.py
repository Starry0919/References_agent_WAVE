"""DiagnosisSession / ProjectObjective / BiologicalContext mutations - the
same event-sourced pattern as `harness/projects/service.py`, writing into
the shared `ProjectEvent` ledger (doc03 6.3).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.diagnosis.models import BiologicalContext, DiagnosisSession, ProjectObjective
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

SESSION_SNAPSHOT_FIELDS = (
    "diagnosis_session_id", "project_id", "workflow_run_id", "triggering_failure_case_id",
    "triggering_learning_cycle_id", "objective_id", "biological_system", "baseline_observation_ids",
    "active_hypothesis_set_version", "status", "data_sufficiency", "approval_state", "version",
    "created_at", "updated_at",
)


def create_objective(
    session: Session,
    *,
    project_id: str,
    created_by: str,
    titer_target: dict[str, Any] | None = None,
    yield_target: dict[str, Any] | None = None,
    productivity_target: dict[str, Any] | None = None,
    growth_viability: dict[str, Any] | None = None,
    stability: dict[str, Any] | None = None,
    scalability: dict[str, Any] | None = None,
    knowledge_gain: dict[str, Any] | None = None,
    risk_tolerance: str = "moderate",
    time_cost_constraint: dict[str, Any] | None = None,
    approval_owner: str | None = None,
) -> ProjectObjective:
    obj = ProjectObjective(
        objective_id=new_id("OBJ"), project_id=project_id, titer_target=titer_target, yield_target=yield_target,
        productivity_target=productivity_target, growth_viability=growth_viability, stability=stability,
        scalability=scalability, knowledge_gain=knowledge_gain, risk_tolerance=risk_tolerance,
        time_cost_constraint=time_cost_constraint, approval_owner=approval_owner, created_by=created_by, created_at=now(),
    )
    session.add(obj)
    session.flush()
    return obj


def create_biological_context(
    session: Session,
    *,
    project_id: str,
    chassis_genotype_ref: str | None = None,
    medium: str | None = None,
    carbon_source: str | None = None,
    environment: dict[str, Any] | None = None,
    process_mode: str | None = None,
    growth_phase: str | None = None,
    process_phase: str | None = None,
    experiment_time: dict[str, Any] | None = None,
    sampling_window: dict[str, Any] | None = None,
    recent_perturbations: list[Any] | None = None,
    state_transition_context: str | None = None,
    steady_state_assumption: bool = True,
) -> BiologicalContext:
    ctx = BiologicalContext(
        context_id=new_id("CTX"), project_id=project_id, chassis_genotype_ref=chassis_genotype_ref, medium=medium,
        carbon_source=carbon_source, environment=environment or {}, process_mode=process_mode, growth_phase=growth_phase,
        process_phase=process_phase, experiment_time=experiment_time, sampling_window=sampling_window,
        recent_perturbations=recent_perturbations or [], state_transition_context=state_transition_context,
        steady_state_assumption=steady_state_assumption, created_at=now(),
    )
    session.add(ctx)
    session.flush()
    return ctx


def start_diagnosis_session(
    session: Session,
    *,
    project_id: str,
    actor_id: str,
    workflow_run_id: str | None = None,
    triggering_failure_case_id: str | None = None,
    triggering_learning_cycle_id: str | None = None,
    objective_id: str | None = None,
    biological_system: dict[str, Any] | None = None,
    baseline_observation_ids: list[str] | None = None,
) -> DiagnosisSession:
    ts = now()
    sess = DiagnosisSession(
        diagnosis_session_id=new_id("DIAG"), project_id=project_id, workflow_run_id=workflow_run_id,
        triggering_failure_case_id=triggering_failure_case_id, triggering_learning_cycle_id=triggering_learning_cycle_id,
        objective_id=objective_id, biological_system=biological_system or {},
        baseline_observation_ids=baseline_observation_ids or [], status="intake", data_sufficiency="insufficient",
        created_at=ts, updated_at=ts,
    )
    session.add(sess)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.DIAGNOSIS_SESSION_STARTED, entity_type="DiagnosisSession",
        entity_id=sess.diagnosis_session_id, payload=snapshot(sess, SESSION_SNAPSHOT_FIELDS),
        actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id, workflow_run_id=workflow_run_id,
    )
    return sess


def get_session(session: Session, diagnosis_session_id: str) -> DiagnosisSession | None:
    return session.get(DiagnosisSession, diagnosis_session_id)
