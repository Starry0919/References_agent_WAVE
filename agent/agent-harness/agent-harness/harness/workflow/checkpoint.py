"""WorkflowRun checkpointing: one JSON snapshot of the whole run per
transition, written atomically (design-review fix #4 - a bare overwrite
killed mid-write would leave an unreadable snapshot with no fallback,
failing the "checkpoint-restore consistency" acceptance test). A
`WorkflowRun` is small (no chat transcript inside it), so a whole-object
snapshot is simpler and just as sufficient as sessions.py's
append-only-JSONL-of-deltas pattern - that pattern earns its complexity
for a growing chat transcript, not here.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from harness.config import PROJECT_ROOT
from harness.workflow.state import WorkflowRun

CHECKPOINT_DIR = PROJECT_ROOT / "workflow_runs"


def _path_for(run_id: str) -> Path:
    return CHECKPOINT_DIR / f"{run_id}.json"


def save(run: WorkflowRun) -> Path:
    """Atomically write `run` as this run's latest checkpoint.

    Write to a temp file in the same directory, then `os.replace` onto the
    real path - `os.replace` is atomic on both POSIX and Windows, so a
    crash mid-write never corrupts the previously-committed checkpoint.
    """
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    target = _path_for(run.run_id)
    fd, tmp_name = tempfile.mkstemp(dir=CHECKPOINT_DIR, prefix=f".{run.run_id}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(run.model_dump_json(indent=2))
        os.replace(tmp_name, target)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
    return target


def load(run_id: str) -> WorkflowRun | None:
    path = _path_for(run_id)
    if not path.is_file():
        return None
    return WorkflowRun.model_validate_json(path.read_text(encoding="utf-8"))


def list_run_ids() -> list[str]:
    if not CHECKPOINT_DIR.is_dir():
        return []
    return sorted(p.stem for p in CHECKPOINT_DIR.glob("*.json"))


def delete(run_id: str) -> bool:
    path = _path_for(run_id)
    if path.is_file():
        path.unlink()
        return True
    return False
