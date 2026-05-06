from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    auth0_id: str 

class UserResponse(BaseModel):
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True
