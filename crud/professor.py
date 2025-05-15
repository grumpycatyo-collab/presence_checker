from core.db import SessionLocal as Session
from models.professor import Professor

def get_professor(db: Session, professor_id: int):
    return db.query(Professor).filter(Professor.professor_id == professor_id).first()

def get_professor_by_email(db: Session, email: str):
    return db.query(Professor).filter(Professor.email == email).first()

def get_professors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Professor).offset(skip).limit(limit).all()

def create_professor(db: Session, name: str, email: str, password_hash: str):
    db_professor = Professor(name=name, email=email, password_hash=password_hash)
    db.add(db_professor)
    db.commit()
    db.refresh(db_professor)
    return db_professor

def update_professor(db: Session, professor_id: int, name: str = None, email: str = None):
    db_professor = db.query(Professor).filter(Professor.professor_id == professor_id).first()
    if db_professor:
        if name:
            db_professor.name = name
        if email:
            db_professor.email = email
        db.commit()
        db.refresh(db_professor)
    return db_professor

def delete_professor(db: Session, professor_id: int):
    db_professor = db.query(Professor).filter(Professor.professor_id == professor_id).first()
    if db_professor:
        db.delete(db_professor)
        db.commit()
    return db_professor