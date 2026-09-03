"""Daily plan: a dated, user-curated selection of tasks.

No automatic task selection — the plan only stores which tasks were
picked for the day. Completion, estimated time, and XP are all derived
from the actual Task objects (status/estimated_minutes/priority stay a
single source of truth on the Task itself, never duplicated onto the
plan).
"""

import uuid
from collections.abc import Sequence
from datetime import date

from pydantic import BaseModel, Field

from app.domain.enums import TaskStatus
from app.domain.task import Task
from app.domain.xp import xp_for_priority


class DailyPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plan_date: date
    task_ids: list[str] = Field(default_factory=list)

    def add_task(self, task_id: str) -> None:
        if task_id not in self.task_ids:
            self.task_ids.append(task_id)

    def remove_task(self, task_id: str) -> None:
        if task_id in self.task_ids:
            self.task_ids.remove(task_id)


class DailyPlanSummary(BaseModel):
    total_tasks: int
    completed_tasks: int
    completion_percentage: int
    total_estimated_minutes: int
    total_xp: int


def summarize_daily_plan(plan: DailyPlan, tasks: Sequence[Task]) -> DailyPlanSummary:
    plan_tasks = [task for task in tasks if task.id in plan.task_ids]
    completed_tasks = [task for task in plan_tasks if task.status == TaskStatus.COMPLETED]

    total = len(plan_tasks)
    completed = len(completed_tasks)
    percentage = round(completed / total * 100) if total else 0
    total_estimated_minutes = sum(task.estimated_minutes or 0 for task in plan_tasks)
    total_xp = sum(xp_for_priority(task.priority) for task in completed_tasks)

    return DailyPlanSummary(
        total_tasks=total,
        completed_tasks=completed,
        completion_percentage=percentage,
        total_estimated_minutes=total_estimated_minutes,
        total_xp=total_xp,
    )
