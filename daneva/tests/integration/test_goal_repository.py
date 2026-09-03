"""Slice 9a: Goal persistence.

Expected behaviour: a GoalRepository backed by a real SQLite database
round-trips a Goal's full field set, including enums and dates, and
supports the basic CRUD a service layer needs.
"""

from datetime import date

from app.domain.enums import GoalCategory, GoalPriority, GoalStatus
from app.domain.goal import Goal
from app.repositories.goal_repository import GoalRepository


def test_save_and_get_roundtrips_all_fields(db_session):
    repo = GoalRepository(db_session)
    goal = Goal(
        title="Launch my portfolio",
        description="Get 3 freelance clients",
        category=GoalCategory.CAREER,
        priority=GoalPriority.HIGH,
        target_date=date(2026, 12, 31),
    )

    repo.save(goal)
    fetched = repo.get(goal.id)

    assert fetched is not None
    assert fetched.id == goal.id
    assert fetched.title == "Launch my portfolio"
    assert fetched.description == "Get 3 freelance clients"
    assert fetched.category == GoalCategory.CAREER
    assert fetched.priority == GoalPriority.HIGH
    assert fetched.status == GoalStatus.ACTIVE
    assert fetched.target_date == date(2026, 12, 31)
    assert fetched.created_date == goal.created_date
    assert fetched.completed_date is None


def test_get_returns_none_for_a_missing_goal(db_session):
    repo = GoalRepository(db_session)

    assert repo.get("does-not-exist") is None


def test_list_all_returns_every_saved_goal(db_session):
    repo = GoalRepository(db_session)
    repo.save(Goal(title="Launch my portfolio"))
    repo.save(Goal(title="Get fit"))

    goals = repo.list_all()

    assert {g.title for g in goals} == {"Launch my portfolio", "Get fit"}


def test_list_all_is_empty_when_nothing_saved(db_session):
    repo = GoalRepository(db_session)

    assert repo.list_all() == []


def test_save_again_updates_the_existing_goal(db_session):
    repo = GoalRepository(db_session)
    goal = Goal(title="Launch my portfolio")
    repo.save(goal)

    goal.pause()
    repo.save(goal)

    fetched = repo.get(goal.id)
    assert fetched.status == GoalStatus.PAUSED
    assert len(repo.list_all()) == 1


def test_delete_removes_the_goal(db_session):
    repo = GoalRepository(db_session)
    goal = Goal(title="Launch my portfolio")
    repo.save(goal)

    repo.delete(goal.id)

    assert repo.get(goal.id) is None
