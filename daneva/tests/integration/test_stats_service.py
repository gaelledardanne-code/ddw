"""Slice 10f: StatsService — aggregates goals/tasks/habits into the
counts evaluate_achievements() needs, and returns which are unlocked.
This is the last piece of use-case orchestration: no new business rules,
just gathering state for the domain's achievement thresholds."""

from datetime import date, timedelta

from app.domain.achievements import AchievementKey
from app.domain.enums import TaskPriority
from app.services.goal_service import GoalService
from app.services.habit_service import HabitService
from app.services.stats_service import StatsService
from app.services.task_service import TaskService


def days_ago(n: int) -> date:
    return date.today() - timedelta(days=n)


def test_stats_of_a_fresh_system_has_zero_counts_and_no_achievements(db_session):
    stats = StatsService(db_session).compute()

    assert stats.total_xp == 0
    assert stats.tasks_completed == 0
    assert stats.goals_completed == 0
    assert stats.longest_streak == 0
    assert stats.achievements == []


def test_stats_reflect_completed_tasks_and_xp(db_session):
    goal = GoalService(db_session).create(title="Launch my portfolio")
    task_service = TaskService(db_session)
    task_a = task_service.create(goal_id=goal.id, title="A", priority=TaskPriority.MEDIUM)
    task_b = task_service.create(goal_id=goal.id, title="B", priority=TaskPriority.LOW)
    task_service.complete(task_a.id)
    task_service.complete(task_b.id)

    stats = StatsService(db_session).compute()

    assert stats.tasks_completed == 2
    assert stats.total_xp == 30
    assert AchievementKey.FIRST_TASK in {a.key for a in stats.achievements}


def test_stats_reflect_completed_goals(db_session):
    goal_service = GoalService(db_session)
    goal = goal_service.create(title="Launch my portfolio")
    goal_service.complete(goal.id)
    goal_service.create(title="Get fit")  # left active

    stats = StatsService(db_session).compute()

    assert stats.goals_completed == 1
    assert AchievementKey.FIRST_GOAL_COMPLETED in {a.key for a in stats.achievements}


def test_stats_reflect_the_longest_habit_streak(db_session):
    habit_service = HabitService(db_session)
    habit_a = habit_service.create(title="Exercise")
    habit_b = habit_service.create(title="Read")
    for n in range(6, -1, -1):
        habit_service.complete(habit_a.id, on_date=days_ago(n))
    habit_service.complete(habit_b.id, on_date=days_ago(0))

    stats = StatsService(db_session).compute()

    assert stats.longest_streak == 7
    assert AchievementKey.SEVEN_DAY_STREAK in {a.key for a in stats.achievements}


def test_stats_unlock_hundred_xp_achievement(db_session):
    goal = GoalService(db_session).create(title="Launch my portfolio")
    task_service = TaskService(db_session)
    for _ in range(3):
        task = task_service.create(goal_id=goal.id, title="A", priority=TaskPriority.HIGH)
        task_service.complete(task.id)

    stats = StatsService(db_session).compute()

    assert stats.total_xp == 120
    assert AchievementKey.HUNDRED_XP in {a.key for a in stats.achievements}
