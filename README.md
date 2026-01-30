# 📖 후기성도 예수그리스도 교회 공과 준비 도우미 AI Agent

후기성도 예수그리스도 교회의 공과 준비를 도와주는 AI Agent 프로그램입니다. 교회 웹사이트에서 현재 주의 공과 정보를 자동으로 가져와서 대상별 맞춤형 공과 준비 자료를 생성하고, 공과에 대한 질의응답을 제공합니다.

## 🆕 v2.0 업데이트 - Vue.js 프론트엔드

v2.0에서는 기존 Streamlit UI를 **Vue.js + FastAPI** 아키텍처로 완전히 재구성했습니다.

### 새로운 기능
- 🚀 **더 빠른 응답 속도**: REST API 기반 비동기 처리
- 🎨 **모던한 UI/UX**: Tailwind CSS 기반의 세련된 디자인
- 📱 **완전한 반응형**: 모바일부터 데스크톱까지 최적화
- 💬 **실시간 채팅**: 자연스러운 대화형 인터페이스
- 📋 **마크다운 렌더링**: 생성된 자료를 보기 좋게 표시
- 🔄 **상태 관리**: Pinia를 통한 효율적인 상태 관리

## 🚀 주요 기능

- ✅ 교회 웹사이트에서 현재 주의 공과 정보 자동 수집
- ✅ 대상별 맞춤형 공과 준비 자료 생성 (성인, 신회원, 청소년, 초등회)
- ✅ Azure OpenAI를 활용한 지능형 공과 자료 생성
- ✅ 생성된 자료의 데이터베이스 저장 및 재사용
- ✅ 공과 자료에 대한 실시간 질의응답 채팅
- ✅ 직관적인 웹 인터페이스
- ✅ 반응형 레이아웃

## 📦 설치

### 사전 요구사항
- Python 3.10+
- Node.js 18+
- npm

### 1. 저장소 클론
```bash
git clone <repository-url>
cd LDSTeachingAgent
```

### 2. 환경변수 설정
```bash
cp env_example.txt .env
```
`.env` 파일을 편집하여 Azure OpenAI 설정을 입력하세요.

### 3. 백엔드 설정
```bash
# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r backend/requirements.txt
```

### 4. 프론트엔드 설정
```bash
cd frontend
npm install
```

## 🎯 사용법

### 방법 1: 통합 실행 (권장)
```bash
./start.sh
```
백엔드와 프론트엔드가 동시에 실행됩니다.

### 방법 2: 개별 실행

**터미널 1 - 백엔드:**
```bash
./start_backend.sh
# 또는
cd backend && uvicorn main:app --reload --port 8000
```

**터미널 2 - 프론트엔드:**
```bash
./start_frontend.sh
# 또는
cd frontend && npm run dev
```

### 접속 URL
- 🎨 **프론트엔드**: http://localhost:5173
- 📡 **백엔드 API**: http://localhost:8000
- 📚 **API 문서**: http://localhost:8000/docs

### 사용 단계

1. 브라우저에서 `http://localhost:5173` 접속

2. 좌측 사이드바에서 주차 선택 및 대상 그룹 선택:
   - 성인
   - 신회원
   - 청소년
   - 초등회

3. "📝 공과 자료 생성" 버튼 클릭

4. 생성된 공과 준비 자료 확인

5. 하단 채팅창에서 공과에 대한 질문 입력

## 📁 프로젝트 구조

```
LDSTeachingAgent/
├── backend/
│   ├── main.py              # FastAPI 백엔드 서버
│   └── requirements.txt     # Python 의존성
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 메인 앱 컴포넌트
│   │   ├── main.js          # Vue.js 진입점
│   │   ├── api.js           # API 클라이언트
│   │   ├── stores/
│   │   │   └── curriculum.js # Pinia 상태 관리
│   │   └── components/
│   │       ├── SettingsPanel.vue     # 설정 패널
│   │       ├── LessonContent.vue     # 공과 내용
│   │       ├── GeneratedMaterial.vue # 생성된 자료
│   │       └── ChatSection.vue       # 채팅 섹션
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── prompts/                  # AI 프롬프트 템플릿
├── curriculum_scraper.py     # 웹 스크래핑 모듈
├── weekly_curriculum_manager.py
├── start.sh                  # 통합 실행 스크립트
├── start_backend.sh          # 백엔드 실행 스크립트
├── start_frontend.sh         # 프론트엔드 실행 스크립트
└── app.py                    # 기존 Streamlit 앱 (레거시)
```

## 🔧 기술 스택

### 백엔드
- **FastAPI**: 고성능 REST API 서버
- **Azure OpenAI**: AI 모델 (GPT-4)
- **BeautifulSoup4**: 웹 스크래핑
- **SQLite**: 데이터베이스
- **Pydantic**: 데이터 검증

### 프론트엔드
- **Vue.js 3**: 프론트엔드 프레임워크
- **Pinia**: 상태 관리
- **Vite**: 빌드 도구
- **Tailwind CSS**: UI 스타일링
- **Axios**: HTTP 클라이언트
- **Marked**: 마크다운 렌더링

## 🔑 Azure OpenAI 설정

1. Azure OpenAI 서비스에서 리소스 생성
2. .env 파일에 다음 변수들을 설정:

```env
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_DEPLOY_CURRICULUM=your_deployment_name_here
```

## 📡 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/weeks` | 사용 가능한 주차 목록 |
| GET | `/api/weeks/current` | 현재 주차 정보 |
| POST | `/api/curriculum` | 특정 주차 공과 정보 |
| POST | `/api/generate-material` | 공과 자료 생성 |
| POST | `/api/chat` | 채팅 응답 생성 |
| GET | `/api/qa/{week}/{audience}` | Q&A 목록 조회 |
| GET | `/api/target-audiences` | 대상 그룹 목록 |

## ⚠️ 주의사항

- 인터넷 연결이 필요합니다 (교회 웹사이트 접근용)
- Azure OpenAI API 사용 시 비용이 발생할 수 있습니다
- 생성된 자료는 SQLite 데이터베이스에 저장됩니다
- 교회 웹사이트 구조 변경 시 스크래핑 기능이 영향을 받을 수 있습니다

## 🛠️ 문제 해결

### 백엔드가 시작되지 않는 경우
- Python 가상환경이 활성화되었는지 확인
- `.env` 파일이 프로젝트 루트에 있는지 확인
- 의존성이 모두 설치되었는지 확인: `pip install -r backend/requirements.txt`

### 프론트엔드가 시작되지 않는 경우
- Node.js가 설치되었는지 확인: `node --version`
- 의존성 설치: `cd frontend && npm install`

### 공과 자료 생성이 실패하는 경우
- Azure OpenAI 설정이 올바르게 완료되었는지 확인
- `.env` 파일의 변수들이 정확히 설정되었는지 확인
- API 사용량 한도를 확인

### CORS 오류가 발생하는 경우
- 백엔드 서버가 8000 포트에서 실행 중인지 확인
- 프론트엔드가 5173 포트에서 실행 중인지 확인

## 🎨 레거시 Streamlit 버전

기존 Streamlit 버전도 여전히 사용 가능합니다:
```bash
pip install -r requirements.txt
streamlit run app.py
```
접속: http://localhost:8501
