from pydantic import BaseModel
from datetime import datetime

# What the frontend sends us: just the raw Google token
class GoogleLoginRequest(BaseModel):
    google_token: str

# What we send back to the frontend
class UserResponse(BaseModel):
    email: str
    first_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    all_time_workouts: int
    all_time_minutes: int
    this_week_workouts: int
    this_week_minutes: int
