"""Request bodies and the one composite response for the Tasks API.
Completing a task returns both the task and the XP it earned — the Task
entity itself has no xp field (XP isn't part of what a task *is*), so a
small response schema is the right place for that pairing."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.domain.enums import EnergyLevel, TaskPriority
from app.domain.task import Task


class TaskCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    energy_level: EnergyLevel = EnergyLevel.MEDIUM
    estimated_minutes: int | None = None
    due_date: date | None = None


class TaskUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    energy_level: EnergyLevel | None = None
    estimated_minutes: int | None = None
    due_date: date | None = None


class TaskCompletionResponse(BaseModel):
    task: Task
    xp_awarded: int
