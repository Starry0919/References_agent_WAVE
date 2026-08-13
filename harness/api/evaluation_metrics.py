"""260718 设计文档 §7 (验证方式) evaluation-metrics API routes. Every route
calls the same `harness.evaluation_metrics` service functions the test suite
exercises; no business logic lives here (same convention as
`harness/api/engineering_design.py`).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.engineering_design.models import EngineeringDesignProject
from harness.evaluation_metrics import aggregator, consistency_sampler
from harness.evaluation_metrics.consistency_sampler import NoHandoffForProjectError

router = APIRouter(prefix="/api/evaluation-metrics", tags=["evaluation-metrics"])


def _consistency_run_dict(run) -> dict:
    return {
        "run_id": run.run_id, "design_project_id": run.design_project_id, "n_samples": run.n_samples,
        "samples": run.samples, "convergence_report": run.convergence_report, "created_by": run.created_by,
        "created_at": run.created_at,
    }


@router.get("/by-project/{project_id}")
def list_design_projects_for_project(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    """Resolves the outer `projects.project_id` (what the frontend route
    carries) to its `EngineeringDesignProject` row(s) - every other
    engineering-design route is keyed by `design_project_id` directly, so the
    metrics dashboard needs this lookup to get started."""
    rows = session.execute(
        select(EngineeringDesignProject)
        .where(EngineeringDesignProject.project_id == project_id)
        .order_by(EngineeringDesignProject.created_at.desc())
    ).scalars().all()
    return {
        "design_projects": [
            {
                "design_project_id": r.design_project_id, "status": r.status,
                "reference_ddr_ids": r.reference_ddr_ids or [], "created_at": r.created_at,
            }
            for r in rows
        ]
    }


@router.get("/projects/{design_project_id}/summary")
def get_metrics_summary(design_project_id: str, session: Session = Depends(get_db_session)) -> dict:
    try:
        return aggregator.compute_all_metrics(session, design_project_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


class ReferenceDdrBody(BaseModel):
    ddr_ids: list[str]


@router.post("/projects/{design_project_id}/reference-ddr")
def set_reference_ddr(design_project_id: str, body: ReferenceDdrBody, session: Session = Depends(get_db_session)) -> dict:
    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None:
        raise HTTPException(404, f"no such design project: {design_project_id}")
    proj.reference_ddr_ids = body.ddr_ids
    session.flush()
    return {"design_project_id": design_project_id, "reference_ddr_ids": proj.reference_ddr_ids}


class ConsistencyRunBody(BaseModel):
    n_samples: int = consistency_sampler.DEFAULT_N_SAMPLES
    actor_id: str


@router.post("/projects/{design_project_id}/consistency-runs")
def start_consistency_run(design_project_id: str, body: ConsistencyRunBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        run = consistency_sampler.run_consistency_sample(
            session, design_project_id=design_project_id, n_samples=body.n_samples, actor_id=body.actor_id,
        )
    except NoHandoffForProjectError as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(404, str(e))
    return _consistency_run_dict(run)


@router.get("/projects/{design_project_id}/consistency-runs")
def list_consistency_runs_route(design_project_id: str, session: Session = Depends(get_db_session)) -> dict:
    runs = consistency_sampler.list_consistency_runs(session, design_project_id)
    return {"runs": [_consistency_run_dict(r) for r in runs]}


@router.get("/projects/{design_project_id}/consistency-runs/{run_id}")
def get_consistency_run(design_project_id: str, run_id: str, session: Session = Depends(get_db_session)) -> dict:
    from harness.evaluation_metrics.models import ConsistencySamplingRun

    run = session.get(ConsistencySamplingRun, run_id)
    if run is None or run.design_project_id != design_project_id:
        raise HTTPException(404, f"no such consistency run: {run_id}")
    return _consistency_run_dict(run)
