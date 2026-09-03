"""Milestones API."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.milestone import Milestone
from app.schemas.milestone import MilestoneCreateRequest
from app.services.goal_service import GoalNotFoundError, GoalService
from app.services.milestone_service import MilestoneService

router = APIRouter(tags=["milestones"])


def _milestones(db: Session = Depends(get_db)) -> MilestoneService:
    return MilestoneService(db)


def _goals(db: Session = Depends(get_db)) -> GoalService:
    return GoalService(db)


@router.post(
    "/goals/{goal_id}/milestones", response_model=Milestone, status_code=status.HTTP_201_CREATED
)
def create_milestone(
    goal_id: str,
    payload: MilestoneCreateRequest,
    goals: GoalService = Depends(_goals),
    milestones: MilestoneService = Depends(_milestones),
) -> Milestone:
    if goals.get(goal_id) is None:
        raise GoalNotFoundError(goal_id)
    return milestones.create(goal_id=goal_id, **payload.model_dump())


@router.get("/goals/{goal_id}/milestones", response_model=list[Milestone])
def list_milestones(
    goal_id: str,
    goals: GoalService = Depends(_goals),
    milestones: MilestoneService = Depends(_milestones),
) -> list[Milestone]:
    if goals.get(goal_id) is None:
        raise GoalNotFoundError(goal_id)
    return milestones.list_by_goal(goal_id)
