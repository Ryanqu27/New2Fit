from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class GoogleLoginRequest(BaseModel):
    google_token: str

class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    first_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    username: Optional[str] = None
    profile_picture_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateUsernameRequest(BaseModel):
    username: str


class UserStatsResponse(BaseModel):
    all_time_workouts: int
    all_time_minutes: int
    this_week_workouts: int
    this_week_minutes: int
