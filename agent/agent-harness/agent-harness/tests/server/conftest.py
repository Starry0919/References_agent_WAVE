"""Shared fixtures for the server/session-persistence test suite.

照抄 tests/workflow 的隔离模式:每个测试的 runs/ 目录指向 tmp_path,
测试不会读写真实项目的 runs/,也不会在项目目录留下 artifacts。
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from harness.sessions import SessionStore


@pytest.fixture
def runs_dir(tmp_path: Path) -> Path:
    """每个测试独立的 runs 目录(替代真实的 PROJECT_ROOT/runs)。"""
    path = tmp_path / "runs"
    path.mkdir()
    return path


@pytest.fixture
def store(runs_dir: Path):
    """指向隔离 runs 目录的 SessionStore;测试结束自动 close_all。"""
    store = SessionStore(runs_dir=runs_dir)
    yield store
    store.close_all()
