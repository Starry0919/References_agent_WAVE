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
from paper_experimental_design_extraction.config import DEFAULT_CONFIG  # noqa: E402
from paper_experimental_design_extraction.workflow import WorkflowEngine  # noqa: E402
from harness.paper_extraction.opus_extractor import MODEL as EXTRACTION_MODEL, make_executor
from harness.paper_extraction.frontend_adapter import execute as route_aware_frontend_execute
from harness.paper_extraction.pipeline_cache import make_cached_executor

UPLOAD_DIR = _VENDOR_DIR / "paper_experimental_design_extraction" / "storage" / "uploads"
RUNTIME_DIR = _VENDOR_DIR / "paper_experimental_design_extraction" / "storage" / "runtime"
# One JSON row per submitted task (metadata + the original request/options
# needed to resume it) - written on submit, dropped on delete. Everything
# else about a run (per-skill progress, the final report) already lives in
# its own `RUNTIME_DIR/<task_id>/checkpoint.json`, written by WorkflowEngine
# itself; this file is only the thin index + resume-recipe that used to
# live solely in the in-memory `_task_meta`/`TaskManager.tasks`, which a
# server restart (or, during development, uvicorn --reload) wiped entirely -
# "刷新后历史记录消失" even though every run's own checkpoint was still
# sitting on disk the whole time.
_REGISTRY_PATH = _VENDOR_DIR / "paper_experimental_design_extraction" / "storage" / "task_registry.json"

_manager: TaskManager | None = None

# The vendored TaskManager only ever stores {status, result, error} per
# task_id - no submission time or request summary, so a returning user has
# no way to tell which past run is which. Kept here rather than in the
# vendored module (frontend-only need, not part of its own input/output
# schema) - repopulated from `_REGISTRY_PATH` by `_restore_registry` on
# first use each process, not just held in memory.
_task_meta: dict[str, dict[str, Any]] = {}


def _load_registry() -> dict[str, dict[str, Any]]:
    if not _REGISTRY_PATH.is_file():
        return {}
    try:
        return json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save_registry(registry: dict[str, dict[str, Any]]) -> None:
    _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = _REGISTRY_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(_REGISTRY_PATH)


def _restore_registry(manager: TaskManager) -> None:
    """Runs once, the first time this process needs a `TaskManager` -
    repopulates `_task_meta` and `manager`'s per-task status/result from
    `_REGISTRY_PATH` + each task's own on-disk checkpoint, so history
    submitted in an earlier process (a prior `--reload` restart, a crash, a
    normal redeploy) is available immediately instead of only for tasks
    submitted since this process started.

    A task whose checkpoint shows it was still `RUNNING`/`CREATED` when the
    process died is genuinely resumed (`WorkflowEngine` checkpoints after
    every skill and `run(resume=True)` already skips whatever finished
    before the crash - see engine.py) rather than left to look silently
    stuck forever. A task that had already reached COMPLETED/FAILED/
    WAITING_REVIEW is not re-run at all: `WorkflowEngine._report()` is a
    pure function of the saved checkpoint state (it never reads `self`),
    so the same report it produced before is rebuilt straight from disk.
    """
    registry = _load_registry()
    engine = WorkflowEngine(DEFAULT_CONFIG)
    for task_id, entry in registry.items():
        meta = entry.get("meta", {})
        _task_meta[task_id] = meta
        checkpoint_path = RUNTIME_DIR / task_id / "checkpoint.json"
        if not checkpoint_path.is_file():
            continue
        try:
            state = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        status = state.get("status")
        if status in ("RUNNING", "CREATED"):
            request = entry.get("request")
            if not request:
                continue
            options = dict(entry.get("options") or {})
            options["executors"] = {
                "skill05_pdf_parser": _SKILL05_EXECUTOR,
                "skill06_markdown_cleaner": _SKILL06_EXECUTOR,
                "skill07_experiment_extraction": make_executor(EXTRACTION_MODEL),
                "skill13_frontend_adapter": route_aware_frontend_execute,
            }
            options["resume"] = True
            manager.submit(request, options)
            continue
        try:
            report = engine._report(None, state)
        except Exception:
            continue
        manager.seed(task_id, str(status).lower(), result=report)


def _get_manager() -> TaskManager:
    global _manager
    if _manager is None:
        _manager = TaskManager()
        _restore_registry(_manager)
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


def _skill05_cache_key(request: dict[str, Any]) -> str:
    artifact = request.get("paper_artifact") or {}
    checksum = artifact.get("integrity", {}).get("checksum_value")
    if not checksum:
        raise ValueError("paper_artifact has no checksum to key the parse cache on")
    policy = request.get("parse_policy") or {}
    return f"{checksum}\0{json.dumps(policy, sort_keys=True)}"


def _skill06_cache_key(request: dict[str, Any]) -> str:
    document = request.get("document_artifact")
    if not document:
        raise ValueError("no document_artifact to key the clean cache on")
    return json.dumps(document, sort_keys=True, ensure_ascii=False)


# Same paper, re-parsed/re-cleaned only once no matter how many projects or
# runs later reference it (skill07's LLM extraction already gets this via
# opus_extractor.py's own cache; these two are the deterministic, but still
# real-time-costing, steps upstream of it - see pipeline_cache.py).
_SKILL05_EXECUTOR = make_cached_executor("skill05_pdf_parser", _skill05_cache_key)
_SKILL06_EXECUTOR = make_cached_executor("skill06_markdown_cleaner", _skill06_cache_key)


