from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.models import Review as ReviewSchema, ReviewCreate, ReviewUpdate, ReviewWithUser
from app.db_models import Review as ReviewModel, Book as BookModel, User as UserModel
from app.database import get_db

router = APIRouter()


@router.get("/book/{book_id}", response_model=list[ReviewWithUser])
async def get_book_reviews(
    book_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """특정 도서의 리뷰 목록 조회"""
    reviews = db.query(ReviewModel).filter(ReviewModel.book_id == book_id).offset(skip).limit(limit).all()
    
    result = []
    for review in reviews:
        user = db.query(UserModel).filter(UserModel.user_id == review.user_id).first()
        review_data = ReviewWithUser(
            review_id=review.review_id,
            user_id=review.user_id,
            book_id=review.book_id,
            rating=review.rating,
            content=review.content,
            created_at=review.created_at,
            user_name=user.name if user else None
        )
        result.append(review_data)
    
    return result


@router.get("/book/{book_id}/stats")
async def get_book_review_stats(book_id: int, db: Session = Depends(get_db)):
    """도서 리뷰 통계 (평균 평점, 리뷰 수)"""
    stats = db.query(
        func.avg(ReviewModel.rating).label("average_rating"),
        func.count(ReviewModel.review_id).label("review_count")
    ).filter(ReviewModel.book_id == book_id).first()
    
    return {
        "book_id": book_id,
        "average_rating": round(float(stats.average_rating), 1) if stats.average_rating else 0,
        "review_count": stats.review_count or 0
    }


@router.post("/", response_model=ReviewSchema, status_code=201)
async def create_review(review_data: ReviewCreate, db: Session = Depends(get_db)):
    """리뷰 작성"""
    # 사용자 확인
    user = db.query(UserModel).filter(UserModel.user_id == review_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다")
    
    # 도서 확인
    book = db.query(BookModel).filter(BookModel.book_id == review_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    
    # 중복 리뷰 체크
    existing = db.query(ReviewModel).filter(
        ReviewModel.user_id == review_data.user_id,
        ReviewModel.book_id == review_data.book_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 이 도서에 리뷰를 작성했습니다")
    
    new_review = ReviewModel(
        user_id=review_data.user_id,
        book_id=review_data.book_id,
        rating=review_data.rating,
        content=review_data.content
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


@router.put("/{review_id}", response_model=ReviewSchema)
async def update_review(review_id: int, review_data: ReviewUpdate, db: Session = Depends(get_db)):
    """리뷰 수정"""
    review = db.query(ReviewModel).filter(ReviewModel.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다")
    
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=204)
async def delete_review(review_id: int, db: Session = Depends(get_db)):
    """리뷰 삭제"""
    review = db.query(ReviewModel).filter(ReviewModel.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다")
    
    db.delete(review)
    db.commit()
