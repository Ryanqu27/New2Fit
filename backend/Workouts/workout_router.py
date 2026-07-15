from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from Workouts import workout_service, workout_schema
from Users.auth import get_current_user
from Users.UserModel import User

router = APIRouter(
    prefix="/api/workouts",
    tags=["Workouts"]
)

@router.post("/log", response_model=workout_schema.WorkoutItem)
def log_workout(request: workout_schema.WorkoutRequest,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return workout_service.log_workout(db, request, user_id=current_user.id)

@router.get("", response_model=workout_schema.WorkoutResponse)
def get_workouts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    workouts, total_count = workout_service.get_workouts(db, current_user.id, skip, limit)
    return {"workouts": workouts, "total_count": total_count}

@router.put("/{workout_id}", response_model=workout_schema.WorkoutItem)
def update_workout(workout_id: int,
                   request: workout_schema.WorkoutRequest,
                   db: Session = Depends(get_db), 
                   current_user: User = Depends(get_current_user)):
    return workout_service.update_workout(db, request, current_user.id, workout_id)