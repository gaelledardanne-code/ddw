"""Enums shared by domain entities."""

from enum import StrEnum


class GoalCategory(StrEnum):
    CAREER = "career"
    CREATIVE = "creative"
    HEALTH = "health"
    FINANCIAL = "financial"
    PERSONAL = "personal"
    RELATIONSHIPS = "relationships"
    LEARNING = "learning"
    OTHER = "other"


class GoalPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GoalStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
