"""Slice 9d: Daily plan persistence.

The plan's task_ids are stored as DailyPlanItem rows (a join table to
tasks). save() replaces the full set of items each time — simpler than
diffing, and correct because the domain DailyPlan already deduplicates
task_ids before it's ever saved.
"""

from datetime import date

from app.domain.daily_plan import DailyPlan
from app.domain.goal import Goal
from app.domain.task import Task
from app.repositories.daily_plan_repository import DailyPlanRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.task_repository import TaskRepository


def make_task(db_session, goal_id: str, title: str) -> Task:
    task_repo = TaskRepository(db_session)
    task = Task.create(goal_id=goal_id, title=title)
    task_repo.save(task)
    return task


def test_save_and_get_roundtrips_plan_date(db_session):
    repo = DailyPlanRepository(db_session)
    plan = DailyPlan(plan_date=date(2026, 9, 3))

    repo.save(plan)
    fetched = repo.get(plan.id)

    assert fetched is not None
    assert fetched.plan_date == date(2026, 9, 3)
    assert fetched.task_ids == []


def test_save_and_get_roundtrips_task_ids(db_session):
    goal_repo = GoalRepository(db_session)
    goal = Goal.create(title="Launch my portfolio")
    goal_repo.save(goal)
    task_a = make_task(db_session, goal.id, "A")
    task_b = make_task(db_session, goal.id, "B")

    plan = DailyPlan(plan_date=date(2026, 9, 3))
    plan.add_task(task_a.id)
    plan.add_task(task_b.id)

    repo = DailyPlanRepository(db_session)
    repo.save(plan)
    fetched = repo.get(plan.id)

    assert set(fetched.task_ids) == {task_a.id, task_b.id}


def test_get_returns_none_for_a_missing_plan(db_session):
    repo = DailyPlanRepository(db_session)

    assert repo.get("does-not-exist") is None


def test_get_by_date_finds_the_plan(db_session):
    repo = DailyPlanRepository(db_session)
    plan = DailyPlan(plan_date=date(2026, 9, 3))
    repo.save(plan)

    fetched = repo.get_by_date(date(2026, 9, 3))

    assert fetched is not None
    assert fetched.id == plan.id


def test_get_by_date_returns_none_when_no_plan_that_day(db_session):
    repo = DailyPlanRepository(db_session)

    assert repo.get_by_date(date(2026, 9, 3)) is None


def test_save_again_replaces_the_task_ids(db_session):
    goal_repo = GoalRepository(db_session)
    goal = Goal.create(title="Launch my portfolio")
    goal_repo.save(goal)
    task_a = make_task(db_session, goal.id, "A")
    task_b = make_task(db_session, goal.id, "B")

    plan = DailyPlan(plan_date=date(2026, 9, 3))
    plan.add_task(task_a.id)
    repo = DailyPlanRepository(db_session)
    repo.save(plan)

    plan.remove_task(task_a.id)
    plan.add_task(task_b.id)
    repo.save(plan)

    fetched = repo.get(plan.id)
    assert set(fetched.task_ids) == {task_b.id}
