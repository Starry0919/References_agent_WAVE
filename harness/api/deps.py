"""Shared FastAPI dependencies for the Problem-02 API routers."""
from __future__ import annotations

from typing import Iterator

from sqlalchemy.orm import Session

from harness.db import get_session_factory


def get_db_session() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
