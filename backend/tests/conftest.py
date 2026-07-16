"""Shared pytest fixtures."""

from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def database_engine(tmp_path: Path) -> Generator[Engine, None, None]:
    """Provide a disposable SQLite engine for a test."""
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def database_session(database_engine: Engine) -> Generator[Session, None, None]:
    """Provide and close a session bound to the test database."""
    session = sessionmaker(bind=database_engine)()
    try:
        yield session
    finally:
        session.close()
