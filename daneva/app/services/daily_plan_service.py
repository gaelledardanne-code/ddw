"""DailyPlanService: orchestrates DailyPlanRepository + TaskRepository
with the domain layer's summarize_daily_plan."""

from datetime import date

from sqlalchemy.orm import Session

from app.domain.daily_plan import DailyPlan, DailyPlanSummary, summarize_daily_plan
from app.repositories.daily_plan_repository import DailyPlanRepository
from app.repositories.task_repository import TaskRepository


class DailyPlanService:
    def __init__(self, session: Session) -> None:
        self.plans = DailyPlanRepository(session)
        self.tasks = TaskRepository(session)

    def get_or_create(self, plan_date: date) -> DailyPlan:
        plan = self.plans.get_by_date(plan_date)
        if plan is None:
            plan = DailyPlan(plan_date=plan_date)
            self.plans.save(plan)
        return plan

    def add_task(self, plan_date: date, task_id: str) -> DailyPlan:
        plan = self.get_or_create(plan_date)
        plan.add_task(task_id)
        self.plans.save(plan)
        return plan

    def remove_task(self, plan_date: date, task_id: str) -> DailyPlan:
        plan = self.get_or_create(plan_date)
        plan.remove_task(task_id)
        self.plans.save(plan)
        return plan

    def get_summary(self, plan_date: date) -> DailyPlanSummary:
        plan = self.get_or_create(plan_date)
        tasks = [task for task in (self.tasks.get(tid) for tid in plan.task_ids) if task]
        return summarize_daily_plan(plan, tasks)
