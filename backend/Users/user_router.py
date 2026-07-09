from fastapi import APIRouter, Depends, Response, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from Users import user_service, user_schema
from Users.auth import get_current_user
from Users.UserModel import User

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


def set_auth_cookie(response: Response, token: str):
    """Helper to set the HttpOnly cookie for authentication."""
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production (HTTPS)
        max_age=7 * 24 * 60 * 60  # 7 days
    )


@router.post("/login", response_model=user_schema.UserResponse)
def google_login(request: user_schema.GoogleLoginRequest, response: Response, db: Session = Depends(get_db)):
    auth_data = user_service.process_oauth_login(db, request)
    set_auth_cookie(response, auth_data["access_token"])
    return auth_data["user"]


@router.post("/login/email", response_model=user_schema.UserResponse)
def email_login(request: user_schema.EmailLoginRequest, response: Response, db: Session = Depends(get_db)):
    auth_data = user_service.process_email_login(db, email=request.email, password=request.password)
    set_auth_cookie(response, auth_data["access_token"])
    return auth_data["user"]


@router.post("/register", response_model=user_schema.UserResponse)
def user_register(request: user_schema.RegisterRequest, response: Response, db: Session = Depends(get_db)):
    auth_data = user_service.register_user(
        db,
        email=request.email,
        first_name=request.first_name,
        password=request.password
    )
    set_auth_cookie(response, auth_data["access_token"])
    return auth_data["user"]


@router.post("/logout")
def logout(response: Response):
    """Log out the user by clearing the HttpOnly cookie."""
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=0  # Expires immediately
    )
    return {"message": "Successfully logged out"}


@router.get("/me/stats", response_model=user_schema.UserStatsResponse)
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.get_user_stats(db, current_user.id)


@router.patch("/me/username", response_model=user_schema.UserResponse)
def update_username(request: user_schema.UpdateUsernameRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.set_username(db, current_user.id, request.username)


@router.post("/me/profile-picture", response_model=user_schema.UserResponse)
def upload_profile_picture(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.set_profile_picture(db, current_user.id, file)
