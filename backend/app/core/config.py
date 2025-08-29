"""
애플리케이션 설정 관리
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # API 설정
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "CISA KEV Monitoring System"
    VERSION: str = "0.1.0"
    
    # 데이터베이스 설정
    DATABASE_URL: str = "postgresql://kev_user:kev_password@localhost:5432/kev_db"
    
    # Redis 설정
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CISA KEV API 설정
    CISA_KEV_URL: str = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    
    # CORS 설정 - 외부 접속 허용
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8000",
        "http://172.25.5.154:3000",
        "http://172.25.5.154:8000",
        "*"  # 개발 환경에서만 사용
    ]
    
    # 보안 설정
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 전역 설정 인스턴스
settings = Settings()