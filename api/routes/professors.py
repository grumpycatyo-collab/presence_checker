from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import bcrypt

from core.db import get_db
from models.professor import Professor
from crud import professor as professor_crud

# Create schemas for request/response
from pydantic import BaseModel, EmailStr

class ProfessorBase(BaseModel):
    name: str
    email: EmailStr

class ProfessorCreate(ProfessorBase):
    password: str

class ProfessorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class ProfessorResponse(ProfessorBase):
    professor_id: int

    class Config:
        orm_mode = True

router = APIRouter(
    prefix="/professors",
    tags=["professors"],
    responses={404: {"description": "Not found"}},
)

# Hash password function
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

@router.post("/", response_model=ProfessorResponse, status_code=status.HTTP_201_CREATED)
def create_professor(professor: ProfessorCreate, db: Session = Depends(get_db)):
    db_professor = professor_crud.get_professor_by_email(db, email=professor.email)
    if db_professor:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = hash_password(professor.password)

    return professor_crud.create_professor(
        db=db,
        name=professor.name,
        email=professor.email,
        password_hash=hashed_password
    )

@router.get("/", response_model=List[ProfessorResponse])
def read_professors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    professors = professor_crud.get_professors(db, skip=skip, limit=limit)
    return professors

@router.get("/{professor_id}", response_model=ProfessorResponse)
def read_professor(professor_id: int, db: Session = Depends(get_db)):
    db_professor = professor_crud.get_professor(db, professor_id=professor_id)
    if db_professor is None:
        raise HTTPException(status_code=404, detail="Professor not found")
    return db_professor

@router.put("/{professor_id}", response_model=ProfessorResponse)
def update_professor(professor_id: int, professor: ProfessorUpdate, db: Session = Depends(get_db)):
    db_professor = professor_crud.get_professor(db, professor_id=professor_id)
    if db_professor is None:
        raise HTTPException(status_code=404, detail="Professor not found")

    # Check email uniqueness if email is being updated
    if professor.email and professor.email != db_professor.email:
        existing_professor = professor_crud.get_professor_by_email(db, email=professor.email)
        if existing_professor:
            raise HTTPException(status_code=400, detail="Email already registered")

    return professor_crud.update_professor(
        db=db,
        professor_id=professor_id,
        name=professor.name,
        email=professor.email
    )

@router.delete("/{professor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professor(professor_id: int, db: Session = Depends(get_db)):
    db_professor = professor_crud.get_professor(db, professor_id=professor_id)
    if db_professor is None:
        raise HTTPException(status_code=404, detail="Professor not found")
    professor_crud.delete_professor(db, professor_id=professor_id)
    return {"detail": "Professor deleted successfully"}