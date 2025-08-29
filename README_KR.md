# CISA KEV 모니터링 시스템

CISA Known Exploited Vulnerabilities (KEV) 카탈로그를 실시간으로 모니터링하는 시스템입니다. 이 웹 애플리케이션은 최신 취약점 정보, 검색 기능, 포괄적인 모니터링 기능을 제공합니다.

## 🚀 주요 기능

- **실시간 데이터 동기화**: CISA KEV API와 자동으로 동기화
- **고급 검색**: CVE, 벤더, 제품, 날짜별 취약점 필터링
- **종합 대시보드**: 취약점 통계 및 트렌드 조회
- **REST API**: OpenAPI 문서와 함께 완전한 API 액세스 제공
- **반응형 디자인**: 모던 UI와 모바일 친화적 인터페이스
- **Docker 지원**: Docker Compose를 통한 쉬운 배포

## 🛠 기술 스택

### 백엔드
- **FastAPI**: 고성능 Python 웹 프레임워크
- **PostgreSQL**: 취약점 데이터 저장을 위한 주 데이터베이스
- **Redis**: 캐싱 및 세션 저장소
- **SQLAlchemy**: 비동기 지원하는 ORM
- **Pydantic**: 데이터 검증 및 직렬화

### 프론트엔드
- **Next.js 15**: App Router를 사용하는 React 프레임워크
- **TypeScript**: 타입 안전한 개발
- **Tailwind CSS**: 유틸리티 우선 CSS 프레임워크
- **React Query**: 데이터 페칭 및 캐싱

## 📦 설치

### 필요 조건
- Docker & Docker Compose
- Python 3.11+ (로컬 개발용)
- Node.js 18+ (로컬 개발용)

### Docker를 이용한 빠른 시작

1. **저장소 클론**
   ```bash
   git clone https://github.com/Mkway/cisa-kev-monitor.git
   cd cisa-kev-monitor
   ```

2. **서비스 시작**
   ```bash
   docker-compose up -d
   ```

3. **데이터베이스 초기화**
   ```bash
   # 백엔드 컨테이너 접속
   docker exec -it cisa-kev-backend bash
   
   # 데이터베이스 초기화 실행
   python -m app.cli init-db
   
   # CISA KEV 데이터 동기화
   python -m app.cli sync-data
   ```

4. **애플리케이션 접속**
   - 프론트엔드: http://localhost:3000
   - 백엔드 API: http://localhost:8000
   - API 문서: http://localhost:8000/docs

### 로컬 개발 환경

#### 백엔드 설정

1. **백엔드 디렉토리로 이동**
   ```bash
   cd backend
   ```

2. **가상환경 생성**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 또는
   venv\Scripts\activate     # Windows
   ```

3. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **PostgreSQL 및 Redis 시작**
   ```bash
   docker-compose up -d postgres redis
   ```

5. **데이터베이스 마이그레이션 실행**
   ```bash
   python -m app.cli init-db
   ```

6. **개발 서버 시작**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### 프론트엔드 설정

1. **프론트엔드 디렉토리로 이동**
   ```bash
   cd frontend
   ```

2. **의존성 설치**
   ```bash
   npm install
   ```

3. **개발 서버 시작**
   ```bash
   npm run dev
   ```

## 🎯 사용법

### API 엔드포인트

#### 취약점
- `GET /api/vulnerabilities/` - 페이지네이션으로 취약점 목록 조회
- `GET /api/vulnerabilities/{cve}` - 특정 취약점 조회
- `POST /api/vulnerabilities/search` - 고급 검색
- `GET /api/vulnerabilities/stats/overview` - 통계 조회

#### 동기화
- `GET /api/sync/status` - 동기화 상태 확인
- `POST /api/sync/manual` - 수동 동기화 실행

#### 벤더
- `GET /api/vulnerabilities/vendors/` - 벤더 목록 조회

### CLI 명령어

```bash
# 데이터베이스 작업
python -m app.cli init-db          # 데이터베이스 초기화
python -m app.cli reset-db         # 데이터베이스 초기화

# 데이터 동기화
python -m app.cli sync-data        # CISA KEV 데이터 동기화
python -m app.cli check-updates    # 업데이트 확인

# 개발 유틸리티
python -m app.cli dev-seed         # 테스트 데이터 생성
```

### 자동화 스크립트

프로젝트에는 개발 워크플로우를 위한 자동화 스크립트가 포함되어 있습니다:

```bash
# 프로젝트 초기화
./scripts/dev_workflow.sh init

# 일일 워크플로우
./scripts/dev_workflow.sh start-day
./scripts/dev_workflow.sh end-day

# 개발 환경
./scripts/dev_workflow.sh start-dev
./scripts/dev_workflow.sh stop-dev

