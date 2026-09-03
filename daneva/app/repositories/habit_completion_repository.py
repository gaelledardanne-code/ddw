"""Translates between the HabitCompletion domain entity and its ORM model."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.habit import HabitCompletion
from app.models.habit import HabitCompletionModel


def _to_model(completion: HabitCompletion) -> HabitCompletionModel:
    return HabitCompletionModel(
        id=completion.id,
        habit_id=completion.habit_id,
        completed_date=completion.completed_date,
    )


def _to_domain(model: HabitCompletionModel) -> HabitCompletion:
    return HabitCompletion(
        id=model.id,
        habit_id=model.habit_id,
        completed_date=model.completed_date,
    )


class HabitCompletionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, completion: HabitCompletion) -> None:
        self.session.add(_to_model(completion))
        self.session.commit()

    def get(self, completion_id: str) -> HabitCompletion | None:
        model = self.session.get(HabitCompletionModel, completion_id)
        return _to_domain(model) if model else None

    def list_by_habit(self, habit_id: str) -> list[HabitCompletion]:
        stmt = select(HabitCompletionModel).where(HabitCompletionModel.habit_id == habit_id)
        models = self.session.execute(stmt).scalars().all()
        return [_to_domain(model) for model in models]
