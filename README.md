# CISA KEV 모니터링 시스템

CISA Known Exploited Vulnerabilities 데이터를 실시간으로 모니터링하고 관리하는 웹 시스템입니다.

## 🚀 Quick Start

### 백엔드 서버 실행
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드 서버 실행
```bash
cd frontend  
npm run dev
```

### 서비스 접속
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 📊 현재 구현 상태

### ✅ 완료된 기능

#### 백엔드 (FastAPI)
- [x] FastAPI 프로젝트 설정 및 구조화
- [x] PostgreSQL 데이터베이스 스키마 설계
- [x] SQLAlchemy ORM 모델 (Vendor, Product, Vulnerability, History, SyncStatus)
- [x] CISA KEV 데이터 동기화 서비스
  - 1,405개 취약점 데이터 수집 완료
  - 자동 중복 제거 및 정규화
  - 백그라운드 동기화 지원
- [x] 완전한 REST API 엔드포인트
  - 취약점 목록 조회 (페이지네이션, 정렬, 필터링)
  - CVE 상세 정보 조회
  - 고급 검색 (POST /api/vulnerabilities/search)
  - 통계 정보 (전체/벤더/월별)
  - 벤더/제품 목록
  - 동기화 관리 API
- [x] Swagger UI 문서화 (/docs)

#### 프론트엔드 (Next.js)
- [x] Next.js 15 + TypeScript 프로젝트 설정
- [x] Tailwind CSS 디자인 시스템
- [x] 타입 안전한 API 클라이언트 (axios)
- [x] UI 컴포넌트 라이브러리
  - Button, Card, Input, Badge, Pagination
- [x] 취약점 관련 컴포넌트
  - VulnerabilityCard (취약점 카드 표시)
  - SearchAndFilters (검색 및 필터링 UI)
- [x] 메인 대시보드 페이지
  - 실시간 통계 카드
  - 취약점 목록 표시 (카드 형태)
  - 페이지네이션 지원
  - 고급 검색 및 필터링
  - 반응형 디자인

### 🚧 개발 예정 (Phase 2)
- [ ] 취약점 상세 페이지
- [ ] 실시간 WebSocket 알림
- [ ] 사용자 인증/인가
- [ ] 개인화된 대시보드
- [ ] 데이터 시각화 차트

### 🔮 향후 계획 (Phase 3)
- [ ] 이메일/Slack 알림
- [ ] 내보내기 기능 (CSV/PDF)
- [ ] 성능 최적화 (Redis 캐싱)
- [ ] 모바일 앱 지원

## 📊 데이터베이스 현황

현재 데이터베이스에 저장된 데이터:
- **취약점**: 1,405개
- **벤더**: 340개 (Microsoft, Adobe, Google 등)
- **제품**: 500개 이상
- **랜섬웨어 관련**: 다수 (known_ransomware_use=true)

## 🛠️ 기술 스택

- **백엔드**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- **프론트엔드**: Next.js 15, TypeScript, Tailwind CSS, Axios
- **데이터베이스**: PostgreSQL (Docker)
- **캐싱**: Redis (향후)
- **배포**: Docker, Docker Compose

## 🏗️ 프로젝트 구조

```
kev/
├── backend/                  # FastAPI 백엔드
│   ├── app/
│   │   ├── api/              # API 라우터
│   │   │   └── endpoints/    # 엔드포인트 구현
│   │   ├── models/           # SQLAlchemy 모델
│   │   ├── schemas/          # Pydantic 스키마
│   │   ├── services/         # 비즈니스 로직
│   │   └── core/             # 설정 및 데이터베이스
│   └── venv/                 # Python 가상환경
├── frontend/                 # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # React 컴포넌트
│   │   │   ├── ui/           # 공통 UI 컴포넌트
│   │   │   └── vulnerability/# 취약점 관련 컴포넌트
│   │   ├── api/              # API 클라이언트
│   │   ├── types/            # TypeScript 타입
│   │   └── lib/              # 유틸리티 함수
│   └── node_modules/
├── docker-compose.yml        # Docker 환경
└── docs/                     # 문서
```

## 📋 개발 가이드

자세한 개발 가이드라인은 [CLAUDE.md](./CLAUDE.md) 파일을 참조하세요.

## 🔒 보안 고려사항

- API 응답에서 민감 정보 제외
- SQL 인젝션 방지 (SQLAlchemy 사용)
- XSS 방지 (입력값 검증)
- CORS 설정 적용
- 환경 변수를 통한 설정 관리

## 📈 성능 최적화

- 데이터베이스 인덱싱 적용
- 페이지네이션으로 대용량 데이터 처리
- API 응답 최적화
- 프론트엔드 코드 스플리팅 (Next.js)

---

**최종 업데이트**: 2025-08-29  
**버전**: MVP 1.0 완료