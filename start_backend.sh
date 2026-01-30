#!/bin/bash

# 백엔드만 실행하는 스크립트

echo "📡 FastAPI 백엔드 서버 시작..."

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# 가상환경 활성화
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "🔧 가상환경 생성 중..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# 의존성 설치
pip install -q -r backend/requirements.txt

echo ""
echo "✅ 백엔드 서버: http://localhost:8000"
echo "📚 API 문서: http://localhost:8000/docs"
echo ""

# 서버 실행
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
