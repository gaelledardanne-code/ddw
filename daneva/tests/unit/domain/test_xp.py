"""Slice 5: XP.

Expected behaviour:

- XP for a completed task is deterministic, based on its priority:
  low -> 10, medium -> 20, high -> 40 (critical extends the same
  doubling pattern -> 80; not specified explicitly but the system is
  meant to be simple and deterministic, so every priority must resolve
  to *some* fixed value).
- Completing a task marks it COMPLETED, stamps completed_at, and
  returns the XP earned.
- Completing an already-completed task is a no-op: it must not award
  XP a second time, and must not touch the original completed_at.
"""

from datetime import datetime

import pytest

from app.domain.enums import TaskPriority
from app.domain.task import Task
from app.domain.xp import complete_task, xp_for_priority


def make_task(priority: TaskPriority) -> Task:
    return Task(goal_id="goal-1", title="Some task", priority=priority)


def test_xp_for_low_priority():
    assert xp_for_priority(TaskPriority.LOW) == 10


def test_xp_for_medium_priority():
    assert xp_for_priority(TaskPriority.MEDIUM) == 20


def test_xp_for_high_priority():
    assert xp_for_priority(TaskPriority.HIGH) == 40


def test_xp_for_critical_priority():
    assert xp_for_priority(TaskPriority.CRITICAL) == 80


@pytest.mark.parametrize(
    ("priority", "expected_xp"),
    [
        (TaskPriority.LOW, 10),
        (TaskPriority.MEDIUM, 20),
        (TaskPriority.HIGH, 40),
        (TaskPriority.CRITICAL, 80),
    ],
)
def test_complete_task_awards_xp_for_its_priority(priority, expected_xp):
    task = make_task(priority)

    xp_awarded = complete_task(task)

    assert xp_awarded == expected_xp
    assert task.status == "completed"
    assert isinstance(task.completed_at, datetime)


def test_complete_task_twice_does_not_award_xp_twice():
    task = make_task(TaskPriority.HIGH)

    first_award = complete_task(task)
    first_completed_at = task.completed_at
    second_award = complete_task(task)

    assert first_award == 40
    assert second_award == 0
    assert task.completed_at == first_completed_at
