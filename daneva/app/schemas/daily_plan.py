"""Request body and combined response for the Daily Plans API — the
response merges DailyPlan (which tasks are selected) with
DailyPlanSummary (completion %, estimated time, XP) into the single
useful view a client actually wants for a given day."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.domain.daily_plan import DailyPlan, DailyPlanSummary


class DailyPlanTaskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str


class DailyPlanResponse(BaseModel):
    id: str
    plan_date: date
    task_ids: list[str]
    total_tasks: int
    completed_tasks: int
    completion_percentage: int
    total_estimated_minutes: int
    total_xp: int

    @classmethod
    def from_plan_and_summary(
        cls, plan: DailyPlan, summary: DailyPlanSummary
    ) -> "DailyPlanResponse":
        return cls(
            id=plan.id,
            plan_date=plan.plan_date,
            task_ids=plan.task_ids,
            **summary.model_dump(),
        )
