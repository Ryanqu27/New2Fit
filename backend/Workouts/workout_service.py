from sqlalchemy.orm import Session
from Workouts import workout_repository, workout_schema

def get_workouts(db: Session, user_id: int):
    return workout_repository.get_workouts_by_user_id(db, user_id)
    

def log_workout(db: Session, request: workout_schema.WorkoutRequest, user_id: int):
    workout_repository.log_workout(db, request, user_id)