def submit_run(payload: dict[str, Any]) -> dict[str, Any]:
    request = build_request(payload)
    source_type = payload.get("source_type", "auto_search")
    manual_candidates = _project_uploaded_papers(payload.get("project_id")) if source_type == "auto_search" else []
    # JSON-safe part of the run's options - persisted below so a later
    # process can resume this exact run; `executors` (a live callable) is
    # rebuilt fresh from `EXTRACTION_MODEL` on resume instead, both here and
    # in `_restore_registry`.
    persistable_options = {
        "pdf_download_policy": {"max_candidates": min(int(payload.get("max_papers", 6)), 8)},
        "retrieval_limit": min(int(payload.get("max_papers", 6)), 8),
        "manual_candidates": manual_candidates,
    }
    # All three source routes converge on the same per-paper skill04-07
    # executors.  Their content-addressed caches avoid re-downloading/
    # re-parsing/re-cleaning/re-extracting a paper already processed by an
    # earlier run - in any project - merely because it was supplied again
    # by DOI instead of upload/search, or the other way around.
    submitted = _get_manager().submit(request, {
        **persistable_options,
        "executors": {
            "skill05_pdf_parser": _SKILL05_EXECUTOR,
            "skill06_markdown_cleaner": _SKILL06_EXECUTOR,
            "skill07_experiment_extraction": make_executor(EXTRACTION_MODEL),
            "skill13_frontend_adapter": route_aware_frontend_execute,
        },
    })
    task_id = submitted["task_id"]
    _task_meta[task_id] = {
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
    registry = _load_registry()
    registry[task_id] = {"meta": _task_meta[task_id], "request": request, "options": persistable_options}
    _save_registry(registry)
    return submitted


def resubmit_task(task_id: str) -> dict[str, Any]:
    """Re-run a past task's exact source spec (same upload/DOI/search
    settings) as a brand-new run - the "重新抽取" action. Reconstructed
    entirely from what `submit_run` already persisted in the registry
    (`meta` + the built `request`), so it works for any past task without
    needing extra state saved up front.

    Raises
    ------
    KeyError
        `task_id` has no registry entry (unknown task).
    FileNotFoundError
        The run was an `upload`/`textbook` submission whose source PDF no
        longer exists on this machine (e.g. it was uploaded on a different
        computer - uploaded files are local-disk only, unlike the synced
        `knowledge/ddr_database/` results).
    """
    registry = _load_registry()
    entry = registry.get(task_id)
    if entry is None:
        raise KeyError(task_id)
    meta = entry.get("meta", {})
    request = entry.get("request", {})
    literature = request.get("literature_source", {})
    files = literature.get("files", [])
    source_type = meta.get("source_type", "auto_search")
    if source_type in ("upload", "textbook"):
        missing = [f for f in files if not Path(f).is_file()]
        if missing:
            raise FileNotFoundError(
                f"original source file(s) not available on this machine, only where they were uploaded: {', '.join(missing)}"
            )
    payload = {
        "project_id": meta.get("project_id"),
        "user_request": request.get("user_request", ""),
        "organism": request.get("target_system", {}).get("organism", ""),
        "strain": request.get("target_system", {}).get("strain", ""),
        "source_type": source_type,
        "result_level": meta.get("result_level", "extract"),
        "document_kind": meta.get("document_kind", "auto"),
        "files": files,
        "doi": literature.get("doi", []),
        "automatic": request.get("mode", {}).get("automatic", True),
        "human_review": request.get("mode", {}).get("human_review", True),
        "max_papers": (entry.get("options") or {}).get("retrieval_limit", 6),
    }
    return submit_run(payload)


def get_status(task_id: str) -> dict[str, Any]:
    manager = _get_manager()
    status = manager.status(task_id)
    # The workflow writes its terminal checkpoint before TaskManager's
    # Future callback updates the in-memory row.  Under a slow/stalled
    # callback (observed after large ~2.5 MB reports), polling could therefore
    # show "running" forever even though every skill and the checkpoint were
    # already complete.  Reconcile the durable terminal state on every poll;
    # the eventual callback is idempotent and may safely write the same result.
    if status.get("status") in {"created", "running"}:
        checkpoint_path = RUNTIME_DIR / task_id / "checkpoint.json"
        try:
            state = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return status
        checkpoint_status = str(state.get("status") or "").upper()
        if checkpoint_status in {"COMPLETED", "FAILED", "WAITING_REVIEW"}:
            try:
                report = WorkflowEngine(DEFAULT_CONFIG)._report(None, state)
            except Exception:
                return status
            manager.seed(task_id, checkpoint_status.lower(), result=report)
            return manager.status(task_id)
    return status


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


def get_live_skill_warnings(task_id: str) -> list[dict[str, Any]]:
    """Best-effort per-skill warning detail while a task is still `running`
    (or once it has finished, if the caller has no cached `result`) - same
    checkpoint-read contract as `get_live_skill_states`: `[]` if unavailable,
    never raises. Lets the frontend show *why* a step is WARNING (e.g. which
    figure/table mismatch or damaged section) instead of just the bare
    status, which the checkpoint's `skill_states` alone can't convey."""
    path = RUNTIME_DIR / task_id / "checkpoint.json"
    if not path.is_file():
        return []
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return state.get("warnings", [])


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
    registry = _load_registry()
    if registry.pop(task_id, None) is not None:
        _save_registry(registry)
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
