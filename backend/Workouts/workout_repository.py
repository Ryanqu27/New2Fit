from sqlalchemy.orm import Session
from Workouts.WorkoutModel import Workout
from Workouts import workout_schema 

def get_workouts_by_user_id(db: Session, user_id: int):
    return db.query(Workout).filter(Workout.user_id == user_id).all()

def get_most_recent_workout_by_user_id(db: Session, user_id: int):
    return db.query(Workout).filter(Workout.user_id == user_id).order_by(Workout.created_at.desc()).first()

def log_workout(db: Session, request: workout_schema.WorkoutRequest, user_id: int):
    new_workout = Workout(**request.model_dump(), user_id=user_id)
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)
    
def update_workout(db: Session, request: workout_schema.WorkoutRequest, user_id: int, workoutID: int):
    workout = db.query(Workout).filter(Workout.id == workoutID, Workout.user_id == user_id).first()
    if workout:
        update_data = request.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(workout, key, value)
            
        db.commit()
        db.refresh(workout)
        
    return workout