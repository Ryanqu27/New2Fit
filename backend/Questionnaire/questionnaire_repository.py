from sqlalchemy.orm import Session
from .RecommendationModel import UserRecommendation

def get_recommendation_by_user_id(db: Session, user_id: int) -> UserRecommendation | None:
    return db.query(UserRecommendation).filter(UserRecommendation.user_id == user_id).first()

def save_recommendation(db: Session, user_id: int, answers: list[str], recommendation: dict) -> UserRecommendation:
    existing_rec = get_recommendation_by_user_id(db, user_id)
    if existing_rec:
        existing_rec.answers = answers
        existing_rec.recommendation = recommendation
        db.commit()
        db.refresh(existing_rec)
        return existing_rec
    else:
        new_rec = UserRecommendation(
            user_id=user_id,
            answers=answers,
            recommendation=recommendation
            
        )
        db.add(new_rec)
        db.commit()
        db.refresh(new_rec)
        return new_rec
