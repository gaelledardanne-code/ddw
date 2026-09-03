"""TaskService: orchestrates TaskRepository with the domain layer."""

from datetime import date

from sqlalchemy.orm import Session

from app.domain.enums import EnergyLevel, TaskPriority
from app.domain.task import Task
from app.domain.xp import complete_task
from app.repositories.task_repository import TaskRepository


class TaskNotFoundError(LookupError):
    """Raised when a task_id doesn't match any saved task."""


class TaskService:
    def __init__(self, session: Session) -> None:
        self.tasks = TaskRepository(session)

    def create(
        self,
        *,
        goal_id: str,
        milestone_id: str | None = None,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        energy_level: EnergyLevel = EnergyLevel.MEDIUM,
        estimated_minutes: int | None = None,
        due_date: date | None = None,
    ) -> Task:
        task = Task.create(
            goal_id=goal_id,
            milestone_id=milestone_id,
            title=title,
            description=description,
            priority=priority,
            energy_level=energy_level,
            estimated_minutes=estimated_minutes,
            due_date=due_date,
        )
        self.tasks.save(task)
        return task

    def get(self, task_id: str) -> Task | None:
        return self.tasks.get(task_id)

    def list_by_goal(self, goal_id: str) -> list[Task]:
        return self.tasks.list_by_goal(goal_id)

    def list_all(self) -> list[Task]:
        return self.tasks.list_all()

    def _require(self, task_id: str) -> Task:
        task = self.tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    # Fields that must go through a dedicated method rather than a
    # generic field update: status/completed_at are set together by
    # complete() (which also awards XP); id is identity, not editable.
    _NOT_DIRECTLY_UPDATABLE = frozenset({"status", "id", "completed_at"})

    def update(self, task_id: str, **fields: object) -> Task:
        disallowed = self._NOT_DIRECTLY_UPDATABLE & fields.keys()
        if disallowed:
            raise ValueError(
                f"cannot update {sorted(disallowed)} directly; use complete() for status"
            )
        task = self._require(task_id)
        updated = Task(**{**task.model_dump(), **fields})
        self.tasks.save(updated)
        return updated

    def complete(self, task_id: str) -> int:
        task = self._require(task_id)
        xp_awarded = complete_task(task)
        self.tasks.save(task)
        return xp_awarded
