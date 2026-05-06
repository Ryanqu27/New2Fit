from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr 
    auth0_id: str


class UserCreate(UserBase):
    pass 

class UserResponse(UserBase):
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True
