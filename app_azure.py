"""
LDS Teaching Agent - Azure Web App 배포용 통합 서버
FastAPI 백엔드 + Vue.js 정적 파일 서빙
Azure Table Storage를 사용한 영구 데이터 저장
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import sys
import hashlib

from dotenv import load_dotenv
from openai import AzureOpenAI

# Azure Table Storage
from azure.data.tables import TableServiceClient, TableClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="LDS Teaching Agent API",
    description="후기성도 예수그리스도 교회 공과 준비 도우미 API",
    version="2.1"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure OpenAI 클라이언트
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview"
)

# Azure Table Storage 설정
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# 테이블 이름
TABLE_MATERIALS = "CurriculumMaterials"
TABLE_QA = "CurriculumQA"
TABLE_WEEKLY = "WeeklyCurriculum"


def get_table_client(table_name: str) -> TableClient:
    """테이블 클라이언트 반환"""
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise HTTPException(status_code=500, detail="Azure Storage 연결 문자열이 설정되지 않았습니다.")
    
    service_client = TableServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    return service_client.get_table_client(table_name)


def init_tables():
    """테이블 초기화 (없으면 생성)"""
    if not AZURE_STORAGE_CONNECTION_STRING:
        print("경고: Azure Storage 연결 문자열이 없습니다. 로컬 모드로 실행됩니다.")
        return
    
    try:
        service_client = TableServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        
        for table_name in [TABLE_MATERIALS, TABLE_QA, TABLE_WEEKLY]:
            try:
                service_client.create_table(table_name)
                print(f"테이블 생성됨: {table_name}")
            except ResourceExistsError:
                print(f"테이블 이미 존재: {table_name}")
    except Exception as e:
        print(f"테이블 초기화 실패: {e}")


def generate_row_key() -> str:
    """고유 RowKey 생성"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    return timestamp


def create_partition_key(week_range: str, target_audience: str) -> str:
    """PartitionKey 생성 (주차_대상그룹)"""
    # 특수문자 제거 및 안전한 키 생성
    safe_week = week_range.replace(" ", "_").replace("~", "-").replace("/", "-")
    safe_audience = target_audience
    return f"{safe_week}_{safe_audience}"


# === Pydantic 모델들 ===
class WeekInfo(BaseModel):
    week_range: str
    title_keywords: str
    start_date: str
    end_date: str
    section: str
    display_text: str


class LessonData(BaseModel):
    title: str
    content: str
    url: str
    week_info: Optional[dict] = None


class GenerateMaterialRequest(BaseModel):
    lesson_title: str
    lesson_content: str
    target_audience: str
    week_range: str


class ChatRequest(BaseModel):
    lesson_title: str
    lesson_content: str
    reference_material: str
    user_question: str
    week_range: str
    target_audience: str


class QAItem(BaseModel):
    question: str
    answer: str
    created_at: str


# === 유틸리티 함수들 ===
def load_prompt_template(filename):
    """프롬프트 템플릿 로드"""
    prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
    with open(os.path.join(prompts_dir, filename), 'r', encoding='utf-8') as f:
        return f.read()


# === API 엔드포인트들 ===
@app.on_event("startup")
async def startup_event():
    """앱 시작 시 테이블 초기화"""
    init_tables()
    
    try:
        from weekly_curriculum_manager import WeeklyCurriculumManager
        current_year = datetime.now().year
        # 임시 SQLite 사용 (커리큘럼 스크래핑용)
        import tempfile
        temp_db = os.path.join(tempfile.gettempdir(), 'curriculum_temp.db')
        manager = WeeklyCurriculumManager(temp_db)
        
        if not manager.check_year_data_exists(current_year):
            try:
                manager.ensure_year_data(current_year)
            except Exception as e:
                print(f"웹사이트 접근 실패, fallback 데이터 사용: {e}")
                if current_year == 2025 or current_year == 2026:
                    fallback_data = manager.get_fallback_data(current_year)
                    if fallback_data:
                        manager.save_weekly_data_to_db(fallback_data, current_year)
    except Exception as e:
        print(f"초기 데이터 로딩 실패: {e}")


@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    storage_status = "connected" if AZURE_STORAGE_CONNECTION_STRING else "not configured"
    return {
        "status": "healthy", 
        "message": "LDS Teaching Agent API v2.1",
        "storage": storage_status
    }


@app.get("/api/weeks", response_model=List[WeekInfo])
async def get_available_weeks():
    """사용 가능한 주차 목록 반환"""
    try:
        from curriculum_scraper import CurriculumScraper
        scraper = CurriculumScraper()
        weeks = scraper.get_available_weeks()
        return weeks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weeks/current")
