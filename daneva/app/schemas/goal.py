"""Request bodies for the Goals API. Responses reuse the domain Goal /
GoalProgress models directly — they're already Pydantic, and there's no
business rule difference between "the goal" and "the goal as returned by
the API", so a separate response schema would just duplicate fields."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.domain.enums import GoalCategory, GoalPriority


class GoalCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str = ""
    category: GoalCategory = GoalCategory.OTHER
    priority: GoalPriority = GoalPriority.MEDIUM
    target_date: date | None = None


class GoalUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    description: str | None = None
    category: GoalCategory | None = None
    priority: GoalPriority | None = None
    target_date: date | None = None
