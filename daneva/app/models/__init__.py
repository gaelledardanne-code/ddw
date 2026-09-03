"""Importing this package registers every ORM model on Base.metadata."""

from app.models.daily_plan import DailyPlanItemModel, DailyPlanModel
from app.models.goal import GoalModel
from app.models.habit import HabitCompletionModel, HabitModel
from app.models.milestone import MilestoneModel
from app.models.task import TaskModel

__all__ = [
    "DailyPlanItemModel",
    "DailyPlanModel",
    "GoalModel",
    "HabitCompletionModel",
    "HabitModel",
    "MilestoneModel",
    "TaskModel",
]
