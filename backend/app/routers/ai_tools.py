"""
AI Tools - 챗봇 함수 호출(Function Calling) 도구 정의
LLM이 사용할 수 있는 도구들의 JSON 스키마와 실행 함수를 정의
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from app.db_models import (
    Book as BookModel, 
    Loan as LoanModel, 
    User as UserModel, 
    SystemConfig,
    LoanStatus
)

# ========== Function Calling JSON 스키마 ===========
# google.genai function calling 형식

TOOL_DECLARATIONS = [
    {
        "name": "borrow_book",
        "description": "도서를 대출합니다. 사용자 ID와 도서 ID 또는 도서 제목이 필요합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "대출할 사용자의 ID"
                },
                "book_id": {
                    "type": "integer",
                    "description": "대출할 도서의 ID (book_id 또는 book_title 중 하나 필요)"
                },
                "book_title": {
                    "type": "string",
                    "description": "대출할 도서의 제목 (book_id 또는 book_title 중 하나 필요)"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "return_book",
        "description": "대출한 도서를 반납합니다. 대출 ID 또는 도서 제목과 사용자 ID가 필요합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "loan_id": {
                    "type": "integer",
                    "description": "반납할 대출 ID"
                },
                "user_id": {
                    "type": "integer",
                    "description": "사용자 ID (book_title과 함께 사용)"
                },
                "book_title": {
                    "type": "string",
                    "description": "반납할 도서의 제목"
                }
            }
        }
    },
    {
        "name": "extend_loan",
        "description": "대출 기간을 연장합니다. 대출 ID 또는 도서 제목과 사용자 ID가 필요합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "loan_id": {
                    "type": "integer",
                    "description": "연장할 대출 ID"
                },
                "user_id": {
                    "type": "integer",
                    "description": "사용자 ID (book_title과 함께 사용)"
                },
                "book_title": {
                    "type": "string",
                    "description": "연장할 도서의 제목"
                }
            }
        }
    },
    {
        "name": "get_user_loans",
        "description": "사용자의 현재 대출 목록을 조회합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "조회할 사용자 ID"
                },
                "status": {
                    "type": "string",
                    "enum": ["borrowed", "returned", "overdue"],
                    "description": "대출 상태 필터 (optional)"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "search_books",
        "description": "도서를 검색합니다. 제목, 저자, 카테고리로 검색할 수 있습니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "검색 키워드 (제목 또는 저자)"
                },
                "category": {
                    "type": "string",
                    "description": "카테고리 필터"
                }
            }
        }
    }
]


# ========== 도구 실행 함수들 ==========

def execute_borrow_book(db: Session, user_id: int, book_id: Optional[int] = None, book_title: Optional[str] = None) -> Dict[str, Any]:
    """도서 대출 실행"""
    # 사용자 확인
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        return {"success": False, "message": f"회원 ID {user_id}를 찾을 수 없습니다"}
    
    # 도서 찾기
    if book_id:
        book = db.query(BookModel).filter(BookModel.book_id == book_id).first()
    elif book_title:
        book = db.query(BookModel).filter(BookModel.title.ilike(f"%{book_title}%")).first()
    else:
        return {"success": False, "message": "도서 ID 또는 도서 제목을 입력해주세요"}
    
    if not book:
        return {"success": False, "message": "도서를 찾을 수 없습니다"}
    
    # 재고 확인
    if book.stock_quantity <= 0:
        return {"success": False, "message": f"《{book.title}》은(는) 현재 재고가 없습니다"}
    
    # 대출 권수 제한 확인
    limit_config = db.query(SystemConfig).filter(SystemConfig.key == "max_loan_limit").first()
    max_limit = int(limit_config.value) if limit_config else 3
    
    current_loans = db.query(LoanModel).filter(
        LoanModel.user_id == user_id,
        LoanModel.status == LoanStatus.BORROWED
    ).count()
    
    if current_loans >= max_limit:
        return {"success": False, "message": f"대출 가능 권수({max_limit}권)를 초과했습니다"}
    
    # 대출 기간 설정
    period_config = db.query(SystemConfig).filter(SystemConfig.key == "loan_period_days").first()
    period_days = int(period_config.value) if period_config else 14
    
    # 대출 처리
    now = datetime.now()
    new_loan = LoanModel(
        user_id=user_id,
        book_id=book.book_id,
        loan_date=now,
        due_date=now + timedelta(days=period_days),
        status=LoanStatus.BORROWED
    )
    
    book.stock_quantity -= 1
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    
    return {
        "success": True,
        "message": f"《{book.title}》을(를) {user.name}님께 대출했습니다. 반납 예정일: {new_loan.due_date.strftime('%Y-%m-%d')}",
        "loan_id": new_loan.loan_id,
        "book_title": book.title,
        "due_date": new_loan.due_date.strftime('%Y-%m-%d')
    }


def execute_return_book(db: Session, loan_id: Optional[int] = None, user_id: Optional[int] = None, book_title: Optional[str] = None) -> Dict[str, Any]:
    """도서 반납 실행"""
    # 대출 정보 찾기
    if loan_id:
        loan = db.query(LoanModel).filter(LoanModel.loan_id == loan_id).first()
    elif user_id and book_title:
        # 사용자 ID와 도서 제목으로 대출 찾기
        loan = db.query(LoanModel).join(BookModel).filter(
            LoanModel.user_id == user_id,
            BookModel.title.ilike(f"%{book_title}%"),
            LoanModel.status == LoanStatus.BORROWED
        ).first()
    else:
        return {"success": False, "message": "대출 ID 또는 (사용자 ID + 도서 제목)을 입력해주세요"}
    
    if not loan:
        return {"success": False, "message": "해당 대출 정보를 찾을 수 없습니다"}
    
    if loan.status == LoanStatus.RETURNED:
        return {"success": False, "message": "이미 반납된 도서입니다"}
    
    # 반납 처리
    loan.return_date = datetime.now()
    loan.status = LoanStatus.RETURNED
    
    # 재고 복구
    book = db.query(BookModel).filter(BookModel.book_id == loan.book_id).first()
    if book:
        book.stock_quantity += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"《{book.title}》이(가) 반납되었습니다",
        "book_title": book.title
    }


def execute_extend_loan(db: Session, loan_id: Optional[int] = None, user_id: Optional[int] = None, book_title: Optional[str] = None) -> Dict[str, Any]:
    """대출 연장 실행"""
    # 대출 정보 찾기
    if loan_id:
        loan = db.query(LoanModel).filter(LoanModel.loan_id == loan_id).first()
    elif user_id and book_title:
        loan = db.query(LoanModel).join(BookModel).filter(
            LoanModel.user_id == user_id,
            BookModel.title.ilike(f"%{book_title}%"),
            LoanModel.status == LoanStatus.BORROWED
        ).first()
    else:
        return {"success": False, "message": "대출 ID 또는 (사용자 ID + 도서 제목)을 입력해주세요"}
    
    if not loan:
        return {"success": False, "message": "해당 대출 정보를 찾을 수 없습니다"}
    
    if loan.status != LoanStatus.BORROWED:
        return {"success": False, "message": "대출 중인 도서만 연장할 수 있습니다"}
    
    # 최대 연장 횟수 확인
    ext_config = db.query(SystemConfig).filter(SystemConfig.key == "max_extension_count").first()
    max_extensions = int(ext_config.value) if ext_config else 1
    
    if loan.extension_count >= max_extensions:
        return {"success": False, "message": f"연장은 최대 {max_extensions}회까지 가능합니다"}
    
    # 연장 처리
    ext_period_config = db.query(SystemConfig).filter(SystemConfig.key == "extension_period_days").first()
    extension_days = int(ext_period_config.value) if ext_period_config else 7
    
    loan.due_date = loan.due_date + timedelta(days=extension_days)
    loan.extension_count += 1
    db.commit()
    db.refresh(loan)
    
    book = db.query(BookModel).filter(BookModel.book_id == loan.book_id).first()
    
    return {
        "success": True,
        "message": f"《{book.title}》 대출이 연장되었습니다. 새 반납 예정일: {loan.due_date.strftime('%Y-%m-%d')}",
        "book_title": book.title,
        "new_due_date": loan.due_date.strftime('%Y-%m-%d')
    }


def execute_get_user_loans(db: Session, user_id: int, status: Optional[str] = None) -> Dict[str, Any]:
    """사용자 대출 목록 조회"""
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        return {"success": False, "message": f"회원 ID {user_id}를 찾을 수 없습니다"}
    
    query = db.query(LoanModel).filter(LoanModel.user_id == user_id)
    
    if status == "borrowed":
        query = query.filter(LoanModel.status == LoanStatus.BORROWED)
    elif status == "returned":
        query = query.filter(LoanModel.status == LoanStatus.RETURNED)
    elif status == "overdue":
        query = query.filter(
            LoanModel.status == LoanStatus.BORROWED,
            LoanModel.due_date < datetime.now()
        )
    
    loans = query.all()
    
    loan_list = []
    for loan in loans:
        book = db.query(BookModel).filter(BookModel.book_id == loan.book_id).first()
        loan_list.append({
            "loan_id": loan.loan_id,
            "book_title": book.title if book else "Unknown",
            "loan_date": loan.loan_date.strftime('%Y-%m-%d'),
            "due_date": loan.due_date.strftime('%Y-%m-%d'),
            "status": loan.status.value,
            "is_overdue": loan.due_date < datetime.now() and loan.status == LoanStatus.BORROWED
        })
    
    return {
        "success": True,
        "user_name": user.name,
        "total_count": len(loan_list),
        "loans": loan_list
    }


def execute_search_books(db: Session, keyword: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
    """도서 검색"""
    query = db.query(BookModel)
    
    if keyword:
        query = query.filter(
            (BookModel.title.ilike(f"%{keyword}%")) | 
            (BookModel.author.ilike(f"%{keyword}%"))
        )
    
    if category:
        query = query.filter(BookModel.category == category)
    
    books = query.limit(10).all()
    
    book_list = [{
        "book_id": b.book_id,
        "title": b.title,
        "author": b.author,
        "category": b.category,
        "stock_quantity": b.stock_quantity
    } for b in books]
    
    return {
        "success": True,
        "count": len(book_list),
        "books": book_list
    }


# ========== 도구 실행 라우터 ==========

def execute_tool(tool_name: str, args: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """도구 이름과 인자를 받아 해당 함수를 실행"""
    print(f"🔧 [AI Tool] 도구 실행: {tool_name}")
    print(f"📋 [AI Tool] 인자: {args}")
    
    if tool_name == "borrow_book":
        result = execute_borrow_book(db, **args)
    elif tool_name == "return_book":
        result = execute_return_book(db, **args)
    elif tool_name == "extend_loan":
        result = execute_extend_loan(db, **args)
    elif tool_name == "get_user_loans":
        result = execute_get_user_loans(db, **args)
    elif tool_name == "search_books":
        result = execute_search_books(db, **args)
    else:
        result = {"success": False, "message": f"알 수 없는 도구: {tool_name}"}
    
    print(f"✅ [AI Tool] 결과: {result.get('success', False)}")
    return result
