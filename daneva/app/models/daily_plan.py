"""SQLAlchemy tables for daily plans and their task selections."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DailyPlanModel(Base):
    __tablename__ = "daily_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)

    items: Mapped[list[DailyPlanItemModel]] = relationship(
        back_populates="daily_plan", cascade="all, delete-orphan"
    )


class DailyPlanItemModel(Base):
    __tablename__ = "daily_plan_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    daily_plan_id: Mapped[str] = mapped_column(ForeignKey("daily_plans.id"), nullable=False)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), nullable=False)

    daily_plan: Mapped[DailyPlanModel] = relationship(back_populates="items")
