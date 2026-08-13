"""BiologicalStateSnapshot / CellStateTrajectory (doc 3.3, 6.7) and a bare
ModelVersion/Prediction/Residual registry (doc 6.12). Condition-scoped and
insert-only: no service function in this codebase updates an existing
snapshot's fields - a new condition, timepoint, or re-measurement always
produces a new row, so two snapshots for the same design under different
media never collapse into one merged "current state" (design-review
requirement for integration scenario C).

Problem 06 (Predictive Simulation Loop & Virtual Cell Integration) is the
"future model integration" this module's own docstring anticipated: rather
than a second, parallel `CellStateSnapshot` table, `harness/virtual_cell/
cell_state_service.py` is the real facade this table never had, and the
columns below (`schema_version`, `version`, `temporal_context`,
`functional_state`, `physiology`, `field_provenance`, `missing_modalities`,
`quality_status`) are additive - every existing caller
(`harness.cell_state.snapshots.record_snapshot`, doc02's own integration
test) keeps working unchanged with these left at their defaults.

`ModelVersion`/`Prediction`/`Residual` remain bare ORM classes with no
facade of their own - Problem 06 does not write through them (its own,
richer `SimulationRun`/`SimulationResult`/`PredictionResidual` tables in
`harness.virtual_cell.models` are the real, adapter-backed equivalents);
they are left as-is rather than deleted since another caller may still
reference the table names.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields


class BiologicalStateSnapshot(Base):
    __tablename__ = "biological_state_snapshots"

    snapshot_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    design_version_id: Mapped[str | None] = mapped_column(String, default=None, index=True)
    experiment_run_id: Mapped[str | None] = mapped_column(String, default=None)
    host: Mapped[dict] = mapped_column(JSON, default=dict)  # {species, strain}
    genotype_ref: Mapped[str | None] = mapped_column(String, default=None)
    environment: Mapped[dict] = mapped_column(JSON, default=dict)  # {medium, carbon_source, temperature_c, oxygenation, cultivation_mode}
    timepoint: Mapped[dict | None] = mapped_column(JSON, default=None)  # {value, unit, phase}
    perturbations: Mapped[list] = mapped_column(JSON, default=list)
    phenotype_observations: Mapped[list] = mapped_column(JSON, default=list)  # observation_ids
    omics_observations: Mapped[list] = mapped_column(JSON, default=list)  # observation_ids
    model_predictions: Mapped[list] = mapped_column(JSON, default=list)  # prediction_ids
    source: Mapped[str] = mapped_column(String, default="observed")  # observed|predicted|inferred
    uncertainty: Mapped[list] = mapped_column(JSON, default=list)
    provenance: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[float] = mapped_column(Float)
    # --- Problem 06 additions (migration 0005_virtual_cell_schema) -----
    schema_version: Mapped[str] = mapped_column(String, default="1")
    version: Mapped[int] = mapped_column(Integer, default=1)
    # {timepoint: {value, unit}, growth_phase, prediction_horizon}. Kept
    # separate from the legacy `timepoint` column above (still populated
    # for back-compat) rather than repurposing it, since prediction_horizon
    # has no equivalent there and doc06 3.1 asks for all three together.
    temporal_context: Mapped[dict] = mapped_column(JSON, default=dict)
    functional_state: Mapped[dict] = mapped_column(JSON, default=dict)  # {flux_ref, pathway_activity_ref, resource_allocation_ref}
    physiology: Mapped[dict] = mapped_column(JSON, default=dict)  # {growth_rate, biomass, substrate_uptake, product_titer, product_yield, productivity, stress_state}
    # Per-field status: {"physiology.growth_rate": "observed"|"model_inferred"|"literature_derived"|"assumed"|"unknown", ...}
    # doc06 3.1's mandatory per-field provenance - never inferred from
    # adjacent strains/omics/embeddings, only ever set explicitly by the
    # caller that wrote the corresponding value.
    field_provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    missing_modalities: Mapped[list] = mapped_column(JSON, default=list)
    quality_status: Mapped[str] = mapped_column(String, default="unknown")  # ok|degraded|unknown


# Only the explicit lifecycle-adjacent fields may change post-creation;
# every substantive state field is condition-scoped and insert-only (module
# docstring) - a re-measurement always creates a new row.
guard_immutable_fields(
    BiologicalStateSnapshot,
    mutable_fields={"phenotype_observations", "omics_observations", "model_predictions", "quality_status"},
)


class CellStateTrajectory(Base):
    __tablename__ = "cell_state_trajectories"

    trajectory_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    baseline_state_id: Mapped[str | None] = mapped_column(String, default=None)
    perturbation: Mapped[dict] = mapped_column(JSON, default=dict)  # {design_version_id, construct_id, environmental_change, time_zero}
    predicted_state_ids: Mapped[list] = mapped_column(JSON, default=list)
    observed_state_ids: Mapped[list] = mapped_column(JSON, default=list)
    timepoints: Mapped[list] = mapped_column(JSON, default=list)
    model_versions: Mapped[list] = mapped_column(JSON, default=list)
    experiment_run_ids: Mapped[list] = mapped_column(JSON, default=list)
    prediction_observation_residuals: Mapped[list] = mapped_column(JSON, default=list)
    uncertainty: Mapped[dict | None] = mapped_column(JSON, default=None)
    applicability_scope: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[float] = mapped_column(Float)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    model_version_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    training_data_snapshot_ref: Mapped[str | None] = mapped_column(String, default=None)
    applicability_scope: Mapped[dict] = mapped_column(JSON, default=dict)
    artifact_checksum: Mapped[str | None] = mapped_column(String, default=None)
    baseline_evaluation: Mapped[dict | None] = mapped_column(JSON, default=None)
    approved_by: Mapped[str | None] = mapped_column(String, default=None)
    is_default: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[float] = mapped_column(Float)


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id: Mapped[str] = mapped_column(String, primary_key=True)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.model_version_id"), index=True)
    subject_design_version_id: Mapped[str | None] = mapped_column(String, default=None)
    input_conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    predicted_value: Mapped[dict] = mapped_column(JSON, default=dict)
    uncertainty: Mapped[dict | None] = mapped_column(JSON, default=None)
    created_at: Mapped[float] = mapped_column(Float)


class Residual(Base):
    __tablename__ = "residuals"

    residual_id: Mapped[str] = mapped_column(String, primary_key=True)
    prediction_id: Mapped[str] = mapped_column(ForeignKey("predictions.prediction_id"), index=True)
    observation_id: Mapped[str] = mapped_column(String)
    residual_value: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[float] = mapped_column(Float)
