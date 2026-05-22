from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from Users import user_service, user_schema
from Users.auth import get_current_user
from Users.UserModel import User

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.post("/login", response_model=user_schema.TokenResponse)
def google_login(request: user_schema.GoogleLoginRequest, db: Session = Depends(get_db)):
    return user_service.process_oauth_login(db, request)


@router.post("/login/email", response_model=user_schema.TokenResponse)
def email_login(request: user_schema.EmailLoginRequest, db: Session = Depends(get_db)):
    return user_service.process_email_login(db, email=request.email, password=request.password)


@router.post("/register", response_model=user_schema.TokenResponse)
def user_register(request: user_schema.RegisterRequest, db: Session = Depends(get_db)):
    return user_service.register_user(
        db,
        email=request.email,
        first_name=request.first_name,
        password=request.password
    )


@router.get("/me/stats", response_model=user_schema.UserStatsResponse)
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.get_user_stats(db, current_user.id)
