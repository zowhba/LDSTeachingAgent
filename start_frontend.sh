#!/bin/bash

# 프론트엔드만 실행하는 스크립트

echo "🎨 Vue.js 프론트엔드 서버 시작..."

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR/frontend"

# 기존 프로세스 정리 (포트 5173)
echo "🔍 기존에 실행 중인 5173 포트 확인 중..."
if command -v lsof > /dev/null; then
    FRONTEND_PIDS=$(lsof -t -i:5173)
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo "🛑 5173 포트를 사용하는 프로세스를 종료합니다. (PID: $FRONTEND_PIDS)"
        kill -9 $FRONTEND_PIDS 2>/dev/null
        sleep 1
    fi
fi

# Node.js 의존성 확인 및 설치
if [ ! -d "node_modules" ]; then
    echo "📦 의존성 설치 중..."
    npm install
fi

echo ""
echo "✅ 프론트엔드 서버: http://localhost:5173"
echo ""

# 서버 실행
npm run dev
