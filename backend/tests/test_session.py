"""Tests for database session infrastructure."""

from unittest.mock import MagicMock

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import session as session_module


def test_test_database_session_is_usable(database_session: Session) -> None:
    """A session can execute SQL against the disposable test database."""
    assert database_session.scalar(text("SELECT 1")) == 1


def test_get_db_session_closes_session(monkeypatch: object) -> None:
    """The FastAPI dependency always closes its session."""
    session = MagicMock(spec=Session)
    monkeypatch.setattr(session_module, "SessionLocal", lambda: session)  # type: ignore[attr-defined]
    dependency = session_module.get_db_session()

    assert next(dependency) is session
    dependency.close()

