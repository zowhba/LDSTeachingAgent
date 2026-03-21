#!/bin/bash

# 백엔드만 실행하는 스크립트

echo "📡 FastAPI 백엔드 서버 시작..."

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 기존 프로세스 정리 (포트 8000)
echo "🔍 기존에 실행 중인 8000 포트 확인 중..."
if command -v lsof > /dev/null; then
    BACKEND_PIDS=$(lsof -t -i:8000)
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo "🛑 8000 포트를 사용하는 프로세스를 종료합니다. (PID: $BACKEND_PIDS)"
        kill -9 $BACKEND_PIDS 2>/dev/null
        sleep 1
    fi
fi

# 가상환경 활성화
if [ -d ".venv" ] && [ ! -x ".venv/bin/python" ]; then
    echo "⚠️ 손상된 가상환경(.venv)을 발견하여 초기화합니다..."
    rm -rf .venv
fi

if [ ! -d ".venv" ]; then
    echo "🔧 가상환경 생성 중..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# 의존성 설치
pip install -q -r backend/requirements.txt

echo ""
echo "✅ 백엔드 서버: http://localhost:8000"
echo "📚 API 문서: http://localhost:8000/docs"
echo ""

# 서버 실행
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
