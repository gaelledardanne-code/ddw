"""Habit domain: recurring actions, their completions, and streaks."""

import uuid
from collections.abc import Sequence
from datetime import date, timedelta

from pydantic import BaseModel, Field, field_validator


class Habit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str | None = None
    title: str
    description: str = ""
    created_date: date = Field(default_factory=date.today)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title must not be blank")
        return value


class HabitCompletion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    habit_id: str
    completed_date: date = Field(default_factory=date.today)

    @field_validator("habit_id")
    @classmethod
    def habit_id_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("habit_id must not be blank")
        return value


def record_completion(
    habit_id: str,
    existing_completions: Sequence[HabitCompletion],
    on_date: date | None = None,
) -> HabitCompletion | None:
    """Record a habit as done on a given day (today by default).

    Returns None without recording anything if the habit was already
    completed that day, so a duplicate same-day completion is a no-op.
    """
    target_date = on_date or date.today()
    already_done = any(
        completion.habit_id == habit_id and completion.completed_date == target_date
        for completion in existing_completions
    )
    if already_done:
        return None

    return HabitCompletion(habit_id=habit_id, completed_date=target_date)


def calculate_streak(completed_dates: Sequence[date]) -> int:
    """Length of the trailing run of consecutive days, ending at the
    most recent completion date. Duplicate dates count once."""
    unique_dates = sorted(set(completed_dates), reverse=True)
    if not unique_dates:
        return 0

    streak = 1
    for later, earlier in zip(unique_dates, unique_dates[1:], strict=False):
        if later - earlier == timedelta(days=1):
            streak += 1
        else:
            break
    return streak
