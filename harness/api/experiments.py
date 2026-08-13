"""ExperimentPlan/ExperimentRun and data-ingestion API routes."""
from __future__ import annotations

import base64
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.experiments import service as exp_svc
from harness.experiments.ingestion.data_ingestor import SampleBinding
from harness.experiments.ingestion.growth_titer_csv import GrowthTiterCsvIngestor
from harness.experiments.ingestion.service import DataIdentityError, ingest_csv_asset

router = APIRouter(prefix="/api/experiments", tags=["experiments"])

_INGESTORS = {"growth_titer_csv": GrowthTiterCsvIngestor()}


class CreatePlanBody(BaseModel):
    project_id: str
    design_version_ids: list[str]
    hypotheses_tested: list[str] = []
    controls: list[str] = []
    factors: list[str] = []
    response_variables: list[str] = []
    acceptance_criteria: list[str] = []
    protocol_ref_id: str | None = None
    created_by: str


@router.post("/plans")
def create_plan(body: CreatePlanBody, session: Session = Depends(get_db_session)) -> dict:
    plan = exp_svc.create_experiment_plan(session, **body.model_dump())
    return {"experiment_plan_id": plan.experiment_plan_id, "approval_state": plan.approval_state}


@router.get("/plans/{experiment_plan_id}")
def get_plan(experiment_plan_id: str, session: Session = Depends(get_db_session)) -> dict:
    plan = exp_svc.get_experiment_plan(session, experiment_plan_id)
    if plan is None:
        raise HTTPException(404, "experiment plan not found")
    return {
        "experiment_plan_id": plan.experiment_plan_id, "project_id": plan.project_id,
        "design_version_ids": plan.design_version_ids, "approval_state": plan.approval_state,
    }


class RecordRunBody(BaseModel):
    project_id: str
    experiment_plan_id: str
    executed_design_version_ids: list[str]
    execution_status: str = "completed"
    deviations: list[str] = []
    operator_or_source: str = ""
    actor_id: str


@router.post("/runs")
def record_run(body: RecordRunBody, session: Session = Depends(get_db_session)) -> dict:
    data = body.model_dump()
    actor_id = data.pop("actor_id")
    run = exp_svc.record_experiment_run(session, actor_id=actor_id, **data)
    return {"experiment_run_id": run.experiment_run_id, "execution_status": run.execution_status}


@router.get("/runs/{experiment_run_id}")
def get_run(experiment_run_id: str, session: Session = Depends(get_db_session)) -> dict:
    run = exp_svc.get_experiment_run(session, experiment_run_id)
    if run is None:
        raise HTTPException(404, "experiment run not found")
    return {
        "experiment_run_id": run.experiment_run_id, "experiment_plan_id": run.experiment_plan_id,
        "execution_status": run.execution_status, "deviations": run.deviations,
    }


class SampleBindingIn(BaseModel):
    design_version_id: str | None = None
    construct_id: str | None = None
    condition_ref: dict[str, Any] = {}
    replicate_group: str | None = None


class IngestBody(BaseModel):
    project_id: str
    experiment_run_id: str
    file_uri: str
    csv_base64: str
    assay_type: str
    ingestor_name: str = "growth_titer_csv"
    sample_manifest: dict[str, SampleBindingIn]
    uploaded_by: str


@router.post("/ingest")
def ingest(body: IngestBody, session: Session = Depends(get_db_session)) -> dict:
    ingestor = _INGESTORS.get(body.ingestor_name)
    if ingestor is None:
        raise HTTPException(400, f"unknown ingestor {body.ingestor_name!r}; available: {list(_INGESTORS)}")
    manifest = {
        sid: SampleBinding(sample_id=sid, **binding.model_dump())
        for sid, binding in body.sample_manifest.items()
    }
    try:
        raw_bytes = base64.b64decode(body.csv_base64)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, f"csv_base64 is not valid base64: {e}")

    try:
        result = ingest_csv_asset(
            session, project_id=body.project_id, experiment_run_id=body.experiment_run_id, file_uri=body.file_uri,
            raw_bytes=raw_bytes, assay_type=body.assay_type, ingestor=ingestor, sample_manifest=manifest,
            uploaded_by=body.uploaded_by,
        )
    except DataIdentityError as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))

    return {
        "duplicate": result.duplicate,
        "data_asset_id": result.data_asset.data_asset_id if result.data_asset else None,
        "committed_observation_ids": result.committed_observation_ids,
        "qc_passed": result.qc_report.passed if result.qc_report else None,
    }


@router.get("/runs/{experiment_run_id}/observations")
def list_observations(experiment_run_id: str, session: Session = Depends(get_db_session)) -> dict:
    from sqlalchemy import select

    from harness.experiments.models import DataAsset, Observation

    asset_ids = [
        a.data_asset_id
        for a in session.execute(select(DataAsset).where(DataAsset.experiment_run_id == experiment_run_id)).scalars()
    ]
    if not asset_ids:
        return {"observations": []}
    all_obs = session.execute(select(Observation)).scalars().all()
    matched = [o for o in all_obs if any(aid in o.data_asset_ids for aid in asset_ids)]
    return {
        "observations": [
            {
                "observation_id": o.observation_id, "metric": o.metric, "value": o.value, "unit": o.unit,
                "condition_ref": o.condition_ref, "qc_status": o.qc_status, "source_type": o.source_type,
            }
            for o in matched
        ]
    }


@router.get("/observations")
def list_project_observations(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    """List persisted measurements that can be linked into a diagnosis."""
    from sqlalchemy import select

    from harness.experiments.models import Observation

    rows = session.execute(
        select(Observation)
        .where(Observation.project_id == project_id)
        .order_by(Observation.created_at.desc())
    ).scalars().all()
    return {
        "observations": [
            {
                "observation_id": o.observation_id,
                "metric": o.metric,
                "value": o.value,
                "unit": o.unit,
                "condition_ref": o.condition_ref,
                "timepoint": o.timepoint,
                "qc_status": o.qc_status,
                "source_type": o.source_type,
            }
            for o in rows
        ]
    }
