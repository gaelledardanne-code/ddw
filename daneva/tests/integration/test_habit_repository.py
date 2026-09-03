"""Slice 9c: Habit persistence, including the Goal -> Habits relationship
(cascade delete) and an optional, un-linked habit."""

from app.domain.goal import Goal
from app.domain.habit import Habit
from app.repositories.goal_repository import GoalRepository
from app.repositories.habit_repository import HabitRepository


def test_save_and_get_roundtrips_all_fields(db_session):
    goal_repo = GoalRepository(db_session)
    goal = Goal.create(title="Get fit")
    goal_repo.save(goal)

    habit_repo = HabitRepository(db_session)
    habit = Habit(goal_id=goal.id, title="Exercise", description="30 minutes, any kind")

    habit_repo.save(habit)
    fetched = habit_repo.get(habit.id)

    assert fetched is not None
    assert fetched.id == habit.id
    assert fetched.goal_id == goal.id
    assert fetched.title == "Exercise"
    assert fetched.description == "30 minutes, any kind"
    assert fetched.created_date == habit.created_date


def test_save_roundtrips_a_habit_with_no_goal(db_session):
    habit_repo = HabitRepository(db_session)
    habit = Habit(title="Journal")

    habit_repo.save(habit)
    fetched = habit_repo.get(habit.id)

    assert fetched.goal_id is None


def test_get_returns_none_for_a_missing_habit(db_session):
    repo = HabitRepository(db_session)

    assert repo.get("does-not-exist") is None


def test_list_by_goal_returns_only_that_goals_habits(db_session):
    goal_repo = GoalRepository(db_session)
    goal_a = Goal.create(title="Get fit")
    goal_repo.save(goal_a)

    habit_repo = HabitRepository(db_session)
    habit_repo.save(Habit(goal_id=goal_a.id, title="Exercise"))
    habit_repo.save(Habit(title="Journal"))  # not linked to any goal

    habits = habit_repo.list_by_goal(goal_a.id)

    assert {h.title for h in habits} == {"Exercise"}


def test_deleting_a_goal_cascades_to_its_habits(db_session):
    goal_repo = GoalRepository(db_session)
    goal = Goal.create(title="Get fit")
    goal_repo.save(goal)

    habit_repo = HabitRepository(db_session)
    habit = Habit(goal_id=goal.id, title="Exercise")
    habit_repo.save(habit)

    goal_repo.delete(goal.id)

    assert habit_repo.get(habit.id) is None
