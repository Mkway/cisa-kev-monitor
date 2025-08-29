-- CISA KEV 데이터베이스 초기 설정 SQL
-- PostgreSQL 15 기준

-- UUID 확장 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 전문 검색을 위한 확장 (선택사항)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 인덱스 최적화를 위한 설정
SET maintenance_work_mem = '256MB';

-- 초기 데이터베이스 설정 완료 로그
DO $$
BEGIN
    RAISE NOTICE 'CISA KEV 데이터베이스 초기 설정 완료';
    RAISE NOTICE '- UUID 확장: 활성화';
    RAISE NOTICE '- 검색 확장: 활성화';
    RAISE NOTICE '- 메모리 설정: 최적화';
END $$;