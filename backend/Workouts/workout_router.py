from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from Workouts import workout_service, workout_schema

router = APIRouter(
    prefix="/api/workouts",
    tags=["Workouts"]
)

@router.post("/log")
def log_workout(request: workout_schema.WorkoutRequest, db: Session = Depends(get_db)):
    workout_service.log_workout(db, request)

@router.get("", response_model=workout_schema.WorkoutResponse)
def get_workouts(user_id: int, db: Session = Depends(get_db)):
    workouts = workout_service.get_workouts(db, user_id)
    return {"workouts": workouts}