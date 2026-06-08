from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from database import SessionLocal
from Users.UserModel import User
from Settings.SettingsModel import UserSettings
from Workouts.WorkoutModel import Workout
from Services.email_service import send_email

INACTIVITY_THRESHOLD_DAYS = 7

def check_and_send_reminders():
    print("Running check_and_send_reminders job...")
    db: Session = SessionLocal()
    try:
        users = db.query(User).join(UserSettings, User.id == UserSettings.user_id).filter(
            UserSettings.workout_reminders == True
        ).all()
        
        now = datetime.now(timezone.utc)
        
        for user in users:
            if not user.email:
                continue
                
            last_workout = db.query(Workout).filter(
                Workout.user_id == user.id
            ).order_by(Workout.created_at.desc()).first()
            
            should_send = False
            
            if last_workout and last_workout.created_at:
                last_logged = last_workout.created_at
                if last_logged.tzinfo is None:
                    last_logged = last_logged.replace(tzinfo=timezone.utc)
                    
                time_passed = now - last_logged
                
                if timedelta(days=INACTIVITY_THRESHOLD_DAYS) <= time_passed < timedelta(days=INACTIVITY_THRESHOLD_DAYS + 1):
                    should_send = True
                    
            if should_send:
                print(f"Sending 7-day reminder to {user.email}")
                subject = "We miss you at New2Fit!"
                html_content = f"""
                <html>
                    <body style="font-family: sans-serif; color: #333; line-height: 1.6;">
                        <h2>Time to hit the gym, {user.first_name}!</h2>
                        <p>It's been a full week since your last logged workout. Consistency is the key to reaching your goals.</p>
                        <p>Log in to New2Fit today and log a quick session!</p>
                        <br>
                    </body>
                </html>
                """
                send_email(user.email, subject, html_content)
                
    except Exception as e:
        print(f"Error in check_and_send_reminders: {e}")
    finally:
        db.close()
