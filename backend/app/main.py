"""
CISA KEV 모니터링 시스템 - FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import api_router

app = FastAPI(
    title="CISA KEV Monitoring System",
    description="CISA Known Exploited Vulnerabilities 모니터링 시스템",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "CISA KEV Monitoring System API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )