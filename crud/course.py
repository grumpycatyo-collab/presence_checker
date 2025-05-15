from sqlalchemy.orm import Session
from models.course import Course, CourseGroup

def get_course(db: Session, course_id: int):
    return db.query(Course).filter(Course.course_id == course_id).first()

def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Course).offset(skip).limit(limit).all()

def get_courses_by_professor(db: Session, professor_id: int):
    return db.query(Course).filter(Course.professor_id == professor_id).all()

def create_course(db: Session, name: str, professor_id: int):
    db_course = Course(name=name, professor_id=professor_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def update_course(db: Session, course_id: int, name: str = None, professor_id: int = None):
    db_course = db.query(Course).filter(Course.course_id == course_id).first()
    if db_course:
        if name:
            db_course.name = name
        if professor_id:
            db_course.professor_id = professor_id
        db.commit()
        db.refresh(db_course)
    return db_course

def delete_course(db: Session, course_id: int):
    db_course = db.query(Course).filter(Course.course_id == course_id).first()
    if db_course:
        db.delete(db_course)
        db.commit()
    return db_course

## TODO: Should work but needs GROUPS crud
def add_group_to_course(db: Session, course_id: int, group_id: int):
    db_course_group = CourseGroup(course_id=course_id, group_id=group_id)
    db.add(db_course_group)
    db.commit()
    db.refresh(db_course_group)
    return db_course_group

def get_course_groups(db: Session, course_id: int):
    return db.query(CourseGroup).filter(CourseGroup.course_id == course_id).all()