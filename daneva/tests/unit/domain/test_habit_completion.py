"""Slice 6b: recording habit completions.

Expected behaviour:
- Recording a completion for a habit creates a HabitCompletion, dated
  today by default or an explicit date if given.
- Recording a second completion for the same habit on the same day is
  a no-op (returns None) — a habit can only be "done" once per day.
- Completing on a different day is allowed as usual.
"""

from datetime import date, timedelta

import pytest

from app.domain.habit import HabitCompletion, record_completion


def test_record_completion_defaults_to_today():
    completion = record_completion("habit-1", existing_completions=[])

    assert completion is not None
    assert completion.habit_id == "habit-1"
    assert completion.completed_date == date.today()


def test_record_completion_for_a_given_date():
    target = date(2026, 1, 5)

    completion = record_completion("habit-1", existing_completions=[], on_date=target)

    assert completion is not None
    assert completion.completed_date == target


def test_record_completion_rejects_a_second_completion_on_the_same_day():
    target = date(2026, 1, 5)
    existing = [HabitCompletion(habit_id="habit-1", completed_date=target)]

    completion = record_completion("habit-1", existing_completions=existing, on_date=target)

    assert completion is None


def test_record_completion_allows_a_different_habit_on_the_same_day():
    target = date(2026, 1, 5)
    existing = [HabitCompletion(habit_id="habit-1", completed_date=target)]

    completion = record_completion("habit-2", existing_completions=existing, on_date=target)

    assert completion is not None


def test_record_completion_allows_the_next_day():
    target = date(2026, 1, 5)
    existing = [HabitCompletion(habit_id="habit-1", completed_date=target)]

    completion = record_completion(
        "habit-1", existing_completions=existing, on_date=target + timedelta(days=1)
    )

    assert completion is not None


@pytest.mark.parametrize("blank_habit_id", ["", "   "])
def test_habit_completion_rejects_a_blank_habit_id(blank_habit_id):
    with pytest.raises(ValueError):
        HabitCompletion(habit_id=blank_habit_id)
