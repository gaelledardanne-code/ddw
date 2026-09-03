"""Translates between the Task domain entity and its ORM model."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import EnergyLevel, TaskPriority, TaskStatus
from app.domain.task import Task
from app.models.task import TaskModel


def _to_model(task: Task) -> TaskModel:
    return TaskModel(
        id=task.id,
        goal_id=task.goal_id,
        milestone_id=task.milestone_id,
        title=task.title,
        description=task.description,
        status=task.status.value,
        priority=task.priority.value,
        energy_level=task.energy_level.value,
        estimated_minutes=task.estimated_minutes,
        due_date=task.due_date,
        completed_at=task.completed_at,
    )


def _to_domain(model: TaskModel) -> Task:
    return Task(
        id=model.id,
        goal_id=model.goal_id,
        milestone_id=model.milestone_id,
        title=model.title,
        description=model.description,
        status=TaskStatus(model.status),
        priority=TaskPriority(model.priority),
        energy_level=EnergyLevel(model.energy_level),
        estimated_minutes=model.estimated_minutes,
        due_date=model.due_date,
        completed_at=model.completed_at,
    )


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, task: Task) -> None:
        self.session.merge(_to_model(task))
        self.session.commit()

    def get(self, task_id: str) -> Task | None:
        model = self.session.get(TaskModel, task_id)
        return _to_domain(model) if model else None

    def list_by_goal(self, goal_id: str) -> list[Task]:
        stmt = select(TaskModel).where(TaskModel.goal_id == goal_id)
        models = self.session.execute(stmt).scalars().all()
        return [_to_domain(model) for model in models]
