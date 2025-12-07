from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/members", tags=["Members"])

@router.get("", response_model=List[schemas.MemberOut])
def list_members(db: Session = Depends(get_db)):
    return db.query(models.Member).all()

@router.post("", response_model=schemas.MemberOut, status_code=201)
def create_member(payload: schemas.MemberCreate, db: Session = Depends(get_db)):
    if db.query(models.Member).filter(models.Member.email == payload.email).first():
        raise HTTPException(400, "Email already exists")
    m = models.Member(**payload.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

@router.get("/{member_id}", response_model=schemas.MemberOut)
def get_member(member_id: int, db: Session = Depends(get_db)):
    m = db.query(models.Member).get(member_id)
    if not m:
        raise HTTPException(404, "Member not found")
    return m

@router.put("/{member_id}", response_model=schemas.MemberOut)
def update_member(member_id: int, payload: schemas.MemberCreate, db: Session = Depends(get_db)):
    m = db.query(models.Member).get(member_id)
    if not m:
        raise HTTPException(404, "Member not found")
    for k,v in payload.model_dump().items():
        setattr(m,k,v)
    db.commit()
    db.refresh(m)
    return m

@router.delete("/{member_id}", status_code=204)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    m = db.query(models.Member).get(member_id)
    if not m:
        raise HTTPException(404, "Member not found")
    db.delete(m)
    db.commit()
    return

@router.get("/{member_id}/books", response_model=List[schemas.BookOut])
def books_borrowed_by_member(member_id: int, db: Session = Depends(get_db)):
    trs = db.query(models.Transaction).filter(models.Transaction.member_id == member_id,
                                              models.Transaction.status != models.TransactionStatus.returned).all()
    return [tr.book for tr in trs]

@router.get("/{member_id}/transactions", response_model=List[schemas.TransactionOut])
def transactions_of_member(member_id: int, db: Session = Depends(get_db)):
    return db.query(models.Transaction).filter(models.Transaction.member_id == member_id).all()