async def get_current_week():
    """현재 주차 정보 반환"""
    try:
        from curriculum_scraper import CurriculumScraper
        scraper = CurriculumScraper()
        weeks = scraper.get_available_weeks()
        
        current_date = datetime.now()
        for i, week in enumerate(weeks):
            start_date = datetime.strptime(week['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(week['end_date'], '%Y-%m-%d')
            current_date_only = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if start_date <= current_date_only <= end_date:
                return {"index": i, "week": week}
        
        return {"index": 0, "week": weeks[0] if weeks else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/curriculum")
async def get_curriculum_by_week(week_data: dict):
    """특정 주차의 공과 정보 반환"""
    try:
        from curriculum_scraper import CurriculumScraper
        scraper = CurriculumScraper()
        
        start_date = datetime.strptime(week_data['start_date'], '%Y-%m-%d')
        lesson_data = scraper.get_curriculum_by_date(start_date)
        
        return lesson_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-material")
async def generate_curriculum_material(request: GenerateMaterialRequest):
    """공과 자료 생성"""
    try:
        # Azure Table Storage에서 캐시 확인
        if AZURE_STORAGE_CONNECTION_STRING:
            try:
                table_client = get_table_client(TABLE_MATERIALS)
                partition_key = create_partition_key(request.week_range, request.target_audience)
                
                # 제목으로 검색
                filter_query = f"PartitionKey eq '{partition_key}' and LessonTitle eq '{request.lesson_title}'"
                entities = list(table_client.query_entities(filter_query, results_per_page=1))
                
                if entities:
                    return {"material": entities[0]['Content'], "is_cached": True}
            except Exception as e:
                print(f"캐시 조회 실패: {e}")
        
        # AI로 새 자료 생성
        template = load_prompt_template('curriculum_template.txt')
        prompt = template.format(
            target_audience=request.target_audience,
            lesson_title=request.lesson_title,
            lesson_content=request.lesson_content
        )
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOY_CURRICULUM"),
            messages=[
                {"role": "system", "content": "당신은 후기성도 예수그리스도 교회의 공과 준비 전문가입니다. 상세하고 깊이 있는 공과 자료를 작성해주세요. 모든 핵심 교리를 동일한 깊이와 상세함으로 작성해야 합니다. 절대로 뒤의 교리들을 간략하게 처리하지 마세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8000
        )
        
        generated_material = response.choices[0].message.content
        
        # Azure Table Storage에 저장
        if AZURE_STORAGE_CONNECTION_STRING:
            try:
                table_client = get_table_client(TABLE_MATERIALS)
                partition_key = create_partition_key(request.week_range, request.target_audience)
                
                entity = {
                    "PartitionKey": partition_key,
                    "RowKey": generate_row_key(),
                    "WeekRange": request.week_range,
                    "TargetAudience": request.target_audience,
                    "LessonTitle": request.lesson_title,
                    "Content": generated_material,
                    "CreatedAt": datetime.utcnow().isoformat()
                }
                table_client.create_entity(entity)
                print(f"교재 저장 완료: {request.lesson_title}")
            except Exception as e:
                print(f"교재 저장 실패: {e}")
        
        return {"material": generated_material, "is_cached": False}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat_response(request: ChatRequest):
    """채팅 응답 생성"""
    try:
        template = load_prompt_template('chat_template.txt')
        prompt = template.format(
            lesson_title=request.lesson_title,
            lesson_content=request.lesson_content,
            reference_material=request.reference_material,
            user_question=request.user_question
        )
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOY_CURRICULUM"),
            messages=[
                {"role": "system", "content": "당신은 후기성도 예수그리스도 교회의 공과 준비 도우미입니다. 답변은 반드시 600자 이내로 간결하게 작성해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content
        
        if len(response_text) > 600:
            truncated = response_text[:600]
            sentence_endings = ['.', '!', '?', '。', '！', '？']
            cut_point = -1
            for ending in sentence_endings:
                pos = truncated.rfind(ending)
                if pos > cut_point:
                    cut_point = pos
            
            if cut_point > 500:
                response_text = truncated[:cut_point + 1]
            else:
                response_text = truncated.rstrip() + "..."
        
        # Azure Table Storage에 Q&A 저장
        if AZURE_STORAGE_CONNECTION_STRING:
            try:
                table_client = get_table_client(TABLE_QA)
                partition_key = create_partition_key(request.week_range, request.target_audience)
                
                entity = {
                    "PartitionKey": partition_key,
                    "RowKey": generate_row_key(),
                    "WeekRange": request.week_range,
                    "TargetAudience": request.target_audience,
                    "Question": request.user_question,
                    "Answer": response_text,
                    "CreatedAt": datetime.utcnow().isoformat()
                }
                table_client.create_entity(entity)
                print(f"Q&A 저장 완료")
            except Exception as e:
                print(f"Q&A 저장 실패: {e}")
        
        return {"answer": response_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/qa/{week_range}/{target_audience}", response_model=List[QAItem])
async def get_qa_list(week_range: str, target_audience: str):
    """Q&A 목록 반환"""
    try:
        if not AZURE_STORAGE_CONNECTION_STRING:
            return []
        
        table_client = get_table_client(TABLE_QA)
        partition_key = create_partition_key(week_range, target_audience)
        
        # PartitionKey로 필터링
        filter_query = f"PartitionKey eq '{partition_key}'"
        entities = list(table_client.query_entities(filter_query))
        
        # 최신순 정렬
        entities.sort(key=lambda x: x.get('CreatedAt', ''), reverse=True)
        
        return [
            {
                "question": e.get('Question', ''),
                "answer": e.get('Answer', ''),
                "created_at": e.get('CreatedAt', '')
            }
            for e in entities
        ]
        
    except Exception as e:
        print(f"Q&A 조회 실패: {e}")
        return []


@app.get("/api/target-audiences")
async def get_target_audiences():
    """대상 그룹 목록 반환"""
    return ["성인", "신회원", "청소년", "초등회"]


# Vue.js 정적 파일 서빙 (프로덕션)
static_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """SPA 라우팅을 위한 catch-all"""
        # API 경로가 아닌 경우 index.html 반환
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        return FileResponse(os.path.join(static_dir, "index.html"))


# 앱 실행 (로컬 개발용)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
