#!/bin/bash

# CISA KEV 프로젝트 개발 워크플로우 자동화 스크립트

set -e

PROJECT_ROOT="/home/wsl/kev"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
DATA_DIR="$PROJECT_ROOT/data"
REPORTS_DIR="$PROJECT_ROOT/reports"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 프로젝트 초기 설정
init_project() {
    log_info "프로젝트 초기화 중..."
    
    # 디렉토리 생성
    mkdir -p "$DATA_DIR" "$REPORTS_DIR"
    mkdir -p "$PROJECT_ROOT/backend" "$PROJECT_ROOT/frontend"
    mkdir -p "$PROJECT_ROOT/docs" "$PROJECT_ROOT/tests"
    
    # Python 가상환경 설정 (backend)
    if [ ! -d "$PROJECT_ROOT/backend/venv" ]; then
        log_info "Python 가상환경 생성 중..."
        cd "$PROJECT_ROOT/backend"
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        log_success "Python 가상환경 생성 완료"
    fi
    
    # MVP 작업 목록 초기화
    log_info "MVP 작업 목록 초기화 중..."
    python3 "$SCRIPTS_DIR/task_manager.py" init
    
    log_success "프로젝트 초기화 완료!"
}

# 일일 작업 시작
start_day() {
    log_info "새로운 작업일 시작..."
    
    # 현재 상태 확인
    log_info "현재 프로젝트 상태:"
    python3 "$SCRIPTS_DIR/task_manager.py" status
    
    # 일일 리포트 생성
    python3 "$SCRIPTS_DIR/task_manager.py" report
    
    log_success "작업 준비 완료! 좋은 하루 되세요! 🚀"
}

# 작업 완료 체크
end_day() {
    log_info "작업일 마무리 중..."
    
    # 일일 리포트 생성 및 저장
    python3 "$SCRIPTS_DIR/task_manager.py" report
    
    # Git 상태 확인
    if [ -d "$PROJECT_ROOT/.git" ]; then
        log_info "Git 상태 확인:"
        git status --short
        
        # 변경사항이 있으면 경고
        if [ -n "$(git status --porcelain)" ]; then
            log_warning "커밋되지 않은 변경사항이 있습니다!"
        fi
    fi
    
    log_success "오늘 하루 수고하셨습니다! 💪"
}

# 개발 환경 실행
start_dev() {
    log_info "개발 환경 시작 중..."
    
    # Docker 컨테이너 실행 (있는 경우)
    if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
        log_info "Docker 컨테이너 시작..."
        cd "$PROJECT_ROOT"
        docker-compose up -d
        log_success "Docker 컨테이너 시작됨"
    fi
    
    # 백엔드 개발 서버 실행
    if [ -f "$PROJECT_ROOT/backend/app/main.py" ]; then
        log_info "백엔드 서버를 백그라운드에서 시작합니다..."
        cd "$PROJECT_ROOT/backend"
        source venv/bin/activate
        nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
        echo $! > backend.pid
        log_success "백엔드 서버 시작됨 (PID: $(cat backend.pid))"
    fi
    
    # 프론트엔드 개발 서버 실행 준비
    if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
        log_info "프론트엔드 서버 시작 준비..."
        log_info "다음 명령어로 프론트엔드를 실행하세요:"
        echo "  cd $PROJECT_ROOT/frontend && npm run dev"
    fi
}

# 개발 환경 정지
stop_dev() {
    log_info "개발 환경 정지 중..."
    
    # 백엔드 서버 종료
    if [ -f "$PROJECT_ROOT/backend/backend.pid" ]; then
        PID=$(cat "$PROJECT_ROOT/backend/backend.pid")
        kill $PID 2>/dev/null || true
        rm "$PROJECT_ROOT/backend/backend.pid"
        log_success "백엔드 서버 종료됨"
    fi
    
    # Docker 컨테이너 정지
    if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
        cd "$PROJECT_ROOT"
        docker-compose down
        log_success "Docker 컨테이너 정지됨"
    fi
}

