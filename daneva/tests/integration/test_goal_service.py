"""Slice 10a: GoalService — orchestrates GoalRepository (+ TaskRepository
for progress) with the domain layer. save/get/list/update/lifecycle all
round-trip through a real database; nothing here is new business logic,
just wiring."""

import pytest

from app.domain.enums import GoalPriority, GoalStatus, TaskStatus
from app.domain.task import Task
from app.repositories.task_repository import TaskRepository
from app.services.goal_service import GoalNotFoundError, GoalService


def test_create_saves_and_returns_a_new_goal(db_session):
    service = GoalService(db_session)

    goal = service.create(title="Launch my portfolio")

    assert goal.status == GoalStatus.ACTIVE
    assert service.get(goal.id) is not None


def test_get_returns_none_for_a_missing_goal(db_session):
    service = GoalService(db_session)

    assert service.get("does-not-exist") is None


def test_list_all_returns_every_created_goal(db_session):
    service = GoalService(db_session)
    service.create(title="Launch my portfolio")
    service.create(title="Get fit")

    assert {g.title for g in service.list_all()} == {"Launch my portfolio", "Get fit"}


def test_update_changes_only_the_given_fields(db_session):
    service = GoalService(db_session)
    goal = service.create(title="Launch my portfolio", priority=GoalPriority.LOW)

    updated = service.update(goal.id, title="Launch my new portfolio")

    assert updated.title == "Launch my new portfolio"
    assert updated.priority == GoalPriority.LOW


def test_update_rejects_an_invalid_new_value(db_session):
    service = GoalService(db_session)
    goal = service.create(title="Launch my portfolio")

    with pytest.raises(ValueError):
        service.update(goal.id, title="   ")


def test_update_raises_for_a_missing_goal(db_session):
    service = GoalService(db_session)

    with pytest.raises(GoalNotFoundError):
        service.update("does-not-exist", title="New title")


def test_update_rejects_a_status_change_via_generic_fields(db_session):
    """status must go through pause/resume/complete/abandon — bypassing
    them via update() would skip lifecycle validation and leave
    completed_date unset even though status says COMPLETED."""
    service = GoalService(db_session)
    goal = service.create(title="Launch my portfolio")

    with pytest.raises(ValueError):
        service.update(goal.id, status=GoalStatus.COMPLETED)

    assert service.get(goal.id).status == GoalStatus.ACTIVE


@pytest.mark.parametrize(
    ("action", "expected_status"),
    [
        ("pause", GoalStatus.PAUSED),
        ("complete", GoalStatus.COMPLETED),
        ("abandon", GoalStatus.ABANDONED),
    ],
)
def test_lifecycle_action_persists_the_new_status(db_session, action, expected_status):
    service = GoalService(db_session)
    goal = service.create(title="Launch my portfolio")

    getattr(service, action)(goal.id)

    assert service.get(goal.id).status == expected_status


def test_resume_persists_active_status(db_session):
    service = GoalService(db_session)
    goal = service.create(title="Launch my portfolio")
    service.pause(goal.id)

    service.resume(goal.id)

    assert service.get(goal.id).status == GoalStatus.ACTIVE


@pytest.mark.parametrize("action", ["pause", "resume", "complete", "abandon"])
def test_lifecycle_action_raises_for_a_missing_goal(db_session, action):
    service = GoalService(db_session)

    with pytest.raises(GoalNotFoundError):
        getattr(service, action)("does-not-exist")


def test_delete_removes_the_goal(db_session):
    service = GoalService(db_session)
    goal = service.create(title="Launch my portfolio")

    service.delete(goal.id)

    assert service.get(goal.id) is None


def test_get_progress_computes_from_the_goals_tasks(db_session):
    service = GoalService(db_session)
    goal = service.create(title="Launch my portfolio")

    task_repo = TaskRepository(db_session)
    task_a = Task.create(goal_id=goal.id, title="A")
    task_a.status = TaskStatus.COMPLETED
    task_repo.save(task_a)
    task_repo.save(Task.create(goal_id=goal.id, title="B"))

    progress = service.get_progress(goal.id)

    assert progress.total_tasks == 2
    assert progress.completed_tasks == 1
    assert progress.completion_percentage == 50


def test_get_progress_raises_for_a_missing_goal(db_session):
    service = GoalService(db_session)

    with pytest.raises(GoalNotFoundError):
        service.get_progress("does-not-exist")
