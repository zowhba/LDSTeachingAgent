#!/bin/bash

# LDS Teaching Agent - 실행 스크립트
# FastAPI 백엔드와 Vue.js 프론트엔드를 동시에 실행합니다.

echo "🚀 LDS Teaching Agent v2.0 시작..."
echo ""

# 프로젝트 루트 디렉토리
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 백엔드 실행
echo "📡 백엔드 서버 시작 중..."
cd "$PROJECT_DIR"
source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
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
