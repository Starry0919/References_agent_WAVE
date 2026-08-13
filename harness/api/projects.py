"""Project + Iterative Design Loop API routes (doc 16). `web/index.html` is
unchanged this round (API-first, per plan) - these routes are the full
capability surface a future dashboard would call.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.designs.lineage import build_lineage_graph
from harness.memory.context_builder import build_context_bundle
from harness.memory.event_store import project_events
from harness.memory.views import build_project_status_view, build_project_status_view_from_ledger
from harness.projects import service as proj_svc
from harness.projects.models import Project
from harness.workflow.iterative_loop import GateRejectedError, IllegalCycleTransitionError, IterativeLoopController

router = APIRouter(prefix="/api/projects", tags=["projects"])
_loop = IterativeLoopController()
DEFAULT_HOST = {"species": "Escherichia coli", "strain": "K-12"}
logger = logging.getLogger(__name__)


def _host_or_default(value: dict[str, Any] | None) -> dict[str, Any]:
    supplied = value or {}
    return {**DEFAULT_HOST, **supplied, "defaulted": not bool(supplied.get("species") and supplied.get("strain"))}


class CreateProjectBody(BaseModel):
    name: str
    host_definition: dict[str, Any] = {}
    target_product: str
    objectives: list[str] = []
    constraints: list[str] = []
    actor_id: str


def _auto_submit_idea_retrieval(*, project_id: str, host_definition: dict[str, Any], target_product: str, objectives: list[str]) -> None:
    """Kicks off a literature retrieval run (same `auto_search` request the
    Idea Workspace's "获取思路" button submits) the moment a project is
    created, scoped to its target product/host - so the dashboard's
    "候选路径" (candidate paths) panel and the Idea Workspace already have a
    full, target-matched candidate set to show instead of staying empty
    until a human manually clicks retrieve. Fire-and-forget: `submit_run`
    just enqueues onto the module's own thread pool and returns
    immediately, so this never blocks project creation; a search/LLM
    hiccup here is logged and swallowed rather than failing the request
    that has nothing to do with retrieval succeeding.

    Skipped entirely under pytest: 30+ test files across the suite create
    projects through this same endpoint without ever mocking the paper
    extraction pipeline, and `TaskManager`'s `ThreadPoolExecutor` threads
    are non-daemon - letting a real literature search/LLM extraction fire
    on every one of those would make unrelated suites slow/flaky and can
    hang interpreter exit waiting for those threads to finish real network
    calls. Real usage (frontend, manual API calls) is unaffected; the
    pipeline's own dedicated tests still exercise it directly."""
    if "PYTEST_CURRENT_TEST" in os.environ:
        return
    from harness.paper_extraction import service as paper_extraction_service

    objective = " · ".join(o for o in objectives if o and o.strip()) or target_product
    user_request = " ".join(
        part for part in (host_definition.get("species"), host_definition.get("strain"), objective) if part and str(part).strip()
    ).strip()
    if not user_request:
        return
    try:
        paper_extraction_service.submit_run({
            "project_id": project_id,
            "user_request": user_request,
            "organism": host_definition.get("species", ""),
            "strain": host_definition.get("strain", ""),
            "source_type": "auto_search",
            "result_level": "extract",
            "document_kind": "auto",
        })
    except Exception:
        logger.exception("auto idea-retrieval submission failed for project %s", project_id)


@router.post("")
def create_project(body: CreateProjectBody, session: Session = Depends(get_db_session)) -> dict:
    host_definition = {**DEFAULT_HOST, **(body.host_definition or {})}
    p = proj_svc.create_project(
        session, name=body.name, host_definition=host_definition, target_product=body.target_product,
        objectives=body.objectives, constraints=body.constraints, actor_id=body.actor_id,
    )
    _auto_submit_idea_retrieval(
        project_id=p.project_id, host_definition=host_definition, target_product=body.target_product, objectives=body.objectives,
    )
    return {"project_id": p.project_id, "name": p.name, "status": p.status, "lifecycle_stage": p.lifecycle_stage, "version": p.version}


@router.get("")
def list_projects(session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(select(Project).order_by(Project.created_at.desc())).scalars().all()
    return {"projects": [{"project_id": r.project_id, "name": r.name, "status": r.status, "lifecycle_stage": r.lifecycle_stage} for r in rows]}


@router.get("/{project_id}")
def get_project(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    p = proj_svc.get_project(session, project_id)
    if p is None:
        raise HTTPException(404, "project not found")
    return {
        "project_id": p.project_id, "name": p.name, "target_product": p.target_product, "host_definition": _host_or_default(p.host_definition),
        "objectives": p.objectives, "constraints": p.constraints, "status": p.status, "lifecycle_stage": p.lifecycle_stage,
        "current_design_version_id": p.current_design_version_id, "version": p.version, "owners": p.owners,
    }


class UpdateProjectBody(BaseModel):
    name: str | None = None
    host_definition: dict[str, Any] | None = None
    target_product: str | None = None
    objectives: list[str] | None = None
    constraints: list[str] | None = None
    actor_id: str = "frontend-user"
    expected_version: int | None = None


@router.patch("/{project_id}")
def update_project(project_id: str, body: UpdateProjectBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        p = proj_svc.update_project_context(session, project_id=project_id, **body.model_dump())
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {
        "project_id": p.project_id, "name": p.name, "target_product": p.target_product,
        "host_definition": _host_or_default(p.host_definition), "objectives": p.objectives,
        "constraints": p.constraints, "status": p.status, "lifecycle_stage": p.lifecycle_stage,
        "current_design_version_id": p.current_design_version_id, "version": p.version, "owners": p.owners,
    }


@router.delete("/{project_id}")
def delete_project(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    try:
        proj_svc.delete_project(session, project_id=project_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"deleted": True, "project_id": project_id}


@router.get("/{project_id}/status")
def get_project_status(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    try:
        return build_project_status_view(session, project_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/{project_id}/status/from-ledger")
def get_project_status_from_ledger(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    """Reconstructs the same core facts purely from the event ledger -
    the "can this be rebuilt with no chat history" proof, exposed as a
    first-class endpoint rather than a test-only function."""
    return build_project_status_view_from_ledger(session, project_id)


@router.get("/{project_id}/timeline")
def get_project_timeline(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    events = project_events(session, project_id)
    return {
        "events": [
            {
                "seq": e.seq, "event_id": e.event_id, "event_type": e.event_type, "entity_type": e.entity_type,
                "entity_id": e.entity_id, "actor_type": e.actor_type, "actor_id": e.actor_id, "timestamp": e.timestamp,
            }
            for e in events
        ]
    }


@router.get("/{project_id}/lineage")
def get_lineage(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    return build_lineage_graph(session, project_id)


@router.get("/{project_id}/context-bundle")
def get_context_bundle(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    try:
        bundle = build_context_bundle(session, project_id=project_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return bundle.to_dict()


@router.get("/{project_id}/cycle")
def get_cycle(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    cycle = proj_svc.get_active_cycle(session, project_id)
    if cycle is None:
        raise HTTPException(404, "no active cycle for this project")
    return {
        "cycle_state_id": cycle.cycle_state_id, "current_state": cycle.current_state, "status": cycle.status,
        "pending_gate": cycle.pending_gate, "active_design_version_id": cycle.active_design_version_id,
        "active_experiment_plan_id": cycle.active_experiment_plan_id, "active_experiment_run_id": cycle.active_experiment_run_id,
        "termination_reason": cycle.termination_reason,
    }


# Transitions requiring only plain kwargs (actor_id + simple id/string
# arguments) are dispatched generically here. Transitions that need a
# GateResult (run_data_qc, enter_learning_update_gate,
# create_new_design_version) are computed server-side by the learning
# engine and are not exposed as a raw HTTP passthrough this round -
# constructing a trustworthy GateResult over the wire is out of scope.
_CYCLE_ACTIONS = (
    "capture_baseline", "propose_design", "enter_human_design_gate", "approve_design_and_handoff",
    "enter_waiting_for_results", "begin_data_ingestion", "extract_observations", "interpret_results",
    "update_hypothesis", "classify_outcome", "decide_redesign_or_stop", "pause_project", "complete_project",
    "resolve_pending_gate",
)


class CycleActionBody(BaseModel):
    actor_id: str
    kwargs: dict[str, Any] = {}


@router.post("/{project_id}/cycle/{action}")
def cycle_action(project_id: str, action: str, body: CycleActionBody, session: Session = Depends(get_db_session)) -> dict:
    if action not in _CYCLE_ACTIONS:
        raise HTTPException(400, f"unknown or unsupported cycle action {action!r}; must be one of {_CYCLE_ACTIONS}")
    cycle = proj_svc.get_active_cycle(session, project_id)
    if cycle is None:
        raise HTTPException(404, "no active cycle for this project")
    # Single-source-of-truth guard (查缺补漏03 Phase 1, mirrors create_run's
    # own guard in harness/orchestrator/service.py): once a project has
    # adopted the Unified Scientific Workflow Orchestrator, its
    # UnifiedWorkflowRun is the sole authority for that project's DBTL
    # state - the legacy Cycle engine must not also be driven forward.
    from harness.orchestrator.service import get_latest_run_for_project

    run = get_latest_run_for_project(session, project_id)
    if run is not None:
        raise HTTPException(
            409,
            f"project {project_id} is driven by orchestrator run {run.workflow_run_id!r} (phase={run.current_phase!r}) - "
            "use the /api/orchestrator endpoints for this project, not the legacy /cycle actions",
        )
    fn = getattr(_loop, action)
    try:
        fn(session, cycle, actor_id=body.actor_id, **body.kwargs)
    except IllegalCycleTransitionError as e:
        raise HTTPException(409, str(e))
    except GateRejectedError as e:
        raise HTTPException(422, str(e))
    return {
        "cycle_state_id": cycle.cycle_state_id, "current_state": cycle.current_state,
        "status": cycle.status, "pending_gate": cycle.pending_gate,
    }
