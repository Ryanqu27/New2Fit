from pydantic import BaseModel
from datetime import datetime

# What the frontend sends us: just the raw Google token
class GoogleLoginRequest(BaseModel):
    google_token: str

# What we send back to the frontend
class UserResponse(BaseModel):
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
