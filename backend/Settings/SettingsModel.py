from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    theme = Column(String, default="dark")
    unit_preference = Column(String, default="imperial")
    camera_framerate_preference = Column(Integer, default=30)
    workout_reminders = Column(Boolean, default=True)

    user = relationship("User", back_populates="settings")
