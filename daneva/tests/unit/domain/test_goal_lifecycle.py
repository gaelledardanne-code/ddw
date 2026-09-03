"""Slice 2: Goal lifecycle.

Expected behaviour — the only legal transitions are:

    active  --pause-->    paused
    paused  --resume-->   active
    active  --complete--> completed
    paused  --complete--> completed
    active  --abandon-->  abandoned
    paused  --abandon-->  abandoned

`completed` and `abandoned` are terminal: no further transition is
allowed from either. Completing a goal stamps `completed_date` to today;
abandoning one does not (the goal was never finished).
"""

from datetime import date

import pytest

from app.domain.enums import GoalStatus
from app.domain.goal import Goal, GoalLifecycleError


def make_goal(status: GoalStatus = GoalStatus.ACTIVE) -> Goal:
    goal = Goal(title="Launch my portfolio")
    goal.status = status
    return goal


def test_pause_active_goal_sets_status_paused():
    goal = make_goal(GoalStatus.ACTIVE)

    goal.pause()

    assert goal.status == GoalStatus.PAUSED


@pytest.mark.parametrize("status", [GoalStatus.PAUSED, GoalStatus.COMPLETED, GoalStatus.ABANDONED])
def test_pause_non_active_goal_raises(status):
    goal = make_goal(status)

    with pytest.raises(GoalLifecycleError):
        goal.pause()

    assert goal.status == status


def test_resume_paused_goal_sets_status_active():
    goal = make_goal(GoalStatus.PAUSED)

    goal.resume()

    assert goal.status == GoalStatus.ACTIVE


@pytest.mark.parametrize("status", [GoalStatus.ACTIVE, GoalStatus.COMPLETED, GoalStatus.ABANDONED])
def test_resume_non_paused_goal_raises(status):
    goal = make_goal(status)

    with pytest.raises(GoalLifecycleError):
        goal.resume()

    assert goal.status == status


@pytest.mark.parametrize("status", [GoalStatus.ACTIVE, GoalStatus.PAUSED])
def test_complete_goal_sets_status_and_completed_date(status):
    goal = make_goal(status)

    goal.complete()

    assert goal.status == GoalStatus.COMPLETED
    assert goal.completed_date == date.today()


@pytest.mark.parametrize("status", [GoalStatus.COMPLETED, GoalStatus.ABANDONED])
def test_complete_terminal_goal_raises(status):
    goal = make_goal(status)

    with pytest.raises(GoalLifecycleError):
        goal.complete()

    assert goal.status == status


@pytest.mark.parametrize("status", [GoalStatus.ACTIVE, GoalStatus.PAUSED])
def test_abandon_goal_sets_status_abandoned(status):
    goal = make_goal(status)

    goal.abandon()

    assert goal.status == GoalStatus.ABANDONED


@pytest.mark.parametrize("status", [GoalStatus.ACTIVE, GoalStatus.PAUSED])
def test_abandon_does_not_set_completed_date(status):
    goal = make_goal(status)

    goal.abandon()

    assert goal.completed_date is None


@pytest.mark.parametrize("status", [GoalStatus.COMPLETED, GoalStatus.ABANDONED])
def test_abandon_terminal_goal_raises(status):
    goal = make_goal(status)

    with pytest.raises(GoalLifecycleError):
        goal.abandon()

    assert goal.status == status
