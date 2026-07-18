import os
import jwt
from datetime import datetime, timedelta, timezone
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from database import get_db

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 7


def verify_google_token(token: str) -> dict:
    """Verify a Google OAuth ID token and return the user info."""
    try:
        id_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )
        return {
            "google_id": id_info["sub"],
            "email": id_info["email"],
            "first_name": id_info.get("given_name", "")
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token. Reason: {str(e)}")


def create_access_token(user_id: int) -> str:
    """Create a signed JWT for the given user ID."""
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user_id(access_token: str = Cookie(None)) -> int:
    """
    Lightweight FastAPI dependency that validates the JWT from the HttpOnly
    cookie and returns just the user_id — no database call required.
    Use this on any route that only needs the user's ID.
    """
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. No access token cookie found."
        )

    try:
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token.")


def get_current_user(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    FastAPI dependency that fetches the full User ORM object from the DB.
    Prefer get_current_user_id when you only need the user's ID.
    """
    from Users.user_repository import get_user_by_id
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return user
