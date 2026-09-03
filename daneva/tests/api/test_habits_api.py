"""Slice 13: Habits API."""

from datetime import date, timedelta


def days_ago(n: int) -> str:
    return (date.today() - timedelta(days=n)).isoformat()


def test_create_habit_returns_201(client):
    response = client.post("/habits", json={"title": "Exercise"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Exercise"
    assert body["id"]


def test_list_habits_returns_every_created_habit(client):
    client.post("/habits", json={"title": "Exercise"})
    client.post("/habits", json={"title": "Read"})

    response = client.get("/habits")

    assert response.status_code == 200
    assert {h["title"] for h in response.json()} == {"Exercise", "Read"}


def test_complete_habit_records_a_completion_for_today(client):
    habit = client.post("/habits", json={"title": "Exercise"}).json()

    response = client.post(f"/habits/{habit['id']}/complete")

    assert response.status_code == 201
    body = response.json()
    assert body["habit_id"] == habit["id"]
    assert body["completed_date"] == date.today().isoformat()


def test_completing_a_habit_twice_the_same_day_returns_409(client):
    habit = client.post("/habits", json={"title": "Exercise"}).json()
    client.post(f"/habits/{habit['id']}/complete")

    response = client.post(f"/habits/{habit['id']}/complete")

    assert response.status_code == 409


def test_complete_missing_habit_returns_404(client):
    response = client.post("/habits/does-not-exist/complete")

    assert response.status_code == 404


def test_complete_habit_on_a_specific_date(client):
    habit = client.post("/habits", json={"title": "Exercise"}).json()

    response = client.post(f"/habits/{habit['id']}/complete", json={"on_date": days_ago(3)})

    assert response.status_code == 201
    assert response.json()["completed_date"] == days_ago(3)


def test_get_streak_after_seven_consecutive_days(client):
    habit = client.post("/habits", json={"title": "Exercise"}).json()
    for n in range(6, -1, -1):
        client.post(f"/habits/{habit['id']}/complete", json={"on_date": days_ago(n)})

    response = client.get(f"/habits/{habit['id']}/streak")

    assert response.status_code == 200
    assert response.json()["streak"] == 7


def test_get_streak_for_missing_habit_returns_404(client):
    response = client.get("/habits/does-not-exist/streak")

    assert response.status_code == 404
