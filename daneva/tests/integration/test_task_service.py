"""Slice 10b: TaskService — orchestrates TaskRepository with the domain
layer, including the completion/XP flow (repository fetch -> domain XP
calc -> repository save, idempotently)."""

import pytest

from app.domain.enums import TaskPriority, TaskStatus
from app.services.goal_service import GoalService
from app.services.task_service import TaskNotFoundError, TaskService


def make_goal(db_session):
    return GoalService(db_session).create(title="Launch my portfolio")


def test_create_saves_and_returns_a_new_task(db_session):
    goal = make_goal(db_session)
    service = TaskService(db_session)

    task = service.create(goal_id=goal.id, title="Write landing page copy")

    assert task.status == TaskStatus.TODO
    assert service.get(task.id) is not None


def test_get_returns_none_for_a_missing_task(db_session):
    service = TaskService(db_session)

    assert service.get("does-not-exist") is None


def test_list_by_goal_returns_that_goals_tasks(db_session):
    goal = make_goal(db_session)
    service = TaskService(db_session)
    service.create(goal_id=goal.id, title="A")
    service.create(goal_id=goal.id, title="B")

    assert {t.title for t in service.list_by_goal(goal.id)} == {"A", "B"}


def test_update_changes_only_the_given_fields(db_session):
    goal = make_goal(db_session)
    service = TaskService(db_session)
    task = service.create(goal_id=goal.id, title="A", priority=TaskPriority.LOW)

    updated = service.update(task.id, title="A (revised)")

    assert updated.title == "A (revised)"
    assert updated.priority == TaskPriority.LOW


def test_update_raises_for_a_missing_task(db_session):
    service = TaskService(db_session)

    with pytest.raises(TaskNotFoundError):
        service.update("does-not-exist", title="New title")


def test_update_rejects_a_status_change_via_generic_fields(db_session):
    """status must go through complete() — bypassing it via update()
    would skip XP awarding and leave completed_at unset."""
    goal = make_goal(db_session)
    service = TaskService(db_session)
    task = service.create(goal_id=goal.id, title="A")

    with pytest.raises(ValueError):
        service.update(task.id, status=TaskStatus.COMPLETED)

    assert service.get(task.id).status == TaskStatus.TODO


def test_complete_awards_xp_and_persists_completion(db_session):
    goal = make_goal(db_session)
    service = TaskService(db_session)
    task = service.create(goal_id=goal.id, title="A", priority=TaskPriority.MEDIUM)

    xp_awarded = service.complete(task.id)

    assert xp_awarded == 20
    fetched = service.get(task.id)
    assert fetched.status == TaskStatus.COMPLETED
    assert fetched.completed_at is not None


def test_completing_a_task_twice_does_not_award_xp_twice(db_session):
    goal = make_goal(db_session)
    service = TaskService(db_session)
    task = service.create(goal_id=goal.id, title="A", priority=TaskPriority.HIGH)

    first = service.complete(task.id)
    second = service.complete(task.id)

    assert first == 40
    assert second == 0


def test_complete_raises_for_a_missing_task(db_session):
    service = TaskService(db_session)

    with pytest.raises(TaskNotFoundError):
        service.complete("does-not-exist")
