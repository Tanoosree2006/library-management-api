from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas, service

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/overdue", response_model=List[schemas.TransactionOut])
def list_overdue(db: Session = Depends(get_db)):
    service.recalc_overdues(db)
    return db.query(models.Transaction).filter(models.Transaction.status == models.TransactionStatus.overdue).all()

@router.post("/borrow", response_model=schemas.TransactionOut, status_code=201)
def borrow(book_id: int = Query(...), member_id: int = Query(...), db: Session = Depends(get_db)):
    book = db.query(models.Book).get(book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    member = db.query(models.Member).get(member_id)
    if not member:
        raise HTTPException(404, "Member not found")
    try:
        tr = service.borrow_book(db, book, member)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return tr

@router.post("/{transaction_id}/return", response_model=schemas.TransactionOut)
def return_book(transaction_id: int, db: Session = Depends(get_db)):
    tr = db.query(models.Transaction).get(transaction_id)
    if not tr:
        raise HTTPException(404, "Transaction not found")
    try:
        out = service.return_book(db, tr)
        service.suspend_if_needed(db, tr.member)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return out