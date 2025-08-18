#!/bin/bash

# Django 서버 실행 스크립트
# 사용법: ./run_server.sh

set -e  # 에러 발생시 스크립트 중단

echo "=== Django 서버 시작 ==="
echo "현재 디렉토리: $(pwd)"
echo "시작 시간: $(date)"
echo "=========================="

# conda 환경이 이미 활성화되어 있는지 확인
if [[ "$CONDA_DEFAULT_ENV" == "wasso" ]]; then
    echo "✅ conda 환경 'wasso'가 이미 활성화되어 있습니다"
else
    echo "❌ conda 환경 'wasso'가 활성화되지 않았습니다"
    echo "다음 명령어로 환경을 활성화한 후 스크립트를 실행하세요:"
    echo "conda activate wasso && ./scripts/runserver.sh"
    exit 1
fi

echo "Python 버전: $(python --version)"

# Poetry를 통해 Django 서버 실행
echo "Django 서버 실행 중..."
echo "서버 주소: http://0.0.0.0:8001"
echo "종료하려면 Ctrl+C를 누르세요"
echo "=========================="

# 포그라운드에서 서버 실행
poetry run python manage.py runserver 0.0.0.0:8001