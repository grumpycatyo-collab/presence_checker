"""Database model classes."""

from models.professor import Professor
from models.group import Group
from models.student import Student
from models.course import Course, CourseGroup
from models.session import Session, SessionStatus
from models.attendance import Attendance, AttendanceStatus

# This helps identify all models in one place
__all__ = [
    'Professor', 
    'Group', 
    'Student', 
    'Course', 
    'CourseGroup', 
    'Session', 
    'SessionStatus',
    'Attendance', 
    'AttendanceStatus'
]