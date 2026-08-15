from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from limiter import limiter
import os
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
from Messages.message_router import router as messages_router

app = FastAPI(lifespan=lifespan)

# Rate limiting middleware — enforces limits declared in user_router.py
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
app.include_router(messages_router)

os.makedirs("uploads/avatars", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "Hello World"}
