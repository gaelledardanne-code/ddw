"""Maps domain/service exceptions to HTTP responses, once, for every
router — a not-found lookup is always 404, an illegal state transition
is always 409, and any other invalid input (blank title, bad enum
value, a disallowed field on update, ...) is always 422. Routers don't
each need their own try/except for this."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.goal import GoalLifecycleError
from app.services.goal_service import GoalNotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(GoalNotFoundError)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(GoalLifecycleError)
    async def lifecycle_conflict_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
