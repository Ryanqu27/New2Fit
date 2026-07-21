from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from Users.auth import get_current_user_id
from Settings import settings_service, settings_schema
from limiter import limiter

router = APIRouter(
    prefix="/api/settings",
    tags=["Settings"]
)

@router.get("/", response_model=settings_schema.Settings)
@limiter.limit("30/minute")
def get_my_settings(request: Request, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get the current user's settings."""
    return settings_service.get_user_settings(db, user_id)

@router.put("/", response_model=settings_schema.Settings)
@limiter.limit("10/minute")
def update_my_settings(
    request: Request,
    settings_update: settings_schema.SettingsBase,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update the current user's settings."""
    return settings_service.update_user_settings(db, user_id, settings_update)
