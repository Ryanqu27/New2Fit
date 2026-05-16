from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String, nullable=False)           
    notes = Column(String, nullable=False)         
    duration_minutes = Column(Integer, nullable=False)

    date = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="workouts")
