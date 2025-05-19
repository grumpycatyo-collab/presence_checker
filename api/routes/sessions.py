from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

from core.db import get_db
from crud import session as session_crud

class SessionStatus(str, Enum):
    not_started = "not_started"
    active = "active"
    ended = "ended"

# Schemas
class SessionBase(BaseModel):
    course_id: int
    room: str
    date: datetime
    start_time: datetime
    end_time: datetime
    status: SessionStatus

class SessionCreate(SessionBase):
    pass

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

    class Config:
        orm_mode = True

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
