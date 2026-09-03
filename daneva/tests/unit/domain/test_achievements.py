"""Slice 7: Achievements.

Four fixed achievements, each unlocked purely by a threshold on current
state — nothing is stored as a mutable "unlocked" flag. Calling
`evaluate_achievements()` with the same stats always returns the same
result, so "unlocking" is just re-evaluating, safe to call as often as
needed:

- First Task           -> at least 1 completed task
- 100 XP                -> at least 100 total XP
- 7 Day Streak          -> a habit streak of at least 7
- First Goal Completed  -> at least 1 completed goal
"""

from app.domain.achievements import AchievementKey, evaluate_achievements


def unlocked_keys(**stats) -> set[AchievementKey]:
    return {achievement.key for achievement in evaluate_achievements(**stats)}


def test_no_achievements_unlocked_with_zero_stats():
    assert evaluate_achievements() == []


def test_first_task_unlocks_after_one_completed_task():
    assert AchievementKey.FIRST_TASK in unlocked_keys(tasks_completed=1)


def test_first_task_stays_locked_with_zero_completed_tasks():
    assert AchievementKey.FIRST_TASK not in unlocked_keys(tasks_completed=0)


def test_hundred_xp_unlocks_at_100_xp():
    assert AchievementKey.HUNDRED_XP in unlocked_keys(total_xp=100)


def test_hundred_xp_stays_locked_just_below_threshold():
    assert AchievementKey.HUNDRED_XP not in unlocked_keys(total_xp=99)


def test_hundred_xp_stays_unlocked_above_threshold():
    assert AchievementKey.HUNDRED_XP in unlocked_keys(total_xp=250)


def test_seven_day_streak_unlocks_at_streak_of_seven():
    assert AchievementKey.SEVEN_DAY_STREAK in unlocked_keys(longest_streak=7)


def test_seven_day_streak_stays_locked_just_below_threshold():
    assert AchievementKey.SEVEN_DAY_STREAK not in unlocked_keys(longest_streak=6)


def test_first_goal_completed_unlocks_after_one_completed_goal():
    assert AchievementKey.FIRST_GOAL_COMPLETED in unlocked_keys(goals_completed=1)


def test_first_goal_completed_stays_locked_with_zero_completed_goals():
    assert AchievementKey.FIRST_GOAL_COMPLETED not in unlocked_keys(goals_completed=0)


def test_multiple_achievements_unlock_together():
    keys = unlocked_keys(
        tasks_completed=5,
        total_xp=150,
        longest_streak=10,
        goals_completed=2,
    )

    assert keys == {
        AchievementKey.FIRST_TASK,
        AchievementKey.HUNDRED_XP,
        AchievementKey.SEVEN_DAY_STREAK,
        AchievementKey.FIRST_GOAL_COMPLETED,
    }


def test_achievement_objects_carry_a_name_and_description():
    achievements = evaluate_achievements(tasks_completed=1)

    achievement = achievements[0]
    assert achievement.key == AchievementKey.FIRST_TASK
    assert achievement.name
    assert achievement.description


def test_evaluate_achievements_is_pure_and_repeatable():
    first_call = evaluate_achievements(tasks_completed=1, total_xp=100)
    second_call = evaluate_achievements(tasks_completed=1, total_xp=100)

    assert first_call == second_call
