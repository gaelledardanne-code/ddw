"""MilestoneService: orchestrates MilestoneRepository with the domain
layer."""

from sqlalchemy.orm import Session

from app.domain.milestone import Milestone
from app.repositories.milestone_repository import MilestoneRepository


class MilestoneNotFoundError(LookupError):
    """Raised when a milestone_id doesn't match any saved milestone."""


class MilestoneService:
    def __init__(self, session: Session) -> None:
        self.milestones = MilestoneRepository(session)

    def create(self, *, goal_id: str, title: str, description: str = "") -> Milestone:
        milestone = Milestone(goal_id=goal_id, title=title, description=description)
        self.milestones.save(milestone)
        return milestone

    def get(self, milestone_id: str) -> Milestone | None:
        return self.milestones.get(milestone_id)

    def list_by_goal(self, goal_id: str) -> list[Milestone]:
        return self.milestones.list_by_goal(goal_id)
