"""
test_workout_service.py — Unit tests for Workouts/workout_service.py

Tests the workout cooldown logic and time-string formatting directly,
bypassing the HTTP layer for speed and precision.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from Workouts import workout_service, workout_schema


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_request(**kwargs) -> workout_schema.WorkoutRequest:
    defaults = {
        "name": "Test Workout",
        "exercises": [],
        "duration_minutes": 30,
        "date": datetime.now(timezone.utc),
    }
    defaults.update(kwargs)
    return workout_schema.WorkoutRequest(**defaults)


def make_fake_workout(created_at: datetime):
    """Return a mock Workout ORM object with a given created_at timestamp."""
    w = MagicMock()
    w.created_at = created_at
    return w


# ---------------------------------------------------------------------------
# log_workout — cooldown logic
# ---------------------------------------------------------------------------

def test_log_workout_first_time_succeeds(db_session):
    """A user with no prior workouts can always log."""
    from Users.user_repository import create_email_user
    from passlib.context import CryptContext

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = create_email_user(db_session, "firstworkout@test.com", "First", pwd.hash("pw123456"))

    req = make_request()
    # Should not raise
    workout_service.log_workout(db_session, req, user_id=user.id)


def test_log_workout_within_cooldown_raises_429(db_session):
    """Logging a second workout within the cooldown window raises HTTP 429."""
    from Users.user_repository import create_email_user
    from passlib.context import CryptContext

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = create_email_user(db_session, "cooldown@test.com", "Cool", pwd.hash("pw123456"))

    req = make_request()
    workout_service.log_workout(db_session, req, user_id=user.id)  # First log — ok

    with pytest.raises(HTTPException) as exc_info:
        workout_service.log_workout(db_session, req, user_id=user.id)  # Immediate second — 429

    assert exc_info.value.status_code == 429
    assert "Please wait" in exc_info.value.detail


def test_log_workout_after_cooldown_succeeds(db_session):
    """A workout logged after the cooldown has elapsed should succeed."""
    from Users.user_repository import create_email_user
    from passlib.context import CryptContext

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = create_email_user(db_session, "postcooldown@test.com", "Post", pwd.hash("pw123456"))

    req = make_request()
    workout_service.log_workout(db_session, req, user_id=user.id)

    # Simulate that the last workout was 7 hours ago (past the 6h cooldown)
    past = datetime.now(timezone.utc) - timedelta(hours=7)
    fake_last = make_fake_workout(created_at=past)

    with patch("Workouts.workout_repository.get_most_recent_workout_by_user_id", return_value=fake_last):
        # Should not raise
        workout_service.log_workout(db_session, req, user_id=user.id)


# ---------------------------------------------------------------------------
# Time string formatting
# ---------------------------------------------------------------------------

def _get_time_str(remaining_seconds: float) -> str:
    """Helper: drive just the time-string logic by patching the last workout."""
    cooldown = timedelta(hours=workout_service.HOURS_BETWEEN_WORKOUTS)
    remaining = timedelta(seconds=remaining_seconds)
    last_logged = datetime.now(timezone.utc) - (cooldown - remaining)
    fake_last = make_fake_workout(created_at=last_logged)

    db = MagicMock()
    with patch("Workouts.workout_repository.get_most_recent_workout_by_user_id", return_value=fake_last), \
         patch("Workouts.workout_repository.log_workout"):
        try:
            workout_service.log_workout(db, make_request(), user_id=1)
        except HTTPException as e:
            return e.detail
    return ""


def test_cooldown_message_hours_and_minutes():
    msg = _get_time_str(5 * 3600 + 30 * 60 + 5)  # 5h 30m remaining (+ 5s buffer for execution time)
    assert "5h 30m" in msg


def test_cooldown_message_hours_only():
    msg = _get_time_str(2 * 3600 + 5)  # exactly 2h remaining (+ 5s buffer)
    assert "2h" in msg
    assert "0m" not in msg


def test_cooldown_message_minutes_only():
    msg = _get_time_str(45 * 60 + 5)  # 45m remaining (+ 5s buffer)
    assert "45m" in msg


def test_cooldown_message_less_than_minute():
    msg = _get_time_str(30)  # 30 seconds remaining (no buffer needed here, still < 1m)
    assert "less than a minute" in msg


# ---------------------------------------------------------------------------
# update_workout
# ---------------------------------------------------------------------------

def test_update_workout_not_found_raises_404(db_session):
    """Updating a non-existent workout ID raises HTTP 404."""
    req = make_request()
    with pytest.raises(HTTPException) as exc_info:
        workout_service.update_workout(db_session, req, user_id=999, workoutID=99999)
    assert exc_info.value.status_code == 404
