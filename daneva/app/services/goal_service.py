"""GoalService: orchestrates GoalRepository (+ TaskRepository for
progress) with the domain layer. No new business rules live here —
domain functions/methods still own all of that; this just wires them to
persistence for a given use case."""

from datetime import date

from sqlalchemy.orm import Session

from app.domain.enums import GoalCategory, GoalPriority
from app.domain.goal import Goal
from app.domain.progress import GoalProgress, calculate_goal_progress
from app.repositories.goal_repository import GoalRepository
from app.repositories.task_repository import TaskRepository


class GoalNotFoundError(LookupError):
    """Raised when a goal_id doesn't match any saved goal."""


class GoalService:
    def __init__(self, session: Session) -> None:
        self.goals = GoalRepository(session)
        self.tasks = TaskRepository(session)

    def create(
        self,
        *,
        title: str,
        description: str = "",
        category: GoalCategory = GoalCategory.OTHER,
        priority: GoalPriority = GoalPriority.MEDIUM,
        target_date: date | None = None,
    ) -> Goal:
        goal = Goal.create(
            title=title,
            description=description,
            category=category,
            priority=priority,
            target_date=target_date,
        )
        self.goals.save(goal)
        return goal

    def get(self, goal_id: str) -> Goal | None:
        return self.goals.get(goal_id)

    def list_all(self) -> list[Goal]:
        return self.goals.list_all()

    def _require(self, goal_id: str) -> Goal:
        goal = self.goals.get(goal_id)
        if goal is None:
            raise GoalNotFoundError(goal_id)
        return goal

    # Fields that must go through a dedicated method rather than a
    # generic field update: status transitions are guarded by the
    # lifecycle methods (which also stamp completed_date); id and
    # created_date are identity, not editable state.
    _NOT_DIRECTLY_UPDATABLE = frozenset({"status", "id", "created_date"})

    def update(self, goal_id: str, **fields: object) -> Goal:
        disallowed = self._NOT_DIRECTLY_UPDATABLE & fields.keys()
        if disallowed:
            raise ValueError(
                f"cannot update {sorted(disallowed)} directly; "
                "use pause/resume/complete/abandon for status"
            )
        goal = self._require(goal_id)
        updated = Goal(**{**goal.model_dump(), **fields})
        self.goals.save(updated)
        return updated

    def pause(self, goal_id: str) -> Goal:
        goal = self._require(goal_id)
        goal.pause()
        self.goals.save(goal)
        return goal

    def resume(self, goal_id: str) -> Goal:
        goal = self._require(goal_id)
        goal.resume()
        self.goals.save(goal)
        return goal

    def complete(self, goal_id: str) -> Goal:
        goal = self._require(goal_id)
        goal.complete()
        self.goals.save(goal)
        return goal

    def abandon(self, goal_id: str) -> Goal:
        goal = self._require(goal_id)
        goal.abandon()
        self.goals.save(goal)
        return goal

    def delete(self, goal_id: str) -> None:
        self.goals.delete(goal_id)

    def get_progress(self, goal_id: str) -> GoalProgress:
        self._require(goal_id)
        tasks = self.tasks.list_by_goal(goal_id)
        return calculate_goal_progress(tasks)
