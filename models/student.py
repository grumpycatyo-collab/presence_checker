from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from core.db import Base

class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    group_id = Column(Integer, ForeignKey("groups.group_id"))
    rfid_card_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    group = relationship("Group", back_populates="students")
    attendances = relationship("Attendance", back_populates="student")