from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from Users.google_auth import get_current_user
from Users.UserModel import User
from .questionnaire_schema import QuestionnaireSubmit, QuestionDTO
from .questionnaire import get_all_questions_dto, get_workout_recommendation
from .questionnaire_service import store_recommendation, get_recommendation

router = APIRouter(prefix="/api/questionnaire", tags=["Questionnaire"])

@router.get("/questions", response_model=list[QuestionDTO])
def get_questions():
    return get_all_questions_dto()

@router.post("/submit")
def submit_questionnaire(
    submission: QuestionnaireSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recommendation = get_workout_recommendation(submission.answers)
    store_recommendation(db, current_user.id, submission.answers, recommendation)
    return recommendation

@router.get("/recommendation")
def get_saved_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_recommendation(db, current_user.id)