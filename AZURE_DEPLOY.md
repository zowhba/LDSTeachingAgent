# Azure Web App 배포 가이드

이 문서는 LDS Teaching Agent를 Azure Web App에 배포하는 방법을 안내합니다.

## 사전 요구사항

- Azure 계정
- Azure CLI (선택사항)
- Node.js 18+
- Python 3.11+

## 배포 방법

### 방법 1: GitHub Actions 자동 배포 (권장)

#### 1단계: Azure Web App 생성

1. [Azure Portal](https://portal.azure.com) 접속
2. **리소스 만들기** > **웹 앱** 선택
3. 설정:
   - **이름**: `lds-teaching-agent` (원하는 이름)
   - **런타임 스택**: Python 3.11
   - **운영 체제**: Linux
   - **지역**: Korea Central (또는 가까운 지역)
   - **가격 책정 플랜**: B1 이상 권장

4. **검토 + 만들기** > **만들기**

#### 2단계: Azure Storage 계정 생성 (영구 데이터 저장용)

1. [Azure Portal](https://portal.azure.com) 접속
2. **리소스 만들기** > **스토리지 계정** 선택
3. 설정:
   - **스토리지 계정 이름**: `ldsteachingstorage` (고유해야 함)
   - **지역**: Web App과 동일한 지역
   - **성능**: Standard
   - **중복성**: LRS (가장 저렴)
4. **검토 + 만들기** > **만들기**
5. 생성된 스토리지 계정 > **액세스 키** > **연결 문자열** 복사

#### 3단계: 환경 변수 설정

1. 생성된 Web App으로 이동
2. **설정** > **구성** > **애플리케이션 설정**
3. 다음 환경 변수 추가:

| 이름 | 값 |
|------|-----|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI 엔드포인트 URL |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API 키 |
| `AZURE_OPENAI_DEPLOY_CURRICULUM` | 배포 이름 (예: gpt-4) |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Storage 연결 문자열 |

4. **저장**

#### 4단계: 시작 명령 설정

1. **설정** > **구성** > **일반 설정**
2. **시작 명령**에 다음 입력:
   ```
   gunicorn --bind=0.0.0.0:8000 --workers=4 --worker-class=uvicorn.workers.UvicornWorker app_azure:app
   ```
3. **저장**

#### 5단계: GitHub 연결 및 자동 배포

1. **배포 센터** > **GitHub** 선택
2. GitHub 계정 연결 및 리포지토리 선택
3. 브랜치: `main`
4. 빌드 공급자: **GitHub Actions**
5. **저장**

또는 수동으로 GitHub Secrets 설정:

1. GitHub 리포지토리 > **Settings** > **Secrets and variables** > **Actions**
2. **New repository secret** 클릭
3. `AZURE_WEBAPP_PUBLISH_PROFILE` 추가:
   - Azure Portal > Web App > **배포 센터** > **게시 프로필 관리** > **게시 프로필 다운로드**
   - 다운로드한 파일 내용을 Secret 값으로 붙여넣기

4. `.github/workflows/azure-webapps.yml` 파일에서 `AZURE_WEBAPP_NAME`을 실제 앱 이름으로 수정

5. `main` 브랜치에 push하면 자동 배포됨

---

### 방법 2: VS Code Azure 확장

1. VS Code에서 **Azure App Service** 확장 설치
2. Azure 계정 로그인
3. 프론트엔드 빌드:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```
4. 프로젝트 폴더 우클릭 > **Deploy to Web App**
5. Web App 선택 또는 새로 생성

---

### 방법 3: Azure CLI

```bash
# 1. Azure 로그인
az login

# 2. 프론트엔드 빌드
cd frontend
npm install
npm run build
cd ..

# 3. 리소스 그룹 생성 (없는 경우)
az group create --name lds-teaching-rg --location koreacentral

# 4. Web App 생성 및 배포
az webapp up \
  --name lds-teaching-agent \
  --resource-group lds-teaching-rg \
  --runtime "PYTHON:3.11" \
  --sku B1

# 5. 환경 변수 설정
az webapp config appsettings set \
  --name lds-teaching-agent \
  --resource-group lds-teaching-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT="your_endpoint" \
    AZURE_OPENAI_API_KEY="your_key" \
    AZURE_OPENAI_DEPLOY_CURRICULUM="your_deployment"

# 6. 시작 명령 설정
az webapp config set \
  --name lds-teaching-agent \
  --resource-group lds-teaching-rg \
  --startup-file "gunicorn --bind=0.0.0.0:8000 --workers=4 --worker-class=uvicorn.workers.UvicornWorker app_azure:app"
```

---

## 배포 후 확인

1. Azure Portal에서 Web App URL 확인 (예: `https://lds-teaching-agent.azurewebsites.net`)
2. 브라우저에서 접속하여 앱 동작 확인
3. **로그 스트림**에서 오류 확인 가능

## 문제 해결

### 앱이 시작되지 않는 경우

1. **로그 스트림** 확인
2. 환경 변수가 올바르게 설정되었는지 확인
3. 시작 명령이 정확한지 확인

### 502 Bad Gateway 오류

1. 앱이 완전히 시작될 때까지 1-2분 대기
2. 로그에서 Python 패키지 설치 오류 확인
3. `requirements_azure.txt`에 모든 의존성이 있는지 확인

### API 호출 실패

1. Azure OpenAI 환경 변수 확인
2. Azure OpenAI 서비스가 활성화되어 있는지 확인
3. API 키가 유효한지 확인

## 파일 구조

```
LDSTeachingAgent/
├── app_azure.py              # Azure용 통합 서버
├── requirements_azure.txt    # Azure 배포용 의존성
├── startup.sh                # 시작 스크립트
├── deploy_azure.sh           # 로컬 배포 준비 스크립트
├── .github/
│   └── workflows/
│       └── azure-webapps.yml # GitHub Actions 워크플로우
├── frontend/
│   └── dist/                 # 빌드된 프론트엔드 (npm run build 후 생성)
└── prompts/                  # 프롬프트 템플릿
```

## 비용 참고

- **B1 플랜**: 약 $13/월 (기본 권장)
- **F1 플랜**: 무료 (개발/테스트용, 제한 있음)
- **Azure OpenAI**: 사용량에 따라 별도 과금
- **Azure Table Storage**: GB당 약 $0.05/월 (매우 저렴, 거의 무료 수준)
