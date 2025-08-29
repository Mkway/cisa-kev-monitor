"""
API 라우터 설정
"""

from fastapi import APIRouter
from app.api.endpoints import vulnerabilities, sync

# 메인 API 라우터
api_router = APIRouter()

@api_router.get("/status")
async def api_status():
    """API 상태 확인"""
    return {"status": "API is running", "version": "0.1.0"}

# 라우터 등록
api_router.include_router(
    vulnerabilities.router, 
    prefix="/vulnerabilities", 
    tags=["vulnerabilities"]
)

api_router.include_router(
    sync.router, 
    prefix="/sync", 
    tags=["sync"]
)