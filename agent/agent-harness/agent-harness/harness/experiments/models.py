"""ExperimentPlan/ExperimentRun and DataAsset/Observation - two deliberate
splits the doc insists on (8.4, 8.5): plan vs. actual execution (so protocol
deviations and real sample identity are recorded, not inferred), and raw
file vs. derived measurement (so an LLM's interpretation of a file can
never stand in for the file itself).
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields


class ProtocolVersionRef(Base):
    """doc 6.10: protocol version changes what an Observation is comparable
    to, so it is pinned per `ExperimentRun`, never silently repointed to
    "whatever the latest protocol is now" after an update."""

    __tablename__ = "protocol_version_refs"

    protocol_id: Mapped[str] = mapped_column(String, primary_key=True)
    version: Mapped[str] = mapped_column(String)
    immutable_snapshot_or_checksum: Mapped[str | None] = mapped_column(String, default=None)
    authoritative_uri: Mapped[str | None] = mapped_column(String, default=None)
    critical_parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    deviation_record_ids: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[float] = mapped_column(Float)


class ExperimentPlan(Base):
    __tablename__ = "experiment_plans"

    experiment_plan_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    design_version_ids: Mapped[list] = mapped_column(JSON, default=list)
    hypotheses_tested: Mapped[list] = mapped_column(JSON, default=list)  # hypothesis_version_ids
    controls: Mapped[list] = mapped_column(JSON, default=list)
    factors: Mapped[list] = mapped_column(JSON, default=list)
    response_variables: Mapped[list] = mapped_column(JSON, default=list)
    acceptance_criteria: Mapped[list] = mapped_column(JSON, default=list)
    protocol_ref_id: Mapped[str | None] = mapped_column(String, default=None)  # ProtocolVersionRef.protocol_id
    approval_state: Mapped[str] = mapped_column(String, default="proposed")  # proposed|approved|rejected
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"

    experiment_run_id: Mapped[str] = mapped_column(String, primary_key=True)
    experiment_plan_id: Mapped[str] = mapped_column(ForeignKey("experiment_plans.experiment_plan_id"), index=True)
    executed_design_version_ids: Mapped[list] = mapped_column(JSON, default=list)
    execution_status: Mapped[str] = mapped_column(String, default="pending")  # pending|in_progress|completed|failed
    protocol_version_ref_id: Mapped[str | None] = mapped_column(String, default=None)
    deviations: Mapped[list] = mapped_column(JSON, default=list)
    sample_manifest_ref: Mapped[dict | None] = mapped_column(JSON, default=None)
    started_at: Mapped[float | None] = mapped_column(Float, default=None)
    completed_at: Mapped[float | None] = mapped_column(Float, default=None)
    operator_or_source: Mapped[str] = mapped_column(String, default="")


class DataAsset(Base):
    """Raw uploaded file identity. `checksum` is the idempotency anchor
    (doc 9.3): a second upload with the same checksum for the same project
    must be recognized as a duplicate, never silently re-ingested."""

    __tablename__ = "data_assets"

    data_asset_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    experiment_run_id: Mapped[str] = mapped_column(ForeignKey("experiment_runs.experiment_run_id"), index=True)
    file_uri: Mapped[str] = mapped_column(String)
    checksum: Mapped[str] = mapped_column(String, index=True)
    media_type: Mapped[str] = mapped_column(String, default="text/csv")
    assay_type: Mapped[str] = mapped_column(String)  # growth_curve|titer|genotype_verification|...
    parser_name: Mapped[str | None] = mapped_column(String, default=None)
    parser_version: Mapped[str | None] = mapped_column(String, default=None)
    schema_version: Mapped[str] = mapped_column(String, default="1")
    units: Mapped[dict] = mapped_column(JSON, default=dict)
    sample_mapping_ref: Mapped[dict | None] = mapped_column(JSON, default=None)
    qc_status: Mapped[str] = mapped_column(String, default="pending")  # pending|passed|failed|excluded
    source_type: Mapped[str] = mapped_column(String, default="instrument")  # instrument|human_assertion
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    uploaded_by: Mapped[str] = mapped_column(String)
    uploaded_at: Mapped[float] = mapped_column(Float)


class Observation(Base):
    """doc 8.5: a derived, QC'd measurement - always points back to the raw
    `DataAsset`(s) and the parser/pipeline version that produced it. Never
    created directly from LLM text."""

    __tablename__ = "observations"

    observation_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    data_asset_ids: Mapped[list] = mapped_column(JSON, default=list)
    subject_design_version_id: Mapped[str | None] = mapped_column(String, default=None)
    subject_construct_id: Mapped[str | None] = mapped_column(String, default=None)
    condition_ref: Mapped[dict] = mapped_column(JSON, default=dict)  # {medium, carbon_source, temperature_c, oxygenation, cultivation_mode}
    timepoint: Mapped[dict | None] = mapped_column(JSON, default=None)  # {value, unit, phase}
    metric: Mapped[str] = mapped_column(String)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String)
    uncertainty: Mapped[float | None] = mapped_column(Float, default=None)
    replicate_summary: Mapped[dict | None] = mapped_column(JSON, default=None)  # {n, mean, sd, cv}
    qc_flags: Mapped[list] = mapped_column(JSON, default=list)
    qc_status: Mapped[str] = mapped_column(String, default="pending")  # pending|passed|failed|excluded
    analysis_pipeline_version: Mapped[str | None] = mapped_column(String, default=None)
    source_type: Mapped[str] = mapped_column(String, default="instrument")  # instrument|human_assertion
    idempotency_key: Mapped[str | None] = mapped_column(String, index=True, default=None)
    created_at: Mapped[float] = mapped_column(Float)
    # Problem 03 (Bottleneck Diagnosis) fields, added via migration 0002.
    # `metric`/`data_asset_ids` above already cover doc 3.2's
    # feature_or_phenotype/raw_data_reference - reused, not duplicated.
    reference_or_baseline: Mapped[dict | None] = mapped_column(JSON, default=None)
    detection_limit: Mapped[float | None] = mapped_column(Float, default=None)
    replicates: Mapped[int | None] = mapped_column(default=None)
    # Problem 06 Cross-Modal Consistency fields (六大核心模块统一集成 prompt
    # §6.2/§6.4, migration 0008). `metric` above already carries the raw
    # feature name (e.g. "mRNA:trpE") - `modality`/`entity_namespace`/
    # `entity_id` make that machine-queryable across the transcript/
    # protein/metabolite/flux/phenotype layers without a second
    # "OmicsObservation" table duplicating this one. `unknown`/`None` for
    # every pre-existing row and every caller that doesn't set them -
    # never inferred.
    modality: Mapped[str] = mapped_column(String, default="unknown")  # transcriptomic|proteomic|metabolomic|fluxomic|phenotypic|unknown
    entity_namespace: Mapped[str] = mapped_column(String, default="unknown")  # gene|protein|metabolite|reaction|phenotype|unknown
    entity_id: Mapped[str | None] = mapped_column(String, default=None, index=True)
    batch: Mapped[str | None] = mapped_column(String, default=None)
    biological_context_id: Mapped[str | None] = mapped_column(String, default=None, index=True)
    assay_id: Mapped[str | None] = mapped_column(String, default=None)


# The measurement itself is immutable once derived; only its QC
# disposition may change (reprocess/exclude/mark inconclusive - doc 10.2's
# Data QC Gate), never the value/condition/metric it reports.
guard_immutable_fields(Observation, mutable_fields={"qc_status", "qc_flags"})
