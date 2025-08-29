# Claude 개발 지침서

## 프로젝트 개요
- **프로젝트명**: CISA KEV 모니터링 시스템
- **목적**: CISA Known Exploited Vulnerabilities 데이터를 실시간으로 모니터링하고 관리하는 웹 시스템
- **데이터 소스**: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json

## 기술 스택
- **백엔드**: Python + FastAPI
- **데이터베이스**: PostgreSQL + Redis (캐싱)
- **프론트엔드**: Next.js + TypeScript
- **배포**: Docker + Docker Compose

## 핵심 개발 원칙
1. **보안 우선**: 방어적 보안 도구로만 개발, 악의적 용도 코드 거부
2. **단계적 개발**: MVP → 고급 기능 → 확장 기능 순서로 진행
3. **코드 품질**: 타입 안전성, 에러 핸들링, 테스트 코드 필수
4. **실시간 모니터링**: 데이터 변경 감지 및 즉시 알림 시스템

## 프로젝트 구조
```
kev/
├── backend/          # FastAPI 백엔드
│   ├── app/
│   ├── models/       # 데이터베이스 모델
│   ├── api/          # API 엔드포인트
│   ├── services/     # 비즈니스 로직
│   └── tasks/        # 백그라운드 작업
├── frontend/         # Next.js 프론트엔드
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── types/
├── docker-compose.yml
└── docs/
```

## 개발 단계별 체크리스트

### Phase 1: MVP (기본 기능)
- [ ] FastAPI 프로젝트 설정
- [ ] PostgreSQL 스키마 설계
- [ ] CISA KEV 데이터 수집 스크립트
- [ ] 기본 REST API (CRUD)
- [ ] Next.js 프론트엔드 설정
- [ ] 취약점 목록 페이지
- [ ] 기본 검색 및 필터링
- [ ] Docker 환경 설정

### Phase 2: 고급 기능
- [ ] WebSocket 실시간 업데이트
- [ ] 사용자 인증/인가
- [ ] 고급 검색 (전문 검색)
- [ ] 개인화된 대시보드
- [ ] 알림 시스템 기초

### Phase 3: 확장 기능
- [ ] 이메일/Slack 알림
- [ ] 데이터 시각화
- [ ] 내보내기 기능 (CSV/PDF)
- [ ] API 문서화
- [ ] 성능 최적화

## API 설계 원칙
```
GET    /api/vulnerabilities       # 취약점 목록
GET    /api/vulnerabilities/:cve  # CVE 상세 조회
GET    /api/vulnerabilities/search # 검색
GET    /api/statistics            # 통계
POST   /api/notifications         # 알림 설정
```

## 데이터베이스 스키마 핵심 테이블
1. **vulnerabilities**: 취약점 정보
2. **vendors**: 벤더/제조사 정보
3. **products**: 제품 정보
4. **notifications**: 알림 설정
5. **users**: 사용자 정보

## 중요한 개발 고려사항

### 보안
- API 키 환경변수 관리
- SQL 인젝션 방지
- XSS 공격 방지
- CORS 설정
- Rate Limiting 구현

### 성능
- 데이터베이스 인덱싱
- Redis 캐싱 전략
- 페이지네이션 구현
- 이미지/정적 파일 최적화

### 에러 핸들링
- 상세한 로깅 시스템
- 사용자 친화적 에러 메시지
- API 응답 표준화
- 장애 복구 메커니즘

## 테스트 전략
- **단위 테스트**: pytest (백엔드), Jest (프론트엔드)
- **통합 테스트**: API 엔드포인트 테스트
- **E2E 테스트**: Playwright/Cypress 고려
- **성능 테스트**: 대용량 데이터 처리 테스트

## 모니터링 및 운영
- **로깅**: 구조화된 로깅 (JSON 형태)
- **헬스체크**: 데이터베이스, 외부 API 연결 상태
- **메트릭**: 응답 시간, 에러율, 사용량
- **백업**: 정기적 데이터베이스 백업

## 개발 환경 설정 명령어
```bash
# 프로젝트 초기화
mkdir -p backend frontend
cd backend && python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary redis

# 프론트엔드 설정
cd frontend && npx create-next-app@latest . --typescript --tailwind --eslint

# Docker 환경 실행
docker-compose up -d

# 개발 서버 실행
# 백엔드: uvicorn app.main:app --reload
# 프론트엔드: npm run dev
```

## 코딩 컨벤션
- **Python**: PEP 8, Black 포매터, mypy 타입 체킹
- **TypeScript**: ESLint + Prettier, strict 모드
- **커밋 메시지**: Conventional Commits 형식
- **브랜치**: feature/기능명, bugfix/버그명

## 주의사항
1. **CISA API 호출 제한**: 과도한 요청 방지를 위해 적절한 간격 유지
2. **데이터 무결성**: CVE 데이터 검증 및 중복 처리 로직 필수
3. **사용자 경험**: 대용량 데이터 로딩시 로딩 인디케이터 표시
4. **확장성**: 미래 추가 데이터 소스 연동을 고려한 아키텍처 설계

## 문제 해결 가이드
- **데이터베이스 연결 실패**: Docker 컨테이너 상태 확인
- **CORS 에러**: FastAPI CORS 미들웨어 설정 확인
- **빌드 실패**: Node.js 버전 및 의존성 확인
- **성능 이슈**: 데이터베이스 쿼리 최적화 및 캐싱 적용

## Git Commit 자동화 워크플로우

### 개발 진행사항 업데이트 자동화
매번 git commit 할 때마다 다음 명령어를 순서대로 실행:

```bash
# 1. 개발 진행사항 업데이트
python scripts/task_manager.py report

# 2. 변경사항 스테이징
git add .

# 3. 커밋 (진행사항이 자동으로 포함됨)
git commit -m "your commit message"

# 4. GitHub 푸시
git push origin main
```

### 자동화 스크립트 생성 (선택사항)
```bash
# scripts/auto_commit.sh 생성
#!/bin/bash
python scripts/task_manager.py report
git add .
git commit -m "$1"
git push origin main

# 사용법: ./scripts/auto_commit.sh "commit message"
```

### Claude 개발 지침
- **매번 코드 변경 후**: task_manager.py report 실행으로 진행사항 업데이트
- **커밋 전**: 항상 개발 진행사항 보고서 최신화
- **GitHub 동기화**: 모든 변경사항은 즉시 원격 저장소에 반영
- **커밋 메시지**: Claude Code 태그와 Co-Authored-By는 제외하고 작성 (사용자가 단독 작성자로 표시)

## 참고 문서
- FastAPI 공식 문서: https://fastapi.tiangolo.com/
- Next.js 공식 문서: https://nextjs.org/docs
- CISA KEV 문서: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
