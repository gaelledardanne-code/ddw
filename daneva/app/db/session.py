"""Engine/session setup for the running app. Tests override the
DANEVA_DATABASE_URL env var (see tests/api/conftest.py) so importing
this module never touches the real dev database file as a side effect,
and additionally override the get_db dependency itself for full
per-test isolation (see tests/*/conftest.py)."""

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401  registers every table on Base.metadata
from app.db.base import Base

DATABASE_URL = os.environ.get("DANEVA_DATABASE_URL", "sqlite:///./daneva.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
