"""Slice 10c: MilestoneService — orchestrates MilestoneRepository with
the domain layer."""

from app.services.goal_service import GoalService
from app.services.milestone_service import MilestoneService


def make_goal(db_session):
    return GoalService(db_session).create(title="Launch my portfolio")


def test_create_saves_and_returns_a_new_milestone(db_session):
    goal = make_goal(db_session)
    service = MilestoneService(db_session)

    milestone = service.create(goal_id=goal.id, title="Define positioning")

    assert service.get(milestone.id) is not None


def test_get_returns_none_for_a_missing_milestone(db_session):
    service = MilestoneService(db_session)

    assert service.get("does-not-exist") is None


def test_list_by_goal_returns_that_goals_milestones(db_session):
    goal = make_goal(db_session)
    service = MilestoneService(db_session)
    service.create(goal_id=goal.id, title="Define positioning")
    service.create(goal_id=goal.id, title="Build website")

    titles = {m.title for m in service.list_by_goal(goal.id)}
    assert titles == {"Define positioning", "Build website"}
