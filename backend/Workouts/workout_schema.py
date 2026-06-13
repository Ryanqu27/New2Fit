from pydantic import ConfigDict
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExerciseSet(BaseModel):
    name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    
class WorkoutRequest(BaseModel):
    name: str
    exercises: list[ExerciseSet] = []
    duration_minutes: int
    date: datetime
    
class WorkoutItem(BaseModel):
    id: int
    user_id: int
    name: str
    exercises: list[ExerciseSet] = []
    duration_minutes: int
    date: datetime
    model_config = ConfigDict(from_attributes=True)
    
class WorkoutResponse(BaseModel):
    workouts: list[WorkoutItem]
