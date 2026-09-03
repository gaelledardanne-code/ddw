"""Slice 10e: DailyPlanService — orchestrates DailyPlanRepository +
TaskRepository with the domain layer's summarize_daily_plan. Auto-creates
an empty plan for a date that doesn't have one yet, which keeps callers
(and the future API) from having to special-case "no plan today"."""

from datetime import date

from app.domain.enums import TaskPriority
from app.services.daily_plan_service import DailyPlanService
from app.services.goal_service import GoalService
from app.services.task_service import TaskService


def test_get_or_create_creates_a_new_plan_when_none_exists(db_session):
    service = DailyPlanService(db_session)

    plan = service.get_or_create(date(2026, 9, 3))

    assert plan.plan_date == date(2026, 9, 3)
    assert plan.task_ids == []


def test_get_or_create_returns_the_same_plan_on_a_second_call(db_session):
    service = DailyPlanService(db_session)

    first = service.get_or_create(date(2026, 9, 3))
    second = service.get_or_create(date(2026, 9, 3))

    assert first.id == second.id


def test_add_task_creates_the_plan_if_needed_and_adds_the_task(db_session):
    goal = GoalService(db_session).create(title="Launch my portfolio")
    task = TaskService(db_session).create(goal_id=goal.id, title="A")
    service = DailyPlanService(db_session)

    plan = service.add_task(date(2026, 9, 3), task.id)

    assert plan.task_ids == [task.id]


def test_remove_task_removes_it_from_the_plan(db_session):
    goal = GoalService(db_session).create(title="Launch my portfolio")
    task = TaskService(db_session).create(goal_id=goal.id, title="A")
    service = DailyPlanService(db_session)
    service.add_task(date(2026, 9, 3), task.id)

    plan = service.remove_task(date(2026, 9, 3), task.id)

    assert plan.task_ids == []


def test_get_summary_of_a_day_with_no_plan_yet_is_empty(db_session):
    service = DailyPlanService(db_session)

    summary = service.get_summary(date(2026, 9, 3))

    assert summary.total_tasks == 0
    assert summary.completion_percentage == 0


def test_get_summary_reflects_completion_and_xp(db_session):
    goal = GoalService(db_session).create(title="Launch my portfolio")
    task_service = TaskService(db_session)
    task_a = task_service.create(goal_id=goal.id, title="A", priority=TaskPriority.MEDIUM)
    task_b = task_service.create(goal_id=goal.id, title="B")

    plan_service = DailyPlanService(db_session)
    plan_service.add_task(date(2026, 9, 3), task_a.id)
    plan_service.add_task(date(2026, 9, 3), task_b.id)
    task_service.complete(task_a.id)

    summary = plan_service.get_summary(date(2026, 9, 3))

    assert summary.total_tasks == 2
    assert summary.completed_tasks == 1
    assert summary.completion_percentage == 50
    assert summary.total_xp == 20
