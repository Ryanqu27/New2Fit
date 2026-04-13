from fastapi import APIRouter
from .questionnaire_schema import QuestionnaireSubmit, QuestionDTO
from .questionnaire import get_all_questions_dto, get_workout_recommendation

router = APIRouter(prefix="/questionnaire", tags=["Questionnaire"])

@router.get("/questions", response_model=list[QuestionDTO])
def get_questions():
    return get_all_questions_dto()

@router.post("/submit")
def submit_questionnaire(submission: QuestionnaireSubmit):
    return get_workout_recommendation(submission.answers)