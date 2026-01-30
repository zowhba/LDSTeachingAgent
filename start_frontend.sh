#!/bin/bash

# 프론트엔드만 실행하는 스크립트

echo "🎨 Vue.js 프론트엔드 서버 시작..."

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR/frontend"

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
