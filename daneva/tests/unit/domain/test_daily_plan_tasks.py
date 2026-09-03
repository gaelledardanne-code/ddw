"""Slice 8b: adding and removing tasks from a daily plan.

Expected behaviour:
- Adding a task puts its id in the plan.
- Adding the same task twice doesn't duplicate it.
- Removing a task takes it out of the plan.
- Removing a task that isn't in the plan is a no-op, not an error.
"""

from datetime import date

from app.domain.daily_plan import DailyPlan


def make_plan() -> DailyPlan:
    return DailyPlan(plan_date=date(2026, 9, 3))


def test_add_task_puts_its_id_in_the_plan():
    plan = make_plan()

    plan.add_task("task-1")

    assert plan.task_ids == ["task-1"]


def test_add_task_twice_does_not_duplicate_it():
    plan = make_plan()

    plan.add_task("task-1")
    plan.add_task("task-1")

    assert plan.task_ids == ["task-1"]


def test_add_multiple_different_tasks():
    plan = make_plan()

    plan.add_task("task-1")
    plan.add_task("task-2")

    assert plan.task_ids == ["task-1", "task-2"]


def test_remove_task_takes_it_out_of_the_plan():
    plan = make_plan()
    plan.add_task("task-1")
    plan.add_task("task-2")

    plan.remove_task("task-1")

    assert plan.task_ids == ["task-2"]


def test_remove_task_not_in_the_plan_is_a_noop():
    plan = make_plan()
    plan.add_task("task-1")

    plan.remove_task("task-999")

    assert plan.task_ids == ["task-1"]
