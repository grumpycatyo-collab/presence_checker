# api/routes/attendances.py
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.db import get_db
from models.attendance import AttendanceStatus
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
    time: str
    day: str


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

## TODO: Uncomment when session gets implemented
# @router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
# def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
#     return attendance_crud.create_attendance(
#         db=db,
#         session_id=attendance.session_id,
#         student_id=attendance.student_id,
#         status=attendance.status
#     )
#
# @router.get("/", response_model=List[AttendanceResponse])
# def read_attendances(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     attendances = attendance_crud.get_attendances(db, skip=skip, limit=limit)
#     return attendances
#
# @router.get("/session/{session_id}", response_model=List[AttendanceResponse])
# def read_attendances_by_session(session_id: int, db: Session = Depends(get_db)):
#     attendances = attendance_crud.get_attendances_by_session(db, session_id=session_id)
#     return attendances
#
# @router.get("/student/{student_id}", response_model=List[AttendanceResponse])
# def read_attendances_by_student(student_id: int, db: Session = Depends(get_db)):
#     attendances = attendance_crud.get_attendances_by_student(db, student_id=student_id)
#     return attendances
#
# @router.get("/{attendance_id}", response_model=AttendanceResponse)
# def read_attendance(attendance_id: int, db: Session = Depends(get_db)):
#     db_attendance = attendance_crud.get_attendance(db, attendance_id=attendance_id)
#     if db_attendance is None:
#         raise HTTPException(status_code=404, detail="Attendance not found")
#     return db_attendance
#
# @router.put("/{attendance_id}", response_model=AttendanceResponse)
# def update_attendance(attendance_id: int, attendance: AttendanceUpdate, db: Session = Depends(get_db)):
#     db_attendance = attendance_crud.get_attendance(db, attendance_id=attendance_id)
#     if db_attendance is None:
#         raise HTTPException(status_code=404, detail="Attendance not found")
#     return attendance_crud.update_attendance(
#         db=db,
#         attendance_id=attendance_id,
#         status=attendance.status,
#         time=attendance.time
#     )
#
# @router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
#     db_attendance = attendance_crud.get_attendance(db, attendance_id=attendance_id)
#     if db_attendance is None:
#         raise HTTPException(status_code=404, detail="Attendance not found")
#     attendance_crud.delete_attendance(db, attendance_id=attendance_id)
#     return {"detail": "Attendance deleted successfully"}
#
# @router.post("/check", status_code=status.HTTP_200_OK)
# def check_attendance(attendance: AttendanceCheck, db: Session = Depends(get_db)):
#     result = attendance_crud.check_attendance(
#         db=db,
#         rfid_card_id=attendance.rfid_card_id,
#         room=attendance.room,
#         time_str=attendance.time,
#         day_str=attendance.day
#     )
#     return {"message": result}


@router.post("/mock_check", status_code=status.HTTP_200_OK)
def check_attendance(attendance: AttendanceCheck, db: Session = Depends(get_db)):
    """
    Mock endpoint to check attendance based on RFID scan
    """
    result = attendance_crud.mock_check_attendance(
        db=db,
        rfid_card_id=attendance.rfid_card_id,
        room=attendance.room,
        time_str=attendance.time,
        day_str=attendance.day
    )

    status = "unknown"
    if "Marked: present" in result:
        status = "present"
    elif "Marked: late" in result:
        status = "late"
    elif "Unknown card" in result:
        status = "unknown_card"
    elif "Error" in result:
        status = "error"

    return {
        "message": result,
        "status": status,
        "timestamp": datetime.now()
    }