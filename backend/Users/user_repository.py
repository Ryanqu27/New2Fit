from sqlalchemy.orm import Session
from Users.UserModel import User
from Settings.SettingsModel import UserSettings


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_google_id(db: Session, google_id: str):
    return db.query(User).filter(User.google_id == google_id).first()


def create_user(db: Session, google_user: dict):
    """Create a new user from Google OAuth data."""
    db_user = User(
        email=google_user["email"],
        google_id=google_user["google_id"],
        first_name=google_user.get("first_name", "")
    )
    db.add(db_user)
    db.flush() 
    
    db_settings = UserSettings(user_id=db_user.id)
    db.add(db_settings)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def create_email_user(db: Session, email: str, first_name: str, password_hash: str):
    """Create a new user with an email/password credential."""
    db_user = User(
        email=email,
        first_name=first_name,
        password_hash=password_hash
    )
    db.add(db_user)
    db.flush() 
    
    db_settings = UserSettings(user_id=db_user.id)
    db.add(db_settings)

    db.commit()
    db.refresh(db_user)
    return db_user
