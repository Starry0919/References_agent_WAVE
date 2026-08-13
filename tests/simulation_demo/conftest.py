"""Every test here gets TWO isolated, freshly-bootstrapped SQLite
databases: one for `harness.db` (the "real" ledger the main app's routers
read/write) and a SEPARATE one for `harness.simulation_demo.db` (what the
mounted simulation sub-app's overridden dependency reads/writes) - proving
the two truly never share storage, not just asserting it by convention.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from harness import db
from harness.bootstrap import bootstrap_schema
from harness.simulation_demo import db as sim_db


@pytest.fixture(autouse=True)
def isolated_dbs(tmp_path):
    main_path = tmp_path / "test_project_ledger.db"
    sim_path = tmp_path / "test_simulation_demo_ledger.db"
    db.reset_engine_for_tests(f"sqlite:///{main_path}")
    bootstrap_schema()
    sim_db.reset_simulation_engine_for_tests(f"sqlite:///{sim_path}")
    sim_db.bootstrap_simulation_schema()
    yield
