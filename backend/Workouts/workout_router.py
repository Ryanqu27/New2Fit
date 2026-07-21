from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from Workouts import workout_service, workout_schema
from Users.auth import get_current_user_id
from limiter import limiter

router = APIRouter(
    prefix="/api/workouts",
    tags=["Workouts"]
)

@router.post("/log", response_model=workout_schema.WorkoutItem)
@limiter.limit("20/minute")
def log_workout(request: Request,
                body: workout_schema.WorkoutRequest,
                db: Session = Depends(get_db),
                user_id: int = Depends(get_current_user_id)):
    return workout_service.log_workout(db, body, user_id=user_id)

@router.get("", response_model=workout_schema.WorkoutResponse)
@limiter.limit("30/minute")
def get_workouts(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    workouts, total_count = workout_service.get_workouts(db, user_id, skip, limit)
    return {"workouts": workouts, "total_count": total_count}

@router.put("/{workout_id}", response_model=workout_schema.WorkoutItem)
@limiter.limit("20/minute")
def update_workout(request: Request,
                   workout_id: int,
                   body: workout_schema.WorkoutRequest,
                   db: Session = Depends(get_db),
                   user_id: int = Depends(get_current_user_id)):
    return workout_service.update_workout(db, body, user_id, workout_id)