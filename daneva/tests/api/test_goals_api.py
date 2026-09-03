"""Slice 11: Goals API. Verifies HTTP wiring (status codes, request/
response shape, error mapping) — the underlying business rules are
already covered by the domain and service tests, so this doesn't
re-test every validation case, just that the API surfaces them
correctly."""


def test_create_goal_returns_201_with_the_created_goal(client):
    response = client.post("/goals", json={"title": "Launch my portfolio"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Launch my portfolio"
    assert body["status"] == "active"
    assert body["id"]


def test_create_goal_rejects_a_blank_title(client):
    response = client.post("/goals", json={"title": "   "})

    assert response.status_code == 422


def test_get_goal_returns_it(client):
    created = client.post("/goals", json={"title": "Launch my portfolio"}).json()

    response = client.get(f"/goals/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_missing_goal_returns_404(client):
    response = client.get("/goals/does-not-exist")

    assert response.status_code == 404


def test_list_goals_returns_every_created_goal(client):
    client.post("/goals", json={"title": "Launch my portfolio"})
    client.post("/goals", json={"title": "Get fit"})

    response = client.get("/goals")

    assert response.status_code == 200
    assert {g["title"] for g in response.json()} == {"Launch my portfolio", "Get fit"}


def test_patch_goal_updates_given_fields_only(client):
    created = client.post(
        "/goals", json={"title": "Launch my portfolio", "priority": "low"}
    ).json()

    response = client.patch(f"/goals/{created['id']}", json={"title": "Launch my new site"})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Launch my new site"
    assert body["priority"] == "low"


def test_patch_goal_rejects_a_status_field(client):
    created = client.post("/goals", json={"title": "Launch my portfolio"}).json()

    response = client.patch(f"/goals/{created['id']}", json={"status": "completed"})

    assert response.status_code == 422
    assert client.get(f"/goals/{created['id']}").json()["status"] == "active"


def test_patch_missing_goal_returns_404(client):
    response = client.patch("/goals/does-not-exist", json={"title": "New title"})

    assert response.status_code == 404


def test_delete_goal_removes_it(client):
    created = client.post("/goals", json={"title": "Launch my portfolio"}).json()

    response = client.delete(f"/goals/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/goals/{created['id']}").status_code == 404


def test_goal_progress_of_a_goal_with_no_tasks(client):
    created = client.post("/goals", json={"title": "Launch my portfolio"}).json()

    response = client.get(f"/goals/{created['id']}/progress")

    assert response.status_code == 200
    body = response.json()
    assert body["total_tasks"] == 0
    assert body["completion_percentage"] == 0


def test_goal_progress_of_missing_goal_returns_404(client):
    response = client.get("/goals/does-not-exist/progress")

    assert response.status_code == 404


def test_pause_then_resume_goal(client):
    created = client.post("/goals", json={"title": "Launch my portfolio"}).json()

    paused = client.post(f"/goals/{created['id']}/pause")
    assert paused.status_code == 200
    assert paused.json()["status"] == "paused"

    resumed = client.post(f"/goals/{created['id']}/resume")
    assert resumed.status_code == 200
    assert resumed.json()["status"] == "active"


def test_complete_goal_sets_status_and_completed_date(client):
    created = client.post("/goals", json={"title": "Launch my portfolio"}).json()

    response = client.post(f"/goals/{created['id']}/complete")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["completed_date"] is not None


def test_abandon_goal_sets_status(client):
    created = client.post("/goals", json={"title": "Launch my portfolio"}).json()

    response = client.post(f"/goals/{created['id']}/abandon")

    assert response.status_code == 200
    assert response.json()["status"] == "abandoned"


def test_completing_an_already_completed_goal_returns_409(client):
    created = client.post("/goals", json={"title": "Launch my portfolio"}).json()
    client.post(f"/goals/{created['id']}/complete")

    response = client.post(f"/goals/{created['id']}/complete")

    assert response.status_code == 409


def test_lifecycle_action_on_missing_goal_returns_404(client):
    response = client.post("/goals/does-not-exist/pause")

    assert response.status_code == 404
