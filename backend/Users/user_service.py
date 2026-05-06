from sqlalchemy.orm import Session
from fastapi import HTTPException
from Users import user_repository, user_schema

def process_oauth_login(db: Session, user_data: user_schema.UserCreate):
    existing_user = user_repository.get_user_by_auth0_id(db, auth0_id=user_data.auth0_id)
    
    if existing_user:
        return existing_user
        
    # If new user
    existing_email = user_repository.get_user_by_email(db, email=user_data.email)
    
    if existing_email:
        # We throw an HTTP 400 Exception if the data is invalid.
        raise HTTPException(status_code=400, detail="Email already registered with a different login provider.")
        
    new_user = user_repository.create_user(db, user_data)
    
    return new_user
