"""Goal domain entity.

Pure business rules for what a Goal is and how it may be created. No
FastAPI, no SQLAlchemy, no I/O — this module is testable with plain
function calls.
"""

import uuid
from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.enums import GoalCategory, GoalPriority, GoalStatus


class GoalLifecycleError(ValueError):
    """Raised when a goal transition isn't allowed from its current status."""


class Goal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str = ""
    category: GoalCategory = GoalCategory.OTHER
    priority: GoalPriority = GoalPriority.MEDIUM
    status: GoalStatus = GoalStatus.ACTIVE
    target_date: date | None = None
    created_date: date = Field(default_factory=date.today)
    completed_date: date | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title must not be blank")
        return value

    @model_validator(mode="after")
    def new_goals_always_start_active(self) -> "Goal":
        self.status = GoalStatus.ACTIVE
        return self

    def pause(self) -> "Goal":
        if self.status != GoalStatus.ACTIVE:
            raise GoalLifecycleError(f"cannot pause a goal with status {self.status}")
        self.status = GoalStatus.PAUSED
        return self

    def resume(self) -> "Goal":
        if self.status != GoalStatus.PAUSED:
            raise GoalLifecycleError(f"cannot resume a goal with status {self.status}")
        self.status = GoalStatus.ACTIVE
        return self

    def complete(self) -> "Goal":
        if self.status not in (GoalStatus.ACTIVE, GoalStatus.PAUSED):
            raise GoalLifecycleError(f"cannot complete a goal with status {self.status}")
        self.status = GoalStatus.COMPLETED
        self.completed_date = date.today()
        return self

    def abandon(self) -> "Goal":
        if self.status not in (GoalStatus.ACTIVE, GoalStatus.PAUSED):
            raise GoalLifecycleError(f"cannot abandon a goal with status {self.status}")
        self.status = GoalStatus.ABANDONED
        return self
