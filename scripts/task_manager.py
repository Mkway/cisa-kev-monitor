#!/usr/bin/env python3
"""
CISA KEV 프로젝트 Task Manager
TODO 리스트 관리 및 개발 히스토리 추적 자동화 도구
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

@dataclass
class Task:
    id: str
    content: str
    status: TaskStatus
    activeForm: str
    created_at: str
    updated_at: str
    phase: str = "MVP"
    priority: str = "medium"
    estimated_hours: int = 0
    actual_hours: int = 0
    description: str = ""
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class HistoryEntry:
    timestamp: str
    action: str
    task_id: str
    old_status: Optional[str]
    new_status: Optional[str]
    notes: str = ""

class TaskManager:
    def __init__(self, project_root: str = "/home/wsl/kev"):
        self.project_root = project_root
        self.tasks_file = os.path.join(project_root, "data", "tasks.json")
        self.history_file = os.path.join(project_root, "data", "history.json")
        self.reports_dir = os.path.join(project_root, "reports")
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        self.tasks: Dict[str, Task] = {}
        self.history: List[HistoryEntry] = []
        
        self.load_data()

    def load_data(self):
        """저장된 데이터 로드"""
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for task_data in data:
                    task = Task(**task_data)
                    task.status = TaskStatus(task.status)
                    self.tasks[task.id] = task
        
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                self.history = [HistoryEntry(**entry) for entry in history_data]

    def save_data(self):
        """데이터 저장"""
        # Tasks 저장
        tasks_data = []
        for task in self.tasks.values():
            task_dict = asdict(task)
            task_dict['status'] = task.status.value
            tasks_data.append(task_dict)
        
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, indent=2, ensure_ascii=False)
        
        # History 저장
        history_data = [asdict(entry) for entry in self.history]
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)

    def add_task(self, content: str, active_form: str, phase: str = "MVP", 
                 priority: str = "medium", estimated_hours: int = 0, 
                 description: str = "", dependencies: List[str] = None) -> str:
        """새 작업 추가"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        now = datetime.now().isoformat()
        
        task = Task(
            id=task_id,
            content=content,
            status=TaskStatus.PENDING,
            activeForm=active_form,
            created_at=now,
            updated_at=now,
            phase=phase,
            priority=priority,
            estimated_hours=estimated_hours,
            description=description,
            dependencies=dependencies or []
        )
        
        self.tasks[task_id] = task
        
        # 히스토리 추가
        self.add_history("created", task_id, None, "pending", f"새 작업 생성: {content}")
        
        self.save_data()
        return task_id

    def update_task_status(self, task_id: str, new_status: TaskStatus, notes: str = ""):
        """작업 상태 업데이트"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        old_status = task.status.value
        task.status = new_status
        task.updated_at = datetime.now().isoformat()
        
        # 히스토리 추가
        self.add_history("status_changed", task_id, old_status, new_status.value, notes)
        
        self.save_data()

    def add_history(self, action: str, task_id: str, old_status: Optional[str], 
                   new_status: Optional[str], notes: str = ""):
        """히스토리 엔트리 추가"""
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(),
            action=action,
            task_id=task_id,
            old_status=old_status,
            new_status=new_status,
            notes=notes
        )
        self.history.append(entry)

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """상태별 작업 조회"""
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_phase(self, phase: str) -> List[Task]:
        """단계별 작업 조회"""
        return [task for task in self.tasks.values() if task.phase == phase]

    def generate_daily_report(self) -> str:
        """일일 리포트 생성"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 오늘의 활동 조회
        today_history = [h for h in self.history 
                        if h.timestamp.startswith(today)]
        
        # 현재 상태별 작업 수
        pending_count = len(self.get_tasks_by_status(TaskStatus.PENDING))
        in_progress_count = len(self.get_tasks_by_status(TaskStatus.IN_PROGRESS))
        completed_count = len(self.get_tasks_by_status(TaskStatus.COMPLETED))
        blocked_count = len(self.get_tasks_by_status(TaskStatus.BLOCKED))
        
        report = f"""# CISA KEV 프로젝트 일일 리포트 - {today}

## 전체 현황
- 📝 대기중: {pending_count}개
- 🔄 진행중: {in_progress_count}개  
- ✅ 완료: {completed_count}개
- 🚫 블록: {blocked_count}개

## 오늘의 활동 ({len(today_history)}건)
"""
        
        for entry in today_history:
            task = self.tasks.get(entry.task_id)
            task_title = task.content if task else "Unknown Task"
            report += f"- [{entry.timestamp[11:16]}] {entry.action}: {task_title}\n"
            if entry.notes:
                report += f"  💬 {entry.notes}\n"
        
        report += "\n## 진행중인 작업\n"
        in_progress_tasks = self.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        for task in in_progress_tasks:
            report += f"- 🔄 {task.content} ({task.phase})\n"
        
        report += "\n## 다음 예정 작업\n"
        pending_tasks = self.get_tasks_by_status(TaskStatus.PENDING)[:5]  # 상위 5개
        for task in pending_tasks:
            report += f"- 📝 {task.content} ({task.phase})\n"
        
        return report

    def export_claude_todos(self) -> List[Dict]:
        """Claude TodoWrite 형식으로 내보내기"""
        claude_todos = []
        for task in self.tasks.values():
            claude_todo = {
                "content": task.content,
                "status": task.status.value,
                "activeForm": task.activeForm
            }
            claude_todos.append(claude_todo)
        return claude_todos

    def import_from_claude_todos(self, claude_todos: List[Dict]):
        """Claude TodoWrite 형식에서 가져오기"""
        for todo in claude_todos:
            # 기존 작업이 있는지 확인
            existing_task = None
            for task in self.tasks.values():
                if task.content == todo["content"]:
                    existing_task = task
                    break
            
            if existing_task:
                # 상태 업데이트
                new_status = TaskStatus(todo["status"])
                if existing_task.status != new_status:
                    self.update_task_status(existing_task.id, new_status, "Claude에서 동기화")
            else:
                # 새 작업 추가
                self.add_task(
                    content=todo["content"],
                    active_form=todo["activeForm"]
                )

