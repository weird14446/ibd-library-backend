"""
AI Router - 도서 추천 및 AI 챗봇 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from dotenv import load_dotenv
import os

# .env 파일 로드
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from app.database import get_db
from app.db_models import Book as BookModel, Loan as LoanModel, Review as ReviewModel, SystemConfig, User as UserModel, LoanStatus

router = APIRouter()

# ========== Pydantic Models ==========
class RecommendRequest(BaseModel):
    user_id: Optional[int] = None
    category: Optional[str] = None
    limit: int = 5

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []

# ========== Helper Functions ==========
def get_rag_context(db: Session) -> str:
    """RAG: books 테이블과 system_config 테이블에서 컨텍스트 수집"""
    # 시스템 설정 정보
    configs = db.query(SystemConfig).all()
    config_info = "\n".join([f"- {c.key}: {c.value} ({c.description or ''})" for c in configs])
    
    # 도서 정보 (상위 20권)
    books = db.query(BookModel).limit(20).all()
    book_info = "\n".join([
        f"- 《{b.title}》 저자: {b.author}, 카테고리: {b.category or '미분류'}, 재고: {b.stock_quantity}권"
        for b in books
    ])
    
    # 카테고리 목록
    categories = db.query(BookModel.category).distinct().all()
    category_list = ", ".join([c[0] for c in categories if c[0]])
    
    context = f"""
### IBD Library 도서관 정보

**시스템 설정:**
{config_info}

**보유 도서 (일부):**
{book_info}

**도서 카테고리:** {category_list}

**운영 정보:**
- 운영시간: 평일 09:00-21:00, 주말 10:00-18:00
- 휴관일: 매월 첫째, 셋째 월요일
- 연락처: 02-1234-5678, contact@ibd-library.com
"""
    return context

# ========== Recommendation API ==========
@router.post("/recommend")
async def get_recommendations(req: RecommendRequest, db: Session = Depends(get_db)):
    """도서 추천 API - 협업 필터링 + 인기도 기반"""
    recommended_books = []
    
    # 1. 사용자 대출 이력 기반 추천 (로그인 시)
    if req.user_id:
        # 사용자가 대출한 도서의 카테고리 조회
        user_loans = db.query(LoanModel).filter(LoanModel.user_id == req.user_id).all()
        borrowed_book_ids = [loan.book_id for loan in user_loans]
        
        if borrowed_book_ids:
            # 대출한 도서의 카테고리 빈도 분석
            borrowed_categories = db.query(BookModel.category, func.count(BookModel.category).label('cnt'))\
                .filter(BookModel.book_id.in_(borrowed_book_ids))\
                .group_by(BookModel.category)\
                .order_by(func.count(BookModel.category).desc())\
                .all()
            
            if borrowed_categories:
                top_category = borrowed_categories[0][0]
                # 같은 카테고리에서 대출하지 않은 도서 추천
                category_books = db.query(BookModel)\
                    .filter(BookModel.category == top_category)\
                    .filter(BookModel.book_id.notin_(borrowed_book_ids))\
                    .filter(BookModel.stock_quantity > 0)\
                    .limit(req.limit).all()
                recommended_books.extend(category_books)
    
    # 2. 특정 카테고리 요청 시
    if req.category and len(recommended_books) < req.limit:
        category_books = db.query(BookModel)\
            .filter(BookModel.category == req.category)\
            .filter(BookModel.stock_quantity > 0)\
            .limit(req.limit - len(recommended_books)).all()
        for book in category_books:
            if book not in recommended_books:
                recommended_books.append(book)
    
    # 3. 높은 평점 도서 추천
    if len(recommended_books) < req.limit:
        # 평균 평점이 높은 도서 (MySQL 호환: COALESCE 사용)
        high_rated = db.query(
            BookModel,
            func.coalesce(func.avg(ReviewModel.rating), 0).label('avg_rating')
        ).outerjoin(ReviewModel).group_by(BookModel.book_id)\
            .filter(BookModel.stock_quantity > 0)\
            .order_by(func.coalesce(func.avg(ReviewModel.rating), 0).desc())\
            .limit(req.limit * 2).all()
        
        for book, rating in high_rated:
            if book not in recommended_books and len(recommended_books) < req.limit:
                recommended_books.append(book)
    
    # 4. 인기 도서 (대출 횟수 기반) 보충
    if len(recommended_books) < req.limit:
        popular = db.query(
            BookModel,
            func.count(LoanModel.loan_id).label('loan_count')
        ).outerjoin(LoanModel).group_by(BookModel.book_id)\
            .filter(BookModel.stock_quantity > 0)\
            .order_by(func.count(LoanModel.loan_id).desc())\
            .limit(req.limit * 2).all()
        
        for book, count in popular:
            if book not in recommended_books and len(recommended_books) < req.limit:
                recommended_books.append(book)
    
    # 결과 포맷팅
    result = []
    for book in recommended_books[:req.limit]:
        # 평균 평점 계산
        stats = db.query(func.avg(ReviewModel.rating)).filter(ReviewModel.book_id == book.book_id).scalar()
        result.append({
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author,
            "category": book.category,
            "description": book.description,
            "stock_quantity": book.stock_quantity,
            "average_rating": round(float(stats), 1) if stats else None
        })
    
    return {"recommendations": result}

# ========== Chatbot API ==========
@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(req: ChatRequest, db: Session = Depends(get_db)):
    """AI 챗봇 API - Gemini + RAG"""
    try:
        from google import genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            # API 키가 없으면 간단한 규칙 기반 응답
            print("⚠️  [AI Chat] GEMINI_API_KEY가 설정되지 않음 - 폴백 모드 사용")
            return fallback_response(req.message, db)
        
        print(f"🤖 [AI Chat] Gemini API 연결 시도...")
        print(f"📝 [AI Chat] 사용자 질문: {req.message}")
        
        # 새로운 google.genai 클라이언트 생성
        client = genai.Client(api_key=api_key)
        
        # RAG 컨텍스트 수집
        context = get_rag_context(db)
        
        # 프롬프트 구성
        prompt = f"""당신은 IBD Library 도서관의 AI 사서입니다. 친절하고 도움이 되는 답변을 제공하세요.
