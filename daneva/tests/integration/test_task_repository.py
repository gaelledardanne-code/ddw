"""Slice 9b: Task persistence, including the Goal -> Tasks relationship
(cascade delete) and the optional Milestone -> Tasks link."""

from datetime import date, datetime

from app.domain.enums import EnergyLevel, TaskPriority, TaskStatus
from app.domain.goal import Goal
from app.domain.milestone import Milestone
from app.domain.task import Task
from app.repositories.goal_repository import GoalRepository
from app.repositories.milestone_repository import MilestoneRepository
from app.repositories.task_repository import TaskRepository


def make_goal(db_session) -> Goal:
    goal_repo = GoalRepository(db_session)
    goal = Goal.create(title="Launch my portfolio")
    goal_repo.save(goal)
    return goal


def test_save_and_get_roundtrips_all_fields(db_session):
    goal = make_goal(db_session)
    task_repo = TaskRepository(db_session)
    task = Task.create(
        goal_id=goal.id,
        title="Write landing page copy",
        description="Focus on the hero section",
        priority=TaskPriority.HIGH,
        energy_level=EnergyLevel.HIGH,
        estimated_minutes=45,
        due_date=date(2026, 9, 10),
    )

    task_repo.save(task)
    fetched = task_repo.get(task.id)

    assert fetched is not None
    assert fetched.goal_id == goal.id
    assert fetched.milestone_id is None
    assert fetched.title == "Write landing page copy"
    assert fetched.description == "Focus on the hero section"
    assert fetched.status == TaskStatus.TODO
    assert fetched.priority == TaskPriority.HIGH
    assert fetched.energy_level == EnergyLevel.HIGH
    assert fetched.estimated_minutes == 45
    assert fetched.due_date == date(2026, 9, 10)
    assert fetched.completed_at is None


def test_save_roundtrips_a_task_attached_to_a_milestone(db_session):
    goal = make_goal(db_session)
    milestone_repo = MilestoneRepository(db_session)
    milestone = Milestone(goal_id=goal.id, title="Build website")
    milestone_repo.save(milestone)

    task_repo = TaskRepository(db_session)
    task = Task.create(goal_id=goal.id, milestone_id=milestone.id, title="Pick a template")
    task_repo.save(task)

    fetched = task_repo.get(task.id)

    assert fetched.milestone_id == milestone.id


def test_save_roundtrips_a_completed_task(db_session):
    goal = make_goal(db_session)
    task_repo = TaskRepository(db_session)
    task = Task.create(goal_id=goal.id, title="Write landing page copy")
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime(2026, 9, 3, 14, 30)

    task_repo.save(task)
    fetched = task_repo.get(task.id)

    assert fetched.status == TaskStatus.COMPLETED
    assert fetched.completed_at == datetime(2026, 9, 3, 14, 30)


def test_get_returns_none_for_a_missing_task(db_session):
    repo = TaskRepository(db_session)

    assert repo.get("does-not-exist") is None


def test_list_by_goal_returns_only_that_goals_tasks(db_session):
    goal_a = make_goal(db_session)
    goal_b_repo = GoalRepository(db_session)
    goal_b = Goal.create(title="Get fit")
    goal_b_repo.save(goal_b)

    task_repo = TaskRepository(db_session)
    task_repo.save(Task.create(goal_id=goal_a.id, title="A"))
    task_repo.save(Task.create(goal_id=goal_a.id, title="B"))
    task_repo.save(Task.create(goal_id=goal_b.id, title="C"))

    tasks = task_repo.list_by_goal(goal_a.id)

    assert {t.title for t in tasks} == {"A", "B"}


def test_deleting_a_goal_cascades_to_its_tasks(db_session):
    goal = make_goal(db_session)
    task_repo = TaskRepository(db_session)
    task = Task.create(goal_id=goal.id, title="Write landing page copy")
    task_repo.save(task)

    goal_repo = GoalRepository(db_session)
    goal_repo.delete(goal.id)

    assert task_repo.get(task.id) is None
