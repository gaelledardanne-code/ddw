"""Goal progress calculation.

Progress is derived purely from a goal's tasks — it doesn't need the Goal
entity itself, so it's tested and used with a plain list of Task objects.
"""

from collections.abc import Sequence

from pydantic import BaseModel

from app.domain.enums import TaskStatus
from app.domain.task import Task


class GoalProgress(BaseModel):
    total_tasks: int
    completed_tasks: int
    remaining_tasks: int
    completion_percentage: int


def calculate_goal_progress(tasks: Sequence[Task]) -> GoalProgress:
    countable = [task for task in tasks if task.status != TaskStatus.CANCELLED]
    total = len(countable)
    completed = sum(1 for task in countable if task.status == TaskStatus.COMPLETED)
    remaining = total - completed
    percentage = round(completed / total * 100) if total else 0

    return GoalProgress(
        total_tasks=total,
        completed_tasks=completed,
        remaining_tasks=remaining,
        completion_percentage=percentage,
    )
