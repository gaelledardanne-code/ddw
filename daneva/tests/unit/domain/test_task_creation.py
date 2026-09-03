"""Slice 3b: Task creation.

Expected behaviour:
- A Task always belongs to a goal (`goal_id` required, cannot be blank).
- It may optionally belong to a milestone within that goal
  (`milestone_id`); when absent, the task belongs directly to the goal.
- `title` is required and cannot be blank.
- `status` always starts TODO — `Task.create()` doesn't even accept a
  status argument. (The plain `Task(...)` constructor still accepts any
  status/completed_at; that's for reconstructing an existing task from
  storage, not for creating a new one.)
- `priority` defaults to MEDIUM, `energy_level` defaults to MEDIUM.
- `estimated_minutes` is optional but must be positive when given.
- `due_date` is optional and unset by default.
"""

from datetime import date, datetime

import pytest

from app.domain.enums import EnergyLevel, TaskPriority, TaskStatus
from app.domain.task import Task


def test_create_task_with_minimal_fields_applies_defaults():
    task = Task.create(goal_id="goal-1", title="Write landing page copy")

    assert task.goal_id == "goal-1"
    assert task.milestone_id is None
    assert task.title == "Write landing page copy"
    assert task.description == ""
    assert task.status == TaskStatus.TODO
    assert task.priority == TaskPriority.MEDIUM
    assert task.energy_level == EnergyLevel.MEDIUM
    assert task.estimated_minutes is None
    assert task.due_date is None
    assert task.completed_at is None


def test_create_task_assigns_a_unique_id():
    task_a = Task.create(goal_id="goal-1", title="Write landing page copy")
    task_b = Task.create(goal_id="goal-1", title="Pick a color palette")

    assert task_a.id
    assert task_a.id != task_b.id


def test_create_task_can_belong_directly_to_a_goal():
    task = Task.create(goal_id="goal-1", title="Write landing page copy")

    assert task.goal_id == "goal-1"
    assert task.milestone_id is None


def test_create_task_can_belong_to_a_milestone_within_a_goal():
    task = Task.create(goal_id="goal-1", milestone_id="milestone-1", title="Build website")

    assert task.goal_id == "goal-1"
    assert task.milestone_id == "milestone-1"


@pytest.mark.parametrize("blank_title", ["", "   ", "\t"])
def test_create_task_rejects_blank_title(blank_title):
    with pytest.raises(ValueError):
        Task.create(goal_id="goal-1", title=blank_title)


@pytest.mark.parametrize("blank_goal_id", ["", "   "])
def test_create_task_rejects_blank_goal_id(blank_goal_id):
    with pytest.raises(ValueError):
        Task.create(goal_id=blank_goal_id, title="Write landing page copy")


def test_create_task_requires_goal_id():
    with pytest.raises(ValueError):
        Task(title="Write landing page copy")


def test_create_task_does_not_accept_a_status_argument():
    with pytest.raises(TypeError):
        Task.create(goal_id="goal-1", title="Write landing page copy", status=TaskStatus.COMPLETED)


def test_create_task_rejects_invalid_priority():
    with pytest.raises(ValueError):
        Task.create(goal_id="goal-1", title="Write landing page copy", priority="urgent")


def test_create_task_rejects_invalid_energy_level():
    with pytest.raises(ValueError):
        Task.create(goal_id="goal-1", title="Write landing page copy", energy_level="extreme")


@pytest.mark.parametrize("bad_minutes", [0, -1, -30])
def test_create_task_rejects_non_positive_estimated_minutes(bad_minutes):
    with pytest.raises(ValueError):
        Task.create(
            goal_id="goal-1", title="Write landing page copy", estimated_minutes=bad_minutes
        )


def test_create_task_accepts_positive_estimated_minutes():
    task = Task.create(goal_id="goal-1", title="Write landing page copy", estimated_minutes=45)

    assert task.estimated_minutes == 45


def test_create_task_with_all_fields():
    due = date(2026, 10, 1)

    task = Task.create(
        goal_id="goal-1",
        milestone_id="milestone-1",
        title="Build website",
        description="Static site, no CMS",
        priority=TaskPriority.HIGH,
        energy_level=EnergyLevel.HIGH,
        estimated_minutes=120,
        due_date=due,
    )

    assert task.description == "Static site, no CMS"
    assert task.priority == TaskPriority.HIGH
    assert task.energy_level == EnergyLevel.HIGH
    assert task.estimated_minutes == 120
    assert task.due_date == due


def test_task_reconstruction_accepts_any_persisted_status_and_completed_at():
    """The plain constructor (unlike .create()) accepts any status and
    completed_at — this is what a repository uses to rebuild a Task
    loaded from storage."""
    completed = datetime(2026, 9, 3, 14, 30)

    task = Task(
        goal_id="goal-1",
        title="Write landing page copy",
        status=TaskStatus.COMPLETED,
        completed_at=completed,
    )

    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at == completed


def test_task_status_enum_has_expected_members():
    assert {s.value for s in TaskStatus} == {"todo", "in_progress", "completed", "cancelled"}


def test_task_priority_enum_has_expected_members():
    assert {p.value for p in TaskPriority} == {"low", "medium", "high", "critical"}


def test_energy_level_enum_has_expected_members():
    assert {e.value for e in EnergyLevel} == {"low", "medium", "high"}
