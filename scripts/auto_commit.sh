 # scripts/auto_commit.sh 생성
 #!/bin/bash
 python scripts/task_manager.py report
 git add .
 git commit -m "$1"
 git push origin main

 # 사용법: ./scripts/auto_commit.sh "commit message"
