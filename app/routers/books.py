from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("", response_model=List[schemas.BookOut])
def list_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

@router.post("", response_model=schemas.BookOut, status_code=201)
def create_book(payload: schemas.BookCreate, db: Session = Depends(get_db)):
    book = models.Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.get("/{book_id}", response_model=schemas.BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).get(book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    return book

@router.put("/{book_id}", response_model=schemas.BookOut)
def update_book(book_id: int, payload: schemas.BookCreate, db: Session = Depends(get_db)):
    book = db.query(models.Book).get(book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    for k, v in payload.model_dump().items():
        setattr(book, k, v)
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).get(book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    db.delete(book)
    db.commit()
    return

@router.get("/available/list", response_model=List[schemas.BookOut])
def available_books(db: Session = Depends(get_db)):
    return db.query(models.Book).filter(models.Book.status == models.BookStatus.available).all()