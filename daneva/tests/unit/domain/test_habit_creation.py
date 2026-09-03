"""Slice 6a: Habit creation.

Expected behaviour:
- `title` is required and cannot be blank, same rule as Goal/Task/
  Milestone.
- A habit may optionally be linked to a goal it contributes to
  (`goal_id`); when omitted it's just a personal habit.
- `id` is unique and auto-generated; `created_date` is stamped today.
"""

from datetime import date

import pytest

from app.domain.habit import Habit


def test_create_habit_with_minimal_fields_applies_defaults():
    habit = Habit(title="Exercise")

    assert habit.title == "Exercise"
    assert habit.description == ""
    assert habit.goal_id is None
    assert habit.created_date == date.today()


def test_create_habit_assigns_a_unique_id():
    habit_a = Habit(title="Exercise")
    habit_b = Habit(title="Read")

    assert habit_a.id
    assert habit_a.id != habit_b.id


def test_create_habit_can_be_linked_to_a_goal():
    habit = Habit(title="Practice guitar", goal_id="goal-1")

    assert habit.goal_id == "goal-1"


@pytest.mark.parametrize("blank_title", ["", "   ", "\t"])
def test_create_habit_rejects_blank_title(blank_title):
    with pytest.raises(ValueError):
        Habit(title=blank_title)
