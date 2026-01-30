from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import books, users, loans, reviews
from app.database import init_db, SessionLocal
from app.db_models import Book, User, UserRole


def seed_data():
    """초기 샘플 데이터 삽입"""
    db = SessionLocal()
    try:
        # 관리자 사용자 생성
        if db.query(User).count() == 0:
            import hashlib
            admin = User(
                email="admin@library.com",
                password=hashlib.sha256("admin123".encode()).hexdigest(),
                name="관리자",
                role=UserRole.LIBRARIAN
            )
            member = User(
                email="user@example.com",
                password=hashlib.sha256("user123".encode()).hexdigest(),
                name="홍길동",
                phone="010-1234-5678",
                address="서울시 강남구"
            )
            db.add_all([admin, member])
            db.commit()
            print("✅ Sample users seeded")
        
        # 도서 데이터 생성
        if db.query(Book).count() == 0:
            sample_books = [
                Book(isbn="978-89-123-0001", title="클린 코드", author="로버트 C. 마틴", publisher="인사이트", published_year=2013, category="프로그래밍", stock_quantity=3),
                Book(isbn="978-89-123-0002", title="디자인 패턴", author="GoF", publisher="프로텍미디어", published_year=2015, category="프로그래밍", stock_quantity=2),
                Book(isbn="978-89-123-0003", title="리팩터링", author="마틴 파울러", publisher="한빛미디어", published_year=2020, category="프로그래밍", stock_quantity=1),
                Book(isbn="978-89-123-0004", title="도메인 주도 설계", author="에릭 에반스", publisher="위키북스", published_year=2011, category="아키텍처", stock_quantity=2),
                Book(isbn="978-89-123-0005", title="실용주의 프로그래머", author="데이비드 토머스", publisher="인사이트", published_year=2022, category="프로그래밍", stock_quantity=4),
                Book(isbn="978-89-123-0006", title="소프트웨어 장인", author="산드로 만쿠소", publisher="길벗", published_year=2015, category="커리어", stock_quantity=2),
            ]
            db.add_all(sample_books)
            db.commit()
            print("✅ Sample books seeded")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 lifecycle 이벤트"""
    init_db()
    seed_data()
    print("🚀 Database initialized")
    yield
    print("👋 Application shutdown")


app = FastAPI(
    title="IBD Library API",
    description="도서관 관리 시스템 API - Vibe Coding으로 생성",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(books.router, prefix="/api/books", tags=["도서"])
app.include_router(users.router, prefix="/api/users", tags=["회원"])
app.include_router(loans.router, prefix="/api/loans", tags=["대출"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["리뷰"])

# 정적 파일 경로
STATIC_DIR = Path(__file__).parent.parent / "static"


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}


# 정적 파일 서빙 - 별도 라우터로 등록
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

spa_router = APIRouter()

if STATIC_DIR.exists():
    # assets 마운트
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")
    
    # 루트 경로
    @spa_router.get("/", response_class=HTMLResponse)
    async def serve_index():
        return FileResponse(STATIC_DIR / "index.html")
    
    # SPA 폴백 - 가장 마지막에 처리
    @spa_router.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """SPA 폴백 라우팅"""
        # /api로 시작하는 경로는 이 라우터에서 처리하지 않음
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")

    # SPA 라우터를 가장 마지막에 등록 (API 라우터 이후)
    app.include_router(spa_router, tags=["SPA"])
