from sqlalchemy import Column, Integer, String, Boolean, Text, Enum as SQLEnum, DateTime
from sqlalchemy.sql import func
import enum

from app.database import Base


class BookCategory(str, enum.Enum):
    PROGRAMMING = "프로그래밍"
    ARCHITECTURE = "아키텍처"
    CAREER = "커리어"
    SCIENCE = "과학"
    LITERATURE = "문학"
    OTHER = "기타"


class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    category = Column(SQLEnum(BookCategory), default=BookCategory.OTHER)
    isbn = Column(String(20), unique=True, nullable=True)
    description = Column(Text, nullable=True)
    cover = Column(String(10), default="📘")
    available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"
