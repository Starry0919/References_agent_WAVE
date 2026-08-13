"""ExperimentPlan / ExperimentRun mutations (doc 8.4). Plan and actual
execution are kept as separate rows specifically so protocol deviations
and real executed identity can diverge from what was planned.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.experiments.models import ExperimentPlan, ExperimentRun
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

PLAN_SNAPSHOT_FIELDS = (
    "experiment_plan_id", "project_id", "design_version_ids", "hypotheses_tested", "controls",
    "factors", "response_variables", "acceptance_criteria", "protocol_ref_id", "approval_state",
    "created_by", "created_at",
)

RUN_SNAPSHOT_FIELDS = (
    "experiment_run_id", "experiment_plan_id", "executed_design_version_ids", "execution_status",
    "protocol_version_ref_id", "deviations", "sample_manifest_ref", "started_at", "completed_at",
    "operator_or_source",
)


def create_experiment_plan(
    session: Session,
    *,
    project_id: str,
    design_version_ids: list[str],
    hypotheses_tested: list[str] | None = None,
    controls: list[str] | None = None,
    factors: list[str] | None = None,
    response_variables: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
    protocol_ref_id: str | None = None,
    created_by: str,
) -> ExperimentPlan:
    plan = ExperimentPlan(
        experiment_plan_id=new_id("PLAN"),
        project_id=project_id,
        design_version_ids=design_version_ids,
        hypotheses_tested=hypotheses_tested or [],
        controls=controls or [],
        factors=factors or [],
        response_variables=response_variables or [],
        acceptance_criteria=acceptance_criteria or [],
        protocol_ref_id=protocol_ref_id,
        approval_state="proposed",
        created_by=created_by,
        created_at=now(),
    )
    session.add(plan)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.EXPERIMENT_PLANNED, entity_type="ExperimentPlan",
        entity_id=plan.experiment_plan_id, payload=snapshot(plan, PLAN_SNAPSHOT_FIELDS),
        actor_type="human", actor_id=created_by,
    )
    return plan


def approve_experiment_plan(session: Session, *, experiment_plan_id: str, approver_id: str) -> ExperimentPlan:
    plan = session.get(ExperimentPlan, experiment_plan_id)
    if plan is None:
        raise ValueError(f"no such experiment plan: {experiment_plan_id}")
    if plan.created_by == approver_id:
        from harness.designs.service import SelfApprovalError

        raise SelfApprovalError(f"actor {approver_id!r} created {experiment_plan_id} and cannot also approve it")
    plan.approval_state = "approved"
    session.flush()
    append_event(
        session, project_id=plan.project_id, event_type=et.EXPERIMENT_PLANNED, entity_type="ExperimentPlan",
        entity_id=plan.experiment_plan_id, payload=snapshot(plan, PLAN_SNAPSHOT_FIELDS),
        actor_type="human", actor_id=approver_id,
    )
    return plan


def record_experiment_run(
    session: Session,
    *,
    project_id: str,
    experiment_plan_id: str,
    executed_design_version_ids: list[str],
    execution_status: str = "completed",
    protocol_version_ref_id: str | None = None,
    deviations: list[str] | None = None,
    sample_manifest_ref: dict[str, Any] | None = None,
    started_at: float | None = None,
    completed_at: float | None = None,
    operator_or_source: str = "",
    actor_id: str,
) -> ExperimentRun:
    run = ExperimentRun(
        experiment_run_id=new_id("RUN"),
        experiment_plan_id=experiment_plan_id,
        executed_design_version_ids=executed_design_version_ids,
        execution_status=execution_status,
        protocol_version_ref_id=protocol_version_ref_id,
        deviations=deviations or [],
        sample_manifest_ref=sample_manifest_ref,
        started_at=started_at or now(),
        completed_at=completed_at,
        operator_or_source=operator_or_source,
    )
    session.add(run)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.RUN_RECORDED, entity_type="ExperimentRun",
        entity_id=run.experiment_run_id, payload=snapshot(run, RUN_SNAPSHOT_FIELDS),
        actor_type="human", actor_id=actor_id,
    )
    return run


def get_experiment_run(session: Session, experiment_run_id: str) -> ExperimentRun | None:
    return session.get(ExperimentRun, experiment_run_id)


def get_experiment_plan(session: Session, experiment_plan_id: str) -> ExperimentPlan | None:
    return session.get(ExperimentPlan, experiment_plan_id)
