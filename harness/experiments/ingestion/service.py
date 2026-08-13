"""Upload orchestration (doc 11.2): checksum & type detection -> project/
run/sample binding -> schema validation -> QC -> parser creates
observations -> caller previews -> commit. Idempotency is checksum-based
(doc 9.3): a second upload with the same checksum for the same project
returns the existing `DataAsset` instead of silently re-ingesting.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.experiments.ingestion.data_ingestor import (
    AssetMetadata,
    DataIngestor,
    ParsedDataset,
    QCReport,
    SampleBinding,
)
from harness.experiments.models import DataAsset, Observation
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.workflow.gates import data_identity_gate, data_qc_gate

OBSERVATION_SNAPSHOT_FIELDS = (
    "observation_id", "project_id", "data_asset_ids", "subject_design_version_id", "subject_construct_id",
    "condition_ref", "timepoint", "metric", "value", "unit", "uncertainty", "replicate_summary",
    "qc_flags", "qc_status", "analysis_pipeline_version", "source_type", "created_at",
)

DATA_ASSET_SNAPSHOT_FIELDS = (
    "data_asset_id", "project_id", "experiment_run_id", "file_uri", "checksum", "media_type", "assay_type",
    "parser_name", "parser_version", "schema_version", "units", "sample_mapping_ref", "qc_status",
    "source_type", "provenance", "uploaded_by", "uploaded_at",
)


class DataIdentityError(RuntimeError):
    """Raised when one or more parsed samples have no sample-manifest
    binding - the Data Identity Gate rejecting the upload outright."""


@dataclass
class IngestionResult:
    duplicate: bool
    data_asset: DataAsset | None
    observations: list[dict[str, Any]] = field(default_factory=list)
    qc_report: QCReport | None = None
    committed_observation_ids: list[str] = field(default_factory=list)


def _checksum(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


def find_duplicate_asset(session: Session, *, project_id: str, checksum: str) -> DataAsset | None:
    return session.execute(
        select(DataAsset).where(DataAsset.project_id == project_id, DataAsset.checksum == checksum)
    ).scalars().first()


def ingest_csv_asset(
    session: Session,
    *,
    project_id: str,
    experiment_run_id: str,
    file_uri: str,
    raw_bytes: bytes,
    assay_type: str,
    ingestor: DataIngestor,
    sample_manifest: dict[str, SampleBinding],
    uploaded_by: str,
    commit: bool = True,
) -> IngestionResult:
    """Runs the full doc-11.2 pipeline for one CSV asset against one
    `DataIngestor`. Raises `DataIdentityError` if any parsed sample lacks a
    manifest binding - ingestion is rejected outright, not partially
    processed with a caveat. `commit=False` returns a preview (parsed +
    QC'd Observation dicts) without writing anything to the database."""
    checksum = _checksum(raw_bytes)
    existing = find_duplicate_asset(session, project_id=project_id, checksum=checksum)
    if existing is not None:
        return IngestionResult(duplicate=True, data_asset=existing)

    raw_text = raw_bytes.decode("utf-8")
    metadata = AssetMetadata(file_uri=file_uri, media_type="text/csv", assay_type=assay_type, checksum=checksum)
    if not ingestor.can_handle(metadata):
        raise ValueError(f"ingestor {ingestor.name!r} cannot handle assay_type={assay_type!r}")

    validation = ingestor.validate(raw_text)
    if not validation.valid:
        raise ValueError(f"validation failed: {validation.errors}")

    parsed: ParsedDataset = ingestor.parse(raw_text, sample_manifest)

    unmapped = sorted({row.sample_id for row in parsed.rows} - set(sample_manifest.keys()))
    identity_result = data_identity_gate(unmapped)
    if identity_result.status.value == "fail":
        raise DataIdentityError(
            f"{len(unmapped)} sample(s) have no sample-manifest binding: {unmapped}; "
            f"gate violations: {[v.message for v in identity_result.violations]}"
        )

    qc_report = ingestor.qc(parsed)
    observation_dicts = ingestor.to_observation_dicts(parsed, qc_report, sample_manifest)

    if not commit:
        return IngestionResult(duplicate=False, data_asset=None, observations=observation_dicts, qc_report=qc_report)

    ts = now()
    asset = DataAsset(
        data_asset_id=new_id("ASSET"),
        project_id=project_id,
        experiment_run_id=experiment_run_id,
        file_uri=file_uri,
        checksum=checksum,
        media_type="text/csv",
        assay_type=assay_type,
        parser_name=parsed.parser_name,
        parser_version=parsed.parser_version,
        qc_status="passed" if qc_report.passed else "failed",
        source_type="instrument",
        uploaded_by=uploaded_by,
        uploaded_at=ts,
    )
    session.add(asset)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.DATA_INGESTED, entity_type="DataAsset",
        entity_id=asset.data_asset_id, payload=snapshot(asset, DATA_ASSET_SNAPSHOT_FIELDS),
        actor_type="human", actor_id=uploaded_by,
    )
    append_event(
        session, project_id=project_id, event_type=et.QC_COMPLETED, entity_type="DataAsset",
        entity_id=asset.data_asset_id,
        payload={"qc_status": asset.qc_status, "flags": [f.__dict__ for f in qc_report.flags]},
        actor_type="agent", actor_id="qc_pipeline",
    )

    committed_ids = []
    for obs_dict in observation_dicts:
        obs = Observation(
            observation_id=new_id("OBS"),
            project_id=project_id,
            data_asset_ids=[asset.data_asset_id],
            subject_design_version_id=obs_dict.get("subject_design_version_id"),
            subject_construct_id=obs_dict.get("subject_construct_id"),
            condition_ref=obs_dict.get("condition_ref", {}),
            timepoint=obs_dict.get("timepoint"),
            metric=obs_dict["metric"],
            value=obs_dict["value"],
            unit=obs_dict["unit"],
            replicate_summary=obs_dict.get("replicate_summary"),
            qc_flags=obs_dict.get("qc_flags", []),
            qc_status=obs_dict.get("qc_status", "pending"),
            analysis_pipeline_version=obs_dict.get("analysis_pipeline_version"),
            source_type=obs_dict.get("source_type", "instrument"),
            idempotency_key=f"{checksum}:{obs_dict.get('metric')}:{committed_ids and len(committed_ids) or 0}",
            created_at=ts,
        )
        session.add(obs)
        session.flush()
        committed_ids.append(obs.observation_id)
        append_event(
            session, project_id=project_id, event_type=et.OBSERVATION_DERIVED, entity_type="Observation",
            entity_id=obs.observation_id, payload=snapshot(obs, OBSERVATION_SNAPSHOT_FIELDS),
            actor_type="agent", actor_id="qc_pipeline",
        )

    return IngestionResult(
        duplicate=False, data_asset=asset, observations=observation_dicts,
        qc_report=qc_report, committed_observation_ids=committed_ids,
    )


def record_human_assertion_observation(
    session: Session,
    *,
    project_id: str,
    subject_design_version_id: str | None,
    condition_ref: dict[str, Any],
    metric: str,
    value: float,
    unit: str,
    asserted_by: str,
    timepoint: dict[str, Any] | None = None,
) -> Observation:
    """doc 11.2: a human-typed structured conclusion is a legitimate first-
    wave input, but must be tagged `source_type: human_assertion` and never
    conflated with instrument-derived data."""
    obs = Observation(
        observation_id=new_id("OBS"),
        project_id=project_id,
        data_asset_ids=[],
        subject_design_version_id=subject_design_version_id,
        condition_ref=condition_ref,
        timepoint=timepoint,
        metric=metric,
        value=value,
        unit=unit,
        qc_status="passed",
        source_type="human_assertion",
        created_at=now(),
    )
    session.add(obs)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.OBSERVATION_DERIVED, entity_type="Observation",
        entity_id=obs.observation_id, payload=snapshot(obs, OBSERVATION_SNAPSHOT_FIELDS),
        actor_type="human", actor_id=asserted_by,
    )
    return obs
