"""Task domain entity.

A task belongs directly to a goal, or to a milestone within that goal —
`goal_id` is always set (even via a milestone) so goal-wide progress can
be computed without walking through milestones.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.enums import EnergyLevel, TaskPriority, TaskStatus


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str
    milestone_id: str | None = None
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    energy_level: EnergyLevel = EnergyLevel.MEDIUM
    estimated_minutes: int | None = None
    due_date: date | None = None
    completed_at: datetime | None = None

    @field_validator("goal_id", "title")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("estimated_minutes")
    @classmethod
    def estimated_minutes_must_be_positive(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("estimated_minutes must be positive")
        return value

    @classmethod
    def create(
        cls,
        *,
        goal_id: str,
        milestone_id: str | None = None,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        energy_level: EnergyLevel = EnergyLevel.MEDIUM,
        estimated_minutes: int | None = None,
        due_date: date | None = None,
    ) -> "Task":
        """Create a brand-new task. Always starts TODO, uncompleted —
        status and completed_at aren't parameters here.

        Reconstructing an existing task (e.g. from a repository) uses the
        plain constructor instead, which accepts any persisted status.
        """
        return cls(
            goal_id=goal_id,
            milestone_id=milestone_id,
            title=title,
            description=description,
            priority=priority,
            energy_level=energy_level,
            estimated_minutes=estimated_minutes,
            due_date=due_date,
        )
