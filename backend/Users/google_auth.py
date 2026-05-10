import os
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException

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
