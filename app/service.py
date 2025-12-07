from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from . import models

LOAN_DAYS = 14
FINE_PER_DAY = 0.50
MAX_BORROWED = 3

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def recalc_overdues(db: Session) -> int:
    """Recalculate overdue transactions and fines. Returns count processed."""
    count = 0
    for tr in db.query(models.Transaction).filter(models.Transaction.status != models.TransactionStatus.returned).all():
        if tr.due_at < now_utc():
            tr.status = models.TransactionStatus.overdue
            count += 1
    db.commit()
    return count

def count_open_borrows(db: Session, member_id: int) -> int:
    q = db.query(models.Transaction).filter(
        models.Transaction.member_id == member_id,
        models.Transaction.status != models.TransactionStatus.returned
    )
    return q.count()

def member_has_unpaid_fines(db: Session, member_id: int) -> bool:
    return db.query(models.Fine).filter(models.Fine.member_id == member_id, models.Fine.status == "unpaid").count() > 0

def suspend_if_needed(db: Session, member: models.Member):
    # suspend if 3+ overdue
    overdue_count = db.query(models.Transaction).filter(
        models.Transaction.member_id == member.id,
        models.Transaction.status == models.TransactionStatus.overdue
    ).count()
    if overdue_count >= 3 and member.status != models.MemberStatus.suspended:
        member.status = models.MemberStatus.suspended
    elif overdue_count == 0 and member.status == models.MemberStatus.suspended and not member_has_unpaid_fines(db, member.id):
        # allow auto-reactivation when all clear
        member.status = models.MemberStatus.active

def borrow_book(db: Session, book: models.Book, member: models.Member) -> models.Transaction:
    if book.status != models.BookStatus.available:
        raise ValueError("Book is not available to borrow.")
    if member.status != models.MemberStatus.active:
        raise ValueError("Member is not active.")
    if member_has_unpaid_fines(db, member.id) or member.total_fines_due > 0:
        raise ValueError("Member has unpaid fines.")
    if count_open_borrows(db, member.id) >= MAX_BORROWED:
        raise ValueError("Borrowing limit reached (3).")

    borrowed_at = now_utc()
    due_at = borrowed_at + timedelta(days=LOAN_DAYS)
    tr = models.Transaction(book_id=book.id, member_id=member.id, status=models.TransactionStatus.open,
                            borrowed_at=borrowed_at, due_at=due_at)
    book.status = models.BookStatus.borrowed
    db.add(tr)
    db.commit()
    db.refresh(tr)
    return tr

def return_book(db: Session, tr: models.Transaction) -> models.Transaction:
    if tr.status == models.TransactionStatus.returned:
        raise ValueError("Transaction already closed.")
    book = tr.book
    tr.returned_at = now_utc()
    # compute fine if overdue
    overdue_days = (tr.returned_at.date() - tr.due_at.date()).days
    if overdue_days > 0:
        amount = round(overdue_days * FINE_PER_DAY, 2)
        fine = models.Fine(member_id=tr.member_id, transaction_id=tr.id, amount=amount, reason=f"Overdue {overdue_days} day(s)",
                           status="unpaid")
        tr.member.total_fines_due += amount
        db.add(fine)
    tr.status = models.TransactionStatus.returned
    book.status = models.BookStatus.available
    db.commit()
    db.refresh(tr)
    return tr

def pay_fine(db: Session, fine: models.Fine, amount: float):
    if amount < fine.amount:
        raise ValueError("Partial payments are not supported in this simple implementation.")
    if fine.status == "paid":
        return
    fine.status = "paid"
    # reduce member due
    member = fine.member
    member.total_fines_due = max(0.0, round(member.total_fines_due - fine.amount, 2))
    db.commit()
    # potentially unsuspend
    suspend_if_needed(db, member)