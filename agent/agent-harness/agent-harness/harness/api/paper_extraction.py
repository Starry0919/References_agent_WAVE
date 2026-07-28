"""Paper Experimental Design Extraction module API routes.

Wraps the vendored 13-skill pipeline (harness/paper_extraction/) - requirement
parsing, literature retrieval, citation validation, PDF acquisition/parsing,
markdown cleaning, experiment extraction, evidence binding, quality
evaluation, K12 transfer analysis, engineering proposal, QC/human review and
frontend adaptation. Runs are async (thread-pool backed, PDF download/parsing
can take a while) - submit, then poll the combined status+result endpoint.

Independent of the project ledger DB (harness/db.py): the module keeps its
own file-based checkpoint/artifact store under
harness/paper_extraction/vendor/paper_experimental_design_extraction/storage/,
matching the simulation_demo precedent of a self-contained sub-system that
never touches the real ledger.
"""
from __future__ import annotations

import base64
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from harness.paper_extraction import service

router = APIRouter(prefix="/api/paper-extraction", tags=["paper-extraction"])


class RunRequestBody(BaseModel):
    project_id: str | None = None
    user_request: str
    organism: str = ""
    strain: str = ""
    source_type: Literal["auto_search", "upload", "doi", "textbook"] = "auto_search"
    result_level: Literal["extract", "compare", "adapt", "engineering_plan"] = "extract"
    document_kind: Literal["auto", "paper", "textbook"] = "auto"
    files: list[str] = Field(default_factory=list)
    doi: list[str] = Field(default_factory=list)
    requirements: dict[str, Any] = Field(default_factory=dict)
    automatic: bool = True
    human_review: bool = True
    max_papers: int = Field(default=6, ge=1, le=8)


class UploadBody(BaseModel):
    filename: str
    content_base64: str


@router.post("/uploads")
def upload_paper(body: UploadBody) -> dict:
    # base64-in-JSON, not multipart (harness/api/experiments.py precedent):
    # keeps this router dependency-free (no python-multipart requirement).
    try:
        data = base64.b64decode(body.content_base64)
    except Exception as exc:
        raise HTTPException(400, f"content_base64 is not valid base64: {exc}") from exc
    if not data:
        raise HTTPException(422, "uploaded file is empty")
    path = service.save_upload(body.filename, data)
    return {"path": path, "filename": body.filename}


@router.post("/tasks", status_code=202)
def submit_task(body: RunRequestBody) -> dict:
    try:
        return service.submit_run(body.model_dump())
    except Exception as exc:  # invalid request shape against the module's own input schema
        raise HTTPException(400, str(exc)) from exc


@router.get("/tasks")
def list_tasks(project_id: str | None = Query(default=None)) -> dict:
    """Run history (newest first) - lets the page show past/in-progress
    runs instead of resetting to a blank submission form whenever the
    `?task=` URL param is lost (navigating away and back, a fresh tab)."""
    return {"tasks": service.list_tasks(project_id=project_id)}


@router.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict[str, Any]:
    """Combined status+result poll target: `result` stays null while the
    task is still running so the frontend can poll one endpoint uniformly
    instead of juggling a 202-vs-200 status/result split.

    `skill_states` is included at the top level too (not just inside
    `result`, which is only ever populated once the whole run finishes) -
    it's read from the run's on-disk checkpoint, updated after every skill,
    so a client polling this endpoint can show live per-step progress
    instead of an undifferentiated spinner for the whole run.
    """
    try:
        status = service.get_status(task_id)
    except KeyError:
        raise HTTPException(404, "task not found")
    result = service.get_result(task_id)
    skill_states = result["skill_states"] if result else service.get_live_skill_states(task_id)
    # Only meaningful while still running - a finished result has nothing left
    # in progress, and the engine never puts `skill_progress` in `_report()`.
    skill_progress = {} if result else service.get_live_skill_progress(task_id)
    return {**status, "result": result, "skill_states": skill_states, "skill_progress": skill_progress}


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str) -> dict[str, Any]:
    """Remove a finished run from history (both the list and its own
    detail poll target 404 afterwards) - lets the frontend's run-history
    panel offer a delete action instead of accumulating every past run
    forever."""
    try:
        service.delete_task(task_id)
    except KeyError:
        raise HTTPException(404, "task not found")
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return {"deleted": True, "task_id": task_id}
