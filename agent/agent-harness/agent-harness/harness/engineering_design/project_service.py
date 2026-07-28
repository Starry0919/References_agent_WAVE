"""`EngineeringDesignProject` mutations (doc04 3.1, §2.2): Objective and
Constraint Formalization. Preferences/weights may reorder candidates; they
must never be readable by anything upstream of this package (diagnosis
confidence, evidence tiers) - enforced structurally, same as Problem 03's
`ProjectObjective`/`HypothesisAssessment` separation: nothing in
`harness.diagnosis` ever imports from this package.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.db import check_and_bump_version
from harness.engineering_design.models import EngineeringDesignProject
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.workflow.gates import design_objective_gate

PROJECT_SNAPSHOT_FIELDS = (
    "design_project_id", "project_id", "schema_version", "chassis", "chassis_version_or_genotype",
    "baseline_state_id", "diagnosis_session_id", "diagnosis_decision_id", "diagnosis_version",
    "temporal_and_environmental_context", "primary_metrics", "secondary_metrics", "hard_constraints",
    "preferences_or_weights", "available_resources", "autonomy_level", "required_human_gates",
    "status", "revision_count", "created_by", "created_at", "updated_at", "version",
)


class ObjectiveRejected(RuntimeError):
    """DesignObjectiveGate rejected the objective formalization (missing
    primary metrics or never-reviewed hard constraints)."""


def create_design_project(
    session: Session,
    *,
    project_id: str,
    chassis: str,
    chassis_version_or_genotype: str,
    diagnosis_session_id: str,
    diagnosis_decision_id: str,
    diagnosis_version: int,
    actor_id: str,
    baseline_state_id: str | None = None,
    temporal_and_environmental_context: dict[str, Any] | None = None,
    autonomy_level: str = "recommend_only",
    required_human_gates: list[str] | None = None,
) -> EngineeringDesignProject:
    ts = now()
    proj = EngineeringDesignProject(
        design_project_id=new_id("EDP"), project_id=project_id, chassis=chassis,
        chassis_version_or_genotype=chassis_version_or_genotype, baseline_state_id=baseline_state_id,
        diagnosis_session_id=diagnosis_session_id, diagnosis_decision_id=diagnosis_decision_id,
        diagnosis_version=diagnosis_version, temporal_and_environmental_context=temporal_and_environmental_context or {},
        autonomy_level=autonomy_level, required_human_gates=required_human_gates or ["build_approval"],
        status="diagnostic_blocked", created_by=actor_id, created_at=ts, updated_at=ts,
    )
    session.add(proj)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.DESIGN_PROJECT_CREATED, entity_type="EngineeringDesignProject",
        entity_id=proj.design_project_id, payload=snapshot(proj, PROJECT_SNAPSHOT_FIELDS),
        actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
    )
    return proj


def get_design_project(session: Session, design_project_id: str) -> EngineeringDesignProject | None:
    return session.get(EngineeringDesignProject, design_project_id)


def set_objectives(
    session: Session,
    *,
    design_project_id: str,
    primary_metrics: list[dict[str, Any]],
    secondary_metrics: list[dict[str, Any]] | None,
    hard_constraints: list[dict[str, Any]],
    preferences_or_weights: list[dict[str, Any]] | None,
    available_resources: dict[str, Any] | None,
    expected_version: int,
    actor_id: str,
) -> EngineeringDesignProject:
    """doc04 §2.2: hard constraints, preferences/weights are recorded
    explicitly (an empty list is a valid, reviewed answer; `None` is not -
    the caller must always pass a list, even if empty, for
    `hard_constraints`)."""
    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None:
        raise ValueError(f"no such design project: {design_project_id}")

    gate = design_objective_gate(has_primary_metrics=bool(primary_metrics), has_hard_constraints_declared=hard_constraints is not None)
    if gate.status.value != "pass":
        raise ObjectiveRejected(f"objective rejected by DesignObjectiveGate: {[v.message for v in gate.violations]}")

    check_and_bump_version(proj, expected_version)
    proj.primary_metrics = primary_metrics
    proj.secondary_metrics = secondary_metrics or []
    proj.hard_constraints = hard_constraints
    proj.preferences_or_weights = preferences_or_weights or []
    proj.available_resources = available_resources or {}
    proj.updated_at = now()
    session.flush()
    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_PROJECT_CREATED, entity_type="EngineeringDesignProject",
        entity_id=proj.design_project_id, payload=snapshot(proj, PROJECT_SNAPSHOT_FIELDS),
        actor_type="human", actor_id=actor_id,
    )
    return proj
