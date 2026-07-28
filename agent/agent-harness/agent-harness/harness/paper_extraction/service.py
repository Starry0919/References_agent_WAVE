"""One entry point for retrieval/upload/DOI paper-design extraction.

All source routes converge before the per-paper extraction stage.  Skill07
is Opus-routed and content-addressed, so downstream K-12 comparison and DBTL
planning consume one durable extraction representation instead of three
source-specific implementations.
"""
from __future__ import annotations

import json
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from . import _VENDOR_DIR  # noqa: F401  (import triggers the sys.path bootstrap)

from paper_experimental_design_extraction.api.task_manager import TaskManager  # noqa: E402
from harness.paper_extraction.opus_extractor import MODEL as EXTRACTION_MODEL, make_executor

UPLOAD_DIR = _VENDOR_DIR / "paper_experimental_design_extraction" / "storage" / "uploads"
RUNTIME_DIR = _VENDOR_DIR / "paper_experimental_design_extraction" / "storage" / "runtime"

_manager: TaskManager | None = None

# The vendored TaskManager only ever stores {status, result, error} per
# task_id - no submission time or request summary, so a returning user has
# no way to tell which past run is which. Kept here rather than in the
# vendored module (frontend-only need, not part of its own input/output
# schema) - process-lifetime only, same durability as the TaskManager
# itself (an in-memory dict; a server restart loses in-flight runs either
# way).
_task_meta: dict[str, dict[str, Any]] = {}


def _get_manager() -> TaskManager:
    global _manager
    if _manager is None:
        _manager = TaskManager()
    return _manager


def save_upload(filename: str, data: bytes) -> str:
    """Persist an uploaded PDF to local disk and return its absolute path.

    Skill04 (PDF acquisition) reads `manual_uploads[].path` from the local
    filesystem and verifies a checksum against it - it does not accept raw
    bytes over the wire, so uploads must land on disk before a run starts.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name or "upload.pdf"
    target = UPLOAD_DIR / f"{uuid.uuid4().hex}_{safe_name}"
    target.write_bytes(data)
    return str(target)


def build_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Translate the frontend's run-submission payload into the module's
    `input.schema.json` envelope (task_id/user_request/target_system/
    literature_source/requirements/mode)."""
    task_id = payload.get("task_id") or uuid.uuid4().hex
    source_type = payload.get("source_type", "auto_search")
    requirements = {
        "year": {"from": 2020, "until": 2026},
        "result_level": payload.get("result_level", "extract"),
        "document_kind": payload.get("document_kind", "auto"),
        "article_type_gate_required": True,
        "full_text_strain_identification_required": True,
        "figure_review_required": True,
        **payload.get("requirements", {}),
    }
    normalized_source_type = "upload" if source_type == "textbook" else source_type
    return {
        "task_id": task_id,
        "user_request": payload["user_request"],
        "target_system": {
            "organism": payload.get("organism", ""),
            "strain": payload.get("strain", ""),
        },
        "literature_source": {
            "type": normalized_source_type,
            "files": payload.get("files", []),
            "doi": payload.get("doi", []),
        },
        "requirements": requirements,
        "mode": {
            "automatic": payload.get("automatic", True),
            "human_review": payload.get("human_review", True),
        },
    }


