"""Slice 9c: HabitCompletion persistence.

The domain layer already prevents a duplicate same-day completion at the
service level (record_completion() checks existing completions before
creating one). This adds a DB-level unique constraint on
(habit_id, completed_date) as a second line of defense — an integration
test for real database behaviour, per the test pyramid.
"""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.domain.habit import Habit, HabitCompletion
from app.repositories.habit_completion_repository import HabitCompletionRepository
from app.repositories.habit_repository import HabitRepository


def make_habit(db_session) -> Habit:
    habit_repo = HabitRepository(db_session)
    habit = Habit(title="Exercise")
    habit_repo.save(habit)
    return habit


def test_save_and_get_roundtrips_all_fields(db_session):
    habit = make_habit(db_session)
    completion_repo = HabitCompletionRepository(db_session)
    completion = HabitCompletion(habit_id=habit.id, completed_date=date(2026, 9, 3))

    completion_repo.save(completion)
    fetched = completion_repo.get(completion.id)

    assert fetched is not None
    assert fetched.habit_id == habit.id
    assert fetched.completed_date == date(2026, 9, 3)


def test_list_by_habit_returns_only_that_habits_completions(db_session):
    habit_a = make_habit(db_session)
    habit_b = Habit(title="Read")
    HabitRepository(db_session).save(habit_b)

    completion_repo = HabitCompletionRepository(db_session)
    completion_repo.save(HabitCompletion(habit_id=habit_a.id, completed_date=date(2026, 9, 1)))
    completion_repo.save(HabitCompletion(habit_id=habit_a.id, completed_date=date(2026, 9, 2)))
    completion_repo.save(HabitCompletion(habit_id=habit_b.id, completed_date=date(2026, 9, 1)))

    completions = completion_repo.list_by_habit(habit_a.id)

    assert {c.completed_date for c in completions} == {date(2026, 9, 1), date(2026, 9, 2)}


def test_duplicate_same_day_completion_violates_the_database_constraint(db_session):
    habit = make_habit(db_session)
    completion_repo = HabitCompletionRepository(db_session)
    completion_repo.save(HabitCompletion(habit_id=habit.id, completed_date=date(2026, 9, 3)))

    with pytest.raises(IntegrityError):
        completion_repo.save(HabitCompletion(habit_id=habit.id, completed_date=date(2026, 9, 3)))


def test_deleting_a_habit_cascades_to_its_completions(db_session):
    habit = make_habit(db_session)
    completion_repo = HabitCompletionRepository(db_session)
    completion = HabitCompletion(habit_id=habit.id, completed_date=date(2026, 9, 3))
    completion_repo.save(completion)

    HabitRepository(db_session).delete(habit.id)

    assert completion_repo.get(completion.id) is None
