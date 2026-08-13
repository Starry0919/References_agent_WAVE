from __future__ import annotations
import pytest
from harness import db
from harness.bootstrap import bootstrap_schema

@pytest.fixture(autouse=True)
def isolated_db(tmp_path):
    db.reset_engine_for_tests(f"sqlite:///{tmp_path/'reference_optimization.db'}")
    bootstrap_schema()
    yield

