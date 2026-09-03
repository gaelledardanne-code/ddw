"""Achievements: a small, fixed set unlocked purely by thresholds on
current state. Nothing here is a mutable "unlocked" flag — call
evaluate_achievements() with the current stats whenever you need to know
what's unlocked, and it always answers the same way for the same input.
"""

from enum import StrEnum

from pydantic import BaseModel


class AchievementKey(StrEnum):
    FIRST_TASK = "first_task"
    HUNDRED_XP = "100_xp"
    SEVEN_DAY_STREAK = "7_day_streak"
    FIRST_GOAL_COMPLETED = "first_goal_completed"


class Achievement(BaseModel):
    key: AchievementKey
    name: str
    description: str


_DEFINITIONS: dict[AchievementKey, Achievement] = {
    AchievementKey.FIRST_TASK: Achievement(
        key=AchievementKey.FIRST_TASK,
        name="First Task",
        description="Complete your first task.",
    ),
    AchievementKey.HUNDRED_XP: Achievement(
        key=AchievementKey.HUNDRED_XP,
        name="100 XP",
        description="Earn 100 total XP.",
    ),
    AchievementKey.SEVEN_DAY_STREAK: Achievement(
        key=AchievementKey.SEVEN_DAY_STREAK,
        name="7 Day Streak",
        description="Keep a habit streak going for 7 days.",
    ),
    AchievementKey.FIRST_GOAL_COMPLETED: Achievement(
        key=AchievementKey.FIRST_GOAL_COMPLETED,
        name="First Goal Completed",
        description="Complete your first goal.",
    ),
}


def evaluate_achievements(
    *,
    tasks_completed: int = 0,
    total_xp: int = 0,
    longest_streak: int = 0,
    goals_completed: int = 0,
) -> list[Achievement]:
    unlocked: list[Achievement] = []
    if tasks_completed >= 1:
        unlocked.append(_DEFINITIONS[AchievementKey.FIRST_TASK])
    if total_xp >= 100:
        unlocked.append(_DEFINITIONS[AchievementKey.HUNDRED_XP])
    if longest_streak >= 7:
        unlocked.append(_DEFINITIONS[AchievementKey.SEVEN_DAY_STREAK])
    if goals_completed >= 1:
        unlocked.append(_DEFINITIONS[AchievementKey.FIRST_GOAL_COMPLETED])
    return unlocked