def init_mvp_tasks():
    """MVP 단계 초기 작업들 생성"""
    tm = TaskManager()
    
    mvp_tasks = [
        {
            "content": "FastAPI 프로젝트 기본 구조 설정",
            "active_form": "FastAPI 프로젝트 기본 구조 설정 중",
            "phase": "MVP",
            "priority": "high",
            "estimated_hours": 4,
            "description": "FastAPI 프로젝트 초기 설정, 디렉토리 구조, 기본 설정 파일 생성"
        },
        {
            "content": "PostgreSQL 데이터베이스 스키마 설계 및 구축",
            "active_form": "PostgreSQL 데이터베이스 스키마 설계 및 구축 중",
            "phase": "MVP", 
            "priority": "high",
            "estimated_hours": 6,
            "description": "취약점, 벤더, 제품 테이블 설계 및 SQLAlchemy 모델 생성"
        },
        {
            "content": "CISA KEV 데이터 수집 스크립트 개발",
            "active_form": "CISA KEV 데이터 수집 스크립트 개발 중",
            "phase": "MVP",
            "priority": "high", 
            "estimated_hours": 8,
            "description": "JSON 데이터 파싱, 검증, 데이터베이스 저장 로직 구현"
        },
        {
            "content": "기본 REST API 엔드포인트 구현",
            "active_form": "기본 REST API 엔드포인트 구현 중",
            "phase": "MVP",
            "priority": "medium",
            "estimated_hours": 6,
            "description": "취약점 조회, 검색, 통계 API 구현"
        },
        {
            "content": "Next.js 프론트엔드 프로젝트 설정",
            "active_form": "Next.js 프론트엔드 프로젝트 설정 중",
            "phase": "MVP",
            "priority": "medium",
            "estimated_hours": 3,
            "description": "Next.js, TypeScript, Tailwind CSS 설정"
        }
    ]
    
    for task_data in mvp_tasks:
        tm.add_task(**task_data)
    
    print(f"✅ MVP 단계 {len(mvp_tasks)}개 작업이 생성되었습니다.")
    return tm

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            init_mvp_tasks()
        elif sys.argv[1] == "report":
            tm = TaskManager()
            report = tm.generate_daily_report()
            print(report)
            
            # 리포트 파일로 저장
            today = datetime.now().strftime("%Y%m%d")
            report_file = os.path.join(tm.reports_dir, f"daily_report_{today}.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n📁 리포트 저장: {report_file}")
        elif sys.argv[1] == "status":
            tm = TaskManager()
            print("📊 현재 프로젝트 상태:")
            for status in TaskStatus:
                tasks = tm.get_tasks_by_status(status)
                print(f"  {status.value}: {len(tasks)}개")
    else:
        print("Usage: python task_manager.py [init|report|status]")