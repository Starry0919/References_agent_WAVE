"""Observation Normalizer (doc03 4.2): converts raw structured or freeform
input into Problem 02's `Observation` rows (extended with Problem 03's
fields - see migration `0002_diagnosis_loop_schema`). Freeform text is
tagged `unstructured_input` and only becomes a committed `Observation`
after the same unit/condition/QC/provenance checks as structured input -
never merged or written on the strength of prose alone.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from harness.experiments.models import Observation
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

OBSERVATION_SNAPSHOT_FIELDS = (
    "observation_id", "project_id", "data_asset_ids", "subject_design_version_id", "subject_construct_id",
    "condition_ref", "timepoint", "metric", "value", "unit", "uncertainty", "replicate_summary", "qc_flags",
    "qc_status", "analysis_pipeline_version", "source_type", "created_at",
    "reference_or_baseline", "detection_limit", "replicates", "biological_context_id", "assay_id",
)


@dataclass
class RawObservationInput:
    feature_or_phenotype: str
    value: float | None
    unit: str | None
    condition_id: str | None = None  # BiologicalContext.context_id
    reference_or_baseline: dict[str, Any] | None = None
    uncertainty: float | None = None
    replicates: int | None = None
    qc_status: str | None = None
    detection_limit: float | None = None
    assay_id: str | None = None
    timepoint: dict[str, Any] | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    source_type: str = "structured_input"  # structured_input|unstructured_input
    # Cross-Modal Consistency fields (prompt §6.2/§6.4, migration 0008) -
    # set at construction time only, since `Observation.modality`/etc are
    # immutable after creation (guard_immutable_fields) like every other
    # content field on this row.
    modality: str = "unknown"
    entity_namespace: str = "unknown"
    entity_id: str | None = None
    batch: str | None = None


@dataclass
class NormalizationIssue:
    field: str
    code: str
    message: str
    severity: str = "error"  # error|warning


@dataclass
class NormalizationReport:
    valid: bool
    issues: list[NormalizationIssue] = field(default_factory=list)


def validate_raw_observation(raw: RawObservationInput) -> NormalizationReport:
    issues: list[NormalizationIssue] = []
    if raw.value is None:
        issues.append(NormalizationIssue("value", "missing_value", "no numeric value provided"))
    if not raw.unit:
        issues.append(NormalizationIssue("unit", "missing_unit", "no unit provided"))
    if not raw.condition_id:
        issues.append(NormalizationIssue("condition_id", "missing_condition", "no BiologicalContext bound"))
    if not raw.qc_status:
        issues.append(NormalizationIssue("qc_status", "missing_qc", "no QC status provided", severity="warning"))
    if raw.source_type == "unstructured_input" and not raw.provenance.get("extracted_from"):
        issues.append(NormalizationIssue("provenance", "missing_provenance", "unstructured input has no provenance trail"))
    errors = [i for i in issues if i.severity == "error"]
    return NormalizationReport(valid=not errors, issues=issues)


def normalize_and_commit(
    session: Session, *, project_id: str, raw: RawObservationInput, actor_id: str
) -> tuple[Observation | None, NormalizationReport]:
    """Returns `(None, report)` if validation fails - the caller (Data
    Sufficiency Gate / intake orchestration) decides whether that means
    `data_required` or a limited/partial diagnosis proceeds without this
    particular observation."""
    report = validate_raw_observation(raw)
    if not report.valid:
        return None, report

    obs = Observation(
        observation_id=new_id("OBS"), project_id=project_id, data_asset_ids=[], subject_design_version_id=None,
        condition_ref=raw.provenance.get("condition_ref", {}), timepoint=raw.timepoint, metric=raw.feature_or_phenotype,
        value=raw.value, unit=raw.unit, uncertainty=raw.uncertainty, replicate_summary=None, qc_flags=[],
        qc_status=raw.qc_status or "pending",
        source_type="human_assertion" if raw.source_type == "unstructured_input" else "instrument",
        reference_or_baseline=raw.reference_or_baseline, detection_limit=raw.detection_limit,
        replicates=raw.replicates, biological_context_id=raw.condition_id, assay_id=raw.assay_id, created_at=now(),
        modality=raw.modality, entity_namespace=raw.entity_namespace, entity_id=raw.entity_id, batch=raw.batch,
    )
    session.add(obs)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.DIAGNOSIS_OBSERVATION_NORMALIZED, entity_type="Observation",
        entity_id=obs.observation_id, payload=snapshot(obs, OBSERVATION_SNAPSHOT_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    return obs, report
