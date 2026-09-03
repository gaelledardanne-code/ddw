"""Request bodies and the streak response for the Habits API."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class HabitCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str = ""
    goal_id: str | None = None


class HabitCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    on_date: date | None = None


class HabitStreakResponse(BaseModel):
    streak: int
