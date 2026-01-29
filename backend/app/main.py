from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import books
from app.database import init_db, SessionLocal
from app.db_models import Book, BookCategory


def seed_data():
    """초기 샘플 데이터 삽입"""
    db = SessionLocal()
    try:
        if db.query(Book).count() == 0:
            sample_books = [
                Book(title="클린 코드", author="로버트 C. 마틴", category=BookCategory.PROGRAMMING, available=True, cover="📘"),
                Book(title="디자인 패턴", author="GoF", category=BookCategory.PROGRAMMING, available=True, cover="📗"),
                Book(title="리팩터링", author="마틴 파울러", category=BookCategory.PROGRAMMING, available=False, cover="📙"),
                Book(title="도메인 주도 설계", author="에릭 에반스", category=BookCategory.ARCHITECTURE, available=True, cover="📕"),
                Book(title="실용주의 프로그래머", author="데이비드 토머스", category=BookCategory.PROGRAMMING, available=True, cover="📔"),
                Book(title="소프트웨어 장인", author="산드로 만쿠소", category=BookCategory.CAREER, available=False, cover="📓"),
            ]
            db.add_all(sample_books)
            db.commit()
            print("✅ Sample data seeded successfully")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 lifecycle 이벤트"""
    # Startup
    init_db()
    seed_data()
    print("🚀 Database initialized")
    yield
    # Shutdown
    print("👋 Application shutdown")


app = FastAPI(
    title="IBD Library API",
    description="도서관 관리 시스템 API - Vibe Coding으로 생성",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(books.router, prefix="/api/books", tags=["books"])

# 정적 파일 경로
STATIC_DIR = Path(__file__).parent.parent / "static"


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# 정적 파일 서빙 (API 라우터 이후에 마운트)
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """SPA 폴백 라우팅 - 모든 경로에서 index.html 반환"""
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
