from sqlalchemy.orm import Session
from Workouts.WorkoutModel import Workout
from Workouts import workout_schema 

def get_workouts_by_user_id(db: Session, user_id: int):
    return db.query(Workout).filter(Workout.user_id == user_id).all()

def log_workout(db: Session, request: workout_schema.WorkoutRequest, user_id: int):
    new_workout = Workout(**request.model_dump(), user_id=user_id)
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)
    
