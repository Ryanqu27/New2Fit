from pydantic import BaseModel
from typing import Optional

class SettingsBase(BaseModel):
    theme: Optional[str] = "dark"
    unit_preference: Optional[str] = "imperial"
    camera_framerate_preference: Optional[int] = 30
    workout_reminders: Optional[bool] = True

class Settings(SettingsBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
