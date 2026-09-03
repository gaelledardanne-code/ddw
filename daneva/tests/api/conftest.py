"""Shared fixture for API tests: a FastAPI TestClient wired to its own
isolated, file-based SQLite database per test (via dependency override),
so API tests exercise the real app wiring without touching each other's
data or the dev database."""

import os
import tempfile
from collections.abc import Iterator

# Must be set before app.db.session is first imported (it reads this at
# import time) so the app's own lifespan startup never touches the real
# dev database file as a side effect of running the test suite.
os.environ.setdefault("DANEVA_DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/daneva_test.db")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

import app.models  # noqa: F401,E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "test_api.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    testing_session_local = sessionmaker(bind=engine)

    def override_get_db() -> Iterator:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
