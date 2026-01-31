#!/bin/bash

# Azure Web App 배포 스크립트
# 사용법: ./deploy_azure.sh

echo "🚀 Azure Web App 배포 준비 중..."

# 1. 프론트엔드 빌드
echo "📦 프론트엔드 빌드 중..."
cd frontend
npm install
npm run build
cd ..

# 2. 빌드 결과 확인
if [ ! -d "frontend/dist" ]; then
    echo "❌ 프론트엔드 빌드 실패"
    exit 1
fi

echo "✅ 프론트엔드 빌드 완료"

# 3. Azure CLI로 배포 (az login 필요)
echo ""
echo "📋 다음 단계를 수행하세요:"
echo ""
echo "1. Azure Portal에서 Web App 생성:"
echo "   - Runtime: Python 3.11"
echo "   - OS: Linux"
echo ""
echo "2. 환경 변수 설정 (Configuration > Application settings):"
echo "   - AZURE_OPENAI_ENDPOINT=your_endpoint"
echo "   - AZURE_OPENAI_API_KEY=your_key"
echo "   - AZURE_OPENAI_DEPLOY_CURRICULUM=your_deployment"
echo ""
echo "3. Startup Command 설정 (Configuration > General settings):"
echo "   gunicorn --bind=0.0.0.0:8000 --workers=4 --worker-class=uvicorn.workers.UvicornWorker app_azure:app"
echo ""
echo "4. 배포 (아래 방법 중 선택):"
echo ""
echo "   방법 A - VS Code Azure 확장:"
echo "   - Azure 확장 설치 후 우클릭 > Deploy to Web App"
echo ""
echo "   방법 B - Azure CLI:"
echo "   az webapp up --name <app-name> --resource-group <resource-group> --runtime 'PYTHON:3.11'"
echo ""
echo "   방법 C - GitHub Actions:"
echo "   - Azure Portal에서 Deployment Center > GitHub 연결"
echo ""
echo "✅ 배포 준비 완료!"
