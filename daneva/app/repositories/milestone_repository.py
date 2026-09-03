"""Translates between the Milestone domain entity and its ORM model."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.milestone import Milestone
from app.models.milestone import MilestoneModel


def _to_model(milestone: Milestone) -> MilestoneModel:
    return MilestoneModel(
        id=milestone.id,
        goal_id=milestone.goal_id,
        title=milestone.title,
        description=milestone.description,
        created_date=milestone.created_date,
    )


def _to_domain(model: MilestoneModel) -> Milestone:
    return Milestone(
        id=model.id,
        goal_id=model.goal_id,
        title=model.title,
        description=model.description,
        created_date=model.created_date,
    )


class MilestoneRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, milestone: Milestone) -> None:
        self.session.merge(_to_model(milestone))
        self.session.commit()

    def get(self, milestone_id: str) -> Milestone | None:
        model = self.session.get(MilestoneModel, milestone_id)
        return _to_domain(model) if model else None

    def list_by_goal(self, goal_id: str) -> list[Milestone]:
        stmt = select(MilestoneModel).where(MilestoneModel.goal_id == goal_id)
        models = self.session.execute(stmt).scalars().all()
        return [_to_domain(model) for model in models]
