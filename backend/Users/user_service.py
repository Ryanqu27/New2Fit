from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from Users import user_repository, user_schema
from Users.auth import verify_google_token, create_access_token
import os
import shutil
import uuid
from fastapi import UploadFile

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def process_oauth_login(db: Session, request: user_schema.GoogleLoginRequest) -> dict:
    """Verify a Google ID token, find or create the user, and return a JWT."""
    google_user = verify_google_token(request.google_token)

    user = user_repository.get_user_by_google_id(db, google_id=google_user["google_id"])

    if not user:
        existing_email = user_repository.get_user_by_email(db, email=google_user["email"])
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered with a different login provider."
            )
        user = user_repository.create_user(db, google_user)

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}



def process_email_login(db: Session, email: str, password: str) -> dict:
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password cannot be longer than 72 characters.")

    user = user_repository.get_user_by_email(db, email=email)

    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}



def register_user(db: Session, email: str, first_name: str, password: str) -> dict:
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    # bcrypt has a hard 72-byte limit
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password cannot be longer than 72 characters.")

    if user_repository.get_user_by_email(db, email=email):
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    password_hash = pwd_context.hash(password)
    user = user_repository.create_email_user(
        db,
        email=email,
        first_name=first_name,
        password_hash=password_hash
    )

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}


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


def set_username(db: Session, user_id: int, username: str):
    existing = user_repository.get_user_by_username(db, username)
    if existing and existing.id != user_id:
        raise HTTPException(status_code=409, detail="Username already taken")
    return user_repository.update_username(db, user_id, username)


UPLOAD_DIR = "uploads/avatars"

def set_profile_picture(db: Session, user_id: int, file: UploadFile):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Delete old avatar file if one exists
    user = user_repository.get_user_by_id(db, user_id)
    if user and user.profile_picture_url:
        old_filepath = user.profile_picture_url.lstrip("/")
        if os.path.isfile(old_filepath):
            os.remove(old_filepath)

    ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    url = f"/uploads/avatars/{filename}"
    return user_repository.update_profile_picture(db, user_id, url)
