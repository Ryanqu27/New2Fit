"""
test_user_router.py — Integration tests for /api/users auth endpoints.

Google OAuth is tested by mocking `google.oauth2.id_token.verify_oauth2_token`
so no real network call is made. All other tests use email/password auth.
"""

import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REGISTER_PAYLOAD = {
    "email": "newuser@example.com",
    "first_name": "New",
    "password": "securepassword123",
}

EMAIL_LOGIN_PAYLOAD = {
    "email": "newuser@example.com",
    "password": "securepassword123",
}

GOOGLE_TOKEN_PAYLOAD = {"google_token": "fake-google-id-token"}

MOCK_GOOGLE_USER = {
    "google_id": "google-uid-12345",
    "email": "googleuser@gmail.com",
    "first_name": "Google",
}


def mock_verify_google_token(token_str, request, audience, clock_skew_in_seconds=0):
    """Returns a fake verified Google ID token payload."""
    return {
        "sub": MOCK_GOOGLE_USER["google_id"],
        "email": MOCK_GOOGLE_USER["email"],
        "given_name": MOCK_GOOGLE_USER["first_name"],
    }


# ---------------------------------------------------------------------------
# POST /api/users/register
# ---------------------------------------------------------------------------

def test_register_new_user_success(client):
    response = client.post("/api/users/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == REGISTER_PAYLOAD["email"]
    assert data["first_name"] == REGISTER_PAYLOAD["first_name"]
    assert "id" in data


def test_register_sets_auth_cookie(client):
    response = client.post("/api/users/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 200
    assert "access_token" in response.cookies


def test_register_duplicate_email_fails(client):
    client.post("/api/users/register", json=REGISTER_PAYLOAD)  # First — succeeds
    response = client.post("/api/users/register", json=REGISTER_PAYLOAD)  # Second — duplicate
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_register_password_too_short_fails(client):
    payload = {**REGISTER_PAYLOAD, "password": "abc"}
    response = client.post("/api/users/register", json=payload)
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/users/login/email
# ---------------------------------------------------------------------------

def test_email_login_success(client):
    client.post("/api/users/register", json=REGISTER_PAYLOAD)
    response = client.post("/api/users/login/email", json=EMAIL_LOGIN_PAYLOAD)
    assert response.status_code == 200
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]


def test_email_login_sets_auth_cookie(client):
    client.post("/api/users/register", json=REGISTER_PAYLOAD)
    response = client.post("/api/users/login/email", json=EMAIL_LOGIN_PAYLOAD)
    assert "access_token" in response.cookies


def test_email_login_wrong_password_returns_401(client):
    client.post("/api/users/register", json=REGISTER_PAYLOAD)
    response = client.post("/api/users/login/email", json={**EMAIL_LOGIN_PAYLOAD, "password": "wrongpassword"})
    assert response.status_code == 401


def test_email_login_unknown_email_returns_401(client):
    response = client.post("/api/users/login/email", json={"email": "ghost@test.com", "password": "anything"})
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/users/login (Google OAuth)
# ---------------------------------------------------------------------------

def test_google_login_new_user_success(client):
    with patch(
        "google.oauth2.id_token.verify_oauth2_token",
        side_effect=mock_verify_google_token
    ):
        response = client.post("/api/users/login", json=GOOGLE_TOKEN_PAYLOAD)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == MOCK_GOOGLE_USER["email"]
    assert data["first_name"] == MOCK_GOOGLE_USER["first_name"]


def test_google_login_sets_auth_cookie(client):
    with patch(
        "google.oauth2.id_token.verify_oauth2_token",
        side_effect=mock_verify_google_token
    ):
        response = client.post("/api/users/login", json=GOOGLE_TOKEN_PAYLOAD)

    assert "access_token" in response.cookies


def test_google_login_existing_user_returns_same_user(client):
    """Calling Google login twice for the same google_id should return the same user."""
    with patch(
        "google.oauth2.id_token.verify_oauth2_token",
        side_effect=mock_verify_google_token
    ):
        r1 = client.post("/api/users/login", json=GOOGLE_TOKEN_PAYLOAD)
        r2 = client.post("/api/users/login", json=GOOGLE_TOKEN_PAYLOAD)

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]


def test_google_login_email_conflict_returns_400(client):
    """If an email-registered user tries Google login with same email, it should fail."""
    # Register with email first
    client.post("/api/users/register", json={
        "email": MOCK_GOOGLE_USER["email"],
        "first_name": "Email",
        "password": "password123",
    })

    # Attempt Google login with same email but different google_id
    conflict_google_user = {**MOCK_GOOGLE_USER, "google_id": "different-google-uid"}

    def mock_conflict(token, request, audience, clock_skew_in_seconds=0):
        return {
            "sub": conflict_google_user["google_id"],
            "email": conflict_google_user["email"],
            "given_name": conflict_google_user["first_name"],
        }

    with patch("google.oauth2.id_token.verify_oauth2_token", side_effect=mock_conflict):
        response = client.post("/api/users/login", json=GOOGLE_TOKEN_PAYLOAD)

    assert response.status_code == 400


def test_google_login_invalid_token_returns_401(client):
    """An invalid/expired Google token should return 401."""
    from google.auth.exceptions import GoogleAuthError
    with patch(
        "google.oauth2.id_token.verify_oauth2_token",
        side_effect=ValueError("Token has been revoked")
    ):
        response = client.post("/api/users/login", json=GOOGLE_TOKEN_PAYLOAD)

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/users/logout
# ---------------------------------------------------------------------------

def test_logout_clears_cookie(auth_client, db_session):
    from Users.user_repository import create_email_user
    from passlib.context import CryptContext

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = create_email_user(db_session, "logout@test.com", "Log", pwd.hash("pw123456"))
    c = auth_client(user.id)

    response = c.post("/api/users/logout")
    assert response.status_code == 200
    # Cookie should be expired (max_age=0 sets it to empty string)
    cookie = response.cookies.get("access_token")
    assert cookie is None or cookie == ""


# ---------------------------------------------------------------------------
# GET /api/users/me/stats
# ---------------------------------------------------------------------------

def test_get_stats_unauthenticated(client):
    response = client.get("/api/users/me/stats")
    assert response.status_code == 401


def test_get_stats_authenticated_returns_zeros(auth_client, db_session):
    from Users.user_repository import create_email_user
    from passlib.context import CryptContext

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = create_email_user(db_session, "stats@test.com", "Stats", pwd.hash("pw123456"))
    c = auth_client(user.id)

    response = c.get("/api/users/me/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["all_time_workouts"] == 0
    assert data["all_time_minutes"] == 0
    assert data["this_week_workouts"] == 0
