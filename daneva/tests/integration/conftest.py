"""Shared fixtures for integration tests: a real, file-based SQLite
database per test, so repository behaviour (constraints, cascades,
relationships) is exercised for real rather than mocked."""

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Importing app.models registers every table on Base.metadata.
import app.models  # noqa: F401
from app.db.base import Base


@pytest.fixture
def db_session(tmp_path) -> Iterator[Session]:
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
