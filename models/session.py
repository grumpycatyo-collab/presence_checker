from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from core.db import Base

class SessionStatus(enum.Enum):
    not_started = "not started"
    active = "active"
    ended = "ended"

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    room = Column(String)
    date = Column(DateTime)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(Enum(SessionStatus))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="sessions")
    attendances = relationship("Attendance", back_populates="session")