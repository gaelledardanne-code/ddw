"""Slice 8c: daily plan summary — completion %, estimated time, XP.

The plan only stores task ids; the summary is computed from the actual
Task objects (looked up elsewhere, e.g. by a repository) so a task's
status/estimated_minutes/priority stays a single source of truth rather
than being duplicated onto the plan.

"Completing" a task in a daily plan is just completing the underlying
Task (via xp.complete_task) — the plan doesn't track its own separate
completion state.
"""

from datetime import date

from app.domain.daily_plan import DailyPlan, summarize_daily_plan
from app.domain.enums import TaskPriority
from app.domain.task import Task
from app.domain.xp import complete_task


def make_plan_with_tasks(*tasks: Task) -> tuple[DailyPlan, list[Task]]:
    plan = DailyPlan(plan_date=date(2026, 9, 3))
    for task in tasks:
        plan.add_task(task.id)
    return plan, list(tasks)


def test_summary_of_empty_plan():
    plan = DailyPlan(plan_date=date(2026, 9, 3))

    summary = summarize_daily_plan(plan, tasks=[])

    assert summary.total_tasks == 0
    assert summary.completed_tasks == 0
    assert summary.completion_percentage == 0
    assert summary.total_estimated_minutes == 0
    assert summary.total_xp == 0


def test_summary_only_counts_tasks_that_are_in_the_plan():
    in_plan = Task(goal_id="goal-1", title="In the plan", estimated_minutes=30)
    not_in_plan = Task(goal_id="goal-1", title="Not in the plan", estimated_minutes=99)
    plan, _ = make_plan_with_tasks(in_plan)

    summary = summarize_daily_plan(plan, tasks=[in_plan, not_in_plan])

    assert summary.total_tasks == 1
    assert summary.total_estimated_minutes == 30


def test_summary_total_estimated_minutes_sums_all_tasks_in_plan():
    task_a = Task(goal_id="goal-1", title="A", estimated_minutes=30)
    task_b = Task(goal_id="goal-1", title="B", estimated_minutes=45)
    plan, tasks = make_plan_with_tasks(task_a, task_b)

    summary = summarize_daily_plan(plan, tasks=tasks)

    assert summary.total_estimated_minutes == 75


def test_summary_treats_missing_estimated_minutes_as_zero():
    task = Task(goal_id="goal-1", title="No estimate given")
    plan, tasks = make_plan_with_tasks(task)

    summary = summarize_daily_plan(plan, tasks=tasks)

    assert summary.total_estimated_minutes == 0


def test_summary_completion_percentage_before_completing_anything():
    task_a = Task(goal_id="goal-1", title="A")
    task_b = Task(goal_id="goal-1", title="B")
    plan, tasks = make_plan_with_tasks(task_a, task_b)

    summary = summarize_daily_plan(plan, tasks=tasks)

    assert summary.completed_tasks == 0
    assert summary.completion_percentage == 0


def test_completing_a_task_updates_the_plan_summary():
    task_a = Task(goal_id="goal-1", title="A", priority=TaskPriority.MEDIUM)
    task_b = Task(goal_id="goal-1", title="B")
    plan, tasks = make_plan_with_tasks(task_a, task_b)

    xp_awarded = complete_task(task_a)
    summary = summarize_daily_plan(plan, tasks=tasks)

    assert xp_awarded == 20
    assert summary.completed_tasks == 1
    assert summary.completion_percentage == 50
    assert summary.total_xp == 20


def test_summary_total_xp_only_counts_completed_tasks():
    task_a = Task(goal_id="goal-1", title="A", priority=TaskPriority.LOW)
    task_b = Task(goal_id="goal-1", title="B", priority=TaskPriority.HIGH)
    plan, tasks = make_plan_with_tasks(task_a, task_b)

    complete_task(task_a)
    # task_b is left incomplete.
    summary = summarize_daily_plan(plan, tasks=tasks)

    assert summary.total_xp == 10


def test_summary_when_all_tasks_in_plan_are_completed():
    task_a = Task(goal_id="goal-1", title="A", priority=TaskPriority.LOW)
    task_b = Task(goal_id="goal-1", title="B", priority=TaskPriority.LOW)
    plan, tasks = make_plan_with_tasks(task_a, task_b)

    complete_task(task_a)
    complete_task(task_b)
    summary = summarize_daily_plan(plan, tasks=tasks)

    assert summary.completed_tasks == 2
    assert summary.completion_percentage == 100
    assert summary.total_xp == 20
