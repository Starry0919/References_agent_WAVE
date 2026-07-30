"""Regression tests for the SQLite WAL / busy_timeout fix in
`harness/db.py`: every connection must run with WAL journaling (readers no
longer block behind a writer) and a 5s busy timeout (a lock contender waits
instead of failing immediately with a bare "database is locked" 500)."""
from __future__ import annotations

import time

import pytest
from sqlalchemy import text

from harness import db


@pytest.fixture()
def tmp_engine(tmp_path):
    """Point the module-level engine at an isolated tmp database, then
    restore the default dev ledger so neighbouring suites are unaffected."""
    db.reset_engine_for_tests(f"sqlite:///{tmp_path}/pragma_test.db")
    yield db.get_engine()
    db.reset_engine_for_tests(f"sqlite:///{db.DB_PATH}")


def test_every_connection_gets_wal_and_busy_timeout(tmp_engine) -> None:
    with tmp_engine.connect() as conn:
        journal_mode = conn.exec_driver_sql("PRAGMA journal_mode").scalar()
        busy_timeout = conn.exec_driver_sql("PRAGMA busy_timeout").scalar()
        foreign_keys = conn.exec_driver_sql("PRAGMA foreign_keys").scalar()
    assert journal_mode == "wal"
    assert busy_timeout == 5000
    assert foreign_keys == 1  # pre-existing pragma must survive the change


def test_reader_is_not_blocked_during_an_open_write_transaction(tmp_engine) -> None:
    """The whole point of WAL: while one connection holds an uncommitted
    write, another connection can still read (it sees the pre-write state).
    In rollback-journal mode this reader would hit "database is locked"
    (or stall for the full busy_timeout and then fail)."""
    with tmp_engine.begin() as setup:
        setup.exec_driver_sql("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
        setup.exec_driver_sql("INSERT INTO t (v) VALUES ('before')")

    writer = tmp_engine.connect()
    try:
        writer.exec_driver_sql("INSERT INTO t (v) VALUES ('uncommitted')")
        # `writer` now holds an open write transaction (no commit yet).
        start = time.perf_counter()
        with tmp_engine.connect() as reader:
            rows = reader.exec_driver_sql("SELECT v FROM t ORDER BY id").fetchall()
        elapsed = time.perf_counter() - start
        assert [r[0] for r in rows] == ["before"]  # pre-write snapshot
        assert elapsed < 2.0  # instant - not a busy_timeout stall
    finally:
        writer.rollback()
        writer.close()
