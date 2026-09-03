"""XP: a simple, deterministic reward for completing a task."""

from datetime import datetime

from app.domain.enums import TaskPriority, TaskStatus
from app.domain.task import Task

XP_BY_PRIORITY: dict[TaskPriority, int] = {
    TaskPriority.LOW: 10,
    TaskPriority.MEDIUM: 20,
    TaskPriority.HIGH: 40,
    TaskPriority.CRITICAL: 80,
}


def xp_for_priority(priority: TaskPriority) -> int:
    return XP_BY_PRIORITY[priority]


def complete_task(task: Task) -> int:
    """Mark a task completed and return the XP earned.

    Returns 0 without changing anything if the task was already
    completed, so completing it twice never double-awards XP.
    """
    if task.status == TaskStatus.COMPLETED:
        return 0

    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.now()
    return xp_for_priority(task.priority)
