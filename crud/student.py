from sqlalchemy.orm import Session
from models.student import Student

def get_student(db: Session, student_id: int):
    return db.get(Student, student_id)

def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Student).offset(skip).limit(limit).all()

def create_student(db: Session, name: str, group_id: int, rfid_card_id: str):
    db_student = Student(name=name, group_id=group_id, rfid_card_id=rfid_card_id)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: int, name: str = None, group_id: int = None, rfid_card_id: str = None):
    student = db.get(Student, student_id)
    if student:
        if name:
            student.name = name
        if group_id:
            student.group_id = group_id
        if rfid_card_id:
            student.rfid_card_id = rfid_card_id
        db.commit()
        db.refresh(student)
    return student

def delete_student(db: Session, student_id: int):
    student = db.get(Student, student_id)
    if student:
        db.delete(student)
        db.commit()
    return student
