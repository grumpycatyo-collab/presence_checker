from sqlalchemy.orm import Session
from models.session import Session as SessionModel, SessionStatus
from datetime import datetime, timedelta
from models.professor import Professor
from models.attendance import Attendance
from sqlalchemy.orm import joinedload


def get_session(db: Session, session_id: int):
    return db.query(SessionModel).filter(SessionModel.session_id == session_id).first()

def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SessionModel).offset(skip).limit(limit).all()

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
                joinedload(SessionModel.attendances).joinedload(Attendance.student)
            )
            .filter(
                SessionModel.course_id == course.course_id,
                SessionModel.start_time <= now + buffer,
                SessionModel.end_time >= now - buffer
            )
            .all()
        )
        sessions.extend(course_sessions)

    # TODO: implement filtering based on status
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
                joinedload(SessionModel.attendances).joinedload(Attendance.student)
            )
            .filter(SessionModel.course_id == course.course_id)
            .all()
        )
        sessions.extend(course_sessions)

    return sessions


#TODO: implement a status update mechanism