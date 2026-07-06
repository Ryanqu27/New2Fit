from pydantic import ConfigDict, BaseModel, Field
from datetime import datetime
from typing import Optional

class ExerciseSet(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sets: Optional[int] = Field(default=None, ge=0)
    reps: Optional[int] = Field(default=None, ge=0)
    weight_kg: Optional[float] = Field(default=None, ge=0.0)
    
class WorkoutRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    exercises: list[ExerciseSet] = []
    duration_minutes: int = Field(..., gt=0)
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
    total_count: int
