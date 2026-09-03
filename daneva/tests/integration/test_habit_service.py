"""Slice 10d: HabitService — orchestrates HabitRepository +
HabitCompletionRepository with the domain layer's record_completion /
calculate_streak."""

from datetime import date, timedelta

import pytest

from app.services.habit_service import HabitNotFoundError, HabitService


def days_ago(n: int) -> date:
    return date.today() - timedelta(days=n)


def test_create_saves_and_returns_a_new_habit(db_session):
    service = HabitService(db_session)

    habit = service.create(title="Exercise")

    assert service.get(habit.id) is not None


def test_get_returns_none_for_a_missing_habit(db_session):
    service = HabitService(db_session)

    assert service.get("does-not-exist") is None


def test_list_all_returns_every_created_habit(db_session):
    service = HabitService(db_session)
    service.create(title="Exercise")
    service.create(title="Read")

    assert {h.title for h in service.list_all()} == {"Exercise", "Read"}


def test_complete_records_a_completion_for_today(db_session):
    service = HabitService(db_session)
    habit = service.create(title="Exercise")

    completion = service.complete(habit.id)

    assert completion is not None
    assert completion.completed_date == date.today()


def test_completing_a_habit_twice_the_same_day_is_a_noop(db_session):
    service = HabitService(db_session)
    habit = service.create(title="Exercise")

    first = service.complete(habit.id)
    second = service.complete(habit.id)

    assert first is not None
    assert second is None


def test_get_streak_after_seven_consecutive_days(db_session):
    service = HabitService(db_session)
    habit = service.create(title="Exercise")

    for n in range(6, -1, -1):
        service.complete(habit.id, on_date=days_ago(n))

    assert service.get_streak(habit.id) == 7


def test_get_streak_with_no_completions_is_zero(db_session):
    service = HabitService(db_session)
    habit = service.create(title="Exercise")

    assert service.get_streak(habit.id) == 0


def test_complete_raises_for_a_missing_habit(db_session):
    service = HabitService(db_session)

    with pytest.raises(HabitNotFoundError):
        service.complete("does-not-exist")


def test_get_streak_raises_for_a_missing_habit(db_session):
    service = HabitService(db_session)

    with pytest.raises(HabitNotFoundError):
        service.get_streak("does-not-exist")
