from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from Workouts.reminder_service import check_and_send_reminders

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schedule the reminder job to run every day at 9:00 AM
    scheduler.add_job(
        check_and_send_reminders,
        CronTrigger(hour=9, minute=0)
    )
    scheduler.start()
    yield
    scheduler.shutdown()

from Questionnaire.questionnaire_router import router as questionnaire_router
from GymLocations.gym_locations_router import router as gym_locations_router
from Users.user_router import router as users_router
from Camera.camera_router import router as camera_router
from Workouts.workout_router import router as workouts_router

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from Settings.settings_router import router as settings_router

app.include_router(questionnaire_router)
app.include_router(gym_locations_router)
app.include_router(users_router)
app.include_router(camera_router)
app.include_router(workouts_router)
app.include_router(settings_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
