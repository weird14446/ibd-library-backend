from pydantic import BaseModel
from typing import Optional
from enum import Enum


class BookCategory(str, Enum):
    PROGRAMMING = "프로그래밍"
    ARCHITECTURE = "아키텍처"
    CAREER = "커리어"
    SCIENCE = "과학"
    LITERATURE = "문학"
    OTHER = "기타"


class BookBase(BaseModel):
    title: str
    author: str
    category: BookCategory = BookCategory.OTHER
    isbn: Optional[str] = None
    description: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[BookCategory] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    available: Optional[bool] = None


class Book(BookBase):
    id: int
    available: bool = True
    cover: str = "📘"

    class Config:
        from_attributes = True


class BorrowRequest(BaseModel):
    book_id: int
    user_name: str


class BorrowResponse(BaseModel):
    success: bool
    message: str
    book: Optional[Book] = None
