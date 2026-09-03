"""Tasks API."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.task import Task
from app.schemas.task import TaskCompletionResponse, TaskCreateRequest, TaskUpdateRequest
from app.services.goal_service import GoalNotFoundError, GoalService
from app.services.milestone_service import MilestoneNotFoundError, MilestoneService
from app.services.task_service import TaskNotFoundError, TaskService

router = APIRouter(tags=["tasks"])


def _tasks(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


def _goals(db: Session = Depends(get_db)) -> GoalService:
    return GoalService(db)


def _milestones(db: Session = Depends(get_db)) -> MilestoneService:
    return MilestoneService(db)


@router.post("/goals/{goal_id}/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task_on_goal(
    goal_id: str,
    payload: TaskCreateRequest,
    goals: GoalService = Depends(_goals),
    tasks: TaskService = Depends(_tasks),
) -> Task:
    if goals.get(goal_id) is None:
        raise GoalNotFoundError(goal_id)
    return tasks.create(goal_id=goal_id, **payload.model_dump())


@router.post(
    "/milestones/{milestone_id}/tasks", response_model=Task, status_code=status.HTTP_201_CREATED
)
def create_task_on_milestone(
    milestone_id: str,
    payload: TaskCreateRequest,
    milestones: MilestoneService = Depends(_milestones),
    tasks: TaskService = Depends(_tasks),
) -> Task:
    milestone = milestones.get(milestone_id)
    if milestone is None:
        raise MilestoneNotFoundError(milestone_id)
    return tasks.create(
        goal_id=milestone.goal_id, milestone_id=milestone_id, **payload.model_dump()
    )


@router.get("/tasks", response_model=list[Task])
def list_tasks(tasks: TaskService = Depends(_tasks)) -> list[Task]:
    return tasks.list_all()


@router.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str, tasks: TaskService = Depends(_tasks)) -> Task:
    task = tasks.get(task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    return task


@router.patch("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: str, payload: TaskUpdateRequest, tasks: TaskService = Depends(_tasks)
) -> Task:
    return tasks.update(task_id, **payload.model_dump(exclude_unset=True))


@router.post("/tasks/{task_id}/complete", response_model=TaskCompletionResponse)
def complete_task(task_id: str, tasks: TaskService = Depends(_tasks)) -> TaskCompletionResponse:
    xp_awarded = tasks.complete(task_id)
    task = tasks.get(task_id)
    assert task is not None  # complete() would have raised TaskNotFoundError otherwise
    return TaskCompletionResponse(task=task, xp_awarded=xp_awarded)
