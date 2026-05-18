from sqlalchemy.orm import Session
from fastapi import HTTPException
from Users import user_repository, user_schema
from Users.google_auth import verify_google_token

def process_oauth_login(db: Session, request: user_schema.GoogleLoginRequest):
    google_user = verify_google_token(request.google_token)

    existing_user = user_repository.get_user_by_google_id(db, google_id=google_user["google_id"])
    if existing_user:
        return existing_user

    existing_email = user_repository.get_user_by_email(db, email=google_user["email"])
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered with a different login provider.")

    new_user = user_repository.create_user(db, google_user)
    return new_user

from datetime import datetime, timedelta, timezone
from Workouts.WorkoutModel import Workout

def get_user_stats(db: Session, user_id: int) -> user_schema.UserStatsResponse:
    workouts = db.query(Workout).filter(Workout.user_id == user_id).all()
    
    all_time_workouts = len(workouts)
    all_time_minutes = sum(w.duration_minutes for w in workouts)
    
    now = datetime.now(timezone.utc)
    days_since_monday = now.weekday()
    monday = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
    
    this_week_workouts = 0
    this_week_minutes = 0
    
    for w in workouts:
        w_date = w.date
        if w_date.tzinfo is None:
            w_date = w_date.replace(tzinfo=timezone.utc)
        
        if w_date >= monday:
            this_week_workouts += 1
            this_week_minutes += w.duration_minutes
            
    return user_schema.UserStatsResponse(
        all_time_workouts=all_time_workouts,
        all_time_minutes=all_time_minutes,
        this_week_workouts=this_week_workouts,
        this_week_minutes=this_week_minutes
    )
