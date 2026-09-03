"""Slice 15: Stats API — thin wrapper over StatsService.compute(),
already thoroughly tested at the service level (slice 10). This just
checks the endpoint is wired and shaped correctly."""


def test_stats_of_a_fresh_system(client):
    response = client.get("/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["total_xp"] == 0
    assert body["tasks_completed"] == 0
    assert body["goals_completed"] == 0
    assert body["longest_streak"] == 0
    assert body["achievements"] == []


def test_stats_reflect_completed_work_and_unlocked_achievements(client):
    goal = client.post("/goals", json={"title": "Launch my portfolio"}).json()
    task = client.post(
        f"/goals/{goal['id']}/tasks", json={"title": "A", "priority": "medium"}
    ).json()
    client.post(f"/tasks/{task['id']}/complete")

    response = client.get("/stats")

    body = response.json()
    assert body["total_xp"] == 20
    assert body["tasks_completed"] == 1
    assert any(a["key"] == "first_task" for a in body["achievements"])