# 프로젝트 상태
./scripts/dev_workflow.sh status
```

## 🔧 설정

### 환경 변수

#### 백엔드 (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/cisa_kev
REDIS_URL=redis://localhost:6379
CISA_KEV_API_URL=https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
ALLOWED_HOSTS=["http://localhost:3000"]
```

#### 프론트엔드 (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 데이터베이스 스키마

### 주요 테이블
- **vulnerabilities**: CISA KEV의 핵심 취약점 데이터
- **vendors**: 소프트웨어/하드웨어 벤더
- **products**: 취약한 제품
- **sync_logs**: 데이터 동기화 이력

### 주요 필드
- **CVE ID**: Common Vulnerabilities and Exposures 식별자
- **CVSS Score**: Common Vulnerability Scoring System 점수
- **Known Exploited**: 취약점이 실제로 악용되고 있는지 여부
- **Date Added**: KEV 카탈로그에 취약점이 추가된 날짜
- **Due Date**: 연방 기관의 수정 마감일

## 🧪 테스팅

```bash
# 백엔드 테스트
cd backend
pytest

# 프론트엔드 테스트
cd frontend
npm test

# 통합 테스트
npm run test:e2e
```

## 📈 모니터링

### 헬스 체크
- 데이터베이스 연결: `/api/health/db`
- Redis 연결: `/api/health/redis`
- 외부 API: `/api/health/external`

### 로그
- 애플리케이션 로그: `backend/logs/app.log`
- 접근 로그: `backend/logs/access.log`
- 동기화 로그: 데이터베이스 테이블 `sync_logs`

## 🚀 배포

### 프로덕션 배포

1. **환경 파일 업데이트**
   ```bash
   cp .env.example .env
   # 프로덕션 값으로 .env 수정
   ```

2. **빌드 및 배포**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **프로덕션 데이터베이스 초기화**
   ```bash
   docker exec -it cisa-kev-backend python -m app.cli init-db
   docker exec -it cisa-kev-backend python -m app.cli sync-data
   ```

### SSL 설정
HTTPS를 위한 리버스 프록시(nginx) 설정:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## 📝 API 문서

- **OpenAPI 명세**: `/docs`에서 확인 가능 (Swagger UI)
- **ReDoc**: `/redoc`에서 확인 가능
- **OpenAPI JSON**: `/openapi.json`에서 확인 가능

### API 사용 예제

```javascript
// 취약점 조회
const response = await fetch('/api/vulnerabilities/?page=1&per_page=10');
const data = await response.json();

// 취약점 검색
const searchResponse = await fetch('/api/vulnerabilities/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Microsoft',
    dateFrom: '2024-01-01',
    dateTo: '2024-12-31'
  })
});
```

## 🤝 기여하기

1. **저장소 포크**
2. **기능 브랜치 생성**: `git checkout -b feature/new-feature`
3. **변경사항 커밋**: `git commit -m "새 기능 추가"`
4. **브랜치에 푸시**: `git push origin feature/new-feature`
5. **Pull Request 생성**

### 개발 가이드라인
- Python PEP 8 스타일 가이드 준수
- TypeScript strict 모드 사용
- 새 기능에 대한 단위 테스트 작성
- API 변경 시 문서 업데이트

## 🐛 문제 해결

### 일반적인 문제들

#### 데이터베이스 연결 실패
```bash
# PostgreSQL 컨테이너 확인
docker-compose logs postgres

# 데이터베이스 재시작
docker-compose restart postgres
```

#### CORS 에러
```bash
# backend/app/core/config.py에서 CORS 설정 확인
# ALLOWED_HOSTS에 프론트엔드 URL이 포함되어 있는지 확인
```

#### 빌드 실패
```bash
# 빌드 캐시 정리
docker-compose down -v
docker-compose build --no-cache
```

#### 외부 접속 문제
WSL/로컬 개발 환경에서 외부 접속을 위해:
1. `ALLOWED_HOSTS`에 IP 주소 추가
2. 방화벽 규칙 설정
3. 프론트엔드 `NEXT_PUBLIC_API_URL` 업데이트

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- KEV 카탈로그를 제공해주는 [CISA](https://www.cisa.gov/)
- 뛰어난 웹 프레임워크를 제공하는 [FastAPI](https://fastapi.tiangolo.com/)
- React 프레임워크를 제공하는 [Next.js](https://nextjs.org/)
- 모든 훌륭한 도구와 라이브러리를 제공하는 오픈 소스 커뮤니티

## 📞 지원

- **이슈**: [GitHub Issues](https://github.com/Mkway/cisa-kev-monitor/issues)
- **토론**: [GitHub Discussions](https://github.com/Mkway/cisa-kev-monitor/discussions)
- **이메일**: mkway1004@gmail.com

---

**🔒 보안 공지**: 이 도구는 방어적 보안 목적으로만 설계되었습니다. 보안 팀이 알려진 취약점을 모니터링하고 대응하는 데 도움을 줍니다. 조직의 보안 정책에 따라 책임감 있게 사용하시기 바랍니다.