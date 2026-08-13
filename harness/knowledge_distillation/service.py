"""One entry point for text/upload biological-knowledge distillation runs.

Phase 1 only (see `biological_knowledge_distillation/README.md` "Phase
roadmap"): sources are pasted text or plain-text/Markdown uploads, not PDFs -
there is no PDF/OCR pipeline yet, so `.pdf`/`.docx` uploads are rejected
up front rather than silently producing an empty run.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from . import _VENDOR_DIR  # noqa: F401  (import triggers the sys.path bootstrap)

from biological_knowledge_distillation.api.task_manager import TaskManager  # noqa: E402
from harness.knowledge_distillation.opus_extractor import MODEL as EXTRACTION_MODEL, make_executor  # noqa: E402

UPLOAD_DIR = _VENDOR_DIR / "biological_knowledge_distillation" / "storage" / "uploads"
RUNTIME_DIR = _VENDOR_DIR / "biological_knowledge_distillation" / "storage" / "runtime"
ALLOWED_UPLOAD_SUFFIXES = {".md", ".txt"}

_manager: TaskManager | None = None

# Same rationale as harness/paper_extraction/service.py's _task_meta: the
# vendored TaskManager only stores {status, result, error} per task_id, with
# no submission time or request summary - kept here (frontend-only need,
# process-lifetime only) rather than in the vendored module.
_task_meta: dict[str, dict[str, Any]] = {}


def _get_manager() -> TaskManager:
    global _manager
    if _manager is None:
        _manager = TaskManager()
    return _manager


def save_upload(filename: str, data: bytes) -> str:
    """Persist an uploaded text/Markdown source to disk and return its path.

    Rejects anything that isn't `.md`/`.txt` - Step03 only parses Markdown-
    flavoured plain text (no PDF/OCR pipeline in Phase 1), so accepting a
    PDF here would silently produce a run with zero extracted knowledge
    instead of a clear error at upload time.
    """
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_UPLOAD_SUFFIXES:
        raise ValueError(
            f"unsupported upload type {suffix or '(none)'}: Phase 1 only parses plain text/Markdown "
            f"({', '.join(sorted(ALLOWED_UPLOAD_SUFFIXES))}); PDF/DOCX ingestion is not yet implemented."
        )
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name or "upload.txt"
    target = UPLOAD_DIR / f"{uuid.uuid4().hex}_{safe_name}"
    target.write_bytes(data)
    return str(target)


def _read_source_text(src: dict[str, Any]) -> str:
    if src.get("text"):
        return src["text"]
    file_path = src.get("file_path")
    if file_path and Path(file_path).is_file():
        return Path(file_path).read_text(encoding="utf-8", errors="replace")
    return ""


def build_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Translate the frontend's run-submission payload into the module's
    `input.schema.json` envelope (task_id/user_request/input_sources/...)."""
    task_id = payload.get("task_id") or uuid.uuid4().hex
    sources = []
    for src in payload.get("sources", []):
        biblio = {
            "title": src.get("title", ""),
            "authors_or_editors": src.get("authors", []),
            "publisher": src.get("publisher", ""),
            "publication_year": src.get("publication_year"),
            "isbn": src.get("isbn", []),
            "doi": src.get("doi", ""),
            "edition": src.get("edition", ""),
            "chapter": src.get("chapter", ""),
            "page_range": src.get("page_range", ""),
            "source_type": src.get("source_type", ""),
        }
        sources.append({"source_ref_type": "text", "raw_text": _read_source_text(src), "bibliographic": biblio})

    return {
        "task_id": task_id,
        "user_request": payload["user_request"],
        "input_sources": sources,
        "target_domain": payload.get("target_domain", []),
        "target_organism": payload.get("target_organism", []),
        "target_strain": payload.get("target_strain", []),
        "target_engineering_goal": payload.get("target_engineering_goal", []),
        "requested_output_level": payload.get("requested_output_level") or [
            "level3_engineering_distillation", "level5_knowledge_hub_adapter",
        ],
        "source_languages": payload.get("source_languages", []),
        "output_languages": payload.get("output_languages") or ["zh", "en"],
        "quality_requirement": payload.get("quality_requirement", ""),
        "requires_cross_source_fusion": payload.get("requires_cross_source_fusion", len(sources) > 1),
        "requires_paper_case_linking": bool(payload.get("paper_case_artifacts")),
        "requires_frontend_adapter": payload.get("requires_frontend_adapter", True),
        "paper_case_artifacts": payload.get("paper_case_artifacts", []),
        "mode": {
            "automatic": payload.get("automatic", True),
            "human_review": payload.get("human_review", True),
        },
    }


def submit_run(payload: dict[str, Any]) -> dict[str, Any]:
    request = build_request(payload)
    if not request["input_sources"]:
        raise ValueError("at least one source (pasted text or an uploaded .md/.txt file) is required")
    submitted = _get_manager().submit(request, {
        # Step05 is the only step routed to the LLM (see opus_extractor.py
        # docstring for why) - every other step keeps running the
        # deterministic, tested pipeline built into the vendored module.
        "executors": {"step05_basic_knowledge_extraction": make_executor(EXTRACTION_MODEL)},
    })
    _task_meta[submitted["task_id"]] = {
        "project_id": payload.get("project_id"),
        "submitted_at": time.time(),
        "user_request": payload["user_request"],
        "source_count": len(request["input_sources"]),
        "target_domain": payload.get("target_domain", []),
        "requested_output_level": request["requested_output_level"],
        "extraction_model": EXTRACTION_MODEL,
    }
    return submitted


def get_status(task_id: str) -> dict[str, Any]:
    return _get_manager().status(task_id)


def get_result(task_id: str) -> dict[str, Any] | None:
    return _get_manager().result(task_id)


def get_live_step_states(task_id: str) -> dict[str, str]:
    """Best-effort per-step progress while a task is still running - mirrors
    `harness.paper_extraction.service.get_live_skill_states`: the vendored
    `WorkflowEngine` checkpoints to disk after every step (atomic write via
    `ArtifactStore.save_checkpoint`), so this is always either the previous
    or the just-completed step's state, never a torn file. Returns `{}` if
    the task hasn't checkpointed yet or the id is unknown; never raises."""
    path = RUNTIME_DIR / task_id / "checkpoint.json"
    if not path.is_file():
        return {}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return state.get("step_states", {})


def list_tasks(project_id: str | None = None) -> list[dict[str, Any]]:
    """Every task submitted this process's lifetime, newest first."""
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
