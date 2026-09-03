"""Slice 12a: Milestones API."""


def test_create_milestone_under_a_goal_returns_201(client):
    goal = client.post("/goals", json={"title": "Launch my portfolio"}).json()

    response = client.post(
        f"/goals/{goal['id']}/milestones", json={"title": "Define positioning"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Define positioning"
    assert body["goal_id"] == goal["id"]


def test_create_milestone_under_a_missing_goal_returns_404(client):
    response = client.post(
        "/goals/does-not-exist/milestones", json={"title": "Define positioning"}
    )

    assert response.status_code == 404


def test_list_milestones_for_a_goal(client):
    goal = client.post("/goals", json={"title": "Launch my portfolio"}).json()
    client.post(f"/goals/{goal['id']}/milestones", json={"title": "Define positioning"})
    client.post(f"/goals/{goal['id']}/milestones", json={"title": "Build website"})

    response = client.get(f"/goals/{goal['id']}/milestones")

    assert response.status_code == 200
    titles = {m["title"] for m in response.json()}
    assert titles == {"Define positioning", "Build website"}
