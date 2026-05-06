from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from Users import user_service, user_schema

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

# Endpoint called by the frontend after a successful Auth0/Google login.
@router.post("/login", response_model=user_schema.UserResponse)
def oauth_login(user_data: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = user_service.process_oauth_login(db, user_data)
    
    return user
