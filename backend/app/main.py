from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import books

app = FastAPI(
    title="IBD Library API",
    description="도서관 관리 시스템 API - Vibe Coding으로 생성",
    version="1.0.0"
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
