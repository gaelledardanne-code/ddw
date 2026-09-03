"""Slice 9b: Milestone persistence, including the Goal -> Milestones
relationship (cascade delete)."""

from app.domain.goal import Goal
from app.domain.milestone import Milestone
from app.repositories.goal_repository import GoalRepository
from app.repositories.milestone_repository import MilestoneRepository


def test_save_and_get_roundtrips_all_fields(db_session):
    goal_repo = GoalRepository(db_session)
    goal = Goal.create(title="Launch my portfolio")
    goal_repo.save(goal)

    milestone_repo = MilestoneRepository(db_session)
    milestone = Milestone(goal_id=goal.id, title="Define positioning", description="Who it's for")

    milestone_repo.save(milestone)
    fetched = milestone_repo.get(milestone.id)

    assert fetched is not None
    assert fetched.id == milestone.id
    assert fetched.goal_id == goal.id
    assert fetched.title == "Define positioning"
    assert fetched.description == "Who it's for"
    assert fetched.created_date == milestone.created_date


def test_get_returns_none_for_a_missing_milestone(db_session):
    repo = MilestoneRepository(db_session)

    assert repo.get("does-not-exist") is None


def test_list_by_goal_returns_only_that_goals_milestones(db_session):
    goal_repo = GoalRepository(db_session)
    goal_a = Goal.create(title="Launch my portfolio")
    goal_b = Goal.create(title="Get fit")
    goal_repo.save(goal_a)
    goal_repo.save(goal_b)

    milestone_repo = MilestoneRepository(db_session)
    milestone_repo.save(Milestone(goal_id=goal_a.id, title="Define positioning"))
    milestone_repo.save(Milestone(goal_id=goal_a.id, title="Build website"))
    milestone_repo.save(Milestone(goal_id=goal_b.id, title="Run 5k"))

    milestones = milestone_repo.list_by_goal(goal_a.id)

    assert {m.title for m in milestones} == {"Define positioning", "Build website"}


def test_deleting_a_goal_cascades_to_its_milestones(db_session):
    goal_repo = GoalRepository(db_session)
    goal = Goal.create(title="Launch my portfolio")
    goal_repo.save(goal)

    milestone_repo = MilestoneRepository(db_session)
    milestone = Milestone(goal_id=goal.id, title="Define positioning")
    milestone_repo.save(milestone)

    goal_repo.delete(goal.id)

    assert milestone_repo.get(milestone.id) is None
