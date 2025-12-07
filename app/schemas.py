from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Literal

class BookBase(BaseModel):
    title: str
    author: str
    category: Optional[str] = None

class BookCreate(BookBase): pass

class BookOut(BookBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class MemberBase(BaseModel):
    name: str
    email: EmailStr

class MemberCreate(MemberBase): pass

class MemberOut(MemberBase):
    id: int
    status: str
    total_fines_due: float
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class TransactionOut(BaseModel):
    id: int
    book_id: int
    member_id: int
    status: str
    borrowed_at: datetime
    due_at: datetime
    returned_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class FineOut(BaseModel):
    id: int
    member_id: int
    transaction_id: Optional[int] = None
    amount: float
    reason: str
    status: Literal["paid","unpaid"]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class PayFineIn(BaseModel):
    amount: float = Field(gt=0)