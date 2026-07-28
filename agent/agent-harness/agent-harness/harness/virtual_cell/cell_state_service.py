"""CellStateSnapshot facade (doc06 §3.1) over the existing, previously
un-faceted `harness.cell_state.models.BiologicalStateSnapshot` table (see
that module's docstring). Every field not explicitly supplied by the
caller is recorded as `unknown` in `field_provenance` - never inferred from
adjacent strains, omics, or embeddings (doc06 §2.2).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.cell_state.models import BiologicalStateSnapshot
from harness.cell_state.snapshots import record_snapshot
from harness.designs.models import DesignVersion
from harness.virtual_cell.models import FIELD_STATUS

_PHYSIOLOGY_FIELDS = ("growth_rate", "biomass", "substrate_uptake", "product_titer", "product_yield", "productivity", "stress_state")


def build_baseline_cell_state(
    session: Session,
    *,
    project_id: str,
    design_version: DesignVersion,
    chassis: dict[str, Any],
    environment: dict[str, Any],
    temporal_context: dict[str, Any] | None = None,
    physiology: dict[str, Any] | None = None,
    physiology_status: dict[str, str] | None = None,
    actor_id: str,
) -> BiologicalStateSnapshot:
    """Creates a baseline `CellStateSnapshot` for one `DesignVersion`.
    `physiology_status` maps each *supplied* physiology field to one of
    `FIELD_STATUS` (default `"assumed"` if the caller supplies a value
    without saying where it came from - never silently `"observed"`).
    Every physiology field the caller does NOT supply is recorded as
    `"unknown"` and listed in `missing_modalities`, never defaulted to 0 or
    interpolated from another strain/condition."""
    physiology = dict(physiology or {})
    physiology_status = dict(physiology_status or {})
    field_provenance: dict[str, str] = {}
    missing: list[str] = []

    for field in _PHYSIOLOGY_FIELDS:
        if field in physiology:
            status = physiology_status.get(field, "assumed")
            if status not in FIELD_STATUS:
                raise ValueError(f"unrecognized field status {status!r} for physiology.{field}; must be one of {FIELD_STATUS}")
            field_provenance[f"physiology.{field}"] = status
        else:
            field_provenance[f"physiology.{field}"] = "unknown"
            missing.append(f"physiology.{field}")

    field_provenance["chassis"] = "assumed" if chassis else "unknown"
    field_provenance["environment"] = "assumed" if environment else "unknown"
    field_provenance["molecular_state"] = "unknown"
    field_provenance["functional_state"] = "unknown"
    missing.extend(["molecular_state.transcriptome", "molecular_state.proteome", "molecular_state.metabolome", "functional_state.flux"])

    return record_snapshot(
        session, project_id=project_id, design_version_id=design_version.design_version_id,
        host=chassis, environment=environment, actor_id=actor_id, source="observed" if physiology else "inferred",
        temporal_context=temporal_context or {}, physiology=physiology, field_provenance=field_provenance,
        missing_modalities=missing, quality_status="ok" if physiology else "degraded",
    )


def get_cell_state(session: Session, cell_state_id: str) -> BiologicalStateSnapshot | None:
    return session.get(BiologicalStateSnapshot, cell_state_id)


def cell_state_to_dict(snap: BiologicalStateSnapshot) -> dict[str, Any]:
    return {
        "cell_state_id": snap.snapshot_id, "schema_version": snap.schema_version, "version": snap.version,
        "project_id": snap.project_id, "design_version_id": snap.design_version_id,
        "chassis": snap.host, "environment": snap.environment, "temporal_context": snap.temporal_context,
        "functional_state": snap.functional_state, "physiology": snap.physiology,
        "field_provenance": snap.field_provenance, "missing_modalities": snap.missing_modalities,
        "quality_status": snap.quality_status, "source": snap.source, "created_at": snap.created_at,
    }
