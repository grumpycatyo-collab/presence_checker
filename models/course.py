from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from core.db import Base

class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    professor_id = Column(Integer, ForeignKey("professors.professor_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    update_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    professor = relationship("Professor", back_populates="courses")
    sessions = relationship("Session", back_populates="course")
    course_groups = relationship("CourseGroup", back_populates="course")

class CourseGroup(Base):
    __tablename__ = "courses_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    group_id = Column(Integer, ForeignKey("groups.group_id"))

    # Relationships
    course = relationship("Course", back_populates="course_groups")
    group = relationship("Group", back_populates="course_groups")