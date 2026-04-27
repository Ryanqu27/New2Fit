from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Questionnaire.questionnaire_router import router as questionnaire_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questionnaire_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
