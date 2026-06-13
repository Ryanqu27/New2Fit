from sqlalchemy.orm import Session
from fastapi import HTTPException
from Settings.SettingsModel import UserSettings
from Settings.settings_schema import SettingsBase

def get_user_settings(db: Session, user_id: int) -> UserSettings:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

def update_user_settings(db: Session, user_id: int, settings_update: SettingsBase) -> UserSettings:
    settings = get_user_settings(db, user_id)
    
    update_data = settings_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
        
    db.commit()
    db.refresh(settings)
    return settings
