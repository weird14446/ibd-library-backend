from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.models import Book as BookSchema, BookCreate, BookUpdate
from app.db_models import Book as BookModel
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=list[BookSchema])
async def get_books(
    search: Optional[str] = Query(None, description="제목 또는 저자로 검색"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="반환할 최대 항목 수"),
    db: Session = Depends(get_db)
):
    """도서 목록 조회"""
    query = db.query(BookModel)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (BookModel.title.ilike(search_pattern)) | 
            (BookModel.author.ilike(search_pattern)) |
            (BookModel.isbn.ilike(search_pattern))
        )
    
    if category:
        query = query.filter(BookModel.category == category)
    
    books = query.offset(skip).limit(limit).all()
    return books


@router.get("/{book_id}", response_model=BookSchema)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    """특정 도서 조회"""
    book = db.query(BookModel).filter(BookModel.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    return book


@router.post("/", response_model=BookSchema, status_code=201)
async def create_book(book_data: BookCreate, db: Session = Depends(get_db)):
    """새 도서 등록"""
    # ISBN 중복 체크
    if book_data.isbn:
        existing = db.query(BookModel).filter(BookModel.isbn == book_data.isbn).first()
        if existing:
            raise HTTPException(status_code=400, detail="이미 등록된 ISBN입니다")
    
    new_book = BookModel(**book_data.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.put("/{book_id}", response_model=BookSchema)
async def update_book(book_id: int, book_data: BookUpdate, db: Session = Depends(get_db)):
    """도서 정보 수정"""
    book = db.query(BookModel).filter(BookModel.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    """도서 삭제"""
    book = db.query(BookModel).filter(BookModel.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    
    db.delete(book)
    db.commit()
