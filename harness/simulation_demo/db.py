"""A second, independent SQLAlchemy engine/session-factory for the
Simulation/Demo Workspace - never the same object as `harness.db`'s
module-level engine. This is the actual isolation mechanism (requirement 1
of 查缺补漏04): a real user's browser hitting `/api/simulation/*` can never
reach the production `project_ledger.db` file, because the FastAPI sub-app
serving those routes has its `get_db_session` dependency overridden to
yield sessions from THIS engine instead (see `harness/simulation_demo/app.py`).
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from harness.config import PROJECT_ROOT

SIMULATION_DB_PATH = PROJECT_ROOT / "simulation_demo_ledger.db"

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_simulation_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{SIMULATION_DB_PATH}", future=True)

        @event.listens_for(_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return _engine


def get_simulation_session_factory() -> sessionmaker:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_simulation_engine(), expire_on_commit=False, future=True)
    return _SessionLocal


@contextmanager
def simulation_session_scope() -> Iterator[Session]:
    session = get_simulation_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_simulation_db_session() -> Iterator[Session]:
    """FastAPI dependency - the override target for every content router's
    `Depends(get_db_session)` inside the simulation sub-app (see
    `harness/simulation_demo/app.py`)."""
    session = get_simulation_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_simulation_engine_for_tests(db_url: str) -> None:
    """Test-only: repoints THIS module's engine/session factory (never
    `harness.db`'s) at an isolated database, mirroring
    `harness.db.reset_engine_for_tests` exactly - so tests of the
    simulation sub-app never read or write the real, persistent
    `simulation_demo_ledger.db` file either."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = create_engine(db_url, future=True)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)


def bootstrap_simulation_schema() -> list[str]:
    """Applies the SAME registered migrations `harness.bootstrap` defines
    (importing it is what registers them onto the shared `_MIGRATIONS`
    list - module-level state, not tied to any one engine) against this
    separate simulation engine. Idempotent, safe to call on every process
    start, exactly like `harness.bootstrap.bootstrap_schema()`."""
    import harness.bootstrap  # noqa: F401 - import for its registration side effect
    from harness.migrations import run_migrations

    return run_migrations(get_simulation_session_factory())
