from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.models import Book as BookSchema, BookCreate, BookUpdate, BookCategory, BorrowRequest, BorrowResponse
from app.db_models import Book as BookModel, BookCategory as DBBookCategory
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=list[BookSchema])
async def get_books(
    search: Optional[str] = Query(None, description="제목 또는 저자로 검색"),
    category: Optional[BookCategory] = Query(None, description="카테고리 필터"),
    available: Optional[bool] = Query(None, description="대출 가능 여부 필터"),
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="반환할 최대 항목 수"),
    db: Session = Depends(get_db)
):
    """도서 목록 조회 (검색, 필터링, 페이지네이션 지원)"""
    query = db.query(BookModel)
    
    # 검색
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (BookModel.title.ilike(search_pattern)) | 
            (BookModel.author.ilike(search_pattern))
        )
    
    # 카테고리 필터
    if category:
        query = query.filter(BookModel.category == category.value)
    
    # 대출 가능 여부 필터
    if available is not None:
        query = query.filter(BookModel.available == available)
    
    # 페이지네이션
    books = query.offset(skip).limit(limit).all()
    return books


@router.get("/{book_id}", response_model=BookSchema)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    """특정 도서 조회"""
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    return book


@router.post("/", response_model=BookSchema, status_code=201)
async def create_book(book_data: BookCreate, db: Session = Depends(get_db)):
    """새 도서 등록"""
    covers = ["📘", "📗", "📙", "📕", "📔", "📓"]
    
    new_book = BookModel(
        title=book_data.title,
        author=book_data.author,
        category=book_data.category.value if book_data.category else DBBookCategory.OTHER,
        isbn=book_data.isbn,
        description=book_data.description,
        cover=covers[hash(book_data.title) % len(covers)],
        available=True
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.put("/{book_id}", response_model=BookSchema)
async def update_book(book_id: int, book_data: BookUpdate, db: Session = Depends(get_db)):
    """도서 정보 수정"""
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "category" and value:
            value = value.value
        setattr(book, field, value)
    
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    """도서 삭제"""
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    
    db.delete(book)
    db.commit()


@router.post("/borrow", response_model=BorrowResponse)
async def borrow_book(request: BorrowRequest, db: Session = Depends(get_db)):
    """도서 대출"""
    book = db.query(BookModel).filter(BookModel.id == request.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    
    if not book.available:
        return BorrowResponse(
            success=False,
            message=f"'{book.title}'은(는) 현재 대출 중입니다",
            book=book
        )
    
    book.available = False
    db.commit()
    db.refresh(book)
    
    return BorrowResponse(
        success=True,
        message=f"'{book.title}'을(를) {request.user_name}님께 대출했습니다",
        book=book
    )


@router.post("/{book_id}/return", response_model=BorrowResponse)
async def return_book(book_id: int, db: Session = Depends(get_db)):
    """도서 반납"""
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    
    if book.available:
        return BorrowResponse(
            success=False,
            message=f"'{book.title}'은(는) 이미 반납된 도서입니다",
            book=book
        )
    
    book.available = True
    db.commit()
    db.refresh(book)
    
    return BorrowResponse(
        success=True,
        message=f"'{book.title}'이(가) 반납되었습니다",
        book=book
    )
