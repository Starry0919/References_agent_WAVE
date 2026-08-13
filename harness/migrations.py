"""Small versioned migration runner: ordered, transactional, idempotent.

Not Alembic (yet) - a deliberate, documented, scoped choice for this round
(see 问题02_实施报告.md "known limitations": SQLite's limited `ALTER TABLE`
will force an Alembic adoption once the schema evolves again). Each
registered migration runs in its own transaction and is recorded in
`schema_migrations` so re-running `run_migrations()` is a no-op for
already-applied versions - this is what makes it a real migration runner
and not just "create tables on startup".
"""
from __future__ import annotations

import logging
from typing import Callable

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

MigrationFunc = Callable[[Session], None]

_MIGRATIONS: list[tuple[str, MigrationFunc]] = []


def migration(version: str) -> Callable[[MigrationFunc], MigrationFunc]:
    def decorator(fn: MigrationFunc) -> MigrationFunc:
        _MIGRATIONS.append((version, fn))
        return fn

    return decorator


def _ensure_migrations_table(session: Session) -> None:
    session.execute(
        text(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "version TEXT PRIMARY KEY, applied_at TEXT NOT NULL)"
        )
    )


def applied_versions(session: Session) -> set[str]:
    _ensure_migrations_table(session)
    rows = session.execute(text("SELECT version FROM schema_migrations")).fetchall()
    return {r[0] for r in rows}


def run_migrations(session_factory: sessionmaker) -> list[str]:
    """Apply every not-yet-applied migration, in registration order. Each
    runs in its own transaction; a failure stops the run without marking
    that (or any later) migration as applied. Returns the versions just
    applied (empty list if the schema was already current)."""
    import time

    newly_applied: list[str] = []
    for version, fn in _MIGRATIONS:
        session = session_factory()
        try:
            if version in applied_versions(session):
                continue
            fn(session)
            session.execute(
                text("INSERT INTO schema_migrations (version, applied_at) VALUES (:v, :t)"),
                {"v": version, "t": str(time.time())},
            )
            session.commit()
            newly_applied.append(version)
            logger.info("applied migration %s", version)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    return newly_applied
