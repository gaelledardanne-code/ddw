"""Slice 1: Goal creation.

Expected behaviour:
- A Goal always has a unique id, assigned automatically.
- `title` is required and cannot be blank.
- `category` and `priority` default to sensible values when omitted, and
  reject values outside their enum.
- `status` always starts as ACTIVE, regardless of what the caller passes in.
- `created_date` is stamped automatically to "now"; `completed_date` starts
  unset.
- `target_date` is optional.
"""

from datetime import date

import pytest

from app.domain.enums import GoalCategory, GoalPriority, GoalStatus
from app.domain.goal import Goal


def test_create_goal_with_minimal_fields_applies_defaults():
    goal = Goal(title="Launch my portfolio")

    assert goal.title == "Launch my portfolio"
    assert goal.description == ""
    assert goal.category == GoalCategory.OTHER
    assert goal.priority == GoalPriority.MEDIUM
    assert goal.status == GoalStatus.ACTIVE
    assert goal.target_date is None
    assert goal.completed_date is None


def test_create_goal_assigns_a_unique_id():
    goal_a = Goal(title="Launch my portfolio")
    goal_b = Goal(title="Get fit")

    assert goal_a.id
    assert goal_b.id
    assert goal_a.id != goal_b.id


def test_create_goal_stamps_created_date_today():
    goal = Goal(title="Launch my portfolio")

    assert goal.created_date == date.today()


@pytest.mark.parametrize("blank_title", ["", "   ", "\t"])
def test_create_goal_rejects_blank_title(blank_title):
    with pytest.raises(ValueError):
        Goal(title=blank_title)


def test_create_goal_with_all_fields():
    target = date(2026, 12, 31)

    goal = Goal(
        title="Launch my portfolio",
        description="Get 3 freelance clients by year end",
        category=GoalCategory.CAREER,
        priority=GoalPriority.HIGH,
        target_date=target,
    )

    assert goal.description == "Get 3 freelance clients by year end"
    assert goal.category == GoalCategory.CAREER
    assert goal.priority == GoalPriority.HIGH
    assert goal.target_date == target


def test_create_goal_ignores_caller_supplied_status():
    goal = Goal(title="Launch my portfolio", status=GoalStatus.COMPLETED)

    assert goal.status == GoalStatus.ACTIVE


def test_create_goal_rejects_invalid_category():
    with pytest.raises(ValueError):
        Goal(title="Launch my portfolio", category="not-a-real-category")


def test_create_goal_rejects_invalid_priority():
    with pytest.raises(ValueError):
        Goal(title="Launch my portfolio", priority="not-a-real-priority")


def test_create_goal_rejects_non_date_target_date():
    with pytest.raises(ValueError):
        Goal(title="Launch my portfolio", target_date="not-a-date")


def test_goal_category_enum_has_expected_members():
    assert {c.value for c in GoalCategory} == {
        "career",
        "creative",
        "health",
        "financial",
        "personal",
        "relationships",
        "learning",
        "other",
    }


def test_goal_priority_enum_has_expected_members():
    assert {p.value for p in GoalPriority} == {"low", "medium", "high", "critical"}


def test_goal_status_enum_has_expected_members():
    assert {s.value for s in GoalStatus} == {"active", "paused", "completed", "abandoned"}
