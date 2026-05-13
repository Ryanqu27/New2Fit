from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Questionnaire.questionnaire_router import router as questionnaire_router
from GymLocations.gym_locations_router import router as gym_locations_router
from Users.user_router import router as users_router
from Camera.camera_router import router as camera_router
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questionnaire_router)
app.include_router(gym_locations_router)
app.include_router(users_router)
app.include_router(camera_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
