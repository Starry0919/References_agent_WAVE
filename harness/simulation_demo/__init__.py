"""Simulation/Demo Workspace (查缺补漏04): a sandboxed, browser-visible DBTL
walkthrough backed by a COMPLETELY SEPARATE SQLite database file from the
real project ledger - the same physical-isolation guarantee this repo's own
pytest suite already relies on (`harness.db.reset_engine_for_tests`), just
kept alive as a second persistent engine instead of being torn down at the
end of a test process, since real users may browse it at any time alongside
real production traffic on the main engine.

Nothing here ever touches `harness.db`'s module-level engine/session
factory - see `harness/simulation_demo/db.py`.
"""
