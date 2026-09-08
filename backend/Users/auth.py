import os
import jwt
from datetime import datetime, timedelta, timezone
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from typing import Optional
from fastapi import Depends, HTTPException, Cookie, Header
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


def get_current_user_id(
    access_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
) -> int:
    """
    Lightweight FastAPI dependency that validates the JWT from either the HttpOnly
    cookie OR the Authorization Bearer header, and returns just the user_id.
    """
    token = access_token
    if not token and authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. No access token found in cookie or header."
        )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
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
