import os
from fastapi import APIRouter, Depends, Response, UploadFile, File, Request
from sqlalchemy.orm import Session
from database import get_db
from Users import user_service, user_schema
from Users.auth import get_current_user_id
from limiter import limiter

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

def set_auth_cookie(response: Response, token: str):
    """Helper to set the HttpOnly cookie for authentication."""
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="none" if IS_PRODUCTION else "lax",
        secure=IS_PRODUCTION,
        max_age=7 * 24 * 60 * 60  # 7 days
    )


@router.post("/login", response_model=user_schema.UserResponse)
@limiter.limit("20/minute")
def google_login(request: Request, body: user_schema.GoogleLoginRequest, response: Response, db: Session = Depends(get_db)):
    auth_data = user_service.process_oauth_login(db, body)
    set_auth_cookie(response, auth_data["access_token"])
    return auth_data["user"]


@router.post("/login/email", response_model=user_schema.UserResponse)
@limiter.limit("10/minute")
def email_login(request: Request, body: user_schema.EmailLoginRequest, response: Response, db: Session = Depends(get_db)):
    auth_data = user_service.process_email_login(db, email=body.email, password=body.password)
    set_auth_cookie(response, auth_data["access_token"])
    return auth_data["user"]


@router.post("/register", response_model=user_schema.UserResponse)
@limiter.limit("5/minute")
def user_register(request: Request, body: user_schema.RegisterRequest, response: Response, db: Session = Depends(get_db)):
    auth_data = user_service.register_user(
        db,
        email=body.email,
        first_name=body.first_name,
        password=body.password
    )
    set_auth_cookie(response, auth_data["access_token"])
    return auth_data["user"]


@router.post("/logout")
@limiter.limit("60/minute")
def logout(request: Request, response: Response):
    """Log out the user by clearing the HttpOnly cookie."""
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        samesite="none" if IS_PRODUCTION else "lax",
        secure=IS_PRODUCTION,
        max_age=0  # Expires immediately
    )
    return {"message": "Successfully logged out"}


@router.get("/me/stats", response_model=user_schema.UserStatsResponse)
@limiter.limit("30/minute")
def get_stats(request: Request, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return user_service.get_user_stats(db, user_id)


@router.patch("/me/username", response_model=user_schema.UserResponse)
@limiter.limit("5/minute")
def update_username(request: Request, body: user_schema.UpdateUsernameRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return user_service.set_username(db, user_id, body.username)


@router.post("/me/profile-picture", response_model=user_schema.UserResponse)
@limiter.limit("5/minute")
def upload_profile_picture(request: Request, file: UploadFile = File(...), user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return user_service.set_profile_picture(db, user_id, file)
