
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

class AttendanceCheck(BaseModel):
    id: int
    room: str
    time: str
    day: str

router = APIRouter(
    prefix="/attendances",
    tags=["attendances"],
    responses={404: {"description": "Not found"}},
)


@router.post("/check", response_model=AttendanceCheck, status_code=status.HTTP_201_CREATED)
def check_attendance(attendance: AttendanceCheck ):

    # result = check_attendance(uid, room, time_now, day)
    # Placeholder for the actual attendance check logic
    return attendance