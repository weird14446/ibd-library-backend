from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models import Book, BookCreate, BookUpdate, BookCategory, BorrowRequest, BorrowResponse

router = APIRouter()

# 샘플 도서 데이터 (메모리 DB)
books_db: list[Book] = [
    Book(id=1, title="클린 코드", author="로버트 C. 마틴", category=BookCategory.PROGRAMMING, available=True, cover="📘"),
    Book(id=2, title="디자인 패턴", author="GoF", category=BookCategory.PROGRAMMING, available=True, cover="📗"),
    Book(id=3, title="리팩터링", author="마틴 파울러", category=BookCategory.PROGRAMMING, available=False, cover="📙"),
    Book(id=4, title="도메인 주도 설계", author="에릭 에반스", category=BookCategory.ARCHITECTURE, available=True, cover="📕"),
    Book(id=5, title="실용주의 프로그래머", author="데이비드 토머스", category=BookCategory.PROGRAMMING, available=True, cover="📔"),
    Book(id=6, title="소프트웨어 장인", author="산드로 만쿠소", category=BookCategory.CAREER, available=False, cover="📓"),
]


@router.get("/", response_model=list[Book])
async def get_books(
    search: Optional[str] = Query(None, description="제목 또는 저자로 검색"),
    category: Optional[BookCategory] = Query(None, description="카테고리 필터"),
    available: Optional[bool] = Query(None, description="대출 가능 여부 필터"),
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="반환할 최대 항목 수")
):
    """도서 목록 조회 (검색, 필터링, 페이지네이션 지원)"""
    result = books_db.copy()
    
    # 검색
    if search:
        search_lower = search.lower()
        result = [
            book for book in result
            if search_lower in book.title.lower() or search_lower in book.author.lower()
        ]
    
    # 카테고리 필터
    if category:
        result = [book for book in result if book.category == category]
    
    # 대출 가능 여부 필터
    if available is not None:
        result = [book for book in result if book.available == available]
    
    # 페이지네이션
    return result[skip:skip + limit]


@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: int):
    """특정 도서 조회"""
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")


@router.post("/", response_model=Book, status_code=201)
async def create_book(book_data: BookCreate):
    """새 도서 등록"""
    new_id = max(book.id for book in books_db) + 1 if books_db else 1
    covers = ["📘", "📗", "📙", "📕", "📔", "📓"]
    
    new_book = Book(
        id=new_id,
        **book_data.model_dump(),
        available=True,
        cover=covers[new_id % len(covers)]
    )
    books_db.append(new_book)
    return new_book


@router.put("/{book_id}", response_model=Book)
async def update_book(book_id: int, book_data: BookUpdate):
    """도서 정보 수정"""
    for i, book in enumerate(books_db):
        if book.id == book_id:
            update_data = book_data.model_dump(exclude_unset=True)
            updated_book = book.model_copy(update=update_data)
            books_db[i] = updated_book
            return updated_book
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: int):
    """도서 삭제"""
    for i, book in enumerate(books_db):
        if book.id == book_id:
            books_db.pop(i)
            return
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")


@router.post("/borrow", response_model=BorrowResponse)
async def borrow_book(request: BorrowRequest):
    """도서 대출"""
    for book in books_db:
        if book.id == request.book_id:
            if not book.available:
                return BorrowResponse(
                    success=False,
                    message=f"'{book.title}'은(는) 현재 대출 중입니다",
                    book=book
                )
            book.available = False
            return BorrowResponse(
                success=True,
                message=f"'{book.title}'을(를) {request.user_name}님께 대출했습니다",
                book=book
            )
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")


@router.post("/{book_id}/return", response_model=BorrowResponse)
async def return_book(book_id: int):
    """도서 반납"""
    for book in books_db:
        if book.id == book_id:
            if book.available:
                return BorrowResponse(
                    success=False,
                    message=f"'{book.title}'은(는) 이미 반납된 도서입니다",
                    book=book
                )
            book.available = True
            return BorrowResponse(
                success=True,
                message=f"'{book.title}'이(가) 반납되었습니다",
                book=book
            )
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
