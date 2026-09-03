"""HabitService: orchestrates HabitRepository + HabitCompletionRepository
with the domain layer's record_completion / calculate_streak."""

from datetime import date

from sqlalchemy.orm import Session

from app.domain.habit import Habit, HabitCompletion, calculate_streak, record_completion
from app.repositories.habit_completion_repository import HabitCompletionRepository
from app.repositories.habit_repository import HabitRepository


class HabitService:
    def __init__(self, session: Session) -> None:
        self.habits = HabitRepository(session)
        self.completions = HabitCompletionRepository(session)

    def create(self, *, title: str, description: str = "", goal_id: str | None = None) -> Habit:
        habit = Habit(title=title, description=description, goal_id=goal_id)
        self.habits.save(habit)
        return habit

    def get(self, habit_id: str) -> Habit | None:
        return self.habits.get(habit_id)

    def list_all(self) -> list[Habit]:
        return self.habits.list_all()

    def complete(self, habit_id: str, on_date: date | None = None) -> HabitCompletion | None:
        existing = self.completions.list_by_habit(habit_id)
        completion = record_completion(habit_id, existing, on_date=on_date)
        if completion is not None:
            self.completions.save(completion)
        return completion

    def get_streak(self, habit_id: str) -> int:
        existing = self.completions.list_by_habit(habit_id)
        return calculate_streak([c.completed_date for c in existing])