아래 도서관 정보를 참고하여 사용자 질문에 답변하세요.

{context}

사용자 질문: {req.message}

답변 규칙:
1. 도서관 관련 질문에 정확하게 답변하세요.
2. 도서 추천 요청 시 보유 도서 목록에서 추천하세요.
3. 모르는 정보는 솔직히 모른다고 하세요.
4. 한국어로 친근하게 대답하세요.
"""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        
        print(f"✅ [AI Chat] Gemini API 응답 성공!")
        print(f"📤 [AI Chat] 응답 길이: {len(response.text)} 글자")
        
        return ChatResponse(
            response=response.text,
            sources=["books 테이블", "system_config 테이블"]
        )
        
    except Exception as e:
        # 오류 시 폴백 응답
        print(f"❌ [AI Chat] Gemini API 오류: {str(e)}")
        return fallback_response(req.message, db)

def fallback_response(message: str, db: Session) -> ChatResponse:
    """API 키 없거나 오류 시 규칙 기반 응답"""
    message_lower = message.lower()
    
    # 운영시간 관련
    if "운영" in message or "시간" in message or "언제" in message:
        return ChatResponse(
            response="📍 IBD Library 운영시간\n\n• 평일: 09:00 - 21:00\n• 주말: 10:00 - 18:00\n• 휴관일: 매월 첫째, 셋째 월요일",
            sources=["system_config"]
        )
    
    # 대출 관련
    if "대출" in message or "빌리" in message or "반납" in message:
        config = db.query(SystemConfig).filter(SystemConfig.key == "loan_period_days").first()
        period = config.value if config else "14"
        limit_config = db.query(SystemConfig).filter(SystemConfig.key == "max_loan_limit").first()
        limit = limit_config.value if limit_config else "3"
        return ChatResponse(
            response=f"📚 대출 안내\n\n• 대출 기간: {period}일\n• 최대 대출 권수: {limit}권\n• 연장: 1회 가능 (연체 시 불가)",
            sources=["system_config"]
        )
    
    # 도서 추천
    if "추천" in message or "책" in message:
        books = db.query(BookModel).filter(BookModel.stock_quantity > 0).limit(3).all()
        if books:
            book_list = "\n".join([f"• 《{b.title}》 - {b.author}" for b in books])
            return ChatResponse(
                response=f"✨ 추천 도서\n\n{book_list}\n\n더 많은 도서는 도서 목록에서 확인해보세요!",
                sources=["books"]
            )
    
    # 기본 응답
    return ChatResponse(
        response="안녕하세요! IBD Library AI 사서입니다. 🤖\n\n무엇을 도와드릴까요?\n• 도서관 운영시간\n• 대출/반납 안내\n• 도서 추천\n\n질문해주세요!",
        sources=[]
    )