# 프로젝트 상태 확인
check_status() {
    log_info "프로젝트 전체 상태 확인 중..."
    
    echo "📊 작업 현황:"
    python3 "$SCRIPTS_DIR/task_manager.py" status
    
    echo ""
    echo "📁 프로젝트 구조:"
    tree "$PROJECT_ROOT" -I 'venv|node_modules|__pycache__|.git' -L 2 || ls -la "$PROJECT_ROOT"
    
    echo ""
    echo "🐳 Docker 상태:"
    if command -v docker >/dev/null 2>&1; then
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        echo "Docker가 설치되지 않음"
    fi
    
    echo ""
    echo "💻 개발 서버 상태:"
    if [ -f "$PROJECT_ROOT/backend/backend.pid" ]; then
        PID=$(cat "$PROJECT_ROOT/backend/backend.pid")
        if kill -0 $PID 2>/dev/null; then
            echo "✅ 백엔드 서버 실행 중 (PID: $PID)"
        else
            echo "❌ 백엔드 서버 PID 파일 존재하나 프로세스 없음"
        fi
    else
        echo "⭕ 백엔드 서버 중지됨"
    fi
}

# 작업 추가
add_task() {
    if [ $# -lt 2 ]; then
        log_error "사용법: $0 add-task \"작업내용\" \"진행형태\""
        exit 1
    fi
    
    CONTENT="$1"
    ACTIVE_FORM="$2"
    
    log_info "새 작업 추가: $CONTENT"
    python3 -c "
from scripts.task_manager import TaskManager
tm = TaskManager()
task_id = tm.add_task('$CONTENT', '$ACTIVE_FORM')
print(f'✅ 작업 추가됨: {task_id}')
"
}

# 작업 상태 업데이트
update_task() {
    if [ $# -lt 2 ]; then
        log_error "사용법: $0 update-task TASK_ID STATUS [notes]"
        exit 1
    fi
    
    TASK_ID="$1"
    STATUS="$2"
    NOTES="${3:-}"
    
    log_info "작업 상태 업데이트: $TASK_ID -> $STATUS"
    python3 -c "
from scripts.task_manager import TaskManager, TaskStatus
tm = TaskManager()
tm.update_task_status('$TASK_ID', TaskStatus('$STATUS'), '$NOTES')
print('✅ 작업 상태 업데이트됨')
"
}

# 도움말
show_help() {
    echo "CISA KEV 프로젝트 개발 워크플로우 도구"
    echo ""
    echo "사용법: $0 [명령어] [옵션]"
    echo ""
    echo "명령어:"
    echo "  init                프로젝트 초기 설정"
    echo "  start-day          작업일 시작 (상태 확인 및 리포트)"
    echo "  end-day            작업일 마무리 (리포트 저장)"
    echo "  start-dev          개발 환경 시작"
    echo "  stop-dev           개발 환경 정지"
    echo "  status             프로젝트 전체 상태 확인"
    echo "  add-task           새 작업 추가"
    echo "  update-task        작업 상태 업데이트"
    echo "  help               이 도움말 표시"
    echo ""
    echo "예시:"
    echo "  $0 init"
    echo "  $0 start-day"
    echo "  $0 add-task \"FastAPI 설치\" \"FastAPI 설치 중\""
    echo "  $0 update-task task_20240828_143022 completed \"작업 완료\""
    echo ""
}

# 메인 로직
case "${1:-help}" in
    "init")
        init_project
        ;;
    "start-day")
        start_day
        ;;
    "end-day")
        end_day
        ;;
    "start-dev")
        start_dev
        ;;
    "stop-dev")
        stop_dev
        ;;
    "status")
        check_status
        ;;
    "add-task")
        add_task "$2" "$3"
        ;;
    "update-task")
        update_task "$2" "$3" "$4"
        ;;
    "help"|*)
        show_help
        ;;
esac