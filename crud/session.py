from sqlalchemy.orm import Session
from models.session import Session as SessionModel, SessionStatus
from datetime import datetime, timedelta
from models.professor import Professor
from models.attendance import Attendance
from models.student import Student
from models.course import Course
from sqlalchemy.orm import joinedload


def _update_session_status(session: SessionModel) -> SessionModel:
    """Helper function to update session status based on current time."""
    now = datetime.utcnow()
    if session.end_time < now:
        session.status = SessionStatus.ended
    elif session.start_time <= now <= session.end_time:
        session.status = SessionStatus.active
    else:
        session.status = SessionStatus.not_started
    
    return session


def get_session(db: Session, session_id: int):
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if session:
        session = _update_session_status(session)
        db.commit()
    return session

def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    sessions = db.query(SessionModel).offset(skip).limit(limit).all()
    for session in sessions:
        _update_session_status(session)
    db.commit()
    return sessions

def create_session(
    db: Session,
    course_id: int,
    room: str,
    date: datetime,
    start_time: datetime,
    end_time: datetime,
    status: SessionStatus,
):
    db_session = SessionModel(
        course_id=course_id,
        room=room,
        date=date,
        start_time=start_time,
        end_time=end_time,
        status=status
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session(
    db: Session,
    session_id: int,
    room: str = None,
    date: datetime = None,
    start_time: datetime = None,
    end_time: datetime = None,
    status: SessionStatus = None
):
    db_session = get_session(db, session_id)
    if db_session:
        if room:
            db_session.room = room
        if date:
            db_session.date = date
        if start_time:
            db_session.start_time = start_time
        if end_time:
            db_session.end_time = end_time
        if status:
            db_session.status = status
        db.commit()
        db.refresh(db_session)
    return db_session

def delete_session(db: Session, session_id: int):
    db_session = get_session(db, session_id)
    if db_session:
        db.delete(db_session)
        db.commit()
    return db_session


def get_current_sessions_by_professor_and_time(db: Session, professor_id: int):
    now = datetime.utcnow()
    buffer = timedelta(minutes=5)

    professor = db.get(Professor, professor_id)
    if not professor:
        return []

    sessions = []
    for course in professor.courses:
        course_sessions = (
            db.query(SessionModel)
            .options(
                # joinedload(SessionModel.attendances).joinedload(Attendance.student)
                joinedload(SessionModel.attendances).joinedload(Attendance.student).joinedload(Student.group)
                .joinedload(SessionModel.course).joinedload(Course.group)
            )
            .filter(
                SessionModel.course_id == course.course_id,
                SessionModel.start_time <= now + buffer,
                SessionModel.end_time >= now - buffer
            )
            .all()
        )
        for session in course_sessions:
            _update_session_status(session)
        sessions.extend(course_sessions)
    
    db.commit()
    return sessions

def get_sessions_by_professor(db: Session, professor_id: int):
    professor = db.get(Professor, professor_id)
    if not professor:
        return []

    sessions = []
    for course in professor.courses:
        course_sessions = (
            db.query(SessionModel)
            .options(
                joinedload(SessionModel.attendances).joinedload(Attendance.student).joinedload(Student.group)
                .joinedload(SessionModel.course).joinedload(Course.group)
            )
            .filter(SessionModel.course_id == course.course_id)
            .all()
        )
        for session in course_sessions:
            _update_session_status(session)
        sessions.extend(course_sessions)

    db.commit()
    return sessions
    