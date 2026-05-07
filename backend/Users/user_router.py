from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from Users import user_service, user_schema

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

@router.post("/login", response_model=user_schema.UserResponse)
def google_login(request: user_schema.GoogleLoginRequest, db: Session = Depends(get_db)):
    user = user_service.process_oauth_login(db, request)
    return user
