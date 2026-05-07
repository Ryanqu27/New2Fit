from sqlalchemy.orm import Session
from fastapi import HTTPException
from Users import user_repository, user_schema
from Users.google_auth import verify_google_token

def process_oauth_login(db: Session, request: user_schema.GoogleLoginRequest):
    google_user = verify_google_token(request.google_token)

    existing_user = user_repository.get_user_by_google_id(db, google_id=google_user["google_id"])
    if existing_user:
        return existing_user

    existing_email = user_repository.get_user_by_email(db, email=google_user["email"])
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered with a different login provider.")

    new_user = user_repository.create_user(db, google_user)
    return new_user
