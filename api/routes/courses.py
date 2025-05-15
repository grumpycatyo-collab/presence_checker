from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db import get_db
from models.course import Course
from crud import course as course_crud

# Create schemas for request/response
from pydantic import BaseModel

class CourseBase(BaseModel):
    name: str
    professor_id: int

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    professor_id: Optional[int] = None

class CourseResponse(CourseBase):
    course_id: int

    class Config:
        orm_mode = True

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    # TODO: Check if the professor exists (could be added)
    return course_crud.create_course(
        db=db,
        name=course.name,
        professor_id=course.professor_id
    )

@router.get("/", response_model=List[CourseResponse])
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courses = course_crud.get_courses(db, skip=skip, limit=limit)
    return courses

@router.get("/professor/{professor_id}", response_model=List[CourseResponse])
def read_courses_by_professor(professor_id: int, db: Session = Depends(get_db)):
    courses = course_crud.get_courses_by_professor(db, professor_id=professor_id)
    return courses

@router.get("/{course_id}", response_model=CourseResponse)
def read_course(course_id: int, db: Session = Depends(get_db)):
    db_course = course_crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, course: CourseUpdate, db: Session = Depends(get_db)):
    db_course = course_crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if the professor exists if we're updating professor_id (could be added)
    return course_crud.update_course(
        db=db,
        course_id=course_id,
        name=course.name,
        professor_id=course.professor_id
    )

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = course_crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    course_crud.delete_course(db, course_id=course_id)
    return {"detail": "Course deleted successfully"}