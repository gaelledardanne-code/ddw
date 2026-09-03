"""Slice 6c: streak calculation.

Expected behaviour: the current streak is the number of consecutive
calendar days in the trailing run ending at the most recent completion
date. Duplicate dates don't inflate it, and a gap resets the count to
just the run after the gap.
"""

from datetime import date, timedelta

from app.domain.habit import calculate_streak


def days_ago(n: int) -> date:
    return date.today() - timedelta(days=n)


def test_streak_with_no_completions_is_zero():
    assert calculate_streak([]) == 0


def test_first_completion_gives_a_streak_of_one():
    assert calculate_streak([days_ago(0)]) == 1


def test_consecutive_days_increase_the_streak():
    dates = [days_ago(4), days_ago(3), days_ago(2), days_ago(1), days_ago(0)]

    assert calculate_streak(dates) == 5


def test_broken_streak_only_counts_the_trailing_run():
    # A gap two days back: only the last two consecutive days count.
    dates = [days_ago(10), days_ago(9), days_ago(1), days_ago(0)]

    assert calculate_streak(dates) == 2


def test_duplicate_same_day_completion_does_not_inflate_streak():
    dates = [days_ago(1), days_ago(1), days_ago(0)]

    assert calculate_streak(dates) == 2


def test_seven_consecutive_days_gives_a_streak_of_seven():
    dates = [days_ago(n) for n in range(6, -1, -1)]

    assert calculate_streak(dates) == 7
