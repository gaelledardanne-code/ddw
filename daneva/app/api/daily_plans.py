"""Daily Plans API."""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.daily_plan import DailyPlanResponse, DailyPlanTaskRequest
from app.services.daily_plan_service import DailyPlanService

router = APIRouter(prefix="/daily-plans", tags=["daily-plans"])


def _service(db: Session = Depends(get_db)) -> DailyPlanService:
    return DailyPlanService(db)


def _response(plan_date: date, service: DailyPlanService) -> DailyPlanResponse:
    plan = service.get_or_create(plan_date)
    summary = service.get_summary(plan_date)
    return DailyPlanResponse.from_plan_and_summary(plan, summary)


@router.get("/{plan_date}", response_model=DailyPlanResponse)
def get_daily_plan(
    plan_date: date, service: DailyPlanService = Depends(_service)
) -> DailyPlanResponse:
    return _response(plan_date, service)


@router.post("/{plan_date}/tasks", response_model=DailyPlanResponse)
def add_task_to_plan(
    plan_date: date,
    payload: DailyPlanTaskRequest,
    service: DailyPlanService = Depends(_service),
) -> DailyPlanResponse:
    service.add_task(plan_date, payload.task_id)
    return _response(plan_date, service)


@router.delete("/{plan_date}/tasks/{task_id}", response_model=DailyPlanResponse)
def remove_task_from_plan(
    plan_date: date, task_id: str, service: DailyPlanService = Depends(_service)
) -> DailyPlanResponse:
    service.remove_task(plan_date, task_id)
    return _response(plan_date, service)
