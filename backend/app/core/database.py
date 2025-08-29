"""
데이터베이스 초기화 및 관리 유틸리티
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import logging
from app.core.config import settings
from app.models.base import Base, engine
from app.models.vulnerability import (
    Vendor, Product, Vulnerability, 
    VulnerabilityHistory, DataSyncStatus
)

logger = logging.getLogger(__name__)

def create_database_if_not_exists():
    """데이터베이스가 없으면 생성"""
    try:
        # 데이터베이스 URL에서 데이터베이스명 분리
        db_url_parts = settings.DATABASE_URL.rsplit('/', 1)
        if len(db_url_parts) == 2:
            base_url = db_url_parts[0]
            db_name = db_url_parts[1]
            
            # postgres 데이터베이스에 연결해서 대상 데이터베이스 확인/생성
            admin_engine = create_engine(f"{base_url}/postgres")
            
            with admin_engine.connect() as conn:
                # 데이터베이스 존재 확인
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": db_name}
                )
                
                if not result.fetchone():
                    # 데이터베이스 생성
                    conn.execute(text("COMMIT"))  # 트랜잭션 종료
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    logger.info(f"데이터베이스 '{db_name}' 생성 완료")
                else:
                    logger.info(f"데이터베이스 '{db_name}' 이미 존재")
            
            admin_engine.dispose()
            
    except OperationalError as e:
        logger.warning(f"데이터베이스 생성 중 오류: {e}")
        logger.info("기존 데이터베이스를 사용합니다.")

def create_tables():
    """모든 테이블 생성"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error(f"테이블 생성 중 오류: {e}")
        raise

def drop_tables():
    """모든 테이블 삭제 (개발용)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("데이터베이스 테이블 삭제 완료")
    except Exception as e:
        logger.error(f"테이블 삭제 중 오류: {e}")
        raise

def init_database():
    """데이터베이스 전체 초기화"""
    logger.info("데이터베이스 초기화 시작")
    
    # 1. 데이터베이스 생성 (필요시)
    create_database_if_not_exists()
    
    # 2. 테이블 생성
    create_tables()
    
    # 3. 초기 데이터 삽입
    insert_initial_data()
    
    logger.info("데이터베이스 초기화 완료")

def insert_initial_data():
    """초기 데이터 삽입"""
    from app.models.base import SessionLocal
    
    db = SessionLocal()
    try:
        # DataSyncStatus 초기 레코드 생성
        existing_sync = db.query(DataSyncStatus).filter_by(source="cisa_kev").first()
        if not existing_sync:
            sync_status = DataSyncStatus(
                source="cisa_kev",
                status="pending",
                total_records=0,
                processed_records=0
            )
            db.add(sync_status)
            db.commit()
            logger.info("초기 동기화 상태 레코드 생성")
        
    except Exception as e:
        logger.error(f"초기 데이터 삽입 중 오류: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def reset_database():
    """데이터베이스 초기화 (모든 데이터 삭제 후 재생성)"""
    logger.warning("데이터베이스 리셋 시작 - 모든 데이터가 삭제됩니다!")
    
    drop_tables()
    create_tables()
    insert_initial_data()
    
    logger.info("데이터베이스 리셋 완료")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            init_database()
        elif command == "reset":
            reset_database()
        elif command == "create-tables":
            create_tables()
        elif command == "drop-tables":
            drop_tables()
        else:
            print("Usage: python database.py [init|reset|create-tables|drop-tables]")
    else:
        init_database()