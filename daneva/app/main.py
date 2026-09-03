"""Daneva's FastAPI app: wires routers and error handling together.
No business logic lives here — see app/domain and app/services."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.goals import router as goals_router
from app.api.milestones import router as milestones_router
from app.api.tasks import router as tasks_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="Daneva — Personal Hustle Planner", lifespan=lifespan)

register_exception_handlers(app)
app.include_router(goals_router)
app.include_router(milestones_router)
app.include_router(tasks_router)
