from pydantic import ConfigDict
from pydantic import BaseModel
from datetime import datetime
 
class WorkoutRequest(BaseModel):
    user_id: int
    name: str
    notes: str
    duration_minutes: int
    date: datetime
    
class WorkoutItem(BaseModel):
    id: int
    user_id: int
    name: str
    notes: str
    duration_minutes: int
    date: datetime
    model_config = ConfigDict(from_attributes=True)
    
class WorkoutResponse(BaseModel):
    workouts: list[WorkoutItem]
