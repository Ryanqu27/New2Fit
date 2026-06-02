from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from Users.auth import get_current_user
from Users.UserModel import User
from Settings import settings_service, settings_schema

router = APIRouter(
    prefix="/api/settings",
    tags=["Settings"]
)

@router.get("/", response_model=settings_schema.SettingsResponse)
def get_my_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the current user's settings."""
    return settings_service.get_user_settings(db, current_user.id)

@router.put("/", response_model=settings_schema.SettingsResponse)
def update_my_settings(
    settings_update: settings_schema.SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current user's settings."""
    return settings_service.update_user_settings(db, current_user.id, settings_update)
