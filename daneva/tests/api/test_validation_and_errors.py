"""Slice 16: cross-cutting validation & error-handling consistency.

Individual resources already have their own happy-path and key error
tests (slices 11-15). This checks the things that apply *across* every
resource: that FastAPI's own request-shape validation (missing field,
wrong type) and the app's domain-level validation (blank title, bad
estimated_minutes, ...) produce the *same* error response shape, and
that idempotent-delete / bad-path-param behaviour is deliberate rather
than accidental.
"""

import pytest


@pytest.mark.parametrize(
    ("method", "url", "json"),
    [
        ("post", "/goals", {}),  # missing required "title"
        ("post", "/goals", {"title": 123}),  # wrong type
        ("post", "/goals", {"title": "A", "priority": "urgent"}),  # bad enum, domain-level
        ("post", "/goals", {"title": "   "}),  # blank title, domain-level
    ],
)
def test_422_responses_share_one_consistent_shape(client, method, url, json):
    response = getattr(client, method)(url, json=json)

    assert response.status_code == 422
    body = response.json()
    assert set(body.keys()) == {"detail"}
    assert isinstance(body["detail"], str)


def test_create_task_with_non_positive_estimated_minutes_returns_422(client):
    goal = client.post("/goals", json={"title": "Launch my portfolio"}).json()

    response = client.post(
        f"/goals/{goal['id']}/tasks", json={"title": "A", "estimated_minutes": 0}
    )

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


def test_create_habit_with_blank_title_returns_422(client):
    response = client.post("/habits", json={"title": "   "})

    assert response.status_code == 422


def test_create_milestone_with_blank_title_returns_422(client):
    goal = client.post("/goals", json={"title": "Launch my portfolio"}).json()

    response = client.post(f"/goals/{goal['id']}/milestones", json={"title": "   "})

    assert response.status_code == 422


def test_invalid_date_path_param_returns_422(client):
    response = client.get("/daily-plans/not-a-date")

    assert response.status_code == 422


def test_deleting_an_already_missing_goal_is_idempotent_not_404(client):
    """DELETE is intentionally idempotent: calling it on a goal that was
    never there (or already deleted) still returns 204, matching how
    delete_goal already behaves for a goal deleted a moment ago."""
    response = client.delete("/goals/does-not-exist")

    assert response.status_code == 204


def test_removing_a_task_never_added_to_a_daily_plan_is_a_noop(client):
    goal = client.post("/goals", json={"title": "Launch my portfolio"}).json()
    task = client.post(f"/goals/{goal['id']}/tasks", json={"title": "A"}).json()

    response = client.delete(f"/daily-plans/2026-09-03/tasks/{task['id']}")

    assert response.status_code == 200
    assert response.json()["task_ids"] == []
