from pydantic import BaseModel, EmailStr
from datetime import datetime



class GoogleLoginRequest(BaseModel):
    google_token: str



class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str



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
