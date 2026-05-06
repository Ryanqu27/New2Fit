from sqlalchemy.orm import Session
from Users.UserModel import User
from Users.user_schema import UserCreate

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_auth0_id(db: Session, auth0_id: str):
    return db.query(User).filter(User.auth0_id == auth0_id).first()

def create_user(db: Session, user_data: UserCreate):
    
    db_user = User(email=user_data.email, auth0_id=user_data.auth0_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
