from sqlalchemy import Column, Integer, String, Text, Enum as SQLEnum, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


# Enums
class UserRole(str, enum.Enum):
    MEMBER = "MEMBER"
    LIBRARIAN = "LIBRARIAN"


class LoanStatus(str, enum.Enum):
    BORROWED = "BORROWED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


# Users 테이블
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True, comment="사용자 고유 ID")
    email = Column(String(100), nullable=False, unique=True, comment="로그인 ID (이메일)")
    password = Column(String(255), nullable=False, comment="암호화된 비밀번호")
    name = Column(String(50), nullable=False, comment="사용자 이름")
    phone = Column(String(20), nullable=True, comment="전화번호")
    address = Column(String(255), nullable=True, comment="주소")
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, comment="역할 (일반회원/사서)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="가입일")
    
    # Relationships
    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email='{self.email}', name='{self.name}')>"


# Books 테이블
class Book(Base):
    __tablename__ = "books"
    
    book_id = Column(Integer, primary_key=True, autoincrement=True, comment="도서 고유 ID")
    isbn = Column(String(20), unique=True, nullable=True, comment="ISBN 번호")
    title = Column(String(200), nullable=False, comment="도서 제목")
    author = Column(String(100), nullable=False, comment="저자")
    publisher = Column(String(100), nullable=True, comment="출판사")
    published_year = Column(Integer, nullable=True, comment="출판년도")
    category = Column(String(50), nullable=True, comment="장르/카테고리")
    description = Column(Text, nullable=True, comment="도서 요약/설명")
    stock_quantity = Column(Integer, default=1, comment="현재 대출 가능한 재고 수량")
    cover_image = Column(String(255), nullable=True, comment="표지 이미지 URL")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="등록일")
    
    # Relationships
    loans = relationship("Loan", back_populates="book", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Book(book_id={self.book_id}, title='{self.title}')>"


# Loans 테이블
class Loan(Base):
    __tablename__ = "loans"
    
    loan_id = Column(Integer, primary_key=True, autoincrement=True, comment="대출 고유 ID")
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment="대출한 사용자 ID")
    book_id = Column(Integer, ForeignKey("books.book_id", ondelete="CASCADE"), nullable=False, comment="대출된 도서 ID")
    loan_date = Column(DateTime(timezone=True), server_default=func.now(), comment="대출 일자")
    due_date = Column(DateTime(timezone=True), nullable=False, comment="반납 예정일")
    return_date = Column(DateTime(timezone=True), nullable=True, comment="실제 반납 일자")
    extension_count = Column(Integer, default=0, comment="연장 횟수 (최대 1회)")
    status = Column(SQLEnum(LoanStatus), default=LoanStatus.BORROWED, comment="대출 상태")
    
    # Relationships
    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")
    
    def __repr__(self):
        return f"<Loan(loan_id={self.loan_id}, user_id={self.user_id}, book_id={self.book_id})>"


# Reviews 테이블
class Review(Base):
    __tablename__ = "reviews"
    
    review_id = Column(Integer, primary_key=True, autoincrement=True, comment="리뷰 고유 ID")
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment="작성자 ID")
    book_id = Column(Integer, ForeignKey("books.book_id", ondelete="CASCADE"), nullable=False, comment="도서 ID")
    rating = Column(Integer, nullable=False, comment="평점 (1~5)")
    content = Column(Text, nullable=True, comment="리뷰 내용")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="작성일")
    
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(review_id={self.review_id}, rating={self.rating})>"
