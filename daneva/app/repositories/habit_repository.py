"""Translates between the Habit domain entity and its ORM model."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.habit import Habit
from app.models.habit import HabitModel


def _to_model(habit: Habit) -> HabitModel:
    return HabitModel(
        id=habit.id,
        goal_id=habit.goal_id,
        title=habit.title,
        description=habit.description,
        created_date=habit.created_date,
    )


def _to_domain(model: HabitModel) -> Habit:
    return Habit(
        id=model.id,
        goal_id=model.goal_id,
        title=model.title,
        description=model.description,
        created_date=model.created_date,
    )


class HabitRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, habit: Habit) -> None:
        self.session.merge(_to_model(habit))
        self.session.commit()

    def get(self, habit_id: str) -> Habit | None:
        model = self.session.get(HabitModel, habit_id)
        return _to_domain(model) if model else None

    def list_all(self) -> list[Habit]:
        models = self.session.query(HabitModel).all()
        return [_to_domain(model) for model in models]

    def list_by_goal(self, goal_id: str) -> list[Habit]:
        stmt = select(HabitModel).where(HabitModel.goal_id == goal_id)
        models = self.session.execute(stmt).scalars().all()
        return [_to_domain(model) for model in models]

    def delete(self, habit_id: str) -> None:
        model = self.session.get(HabitModel, habit_id)
        if model is not None:
            self.session.delete(model)
            self.session.commit()
