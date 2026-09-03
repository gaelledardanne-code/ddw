"""Translates between the Goal domain entity and its ORM model."""

from sqlalchemy.orm import Session

from app.domain.enums import GoalCategory, GoalPriority, GoalStatus
from app.domain.goal import Goal
from app.models.goal import GoalModel


def _to_model(goal: Goal) -> GoalModel:
    return GoalModel(
        id=goal.id,
        title=goal.title,
        description=goal.description,
        category=goal.category.value,
        priority=goal.priority.value,
        status=goal.status.value,
        target_date=goal.target_date,
        created_date=goal.created_date,
        completed_date=goal.completed_date,
    )


def _to_domain(model: GoalModel) -> Goal:
    return Goal(
        id=model.id,
        title=model.title,
        description=model.description,
        category=GoalCategory(model.category),
        priority=GoalPriority(model.priority),
        status=GoalStatus(model.status),
        target_date=model.target_date,
        created_date=model.created_date,
        completed_date=model.completed_date,
    )


class GoalRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, goal: Goal) -> None:
        self.session.merge(_to_model(goal))
        self.session.commit()

    def get(self, goal_id: str) -> Goal | None:
        model = self.session.get(GoalModel, goal_id)
        return _to_domain(model) if model else None

    def list_all(self) -> list[Goal]:
        models = self.session.query(GoalModel).all()
        return [_to_domain(model) for model in models]

    def delete(self, goal_id: str) -> None:
        model = self.session.get(GoalModel, goal_id)
        if model is not None:
            self.session.delete(model)
            self.session.commit()
