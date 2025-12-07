from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas, service

router = APIRouter(prefix="/fines", tags=["Fines"])

@router.get("", response_model=List[schemas.FineOut])
def list_fines(db: Session = Depends(get_db)):
    return db.query(models.Fine).all()

@router.post("/recalculate", summary="Recalculate overdue statuses", status_code=200)
def recalc(db: Session = Depends(get_db)):
    processed = service.recalc_overdues(db)
    return {"updated_transactions": processed}

@router.post("/{fine_id}/pay", response_model=schemas.FineOut)
def pay(fine_id: int, payload: schemas.PayFineIn, db: Session = Depends(get_db)):
    fine = db.query(models.Fine).get(fine_id)
    if not fine:
        raise HTTPException(404, "Fine not found")
    try:
        service.pay_fine(db, fine, payload.amount)
    except ValueError as e:
        raise HTTPException(400, str(e))
    db.refresh(fine)
    return fine