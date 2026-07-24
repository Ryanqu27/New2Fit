"""
test_workout_router.py — Integration tests for the /api/workouts endpoints.

Uses the TestClient to hit the real HTTP layer. The DB is an in-memory
SQLite instance (via conftest.py fixtures). JWT auth is bypassed by baking
a valid cookie directly into the auth_client fixture.
"""

import pytest
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WORKOUT_PAYLOAD = {
    "name": "Push Day",
    "exercises": [
        {"name": "Bench Press", "sets": 3, "reps": 10, "weight_kg": 80.0}
    ],
    "duration_minutes": 45,
    "date": datetime.now(timezone.utc).isoformat(),
}


def make_user(db_session, email="workout_router@test.com"):
    from Users.user_repository import create_email_user
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return create_email_user(db_session, email, "Router", pwd.hash("pw123456"))


# ---------------------------------------------------------------------------
# Authentication guard
# ---------------------------------------------------------------------------

def test_log_workout_unauthenticated(client):
    response = client.post("/api/workouts/log", json=WORKOUT_PAYLOAD)
    assert response.status_code == 401


def test_get_workouts_unauthenticated(client):
    response = client.get("/api/workouts")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/workouts
# ---------------------------------------------------------------------------

def test_get_workouts_empty(auth_client, db_session):
    user = make_user(db_session, "empty_workouts@test.com")
    c = auth_client(user.id)
    response = c.get("/api/workouts")
    assert response.status_code == 200
    data = response.json()
    assert data["workouts"] == []
    assert data["total_count"] == 0


def test_get_workouts_returns_logged_workouts(auth_client, db_session):
    user = make_user(db_session, "get_workouts@test.com")
    c = auth_client(user.id)

    c.post("/api/workouts/log", json=WORKOUT_PAYLOAD)
    response = c.get("/api/workouts")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert data["workouts"][0]["name"] == "Push Day"


# ---------------------------------------------------------------------------
# POST /api/workouts/log
# ---------------------------------------------------------------------------

def test_log_workout_success(auth_client, db_session):
    user = make_user(db_session, "log_success@test.com")
    c = auth_client(user.id)

    response = c.post("/api/workouts/log", json=WORKOUT_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Push Day"
    assert data["duration_minutes"] == 45
    assert "id" in data


def test_log_workout_returns_workout_item(auth_client, db_session):
    """Verifies the response schema matches WorkoutItem."""
    user = make_user(db_session, "log_schema@test.com")
    c = auth_client(user.id)

    response = c.post("/api/workouts/log", json=WORKOUT_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "user_id" in data
    assert "exercises" in data
    assert data["user_id"] == user.id


def test_log_workout_cooldown_returns_429(auth_client, db_session):
    """Second immediate log for same user should be rate-limited by the cooldown."""
    user = make_user(db_session, "cooldown_router@test.com")
    c = auth_client(user.id)

    c.post("/api/workouts/log", json=WORKOUT_PAYLOAD)
    response = c.post("/api/workouts/log", json=WORKOUT_PAYLOAD)

    assert response.status_code == 429
    assert "Please wait" in response.json()["detail"]


# ---------------------------------------------------------------------------
# PUT /api/workouts/{workout_id}
# ---------------------------------------------------------------------------

def test_update_workout_success(auth_client, db_session):
    user = make_user(db_session, "update_success@test.com")
    c = auth_client(user.id)

    log_response = c.post("/api/workouts/log", json=WORKOUT_PAYLOAD)
    workout_id = log_response.json()["id"]

    updated_payload = {**WORKOUT_PAYLOAD, "name": "Updated Workout", "duration_minutes": 60}
    response = c.put(f"/api/workouts/{workout_id}", json=updated_payload)

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Workout"
    assert response.json()["duration_minutes"] == 60


def test_update_workout_wrong_user_returns_404(auth_client, db_session):
    """User A cannot update User B's workout."""
    user_a = make_user(db_session, "user_a@test.com")
    user_b = make_user(db_session, "user_b@test.com")

    client_a = auth_client(user_a.id)
    log_response = client_a.post("/api/workouts/log", json=WORKOUT_PAYLOAD)
    workout_id = log_response.json()["id"]

    client_b = auth_client(user_b.id)
    response = client_b.put(f"/api/workouts/{workout_id}", json=WORKOUT_PAYLOAD)
    assert response.status_code == 404
