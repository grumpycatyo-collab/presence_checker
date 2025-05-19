from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from core.db import get_db
from crud import student as student_crud

# --- Schemas ---
class StudentBase(BaseModel):
    name: str
    group_id: int
    rfid_card_id: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    group_id: Optional[int] = None
    rfid_card_id: Optional[int] = None

class StudentResponse(StudentBase):
    student_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Router setup ---
router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Student not found"}},
)

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    return student_crud.create_student(
        db=db,
        name=student.name,
        group_id=student.group_id,
        rfid_card_id=student.rfid_card_id
    )

@router.get("/", response_model=List[StudentResponse])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return student_crud.get_students(db, skip=skip, limit=limit)

@router.get("/{student_id}", response_model=StudentResponse)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = student_crud.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentUpdate, db: Session = Depends(get_db)):
    db_student = student_crud.get_student(db, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student_crud.update_student(
        db=db,
        student_id=student_id,
        name=student.name,
        group_id=student.group_id,
        rfid_card_id=student.rfid_card_id
    )

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = student_crud.get_student(db, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    student_crud.delete_student(db, student_id=student_id)
    return {"detail": "Student deleted successfully"}
