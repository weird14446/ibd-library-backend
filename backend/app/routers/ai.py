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
    """AI 챗봇 API - Gemini + RAG + Function Calling"""
    try:
        from google import genai
        from google.genai import types
        from app.routers.ai_tools import TOOL_DECLARATIONS, execute_tool
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️  [AI Chat] GEMINI_API_KEY가 설정되지 않음 - 폴백 모드 사용")
            return fallback_response(req.message, req.user_id, db)
        
        print(f"🤖 [AI Chat] Gemini API 연결 시도 (Function Calling 활성화)")
        print(f"📝 [AI Chat] 사용자 질문: {req.message}")
        if req.user_id:
            print(f"👤 [AI Chat] 사용자 ID: {req.user_id}")
        
        client = genai.Client(api_key=api_key)
        
        # 모델 설정 (환경변수에서 읽기)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        print(f"🤖 [AI Chat] 사용 모델: {model_name}")
        
        # RAG 컨텍스트 수집
        context = get_rag_context(db)
        
        # 사용자 정보 조회
        user_info = "미로그인 상태입니다. 대출/반납/연장 등의 작업을 요청할 경우 로그인이 필요하다고 안내해주세요."
        if req.user_id:
            user = db.query(UserModel).filter(UserModel.user_id == req.user_id).first()
            if user:
                user_info = f"✅ 로그인됨: {user.name}님 (ID: {user.user_id}, 이메일: {user.email})"
                print(f"👤 [AI Chat] 로그인 사용자: {user.name} (ID: {user.user_id})")
            else:
                user_info = f"사용자 ID {req.user_id}로 로그인됨 (이름 조회 불가)"
        
        # 시스템 프롬프트 구성
        system_instruction = f"""당신은 IBD Library 도서관의 AI 사서입니다. 친절하고 도움이 되는 답변을 제공하세요.

{context}

**당신이 할 수 있는 작업:**
- 도서 대출 (borrow_book): 사용자가 책을 빌리고 싶다고 하면 실행. user_id는 자동으로 제공됩니다.
- 도서 반납 (return_book): 사용자가 책을 반납하고 싶다고 하면 실행. user_id는 자동으로 제공됩니다.
- 대출 연장 (extend_loan): 사용자가 대출 기간을 연장하고 싶다고 하면 실행. user_id는 자동으로 제공됩니다.
- 대출 조회 (get_user_loans): 사용자가 자신의 대출 현황을 보고 싶다고 하면 실행. user_id는 자동으로 제공됩니다.
- 도서 검색 (search_books): 사용자가 책을 검색하고 싶다고 하면 실행

**현재 사용자 상태:** {user_info}

중요: 사용자가 로그인되어 있으면 (✅ 표시가 있으면) 별도로 ID를 물어보지 말고 바로 함수를 호출하세요!
함수 호출 시 user_id 파라미터는 시스템이 자동으로 설정합니다.

답변 규칙:
1. 로그인된 사용자가 대출/반납/연장을 요청하면 즉시 해당 함수를 호출하세요.
2. 함수 호출 결과를 바탕으로 사용자에게 친절하게 안내해주세요.
3. 한국어로 답변하세요.
"""
        
        # Function Calling용 Tool 설정
        tools = [types.Tool(function_declarations=[
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters=tool.get("parameters")
            ) for tool in TOOL_DECLARATIONS
        ])]
        
        # 첫 번째 요청
        response = client.models.generate_content(
            model=model_name,
            contents=req.message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=tools,
                temperature=0.7
            )
        )
        
        # Function Call 처리
        final_response = ""
        sources = ["books 테이블", "system_config 테이블"]
        
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                # 함수 호출인 경우
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    tool_name = function_call.name
                    tool_args = dict(function_call.args) if function_call.args else {}
                    
                    # user_id가 없으면 요청에서 가져오기
                    if 'user_id' not in tool_args and req.user_id:
                        tool_args['user_id'] = req.user_id
                    
                    print(f"🔧 [AI Chat] 함수 호출 감지: {tool_name}")
                    
                    # 도구 실행
                    tool_result = execute_tool(tool_name, tool_args, db)
                    sources.append(f"function:{tool_name}")
                    
                    # 결과를 LLM에 전달하여 최종 응답 생성
                    follow_up = client.models.generate_content(
                        model=model_name,
                        contents=[
                            types.Content(role="user", parts=[types.Part(text=req.message)]),
                            types.Content(role="model", parts=[part]),
                            types.Content(role="user", parts=[types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response=tool_result
                                )
                            )])
                        ],
                        config=types.GenerateContentConfig(
                            system_instruction="함수 호출 결과를 바탕으로 사용자에게 친절하게 결과를 안내해주세요. 한국어로 답변하세요.",
                            temperature=0.7
                        )
                    )
                    final_response = follow_up.text
                
                # 일반 텍스트 응답인 경우
                elif hasattr(part, 'text') and part.text:
                    final_response += part.text
        
        if not final_response:
            final_response = response.text if hasattr(response, 'text') else "응답을 생성할 수 없습니다."
        
        print(f"✅ [AI Chat] 응답 완료!")
        print(f"📤 [AI Chat] 응답 길이: {len(final_response)} 글자")
        
        return ChatResponse(
            response=final_response,
            sources=sources
        )
        
    except Exception as e:
        print(f"❌ [AI Chat] Gemini API 오류: {str(e)}")
        return fallback_response(req.message, req.user_id, db)

def fallback_response(message: str, user_id: Optional[int], db: Session) -> ChatResponse:
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
