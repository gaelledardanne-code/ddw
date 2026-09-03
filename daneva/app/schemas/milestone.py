"""Request body for the Milestones API."""

from pydantic import BaseModel, ConfigDict


class MilestoneCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str = ""
