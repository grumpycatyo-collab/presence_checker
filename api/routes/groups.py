from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db import get_db
from crud import group as group_crud

# Schemas
from pydantic import BaseModel
from datetime import datetime

class GroupBase(BaseModel):
    code: str

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    code: Optional[str] = None

class GroupResponse(GroupBase):
    group_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Group not found"}},
)

@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    return group_crud.create_group(db=db, code=group.code)

@router.get("/", response_model=List[GroupResponse])
def read_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return group_crud.get_groups(db=db, skip=skip, limit=limit)

@router.get("/{group_id}", response_model=GroupResponse)
def read_group(group_id: int, db: Session = Depends(get_db)):
    db_group = group_crud.get_group(db=db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group

@router.put("/{group_id}", response_model=GroupResponse)
def update_group(group_id: int, group: GroupUpdate, db: Session = Depends(get_db)):
    db_group = group_crud.get_group(db=db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group_crud.update_group(db=db, group_id=group_id, code=group.code)

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: int, db: Session = Depends(get_db)):
    db_group = group_crud.get_group(db=db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    group_crud.delete_group(db=db, group_id=group_id)
    return {"detail": "Group deleted successfully"}
