"""Translates between the DailyPlan domain entity and its ORM models.

save() replaces the full set of DailyPlanItem rows for the plan each
time rather than diffing — simpler, and correct because DailyPlan
already deduplicates task_ids in the domain layer before it's saved.
"""

from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.domain.daily_plan import DailyPlan
from app.models.daily_plan import DailyPlanItemModel, DailyPlanModel


def _to_domain(model: DailyPlanModel) -> DailyPlan:
    return DailyPlan(
        id=model.id,
        plan_date=model.plan_date,
        task_ids=[item.task_id for item in model.items],
    )


class DailyPlanRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, plan: DailyPlan) -> None:
        model = self.session.get(DailyPlanModel, plan.id)
        if model is None:
            model = DailyPlanModel(id=plan.id, plan_date=plan.plan_date)
            self.session.add(model)
        else:
            model.plan_date = plan.plan_date

        self.session.execute(
            delete(DailyPlanItemModel).where(DailyPlanItemModel.daily_plan_id == plan.id)
        )
        for task_id in plan.task_ids:
            self.session.add(DailyPlanItemModel(daily_plan_id=plan.id, task_id=task_id))
        self.session.commit()

    def get(self, plan_id: str) -> DailyPlan | None:
        model = self.session.get(DailyPlanModel, plan_id)
        return _to_domain(model) if model else None

    def get_by_date(self, plan_date: date) -> DailyPlan | None:
        stmt = select(DailyPlanModel).where(DailyPlanModel.plan_date == plan_date)
        model = self.session.execute(stmt).scalar_one_or_none()
        return _to_domain(model) if model else None
