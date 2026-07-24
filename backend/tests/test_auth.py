"""
test_auth.py — Unit tests for Users/auth.py

Tests JWT creation and the get_current_user_id dependency in isolation,
without touching the database.
"""

import pytest
import jwt
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from fastapi import HTTPException

from Users.auth import create_access_token, get_current_user_id, JWT_SECRET, JWT_ALGORITHM


# ---------------------------------------------------------------------------
# create_access_token
# ---------------------------------------------------------------------------

def test_create_access_token_contains_user_id():
    token = create_access_token(user_id=42)
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "42"


def test_create_access_token_expires_in_7_days():
    before = datetime.now(timezone.utc)
    token = create_access_token(user_id=1)
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    expected_exp = before + timedelta(days=7)

    # Allow a 5-second buffer for test execution time
    assert abs((exp - expected_exp).total_seconds()) < 5


def test_create_access_token_different_users_produce_different_tokens():
    token_a = create_access_token(user_id=1)
    token_b = create_access_token(user_id=2)
    assert token_a != token_b


# ---------------------------------------------------------------------------
# get_current_user_id (tested via the HTTP layer through client fixture)
# ---------------------------------------------------------------------------

def test_protected_route_missing_cookie_returns_401(client):
    """No cookie → 401."""
    response = client.get("/api/workouts")
    assert response.status_code == 401


def test_protected_route_tampered_token_returns_401(client):
    """A JWT signed with the wrong secret → 401."""
    bad_token = jwt.encode({"sub": "1"}, "wrong-secret", algorithm=JWT_ALGORITHM)
    client.cookies.set("access_token", bad_token)
    response = client.get("/api/workouts")
    assert response.status_code == 401


def test_protected_route_expired_token_returns_401(client):
    """A JWT with exp in the past → 401."""
    expired_payload = {
        "sub": "1",
        "iat": datetime.now(timezone.utc) - timedelta(days=8),
        "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
    }
    expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    client.cookies.set("access_token", expired_token)
    response = client.get("/api/workouts")
    assert response.status_code == 401


def test_protected_route_valid_token_is_accepted(auth_client, db_session):
    """A valid token for an existing user → not a 401."""
    from Users.user_repository import create_email_user
    from passlib.context import CryptContext

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = create_email_user(db_session, "tokentest@test.com", "Token", pwd.hash("password123"))

    c = auth_client(user_id=user.id)
    response = c.get("/api/workouts")
    # 200 means the token was accepted; we don't care about the body here
    assert response.status_code == 200
