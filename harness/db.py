"""SQLAlchemy engine/session setup for the Problem-02 persistent project
ledger. Dev mode: a SQLite file at the project root (gitignored); schema is
written to be Postgres-portable (plain `JSON`/`String`/`Float`/`Integer`
columns, no SQLite-only types), so moving to Postgres later is a connection
string change, not a rewrite - see 问题02_实施报告.md's "known limitations"
for why a hand-rolled migration runner (harness/migrations.py) is used
instead of Alembic this round.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from harness.config import PROJECT_ROOT

DB_PATH = PROJECT_ROOT / "project_ledger.db"


class Base(DeclarativeBase):
    pass


class ImmutableFieldError(RuntimeError):
    """Raised when code attempts to change a field the domain model
    declares immutable (doc: "设计版本必须不可变...禁止覆盖旧 genotype";
    "假设也要版本化...只能生成新版本"). This is an ORM-enforced guarantee,
    not a "we just don't call update" convention - it fires regardless of
    which code path attempted the change."""


def guard_immutable_fields(model_cls: type, mutable_fields: set[str]) -> None:
    """Register a `before_update` listener on `model_cls` that raises
    `ImmutableFieldError` if any column NOT in `mutable_fields` has a
    pending change. Call once per model, right after its class body."""
    column_names = [c.name for c in model_cls.__table__.columns]
    immutable = [c for c in column_names if c not in mutable_fields]

    def _reject(mapper, connection, target) -> None:  # noqa: ANN001, ARG001
        from sqlalchemy.orm import attributes

        for field in immutable:
            if attributes.get_history(target, field).has_changes():
                raise ImmutableFieldError(
                    f"{model_cls.__name__}.{field} is immutable and cannot be modified after creation"
                )

    event.listens_for(model_cls, "before_update")(_reject)


class ConcurrencyConflictError(RuntimeError):
    """Raised when a caller's `expected_version` doesn't match a row's
    current `.version` - an explicit, structured conflict (doc 6.11)
    instead of silent last-write-wins. The caller must reload and retry,
    typically after re-showing the user the current state to compare
    against."""


def check_and_bump_version(row, expected_version: int) -> None:  # noqa: ANN001
    """Optimistic-concurrency guard for any row with an integer `.version`
    column (`Project`, `IterativeCycleState`). Raises before making any
    change if the caller's view was stale; bumps the version as part of
    the same transaction otherwise."""
    if row.version != expected_version:
        identifier = getattr(row, "project_id", None) or getattr(row, "cycle_state_id", None) or "?"
        raise ConcurrencyConflictError(
            f"{type(row).__name__} {identifier}: expected version {expected_version}, "
            f"actual {row.version} - reload and retry"
        )
    row.version += 1


def _make_engine(url: str) -> Engine:
    engine = create_engine(url, future=True)

    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            # WAL: readers no longer block behind the single writer (and vice
            # versa) - before this, any concurrent write during a slow request
            # surfaced as a bare 500 "database is locked". busy_timeout makes a
            # contender wait 5s for the lock instead of failing immediately.
            # journal_mode persists in the db file; busy_timeout is
            # per-connection, so both are (idempotently) set on every connect.
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

    return engine


_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = _make_engine(f"sqlite:///{DB_PATH}")
    return _engine


def get_session_factory() -> sessionmaker:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), expire_on_commit=False, future=True)
    return _SessionLocal


@contextmanager
def session_scope() -> Iterator[Session]:
    """One transaction: commit on success, rollback (and re-raise) on
    exception. Every Problem-02 mutating service function uses exactly one
    of these per logical change, so entity rows and their ProjectEvent(s)
    always commit together or not at all."""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_engine_for_tests(db_url: str) -> None:
    """Test-only: repoint the module-level engine/session factory at an
    isolated database (e.g. a tmp_path SQLite file) so tests never read or
    write the real dev ledger. Disposes the previous engine's connection
    pool explicitly rather than relying on GC timing to release its file
    handle - on Windows an undisposed SQLite handle can otherwise still be
    open when pytest tries to clean up that tmp_path directory a few tests
    later, which showed up as an intermittent single-test failure under
    the full suite (never in isolation) during this round's testing."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = _make_engine(db_url)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
