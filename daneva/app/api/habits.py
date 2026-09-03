"""Habits API."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.habit import Habit, HabitCompletion
from app.schemas.habit import HabitCompleteRequest, HabitCreateRequest, HabitStreakResponse
from app.services.habit_service import HabitService

router = APIRouter(prefix="/habits", tags=["habits"])


class HabitAlreadyCompletedError(ValueError):
    """Raised when a habit already has a completion for the requested
    day — completing it again is a conflict, not a validation error."""


def _service(db: Session = Depends(get_db)) -> HabitService:
    return HabitService(db)


@router.post("", response_model=Habit, status_code=status.HTTP_201_CREATED)
def create_habit(payload: HabitCreateRequest, service: HabitService = Depends(_service)) -> Habit:
    return service.create(**payload.model_dump())


@router.get("", response_model=list[Habit])
def list_habits(service: HabitService = Depends(_service)) -> list[Habit]:
    return service.list_all()


@router.post(
    "/{habit_id}/complete", response_model=HabitCompletion, status_code=status.HTTP_201_CREATED
)
def complete_habit(
    habit_id: str,
    payload: HabitCompleteRequest = HabitCompleteRequest(),
    service: HabitService = Depends(_service),
) -> HabitCompletion:
    completion = service.complete(habit_id, on_date=payload.on_date)
    if completion is None:
        raise HabitAlreadyCompletedError(habit_id)
    return completion


@router.get("/{habit_id}/streak", response_model=HabitStreakResponse)
def get_habit_streak(
    habit_id: str, service: HabitService = Depends(_service)
) -> HabitStreakResponse:
    return HabitStreakResponse(streak=service.get_streak(habit_id))
