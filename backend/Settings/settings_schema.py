from pydantic import BaseModel
from typing import Optional

class SettingsBase(BaseModel):
    theme: Optional[str] = "system"
    unit_preference: Optional[str] = "imperial"
    camera_framerate_preference: Optional[str] = "performance"
    language: Optional[str] = "en"
    workout_reminders: Optional[bool] = True

class SettingsResponse(SettingsBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