def _project_uploaded_papers(project_id: str | None) -> list[dict[str, Any]]:
    """Paper identities from this project's own past `upload`/`textbook`
    runs (skill04's `paper_identity` per acquired PDF, read straight off
    each run's on-disk checkpoint - the same file `get_live_skill_states`
    already reads).  Fed into a later `auto_search` run as `manual_candidates`
    so "获取思路" checks what the user already gave this project before it
    goes out to Crossref/PubMed/Europe PMC for the rest."""
    if not project_id:
        return []
    seen: dict[str, dict[str, Any]] = {}
    for task_id, meta in _task_meta.items():
        if meta.get("project_id") != project_id or meta.get("source_type") not in {"upload", "textbook"}:
            continue
        checkpoint = RUNTIME_DIR / task_id / "checkpoint.json"
        if not checkpoint.is_file():
            continue
        try:
            state = json.loads(checkpoint.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for artifact in state.get("context", {}).get("paper_artifacts", []):
            identity = artifact.get("paper_identity") or {}
            paper_id = identity.get("paper_id")
            if paper_id and paper_id not in seen and identity.get("title"):
                seen[paper_id] = {
                    "source": "ProjectUpload",
                    "title": identity.get("title"),
                    "authors": identity.get("authors", []),
                    "journal": identity.get("journal"),
                    "year": identity.get("year"),
                    "doi": identity.get("doi"),
                }
    return list(seen.values())


def submit_run(payload: dict[str, Any]) -> dict[str, Any]:
    request = build_request(payload)
    source_type = payload.get("source_type", "auto_search")
    manual_candidates = _project_uploaded_papers(payload.get("project_id")) if source_type == "auto_search" else []
    # All three source routes converge on the same per-paper skill07
    # executor.  Its content-addressed cache avoids extracting a paper again
    # merely because it was later supplied by DOI instead of upload/search.
    submitted = _get_manager().submit(request, {
        "executors": {"skill07_experiment_extraction": make_executor(EXTRACTION_MODEL)},
        "pdf_download_policy": {"max_candidates": min(int(payload.get("max_papers", 6)), 8)},
        "retrieval_limit": min(int(payload.get("max_papers", 6)), 8),
        "manual_candidates": manual_candidates,
    })
    _task_meta[submitted["task_id"]] = {
        "project_id": payload.get("project_id"),
        "submitted_at": time.time(),
        "user_request": payload["user_request"],
        "organism": payload.get("organism", ""),
        "strain": payload.get("strain", ""),
        "result_level": payload.get("result_level", "extract"),
        "document_kind": payload.get("document_kind", "auto"),
        "source_type": source_type,
        "extraction_model": EXTRACTION_MODEL,
    }
    return submitted


def get_status(task_id: str) -> dict[str, Any]:
    return _get_manager().status(task_id)


def get_result(task_id: str) -> dict[str, Any] | None:
    return _get_manager().result(task_id)


def get_live_skill_states(task_id: str) -> dict[str, str]:
    """Best-effort per-skill progress while a task is still `running`.

    `TaskManager.result()` stays None until the whole pipeline finishes -
    a user watching a multi-minute run had no way to tell it apart from a
    hang ("需要展示进行到哪一步了"). `WorkflowEngine.run()` (workflow/
    engine.py) now checkpoints to disk after every skill, not just at
    start/end, and `ArtifactStore.save_checkpoint` writes atomically
    (tempfile + os.replace), so reading it here is always either the
    previous or the just-completed skill's state - never a torn file.
    Returns `{}` if the task hasn't checkpointed yet or the id is unknown;
    never raises, since this is read purely for a progress indicator.
    """
    path = RUNTIME_DIR / task_id / "checkpoint.json"
    if not path.is_file():
        return {}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return state.get("skill_states", {})


def get_live_skill_progress(task_id: str) -> dict[str, dict[str, int]]:
    """Best-effort per-skill item progress (e.g. `{"completed": 3, "total": 6}`
    for skill07, which calls the model once per paper, sequentially, and can
    otherwise sit at `RUNNING` for minutes with no visible change). Same
    checkpoint-read contract as `get_live_skill_states`: `{}` if unavailable,
    never raises."""
    path = RUNTIME_DIR / task_id / "checkpoint.json"
    if not path.is_file():
        return {}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return state.get("skill_progress", {})


def delete_task(task_id: str) -> None:
    """Remove a finished (completed/failed) run from history - both the
    frontend-facing metadata (`_task_meta`) and the TaskManager's own
    status/result entry, plus its on-disk checkpoint directory, so a
    deleted run doesn't reappear (e.g. via `_project_uploaded_papers`
    re-reading a stale checkpoint).

    Refuses to delete a task that's still `created`/`running`: the
    background future is still writing to `TaskManager.tasks[task_id]` and
    to the checkpoint file, so popping either out from under it would race
    the in-flight run instead of just discarding a finished one.
    """
    try:
        status = _get_manager().status(task_id)
    except KeyError:
        raise KeyError(task_id) from None
    if status["status"] in ("created", "running"):
        raise ValueError("cannot delete a task that is still running")
    _get_manager().delete(task_id)
    _task_meta.pop(task_id, None)
    shutil.rmtree(RUNTIME_DIR / task_id, ignore_errors=True)


def list_tasks(project_id: str | None = None) -> list[dict[str, Any]]:
    """Every task submitted this process's lifetime, newest first - lets
    the frontend show run history instead of losing track of a task the
    moment its `?task=` URL param is gone (navigating away and back, a
    fresh tab, etc)."""
    rows = []
    for task_id, meta in _task_meta.items():
        if project_id is not None and meta.get("project_id") != project_id:
            continue
        try:
            status = _get_manager().status(task_id)
        except KeyError:
            continue
        rows.append({"task_id": task_id, **meta, **status})
    rows.sort(key=lambda r: r["submitted_at"], reverse=True)
    return rows
