"""StatsService: gathers the counts evaluate_achievements() needs from
goals/tasks/habits, and reports total XP alongside them. No new business
rules — the thresholds themselves still live in app.domain.achievements
and app.domain.xp; this only aggregates state for them."""

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.achievements import Achievement, evaluate_achievements
from app.domain.enums import GoalStatus, TaskStatus
from app.domain.habit import calculate_streak
from app.domain.xp import xp_for_priority
from app.repositories.goal_repository import GoalRepository
from app.repositories.habit_completion_repository import HabitCompletionRepository
from app.repositories.habit_repository import HabitRepository
from app.repositories.task_repository import TaskRepository


class Stats(BaseModel):
    total_xp: int
    tasks_completed: int
    goals_completed: int
    longest_streak: int
    achievements: list[Achievement]


class StatsService:
    def __init__(self, session: Session) -> None:
        self.goals = GoalRepository(session)
        self.tasks = TaskRepository(session)
        self.habits = HabitRepository(session)
        self.completions = HabitCompletionRepository(session)

    def compute(self) -> Stats:
        tasks = self.tasks.list_all()
        completed_tasks = [task for task in tasks if task.status == TaskStatus.COMPLETED]
        total_xp = sum(xp_for_priority(task.priority) for task in completed_tasks)

        goals_completed = sum(
            1 for goal in self.goals.list_all() if goal.status == GoalStatus.COMPLETED
        )

        streaks = [
            calculate_streak([c.completed_date for c in self.completions.list_by_habit(habit.id)])
            for habit in self.habits.list_all()
        ]
        longest_streak = max(streaks, default=0)

        achievements = evaluate_achievements(
            tasks_completed=len(completed_tasks),
            total_xp=total_xp,
            longest_streak=longest_streak,
            goals_completed=goals_completed,
        )

        return Stats(
            total_xp=total_xp,
            tasks_completed=len(completed_tasks),
            goals_completed=goals_completed,
            longest_streak=longest_streak,
            achievements=achievements,
        )
