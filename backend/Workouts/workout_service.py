from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from Workouts import workout_repository, workout_schema

HOURS_BETWEEN_WORKOUTS = 6

def get_workouts(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    workouts = workout_repository.get_workouts_by_user_id(db, user_id, skip, limit)
    total_count = workout_repository.count_workouts_by_user_id(db, user_id)
    return workouts, total_count
    

def log_workout(db: Session, request: workout_schema.WorkoutRequest, user_id: int):
    last_workout = workout_repository.get_most_recent_workout_by_user_id(db, user_id)
    if last_workout and last_workout.created_at:
        now = datetime.now(timezone.utc)
        last_logged = last_workout.created_at
        
        if last_logged.tzinfo is None:
            last_logged = last_logged.replace(tzinfo=timezone.utc)
            
        time_passed = now - last_logged
        cooldown = timedelta(hours=HOURS_BETWEEN_WORKOUTS)
        
        if time_passed < cooldown:
            remaining = cooldown - time_passed
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            
            if hours > 0:
                time_str = f"{hours}h {minutes}m"
            else:
                time_str = f"{minutes}m"
                
            raise HTTPException(
                status_code=429, 
                detail=f"Please wait {time_str} before logging another workout."
            )

    workout_repository.log_workout(db, request, user_id)

def update_workout(db: Session, request: workout_schema.WorkoutRequest, user_id: int, workoutID: int):
    updated_workout = workout_repository.update_workout(db, request, user_id, workoutID)
    if not updated_workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return updated_workout