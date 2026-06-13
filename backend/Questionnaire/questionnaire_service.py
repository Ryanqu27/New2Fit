from sqlalchemy.orm import Session
from Questionnaire import questionnaire_repository

def store_recommendation(db: Session, user_id: int, answers: list[str], recommendation: dict[str, str]):
    return questionnaire_repository.save_recommendation(db, user_id, answers, recommendation)

def get_recommendation(db: Session, user_id: int):
    rec_obj = questionnaire_repository.get_recommendation_by_user_id(db, user_id)
    if rec_obj:
        return rec_obj.recommendation
    return None
