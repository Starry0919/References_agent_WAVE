"""BiologicalStateSnapshot creation (doc 3.3, 6.7): insert-only and
condition-scoped. No function here ever updates an existing snapshot - a
new condition, timepoint, or design always produces a new row, so two
snapshots for the same design under different media coexist rather than
one silently overwriting the other (integration scenario C).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.cell_state.models import BiologicalStateSnapshot
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.memory.event_store import snapshot as event_snapshot

SNAPSHOT_FIELDS = (
    "snapshot_id", "project_id", "design_version_id", "experiment_run_id", "host", "genotype_ref",
    "environment", "timepoint", "perturbations", "phenotype_observations", "omics_observations",
    "model_predictions", "source", "uncertainty", "provenance", "created_at",
    "schema_version", "version", "temporal_context", "functional_state", "physiology",
    "field_provenance", "missing_modalities", "quality_status",
)


def record_snapshot(
    session: Session,
    *,
    project_id: str,
    host: dict[str, Any],
    environment: dict[str, Any],
    actor_id: str,
    design_version_id: str | None = None,
    experiment_run_id: str | None = None,
    timepoint: dict[str, Any] | None = None,
    phenotype_observation_ids: list[str] | None = None,
    omics_observation_ids: list[str] | None = None,
    genotype_ref: str | None = None,
    perturbations: list[Any] | None = None,
    source: str = "observed",
    uncertainty: list[Any] | None = None,
    # --- Problem 06 additions; all optional/back-compat-defaulted so the
    # doc02 caller (`test_scenario_c_cross_condition_results_stay_separate`)
    # and any other pre-existing caller are unaffected. ---
    temporal_context: dict[str, Any] | None = None,
    functional_state: dict[str, Any] | None = None,
    physiology: dict[str, Any] | None = None,
    field_provenance: dict[str, str] | None = None,
    missing_modalities: list[str] | None = None,
    quality_status: str = "unknown",
) -> BiologicalStateSnapshot:
    if source not in ("observed", "predicted", "inferred"):
        raise ValueError(f"unrecognized source {source!r}; must be observed/predicted/inferred")
    snap = BiologicalStateSnapshot(
        snapshot_id=new_id("SNAP"),
        project_id=project_id,
        design_version_id=design_version_id,
        experiment_run_id=experiment_run_id,
        host=host,
        genotype_ref=genotype_ref,
        environment=environment,
        timepoint=timepoint,
        perturbations=perturbations or [],
        phenotype_observations=phenotype_observation_ids or [],
        omics_observations=omics_observation_ids or [],
        model_predictions=[],
        source=source,
        uncertainty=uncertainty or [],
        provenance=[],
        created_at=now(),
        temporal_context=temporal_context or {},
        functional_state=functional_state or {},
        physiology=physiology or {},
        field_provenance=field_provenance or {},
        missing_modalities=missing_modalities or [],
        quality_status=quality_status,
    )
    session.add(snap)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.OBSERVATION_DERIVED, entity_type="BiologicalStateSnapshot",
        entity_id=snap.snapshot_id, payload=event_snapshot(snap, SNAPSHOT_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    return snap


def list_snapshots_for_design(session: Session, design_version_id: str) -> list[BiologicalStateSnapshot]:
    from sqlalchemy import select

    return list(
        session.execute(
            select(BiologicalStateSnapshot).where(BiologicalStateSnapshot.design_version_id == design_version_id)
        ).scalars()
    )
