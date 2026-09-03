"""Slice 14: Daily Plans API."""


def make_task(client, priority: str = "medium") -> dict:
    goal = client.post("/goals", json={"title": "Launch my portfolio"}).json()
    payload = {"title": "A", "priority": priority}
    return client.post(f"/goals/{goal['id']}/tasks", json=payload).json()


def test_get_daily_plan_for_an_unplanned_date_is_empty(client):
    response = client.get("/daily-plans/2026-09-03")

    assert response.status_code == 200
    body = response.json()
    assert body["plan_date"] == "2026-09-03"
    assert body["task_ids"] == []
    assert body["total_tasks"] == 0
    assert body["completion_percentage"] == 0


def test_add_task_to_daily_plan(client):
    task = make_task(client)

    response = client.post("/daily-plans/2026-09-03/tasks", json={"task_id": task["id"]})

    assert response.status_code == 200
    body = response.json()
    assert body["task_ids"] == [task["id"]]
    assert body["total_tasks"] == 1


def test_add_missing_task_to_daily_plan_returns_404(client):
    response = client.post("/daily-plans/2026-09-03/tasks", json={"task_id": "does-not-exist"})

    assert response.status_code == 404


def test_remove_task_from_daily_plan(client):
    task = make_task(client)
    client.post("/daily-plans/2026-09-03/tasks", json={"task_id": task["id"]})

    response = client.delete(f"/daily-plans/2026-09-03/tasks/{task['id']}")

    assert response.status_code == 200
    assert response.json()["task_ids"] == []


def test_daily_plan_reflects_completion_and_xp(client):
    task = make_task(client, priority="high")
    client.post("/daily-plans/2026-09-03/tasks", json={"task_id": task["id"]})

    client.post(f"/tasks/{task['id']}/complete")
    response = client.get("/daily-plans/2026-09-03")

    body = response.json()
    assert body["completed_tasks"] == 1
    assert body["completion_percentage"] == 100
    assert body["total_xp"] == 40
