from pydantic import BaseModel

# What frontend sends to backend
class QuestionnaireSubmit(BaseModel):
    answers: list[str]

# What backend sends to frontend for display
class QuestionDTO(BaseModel):
    question: str
    answers: list[str]
    