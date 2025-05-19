from sqlalchemy.orm import Session
from models.group import Group

def get_group(db: Session, group_id: int):
    return db.query(Group).filter(Group.group_id == group_id).first()

def get_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Group).offset(skip).limit(limit).all()

def create_group(db: Session, code: str):
    db_group = Group(code=code)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def update_group(db: Session, group_id: int, code: str = None):
    db_group = db.query(Group).filter(Group.group_id == group_id).first()
    if db_group and code:
        db_group.code = code
        db.commit()
        db.refresh(db_group)
    return db_group

def delete_group(db: Session, group_id: int):
    db_group = db.query(Group).filter(Group.group_id == group_id).first()
    if db_group:
        db.delete(db_group)
        db.commit()
    return db_group
