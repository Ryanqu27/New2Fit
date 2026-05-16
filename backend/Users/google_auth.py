import os
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")

def verify_google_token(token: str) -> dict:
    try:
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        return {
            "google_id": id_info["sub"], 
            "email": id_info["email"],
            "first_name": id_info.get("given_name", "") 
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token.")

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header must start with 'Bearer '.")
    
    token = authorization.removeprefix("Bearer ").strip()
    google_user = verify_google_token(token)

    from Users.user_repository import get_user_by_google_id
    user = get_user_by_google_id(db, google_id=google_user["google_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user
