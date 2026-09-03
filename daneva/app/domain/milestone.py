"""Milestone domain entity — a checkpoint toward completing a goal."""

import uuid
from datetime import date

from pydantic import BaseModel, Field, field_validator


class Milestone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str
    title: str
    description: str = ""
    created_date: date = Field(default_factory=date.today)

    @field_validator("goal_id", "title")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value
