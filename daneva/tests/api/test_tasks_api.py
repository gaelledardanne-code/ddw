"""Slice 12b: Tasks API."""


def make_goal(client):
    return client.post("/goals", json={"title": "Launch my portfolio"}).json()


def test_create_task_directly_on_a_goal_returns_201(client):
    goal = make_goal(client)

    response = client.post(f"/goals/{goal['id']}/tasks", json={"title": "Write copy"})

    assert response.status_code == 201
    body = response.json()
    assert body["goal_id"] == goal["id"]
    assert body["milestone_id"] is None
    assert body["status"] == "todo"


def test_create_task_under_a_missing_goal_returns_404(client):
    response = client.post("/goals/does-not-exist/tasks", json={"title": "Write copy"})

    assert response.status_code == 404


def test_create_task_under_a_milestone_returns_201_with_both_ids(client):
    goal = make_goal(client)
    milestone = client.post(
        f"/goals/{goal['id']}/milestones", json={"title": "Build website"}
    ).json()

    response = client.post(f"/milestones/{milestone['id']}/tasks", json={"title": "Pick a theme"})

    assert response.status_code == 201
    body = response.json()
    assert body["goal_id"] == goal["id"]
    assert body["milestone_id"] == milestone["id"]


def test_create_task_under_a_missing_milestone_returns_404(client):
    response = client.post("/milestones/does-not-exist/tasks", json={"title": "Pick a theme"})

    assert response.status_code == 404


def test_list_tasks_returns_every_created_task(client):
    goal = make_goal(client)
    client.post(f"/goals/{goal['id']}/tasks", json={"title": "A"})
    client.post(f"/goals/{goal['id']}/tasks", json={"title": "B"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert {t["title"] for t in response.json()} == {"A", "B"}


def test_get_task_returns_it(client):
    goal = make_goal(client)
    created = client.post(f"/goals/{goal['id']}/tasks", json={"title": "A"}).json()

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_missing_task_returns_404(client):
    response = client.get("/tasks/does-not-exist")

    assert response.status_code == 404


def test_patch_task_updates_given_fields_only(client):
    goal = make_goal(client)
    created = client.post(
        f"/goals/{goal['id']}/tasks", json={"title": "A", "priority": "low"}
    ).json()

    response = client.patch(f"/tasks/{created['id']}", json={"title": "A (revised)"})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "A (revised)"
    assert body["priority"] == "low"


def test_patch_task_rejects_a_status_field(client):
    goal = make_goal(client)
    created = client.post(f"/goals/{goal['id']}/tasks", json={"title": "A"}).json()

    response = client.patch(f"/tasks/{created['id']}", json={"status": "completed"})

    assert response.status_code == 422
    assert client.get(f"/tasks/{created['id']}").json()["status"] == "todo"


def test_patch_missing_task_returns_404(client):
    response = client.patch("/tasks/does-not-exist", json={"title": "New title"})

    assert response.status_code == 404


def test_complete_task_awards_xp_and_returns_task_plus_xp(client):
    goal = make_goal(client)
    created = client.post(
        f"/goals/{goal['id']}/tasks", json={"title": "A", "priority": "medium"}
    ).json()

    response = client.post(f"/tasks/{created['id']}/complete")

    assert response.status_code == 200
    body = response.json()
    assert body["xp_awarded"] == 20
    assert body["task"]["status"] == "completed"
    assert body["task"]["completed_at"] is not None


def test_completing_a_task_twice_awards_xp_only_once(client):
    goal = make_goal(client)
    created = client.post(
        f"/goals/{goal['id']}/tasks", json={"title": "A", "priority": "high"}
    ).json()

    first = client.post(f"/tasks/{created['id']}/complete").json()
    second = client.post(f"/tasks/{created['id']}/complete").json()

    assert first["xp_awarded"] == 40
    assert second["xp_awarded"] == 0


def test_complete_missing_task_returns_404(client):
    response = client.post("/tasks/does-not-exist/complete")

    assert response.status_code == 404
