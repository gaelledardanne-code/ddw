"""Goals API. No business logic here — validate the request shape,
call GoalService, return the result. Errors from the service (not
found, illegal lifecycle transition, invalid field) are handled once,
centrally, in app.api.errors."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.goal import Goal
from app.domain.progress import GoalProgress
from app.schemas.goal import GoalCreateRequest, GoalUpdateRequest
from app.services.goal_service import GoalNotFoundError, GoalService

router = APIRouter(prefix="/goals", tags=["goals"])


def _service(db: Session = Depends(get_db)) -> GoalService:
    return GoalService(db)


@router.get("", response_model=list[Goal])
def list_goals(service: GoalService = Depends(_service)) -> list[Goal]:
    return service.list_all()


@router.post("", response_model=Goal, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreateRequest, service: GoalService = Depends(_service)) -> Goal:
    return service.create(**payload.model_dump())


@router.get("/{goal_id}", response_model=Goal)
def get_goal(goal_id: str, service: GoalService = Depends(_service)) -> Goal:
    goal = service.get(goal_id)
    if goal is None:
        raise GoalNotFoundError(goal_id)
    return goal


@router.patch("/{goal_id}", response_model=Goal)
def update_goal(
    goal_id: str, payload: GoalUpdateRequest, service: GoalService = Depends(_service)
) -> Goal:
    return service.update(goal_id, **payload.model_dump(exclude_unset=True))


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: str, service: GoalService = Depends(_service)) -> None:
    service.delete(goal_id)


@router.get("/{goal_id}/progress", response_model=GoalProgress)
def get_goal_progress(goal_id: str, service: GoalService = Depends(_service)) -> GoalProgress:
    return service.get_progress(goal_id)


@router.post("/{goal_id}/pause", response_model=Goal)
def pause_goal(goal_id: str, service: GoalService = Depends(_service)) -> Goal:
    return service.pause(goal_id)


@router.post("/{goal_id}/resume", response_model=Goal)
def resume_goal(goal_id: str, service: GoalService = Depends(_service)) -> Goal:
    return service.resume(goal_id)


@router.post("/{goal_id}/complete", response_model=Goal)
def complete_goal(goal_id: str, service: GoalService = Depends(_service)) -> Goal:
    return service.complete(goal_id)


@router.post("/{goal_id}/abandon", response_model=Goal)
def abandon_goal(goal_id: str, service: GoalService = Depends(_service)) -> Goal:
    return service.abandon(goal_id)
