"""Slice 8a: Daily plan creation.

A daily plan is just a dated selection of tasks — no automatic task
selection yet, the user builds it explicitly.
"""

from datetime import date

from app.domain.daily_plan import DailyPlan


def test_create_daily_plan_with_minimal_fields_applies_defaults():
    plan = DailyPlan(plan_date=date(2026, 9, 3))

    assert plan.plan_date == date(2026, 9, 3)
    assert plan.task_ids == []


def test_create_daily_plan_assigns_a_unique_id():
    plan_a = DailyPlan(plan_date=date(2026, 9, 3))
    plan_b = DailyPlan(plan_date=date(2026, 9, 4))

    assert plan_a.id
    assert plan_a.id != plan_b.id
