"""Isolated, freshly-bootstrapped SQLite DB per test - same pattern as
`tests/diagnosis/conftest.py`."""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from harness import db
from harness.bootstrap import bootstrap_schema


@pytest.fixture(autouse=True)
def isolated_db(tmp_path):
    db_path = tmp_path / "test_project_ledger.db"
    db.reset_engine_for_tests(f"sqlite:///{db_path}")
    bootstrap_schema()
    yield
