import os
import jwt
from datetime import datetime, timedelta, timezone
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from database import get_db

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
JWT_SECRET = os.environ.get("JWT_SECRET", "changeme-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 7


def verify_google_token(token: str) -> dict:
    """Verify a Google OAuth ID token and return the user info."""
    try:
        id_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        return {
            "google_id": id_info["sub"],
            "email": id_info["email"],
            "first_name": id_info.get("given_name", "")
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token.")


def create_access_token(user_id: int) -> str:
    """Create a signed JWT for the given user ID."""
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    """
    FastAPI dependency that extracts and validates our own JWT from the
    HttpOnly cookie, then returns the corresponding User from the DB.
    """
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. No access token cookie found."
        )

    try:
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token.")

    from Users.user_repository import get_user_by_id
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return user
