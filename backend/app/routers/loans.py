from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.models import Loan as LoanSchema, LoanCreate, LoanResponse, LoanStatus
from app.db_models import Loan as LoanModel, Book as BookModel, User as UserModel
from app.database import get_db

router = APIRouter()

LOAN_PERIOD_DAYS = 14  # 대출 기간 2주
MAX_EXTENSIONS = 1     # 최대 연장 횟수


@router.get("/", response_model=list[LoanSchema])
async def get_loans(
    user_id: Optional[int] = Query(None, description="사용자 ID로 필터"),
    status: Optional[LoanStatus] = Query(None, description="대출 상태 필터"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """대출 목록 조회"""
    query = db.query(LoanModel)
    
    if user_id:
        query = query.filter(LoanModel.user_id == user_id)
    if status:
        query = query.filter(LoanModel.status == status)
    
    loans = query.offset(skip).limit(limit).all()
    return loans


@router.get("/{loan_id}", response_model=LoanSchema)
async def get_loan(loan_id: int, db: Session = Depends(get_db)):
    """특정 대출 조회"""
    loan = db.query(LoanModel).filter(LoanModel.loan_id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="대출 정보를 찾을 수 없습니다")
    return loan


@router.post("/borrow", response_model=LoanResponse)
async def borrow_book(loan_data: LoanCreate, db: Session = Depends(get_db)):
    """도서 대출"""
    # 사용자 확인
    user = db.query(UserModel).filter(UserModel.user_id == loan_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다")
    
    # 도서 확인
    book = db.query(BookModel).filter(BookModel.book_id == loan_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    
    # 재고 확인
    if book.stock_quantity <= 0:
        return LoanResponse(
            success=False,
            message=f"'{book.title}'은(는) 현재 재고가 없습니다"
        )
    
    # 대출 처리
    now = datetime.now()
    new_loan = LoanModel(
        user_id=loan_data.user_id,
        book_id=loan_data.book_id,
        loan_date=now,
        due_date=now + timedelta(days=LOAN_PERIOD_DAYS),
        status=LoanStatus.BORROWED
    )
    
    book.stock_quantity -= 1
    
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    
    return LoanResponse(
        success=True,
        message=f"'{book.title}'을(를) {user.name}님께 대출했습니다. 반납 예정일: {new_loan.due_date.strftime('%Y-%m-%d')}",
        loan=new_loan
    )


@router.post("/{loan_id}/return", response_model=LoanResponse)
async def return_book(loan_id: int, db: Session = Depends(get_db)):
    """도서 반납"""
    loan = db.query(LoanModel).filter(LoanModel.loan_id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="대출 정보를 찾을 수 없습니다")
    
    if loan.status == LoanStatus.RETURNED:
        return LoanResponse(
            success=False,
            message="이미 반납된 도서입니다"
        )
    
    # 반납 처리
    loan.return_date = datetime.now()
    loan.status = LoanStatus.RETURNED
    
    # 재고 복구
    book = db.query(BookModel).filter(BookModel.book_id == loan.book_id).first()
    if book:
        book.stock_quantity += 1
    
    db.commit()
    db.refresh(loan)
    
    return LoanResponse(
        success=True,
        message=f"'{book.title}'이(가) 반납되었습니다",
        loan=loan
    )


@router.post("/{loan_id}/extend", response_model=LoanResponse)
async def extend_loan(loan_id: int, db: Session = Depends(get_db)):
    """대출 연장 (1회 제한)"""
    loan = db.query(LoanModel).filter(LoanModel.loan_id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="대출 정보를 찾을 수 없습니다")
    
    if loan.status != LoanStatus.BORROWED:
        return LoanResponse(
            success=False,
            message="대출 중인 도서만 연장할 수 있습니다"
        )
    
    if loan.extension_count >= MAX_EXTENSIONS:
        return LoanResponse(
            success=False,
            message="연장은 1회만 가능합니다"
        )
    
    # 연장 처리
    loan.due_date = loan.due_date + timedelta(days=LOAN_PERIOD_DAYS)
    loan.extension_count += 1
    
    db.commit()
    db.refresh(loan)
    
    book = db.query(BookModel).filter(BookModel.book_id == loan.book_id).first()
    
    return LoanResponse(
        success=True,
        message=f"'{book.title}' 대출이 연장되었습니다. 새 반납 예정일: {loan.due_date.strftime('%Y-%m-%d')}",
        loan=loan
    )
