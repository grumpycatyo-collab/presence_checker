from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.db import get_db
from core.websocket_manager import WebSocketManager
from models.attendance import AttendanceStatus
from models.student import Student
from fastapi import WebSocket, WebSocketDisconnect
from crud import attendance as attendance_crud

class AttendanceBase(BaseModel):
    session_id: int
    student_id: int
    status: AttendanceStatus

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    time: Optional[datetime] = None

class AttendanceCheck(BaseModel):
    rfid_card_id: str
    room: str

class AttendanceResponse(AttendanceBase):
    attendance_id: int
    time: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

router = APIRouter(
    prefix="/attendances",
    tags=["attendances"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[AttendanceResponse])
def read_attendances(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    attendances = attendance_crud.get_attendances(db, skip=skip, limit=limit)
    return attendances

@router.get("/session/{session_id}", response_model=List[AttendanceResponse])
def read_attendances_by_session(session_id: int, db: Session = Depends(get_db)):
    attendances = attendance_crud.get_attendances_by_session(db, session_id=session_id)
    return attendances

@router.get("/student/{student_id}", response_model=List[AttendanceResponse])
def read_attendances_by_student(student_id: int, db: Session = Depends(get_db)):
    attendances = attendance_crud.get_attendances_by_student(db, student_id=student_id)
    return attendances

@router.get("/{attendance_id}", response_model=AttendanceResponse)
def read_attendance(attendance_id: int, db: Session = Depends(get_db)):
    db_attendance = attendance_crud.get_attendance(db, attendance_id=attendance_id)
    if db_attendance is None:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return db_attendance

@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(attendance_id: int, attendance: AttendanceUpdate, db: Session = Depends(get_db)):
    db_attendance = attendance_crud.get_attendance(db, attendance_id=attendance_id)
    if db_attendance is None:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return attendance_crud.update_attendance(
        db=db,
        attendance_id=attendance_id,
        status=attendance.status,
        time=attendance.time
    )

@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    db_attendance = attendance_crud.get_attendance(db, attendance_id=attendance_id)
    if db_attendance is None:
        raise HTTPException(status_code=404, detail="Attendance not found")
    attendance_crud.delete_attendance(db, attendance_id=attendance_id)
    return {"detail": "Attendance deleted successfully"}

manager = WebSocketManager()

@router.post("/check", status_code=status.HTTP_200_OK)
async def check_attendance(attendance: AttendanceCheck, db: Session = Depends(get_db)):
    """ Creates the attendance object and checks attendance based on the student rfid id"""
    result = attendance_crud.check_attendance(
        db=db,
        rfid_card_id=attendance.rfid_card_id,
        room=attendance.room
    )

    # Broadcast the attendance event to all connected WebSocket clients
    if result not in ["Unknown card", "No active session", "Error processing attendance"]:
        student = db.query(Student).filter(Student.rfid_card_id == attendance.rfid_card_id).first()
        student_name = student.name if student else "Unknown"

        notification = {
            "type": "attendance",
            "student": student_name,
            "room": attendance.room,
            "status": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        import json
        await manager.broadcast(json.dumps(notification))

    return {"message": result}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Waiting for attendance: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
