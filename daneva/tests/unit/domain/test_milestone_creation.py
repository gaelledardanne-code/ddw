"""Slice 3a: Milestone creation.

Expected behaviour:
- A Milestone always belongs to a goal (`goal_id` is required and cannot
  be blank).
- `title` is required and cannot be blank, same rule as Goal.
- `id` is unique and auto-generated; `created_date` is stamped to today.
"""

from datetime import date

import pytest

from app.domain.milestone import Milestone


def test_create_milestone_with_minimal_fields_applies_defaults():
    milestone = Milestone(goal_id="goal-1", title="Define positioning")

    assert milestone.goal_id == "goal-1"
    assert milestone.title == "Define positioning"
    assert milestone.description == ""
    assert milestone.created_date == date.today()


def test_create_milestone_assigns_a_unique_id():
    milestone_a = Milestone(goal_id="goal-1", title="Define positioning")
    milestone_b = Milestone(goal_id="goal-1", title="Create case studies")

    assert milestone_a.id
    assert milestone_a.id != milestone_b.id


@pytest.mark.parametrize("blank_title", ["", "   ", "\t"])
def test_create_milestone_rejects_blank_title(blank_title):
    with pytest.raises(ValueError):
        Milestone(goal_id="goal-1", title=blank_title)


@pytest.mark.parametrize("blank_goal_id", ["", "   "])
def test_create_milestone_rejects_blank_goal_id(blank_goal_id):
    with pytest.raises(ValueError):
        Milestone(goal_id=blank_goal_id, title="Define positioning")


def test_create_milestone_requires_goal_id():
    with pytest.raises(ValueError):
        Milestone(title="Define positioning")
