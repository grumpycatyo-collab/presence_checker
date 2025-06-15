from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from enum import Enum
from .attendances import AttendanceStats
from pydantic import BaseModel

from core.db import get_db
from crud import session as session_crud

class SessionStatus(str, Enum):
    not_started = "not_started"
    active = "active"
    ended = "ended"

class GroupResponse(BaseModel):
    group_id: int
    code: str

    class Config:
        orm_mode = True

class StudentResponse(BaseModel):
    student_id: int
    name: str
    group: GroupResponse

    class Config:
        orm_mode = True

class CourseResponse(BaseModel):
    course_id: int
    name: str

    class Config:
        orm_mode = True

class AttendanceResponse(BaseModel):
    attendance_id: int
    time : datetime
    status: str
    student: StudentResponse
    class Config:
        orm_mode = True
# Schemas
class SessionBase(BaseModel):
    # course: CourseResponse
    course: Optional[CourseResponse] = None #just to avoid internal server err if db is not populated correctly
    room: str
    date: datetime
    start_time: datetime
    end_time: datetime
    status: SessionStatus

class SessionCreate(BaseModel):
    course_id: int
    room: str
    date: datetime
    start_time: datetime
    end_time: datetime
    status: SessionStatus


class SessionUpdate(BaseModel):
    room: Optional[str] = None
    date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[SessionStatus] = None

class SessionResponse(SessionBase):
    session_id: int
    created_at: datetime
    updated_at: datetime
    attendances: List[AttendanceResponse] = []

    class Config:
        orm_mode = True

class SessionWithStatsResponse(SessionBase):
    session_id: int
    created_at: datetime
    updated_at: datetime
    attendances: List[AttendanceResponse] = []
    attendance_stats: AttendanceStats

    class Config:
        from_attributes = True

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
    responses={404: {"description": "Session not found"}},
)

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    return session_crud.create_session(db=db, **session.dict())

@router.get("/", response_model=List[SessionResponse])
def read_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return session_crud.get_sessions(db=db, skip=skip, limit=limit)

@router.get("/{session_id}", response_model=SessionResponse)
def read_session(session_id: int, db: Session = Depends(get_db)):
    db_session = session_crud.get_session(db=db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@router.put("/{session_id}", response_model=SessionResponse)
def update_session(session_id: int, session: SessionUpdate, db: Session = Depends(get_db)):
    db_session = session_crud.get_session(db=db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_crud.update_session(db=db, session_id=session_id, **session.dict(exclude_unset=True))

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    db_session = session_crud.get_session(db=db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    session_crud.delete_session(db=db, session_id=session_id)
    return {"detail": "Session deleted successfully"}

@router.get("/current/{professor_id}", response_model=List[SessionWithStatsResponse])
def get_current_sessions_by_professor(professor_id: int, db: Session = Depends(get_db)):
    sessions = session_crud.get_current_sessions_by_professor_and_time(
        db=db, professor_id=professor_id
    )

    sessions_with_stats = []
    for session in sessions:
        total_attendances = len(session.attendances)
        present_count = sum(
            1 for a in session.attendances if a.status.value == "present"
        )
        late_count = sum(1 for a in session.attendances if a.status.value == "late")
        absent_count = sum(1 for a in session.attendances if a.status.value == "absent")

        # Create stats object
        stats = AttendanceStats(
            total=total_attendances,
            present=present_count,
            late=late_count,
            absent=absent_count,
        )

        session_response = SessionResponse.model_validate(session, from_attributes=True)
        session_with_stats = SessionWithStatsResponse(
            **session_response.model_dump(), attendance_stats=stats
        )
        sessions_with_stats.append(session_with_stats)

    return sessions_with_stats

@router.get("/professor/{professor_id}", response_model=List[SessionResponse])
def get_all_sessions_by_professor(professor_id: int, db: Session = Depends(get_db)):
    return session_crud.get_sessions_by_professor(db, professor_id=professor_id)

#TODO: add course name in response