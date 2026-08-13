"""Shared pytest fixtures for the workflow-engine test suite.

Every test gets a fresh, isolated `workflow_runs/` checkpoint directory
(monkeypatched onto `harness.workflow.checkpoint`) so tests never read or
write each other's - or a real dev run's - checkpoint files, and never
leave test artifacts behind in the real project directory.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from harness.workflow import checkpoint


@pytest.fixture(autouse=True)
def isolated_checkpoint_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "CHECKPOINT_DIR", tmp_path / "workflow_runs")
    yield tmp_path
