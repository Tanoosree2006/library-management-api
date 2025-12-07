from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from .database import Base
import enum

def utcnow():
    return datetime.now(timezone.utc)

class BookStatus(str, enum.Enum):
    available = "available"
    borrowed = "borrowed"
    reserved = "reserved"
    maintenance = "maintenance"

class MemberStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    closed = "closed"

class TransactionStatus(str, enum.Enum):
    open = "open"           # currently borrowed
    returned = "returned"   # closed
    overdue = "overdue"     # open and past due

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[BookStatus] = mapped_column(Enum(BookStatus), default=BookStatus.available, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    transactions = relationship("Transaction", back_populates="book")

class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    status: Mapped[MemberStatus] = mapped_column(Enum(MemberStatus), default=MemberStatus.active, nullable=False)
    total_fines_due: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    transactions = relationship("Transaction", back_populates="member")
    fines = relationship("Fine", back_populates="member")

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    member_id: Mapped[int] = mapped_column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), default=TransactionStatus.open, nullable=False)
    borrowed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    book = relationship("Book", back_populates="transactions")
    member = relationship("Member", back_populates="transactions")
    fines = relationship("Fine", back_populates="transaction")

    __table_args__ = (
        UniqueConstraint("book_id", "status", name="uq_book_open", deferrable=True, initially="DEFERRED"),
    )

class Fine(Base):
    __tablename__ = "fines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    member_id: Mapped[int] = mapped_column(Integer, ForeignKey("members.id"), nullable=False)
    transaction_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("transactions.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="unpaid", nullable=False)  # unpaid/paid
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    member = relationship("Member", back_populates="fines")
    transaction = relationship("Transaction", back_populates="fines")