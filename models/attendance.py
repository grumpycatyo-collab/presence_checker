from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum

from core.db import Base

class AttendanceStatus(enum.Enum):
    present = "present"
    late = "late"
    absent = "absent"

class Attendance(Base):
    __tablename__ = "attendances"

    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.session_id"))
    student_id = Column(Integer, ForeignKey("students.student_id"))
    time = Column(DateTime)
    status = Column(Enum(AttendanceStatus))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="attendances")
    student = relationship("Student", back_populates="attendances")