"""SQLAlchemy tables for habits and their completions."""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.goal import GoalModel


class HabitModel(Base):
    __tablename__ = "habits"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id: Mapped[str | None] = mapped_column(ForeignKey("goals.id"), nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    created_date: Mapped[date] = mapped_column(Date, nullable=False)

    goal: Mapped[GoalModel | None] = relationship(back_populates="habits")
    completions: Mapped[list[HabitCompletionModel]] = relationship(
        back_populates="habit", cascade="all, delete-orphan"
    )


class HabitCompletionModel(Base):
    __tablename__ = "habit_completions"
    __table_args__ = (UniqueConstraint("habit_id", "completed_date"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    habit_id: Mapped[str] = mapped_column(ForeignKey("habits.id"), nullable=False)
    completed_date: Mapped[date] = mapped_column(Date, nullable=False)

    habit: Mapped[HabitModel] = relationship(back_populates="completions")
