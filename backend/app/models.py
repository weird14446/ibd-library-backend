from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ==================== Enums ====================
class UserRole(str, Enum):
    MEMBER = "MEMBER"
    LIBRARIAN = "LIBRARIAN"


class LoanStatus(str, Enum):
    BORROWED = "BORROWED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


# ==================== User Schemas ====================
class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    role: UserRole = UserRole.MEMBER


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None


class User(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ==================== Book Schemas ====================
class BookBase(BaseModel):
    isbn: Optional[str] = None
    title: str
    author: str
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    stock_quantity: int = 1
    cover_image: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    isbn: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    stock_quantity: Optional[int] = None
    cover_image: Optional[str] = None


class Book(BookBase):
    book_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Loan Schemas ====================
class LoanBase(BaseModel):
    user_id: int
    book_id: int


class LoanCreate(LoanBase):
    pass


class LoanExtend(BaseModel):
    loan_id: int


class Loan(LoanBase):
    loan_id: int
    loan_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    extension_count: int = 0
    status: LoanStatus = LoanStatus.BORROWED

    class Config:
        from_attributes = True


class LoanWithDetails(Loan):
    user_name: Optional[str] = None
    book_title: Optional[str] = None


class LoanResponse(BaseModel):
    success: bool
    message: str
    loan: Optional[Loan] = None


# ==================== Review Schemas ====================
class ReviewBase(BaseModel):
    book_id: int
    rating: int = Field(..., ge=1, le=5, description="평점 (1~5)")
    content: Optional[str] = None


class ReviewCreate(ReviewBase):
    user_id: int


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    content: Optional[str] = None


class Review(ReviewBase):
    review_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewWithUser(Review):
    user_name: Optional[str] = None
