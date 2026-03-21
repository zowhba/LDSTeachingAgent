#!/bin/bash

# LDS Teaching Agent - 실행 스크립트
# FastAPI 백엔드와 Vue.js 프론트엔드를 동시에 실행합니다.

echo "🚀 LDS Teaching Agent v2.0 시작..."
echo ""

# 프로젝트 루트 디렉토리
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 기존 프로세스 정리 (포트 8000, 5173 확인 및 종료)
echo "🔍 기존에 실행 중인 서버 확인 중..."
if command -v lsof > /dev/null; then
    BACKEND_PIDS=$(lsof -t -i:8000)
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo "🛑 8000 포트를 사용하는 프로세스를 종료합니다. (PID: $BACKEND_PIDS)"
        kill -9 $BACKEND_PIDS 2>/dev/null
        sleep 1
    fi
    FRONTEND_PIDS=$(lsof -t -i:5173)
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo "🛑 5173 포트를 사용하는 프로세스를 종료합니다. (PID: $FRONTEND_PIDS)"
        kill -9 $FRONTEND_PIDS 2>/dev/null
        sleep 1
    fi
fi

# 백엔드 실행
echo "📡 백엔드 서버 시작 중..."
cd "$PROJECT_DIR"

if [ -d ".venv" ] && [ ! -x ".venv/bin/python" ]; then
    echo "⚠️ 손상된 가상환경(.venv)을 발견하여 초기화합니다..."
    rm -rf .venv
fi

if [ ! -d ".venv" ]; then
    echo "🔧 가상환경 생성 중..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 프론트엔드 실행
echo "🎨 프론트엔드 서버 시작 중..."
cd "$PROJECT_DIR/frontend"
npm install --silent
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 서버가 시작되었습니다!"
echo ""
echo "📡 백엔드: http://localhost:8000"
echo "🎨 프론트엔드: http://localhost:5173"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."

# 종료 시 프로세스 정리
cleanup() {
    echo ""
    echo "🛑 서버 종료 중..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# 대기
wait
