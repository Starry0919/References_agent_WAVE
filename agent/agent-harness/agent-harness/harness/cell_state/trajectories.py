"""CellStateTrajectory (doc 6.7): links a baseline state through a
perturbation to predicted/observed states over time. Residuals are
appended, never used to overwrite the prediction they're measured against
(doc 6.12) - `predicted_state_ids` and `observed_state_ids` are separate
lists for the same reason `predicted`/`observed`/`inferred` are separate
`BiologicalStateSnapshot.source` values.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.cell_state.models import CellStateTrajectory
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.memory.event_store import snapshot as event_snapshot

TRAJECTORY_FIELDS = (
    "trajectory_id", "project_id", "baseline_state_id", "perturbation", "predicted_state_ids",
    "observed_state_ids", "timepoints", "model_versions", "experiment_run_ids",
    "prediction_observation_residuals", "uncertainty", "applicability_scope", "created_at",
)


def start_trajectory(
    session: Session,
    *,
    project_id: str,
    perturbation: dict[str, Any],
    actor_id: str,
    baseline_state_id: str | None = None,
    applicability_scope: dict[str, Any] | None = None,
) -> CellStateTrajectory:
    traj = CellStateTrajectory(
        trajectory_id=new_id("TRAJ"),
        project_id=project_id,
        baseline_state_id=baseline_state_id,
        perturbation=perturbation,
        predicted_state_ids=[],
        observed_state_ids=[],
        timepoints=[],
        model_versions=[],
        experiment_run_ids=[],
        prediction_observation_residuals=[],
        applicability_scope=applicability_scope or {},
        created_at=now(),
    )
    session.add(traj)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.OBSERVATION_DERIVED, entity_type="CellStateTrajectory",
        entity_id=traj.trajectory_id, payload=event_snapshot(traj, TRAJECTORY_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    return traj


def append_observed_state(
    session: Session,
    *,
    trajectory_id: str,
    observed_state_id: str,
    experiment_run_id: str | None,
    timepoint: dict[str, Any] | None,
    actor_id: str,
) -> CellStateTrajectory:
    traj = session.get(CellStateTrajectory, trajectory_id)
    if traj is None:
        raise ValueError(f"no such trajectory: {trajectory_id}")
    traj.observed_state_ids = [*traj.observed_state_ids, observed_state_id]
    if experiment_run_id and experiment_run_id not in traj.experiment_run_ids:
        traj.experiment_run_ids = [*traj.experiment_run_ids, experiment_run_id]
    if timepoint is not None:
        traj.timepoints = [*traj.timepoints, timepoint]
    session.flush()
    append_event(
        session, project_id=traj.project_id, event_type=et.OBSERVATION_DERIVED, entity_type="CellStateTrajectory",
        entity_id=traj.trajectory_id, payload=event_snapshot(traj, TRAJECTORY_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    return traj


def record_residual(
    session: Session, *, trajectory_id: str, prediction_id: str, observation_id: str, residual_value: dict[str, Any], actor_id: str
) -> CellStateTrajectory:
    """Appends a residual without ever mutating the prediction it's
    measured against - the prediction stays exactly what the model said
    ahead of time (doc 6.12)."""
    traj = session.get(CellStateTrajectory, trajectory_id)
    if traj is None:
        raise ValueError(f"no such trajectory: {trajectory_id}")
    entry = {"prediction_id": prediction_id, "observation_id": observation_id, "residual": residual_value, "recorded_at": now()}
    traj.prediction_observation_residuals = [*traj.prediction_observation_residuals, entry]
    session.flush()
    append_event(
        session, project_id=traj.project_id, event_type=et.OBSERVATION_DERIVED, entity_type="CellStateTrajectory",
        entity_id=traj.trajectory_id, payload=event_snapshot(traj, TRAJECTORY_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    return traj
