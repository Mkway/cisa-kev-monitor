# CISA KEV 프로젝트 자동화 도구

## 개요
이 디렉토리는 CISA KEV 모니터링 시스템 개발을 위한 자동화 도구들을 포함합니다.

## 도구 목록

### 1. task_manager.py
TODO 리스트 관리 및 개발 히스토리 추적 도구

**기능:**
- 작업 생성, 상태 업데이트, 진행 추적
- 개발 히스토리 자동 기록
- 일일/주간 진행 리포트 생성
- Claude TodoWrite와 동기화

**사용법:**
```bash
# MVP 작업 목록 초기화
python3 task_manager.py init

# 현재 상태 확인
python3 task_manager.py status

# 일일 리포트 생성
python3 task_manager.py report
```

### 2. dev_workflow.sh
개발 워크플로우 자동화 스크립트

**기능:**
- 프로젝트 초기 설정
- 일일 작업 시작/마무리 루틴
- 개발 환경 시작/정지
- 프로젝트 상태 종합 확인

**사용법:**
```bash
# 프로젝트 초기 설정
./scripts/dev_workflow.sh init

# 작업일 시작
./scripts/dev_workflow.sh start-day

# 개발 환경 시작
./scripts/dev_workflow.sh start-dev

# 현재 상태 확인
./scripts/dev_workflow.sh status

# 작업 추가
./scripts/dev_workflow.sh add-task "새 작업" "새 작업 진행 중"

# 작업 상태 업데이트
./scripts/dev_workflow.sh update-task task_id completed "완료됨"

# 작업일 마무리
./scripts/dev_workflow.sh end-day

# 개발 환경 정지
./scripts/dev_workflow.sh stop-dev
```

## 자동화된 워크플로우

### 일일 루틴
1. **아침 시작**
   ```bash
   ./scripts/dev_workflow.sh start-day
   ```
   - 현재 프로젝트 상태 확인
   - 일일 리포트 생성
   - 오늘 할 일 목록 표시

2. **개발 중**
   - 작업 상태는 자동으로 추적
   - Claude와 함께 작업하며 TodoWrite 동기화
   - 필요시 수동으로 작업 추가/업데이트

3. **저녁 마무리**
   ```bash
   ./scripts/dev_workflow.sh end-day
   ```
   - 오늘의 진행사항 리포트 저장
   - Git 상태 확인
   - 내일 준비사항 확인

### 개발 환경 관리
```bash
# 개발 시작시
./scripts/dev_workflow.sh start-dev

# 개발 완료시
./scripts/dev_workflow.sh stop-dev
```

## 데이터 저장소

### 파일 구조
```
data/
├── tasks.json          # 작업 목록 데이터
└── history.json        # 개발 히스토리 데이터

reports/
├── daily_report_YYYYMMDD.md  # 일일 리포트
└── weekly_summary_YYYYWW.md  # 주간 요약 (추후 구현)
```

### 작업 데이터 구조
```json
{
  "id": "task_20240828_143022",
  "content": "FastAPI 프로젝트 설정",
  "status": "completed",
  "activeForm": "FastAPI 프로젝트 설정 중",
  "created_at": "2024-08-28T14:30:22",
  "updated_at": "2024-08-28T16:45:30",
  "phase": "MVP",
  "priority": "high",
  "estimated_hours": 4,
  "actual_hours": 3,
  "description": "FastAPI 초기 설정 및 프로젝트 구조 생성"
}
```

## Claude 연동

### TodoWrite 동기화
```python
from scripts.task_manager import TaskManager

tm = TaskManager()

# Claude TodoWrite 형식으로 내보내기
claude_todos = tm.export_claude_todos()

# Claude TodoWrite에서 가져오기
claude_todos = [
    {"content": "작업1", "status": "pending", "activeForm": "작업1 진행 중"},
    {"content": "작업2", "status": "completed", "activeForm": "작업2 완료"}
]
tm.import_from_claude_todos(claude_todos)
```

## 확장 계획

### Phase 2 추가 예정 기능
- 주간/월간 요약 리포트
- 작업 시간 추적 및 생산성 분석
- Git 커밋과 작업 연동
- Slack/Discord 알림 연동
- 웹 대시보드 (선택사항)

### 통합 예정 도구
- GitHub Issues 연동
- Jira/Linear 연동 (필요시)
- 코드 품질 메트릭 추적
- CI/CD 파이프라인 상태 모니터링

## 트러블슈팅

### 일반적인 문제
1. **권한 에러**: `chmod +x scripts/*.sh`로 실행 권한 부여
2. **Python 모듈 없음**: 가상환경 활성화 확인
3. **데이터 파일 없음**: `init` 명령어로 초기화

### 로그 확인
- 백엔드 로그: `backend/logs/backend.log`
- 스크립트 실행 로그: 터미널 출력 확인
- 작업 히스토리: `data/history.json`

## 기여 가이드
1. 새로운 자동화 스크립트는 `scripts/` 디렉토리에 추가
2. 문서는 항상 최신 상태로 유지
3. 스크립트는 실행 권한 설정 필수
4. 에러 처리 및 로깅 포함 권장