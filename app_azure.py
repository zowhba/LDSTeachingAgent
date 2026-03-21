"""
LDS Teaching Agent - FastAPI Backend
Azure Table Storage를 사용한 영구 데이터 저장
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import sys
import tempfile

# 상위 디렉토리의 모듈 import를 위한 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.data.tables import TableServiceClient, TableClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

# 환경변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# FastAPI 앱 생성
app = FastAPI(
    title="LDS Teaching Agent API",
    description="후기성도 예수그리스도 교회 공과 준비 도우미 API (Azure Storage)",
    version="2.5"
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
TABLE_MATERIALS = "CurriculumMaterials"
TABLE_QA = "CurriculumQA"
TABLE_CONFIG = "SystemConfig"
TABLE_BOARD = "CommunityBoard"
TABLE_PRESENTATION = "CurriculumPresentation"

def get_table_client(table_name: str) -> TableClient:
    """테이블 클라이언트 반환"""
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise HTTPException(status_code=500, detail="Azure Storage 연결 문자열이 설정되지 않았습니다.")
    return TableClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING, table_name)

def init_azure_tables():
    """앱 시작 시 필요한 테이블들을 초기화합니다."""
    if not AZURE_STORAGE_CONNECTION_STRING:
        print("❌ 오류: AZURE_STORAGE_CONNECTION_STRING이 설정되지 않았습니다.")
        return
    
    try:
        service_client = TableServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        for table_name in [TABLE_MATERIALS, TABLE_QA, "WeeklyCurriculum", "CurriculumStatus", TABLE_CONFIG, TABLE_BOARD, TABLE_PRESENTATION]:
            try:
                service_client.create_table(table_name)
                print(f"✅ Azure 테이블 확인됨: {table_name}")
            except ResourceExistsError:
                pass
        
        # 초기 관리자 비밀번호 설정
        try:
            config_client = get_table_client(TABLE_CONFIG)
            try:
                config_client.get_entity(partition_key="admin", row_key="password")
            except ResourceNotFoundError:
                config_client.upsert_entity({
                    "PartitionKey": "admin",
                    "RowKey": "password",
                    "Value": os.getenv("ADMIN_PASSWORD", "8838")
                })
                print("✅ 초기 관리자 비밀번호가 설정되었습니다 (8838)")
        except Exception as e:
            print(f"⚠️ 관리자 비밀번호 초기화 실패: {e}")

    except Exception as e:
        print(f"❌ Azure 테이블 초기화 실패: {e}")

def create_partition_key(week_range: str, target_audience: str) -> str:
    """PartitionKey 생성"""
    safe_week = week_range.replace(" ", "_").replace("~", "-").replace("/", "-")
    return f"{safe_week}_{target_audience}"


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
    row_key: Optional[str] = None

class AdminLoginRequest(BaseModel):
    password: str

class DeleteMaterialRequest(BaseModel):
    lesson_title: str
    week_range: str
    target_audience: str

class DeleteQARequest(BaseModel):
    week_range: str
    target_audience: str
    row_key: str

class CreatePostRequest(BaseModel):
    author: str
    title: str
    category: str  # 문의사항 | 기능개발요청 | 오류신고 | 기타
    content: str
    password: str

class UpdatePostRequest(BaseModel):
    row_key: str
    password: str
    title: str
    category: str
    content: str

class DeletePostRequest(BaseModel):
    row_key: str
    password: str

class VerifyPostPasswordRequest(BaseModel):
    row_key: str
    password: str

class GeneratePresentationRequest(BaseModel):
    lesson_title: str
    lesson_content: str
    target_audience: str
    week_range: str


# === 유틸리티 함수들 ===
def load_prompt_template(filename):
    """프롬프트 템플릿 로드"""
    prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
    with open(os.path.join(prompts_dir, filename), 'r', encoding='utf-8') as f:
        return f.read()


# === API 엔드포인트들 ===
@app.on_event("startup")
async def startup_event():
    """앱 시작 시 데이터 확인 및 테이블 초기화"""
    print("🚀 LDS Teaching Agent API 시작 중 (Azure Mode)")
    init_azure_tables()
    
    try:
        from weekly_curriculum_manager import WeeklyCurriculumManager
        current_year = datetime.now().year
        # Manager 내부적으로 Azure를 우선 사용하도록 수정됨
        manager = WeeklyCurriculumManager()
        if not manager.check_year_data_exists(current_year):
            print(f"🔄 {current_year}년 커리큘럼 데이터 초기화 중...")
            manager.ensure_year_data(current_year)
    except Exception as e:
        print(f"❌ 초기 데이터 로딩 실패: {e}")


@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "status": "running", 
        "message": "LDS Teaching Agent API v2.5",
        "storage": "azure_table_storage"
    }


@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy", 
        "message": "LDS Teaching Agent API v2.5",
        "storage": "azure_table_storage",
        "azure_configured": bool(AZURE_STORAGE_CONNECTION_STRING)
    }


@app.get("/api/weeks", response_model=List[WeekInfo])
async def get_available_weeks():
    """사용 가능한 주차 목록 반환"""
    try:
        from curriculum_scraper import CurriculumScraper
        scraper = CurriculumScraper()
        return scraper.get_available_weeks()
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
        current_date_only = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i, week in enumerate(weeks):
            start_date = datetime.strptime(week['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(week['end_date'], '%Y-%m-%d')
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
        return scraper.get_curriculum_by_date(start_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-material")
def generate_curriculum_material(request: GenerateMaterialRequest):
    """공과 자료 생성 (Azure 캐시 지원)"""
    try:
        partition_key = create_partition_key(request.week_range, request.target_audience)
        
        # 1. Azure Table Storage에서 캐시 확인
        try:
            table_client = get_table_client(TABLE_MATERIALS)
            filter_query = f"PartitionKey eq '{partition_key}' and LessonTitle eq '{request.lesson_title}'"
            entities = list(table_client.query_entities(filter_query))
            if entities:
                print(f"📦 Azure 캐시된 교재 사용: {request.lesson_title}")
                return {"material": entities[0]['Content'], "is_cached": True}
        except Exception as e:
            print(f"⚠️ Azure 캐시 조회 실패: {e}")
        
        # 2. 새로운 자료 생성
        template = load_prompt_template('curriculum_template.txt')
        prompt = template.format(
            target_audience=request.target_audience,
            lesson_title=request.lesson_title,
            lesson_content=request.lesson_content
        )
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOY_CURRICULUM"),
            messages=[
                {"role": "system", "content": "당신은 후기성도 예수그리스도 교회의 공과 준비 전문가입니다. 상세하고 깊이 있는 공과 자료를 작성해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8000
        )
        generated_material = response.choices[0].message.content
        
        # 3. Azure Table Storage에 저장
        try:
            table_client = get_table_client(TABLE_MATERIALS)
            import uuid
            entity = {
                "PartitionKey": partition_key,
                "RowKey": str(uuid.uuid4()),
                "WeekRange": request.week_range,
                "TargetAudience": request.target_audience,
                "LessonTitle": request.lesson_title,
                "Content": generated_material,
                "CreatedAt": datetime.utcnow().isoformat()
            }
            table_client.create_entity(entity)
            print(f"✅ Azure 교재 저장 완료: {request.lesson_title}")
        except Exception as e:
            print(f"❌ Azure 저장 실패: {e}")
        
        return {"material": generated_material, "is_cached": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cached-material/{week_range}/{target_audience}/{lesson_title}")
async def get_cached_material(week_range: str, target_audience: str, lesson_title: str):
    """캐시된 자료 반환"""
    try:
        partition_key = create_partition_key(week_range, target_audience)
        table_client = get_table_client(TABLE_MATERIALS)
        filter_query = f"PartitionKey eq '{partition_key}' and LessonTitle eq '{lesson_title}'"
        entities = list(table_client.query_entities(filter_query))
        
        if entities:
            return {"material": entities[0]['Content'], "is_cached": True}
        return {"material": None, "is_cached": False}
    except Exception as e:
        print(f"캐시 조회 실패: {e}")
        return {"material": None, "is_cached": False}


@app.post("/api/chat")
def chat_response(request: ChatRequest):
    """채팅 응답 생성 및 저장"""
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
                {"role": "system", "content": "당신은 후기성도 예수그리스도 교회의 공과 준비 도우미입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        response_text = response.choices[0].message.content
        
        # Azure에 저장
        try:
            import uuid
            table_client = get_table_client(TABLE_QA)
            partition_key = create_partition_key(request.week_range, request.target_audience)
            entity = {
                "PartitionKey": partition_key,
                "RowKey": str(uuid.uuid4()),
                "WeekRange": request.week_range,
                "TargetAudience": request.target_audience,
                "Question": request.user_question,
                "Answer": response_text,
                "CreatedAt": datetime.utcnow().isoformat()
            }
            table_client.create_entity(entity)
            print(f"✅ Q&A 저장 완료")
        except Exception as e:
            print(f"❌ Q&A 저장 실패: {e}")
        
        return {"answer": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/qa/{week_range}/{target_audience}", response_model=List[QAItem])
async def get_qa_list(week_range: str, target_audience: str):
    """Q&A 목록 반환 (Azure 전용)"""
    try:
        partition_key = create_partition_key(week_range, target_audience)
        table_client = get_table_client(TABLE_QA)
        filter_query = f"PartitionKey eq '{partition_key}'"
        entities = list(table_client.query_entities(filter_query))
        
        # 최신순 정렬
        entities.sort(key=lambda x: x.get('CreatedAt', ''), reverse=True)
        
        return [
            {
                "question": e.get('Question', ''),
                "answer": e.get('Answer', ''),
                "created_at": e.get('CreatedAt', ''),
                "row_key": e.get('RowKey', '')
            }
            for e in entities
        ]
    except Exception as e:
        print(f"Q&A 조회 실패: {e}")
        return []


@app.get("/api/target-audiences")
async def get_target_audiences():
    """대상 그룹 목록 반환"""
    return ["성인", "초등회"]


# === 관리자 기능 API ===
@app.post("/api/admin/login")
async def admin_login(request: AdminLoginRequest):
    """관리자 로그인"""
    try:
        config_client = get_table_client(TABLE_CONFIG)
        entity = config_client.get_entity(partition_key="admin", row_key="password")
        if entity.get("Value") == request.password:
            return {"success": True, "message": "로그인 성공"}
        else:
            raise HTTPException(status_code=401, detail="비밀번호가 올바르지 않습니다.")
    except ResourceNotFoundError:
        # 설정이 없는 경우 환경변수 확인
        if request.password == os.getenv("ADMIN_PASSWORD", "8838"):
            return {"success": True, "message": "로그인 성공"}
        raise HTTPException(status_code=401, detail="비밀번호가 올바르지 않습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/delete-material")
async def delete_material(request: DeleteMaterialRequest):
    """공과 자료 삭제"""
    try:
        partition_key = create_partition_key(request.week_range, request.target_audience)
        table_client = get_table_client(TABLE_MATERIALS)
        
        # 해당 제목의 모든 엔티티 찾기
        filter_query = f"PartitionKey eq '{partition_key}' and LessonTitle eq '{request.lesson_title}'"
        entities = list(table_client.query_entities(filter_query))
        
        for entity in entities:
            table_client.delete_entity(partition_key=entity['PartitionKey'], row_key=entity['RowKey'])
            
        return {"success": True, "message": f"{len(entities)}개의 자료가 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/delete-qa")
async def delete_qa(request: DeleteQARequest):
    """Q&A 항목 삭제"""
    try:
        partition_key = create_partition_key(request.week_range, request.target_audience)
        table_client = get_table_client(TABLE_QA)
        table_client.delete_entity(partition_key=partition_key, row_key=request.row_key)
        return {"success": True, "message": "질문이 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === 프리젠테이션 API ===

@app.post("/api/generate-presentation")
def generate_presentation(request: GeneratePresentationRequest):
    """공과 프리젠테이션 HTML 생성 (캐시 우선)"""
    try:
        partition_key = create_partition_key(request.week_range, request.target_audience)

        # 1. 캐시 확인
        try:
            table_client = get_table_client(TABLE_PRESENTATION)
            filter_query = f"PartitionKey eq '{partition_key}' and LessonTitle eq '{request.lesson_title}'"
            entities = list(table_client.query_entities(filter_query))
            if entities:
                print(f"📦 프리젠테이션 캐시 히트: {request.lesson_title}")
                return {"html": entities[0]['HtmlContent'], "is_cached": True}
        except Exception as e:
            print(f"⚠️ 프리젠테이션 캐시 조회 실패: {e}")

        # 2. LLM으로 생성
        template = load_prompt_template('presentation_template.txt')
        prompt = (
            template.replace("{target_audience}", request.target_audience)
            .replace("{lesson_title}", request.lesson_title)
            .replace("{lesson_content}", request.lesson_content)
        )

        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOY_CURRICULUM"),
            messages=[
                {"role": "system", "content": "당신은 아름다운 HTML 프리젠테이션 슬라이드를 만드는 전문가입니다. 요청된 내용을 바탕으로 완전하고 독립적인 HTML 파일을 생성해주세요. HTML 코드만 출력하고 마크다운 코드블록은 사용하지 마세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        html_content = response.choices[0].message.content.strip()

        try:
            from presentation_skeleton import HTML_SKELETON
        except ImportError:
            from backend.presentation_skeleton import HTML_SKELETON

        # 슬라이드 뼈대에 LLM 출력을 삽입하고, 제목 치환
        final_html = HTML_SKELETON.replace("{llm_slides_output}", html_content)
        final_html = final_html.replace("{lesson_title}", request.lesson_title)

        # 3. Azure에 저장 (gzip+base64 압축으로 1MB 제한 우회)
        try:
            import uuid, gzip, base64
            compressed = base64.b64encode(gzip.compress(final_html.encode('utf-8'))).decode('ascii')
            print(f"📦 압축률: {len(final_html)} → {len(compressed)} bytes")

            # 압축 후에도 64KB(Azure 단일 속성 최대) 초과 시 저장 건너뜀 - 메모리 캐시만 사용
            if len(compressed) <= 65536:
                table_client = get_table_client(TABLE_PRESENTATION)
                entity = {
                    "PartitionKey": partition_key,
                    "RowKey": str(uuid.uuid4()),
                    "WeekRange": request.week_range,
                    "TargetAudience": request.target_audience,
                    "LessonTitle": request.lesson_title,
                    "HtmlCompressed": compressed,
                    "CreatedAt": datetime.utcnow().isoformat()
                }
                table_client.create_entity(entity)
                print(f"✅ 프리젠테이션 저장 완료: {request.lesson_title}")
            else:
                print(f"⚠️ 압축 후에도 64KB 초과({len(compressed)}bytes), 이 세션에서만 사용")
        except Exception as e:
            print(f"❌ 프리젠테이션 저장 실패: {e}")

        return {"html": final_html, "is_cached": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cached-presentation/{week_range}/{target_audience}/{lesson_title}")
async def get_cached_presentation(week_range: str, target_audience: str, lesson_title: str):
    """캐시된 프리젠테이션 반환"""
    try:
        partition_key = create_partition_key(week_range, target_audience)
        table_client = get_table_client(TABLE_PRESENTATION)
        filter_query = f"PartitionKey eq '{partition_key}' and LessonTitle eq '{lesson_title}'"
        entities = list(table_client.query_entities(filter_query))
        if entities:
            e = entities[0]
            if 'HtmlCompressed' in e:
                import gzip, base64
                html = gzip.decompress(base64.b64decode(e['HtmlCompressed'])).decode('utf-8')
                return {"html": html, "is_cached": True}
            elif 'HtmlContent' in e:
                # 구 포맷 폴백
                return {"html": e['HtmlContent'], "is_cached": True}
        return {"html": None, "is_cached": False}
    except Exception as e:
        return {"html": None, "is_cached": False}


# === 게시판 API ===
import hashlib
import uuid as _uuid

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@app.get("/api/board")
async def get_board_posts():
    """게시판 글 목록 조회 (최신순)"""
    try:
        table_client = get_table_client(TABLE_BOARD)
        entities = list(table_client.query_entities("PartitionKey eq 'post'"))
        posts = []
        for e in entities:
            posts.append({
                "row_key": e["RowKey"],
                "author": e.get("Author", ""),
                "title": e.get("Title", ""),
                "category": e.get("Category", ""),
                "content": e.get("Content", ""),
                "created_at": e.get("CreatedAt", ""),
                "updated_at": e.get("UpdatedAt", ""),
            })
        posts.sort(key=lambda x: x["created_at"], reverse=True)
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/board")
async def create_board_post(request: CreatePostRequest):
    """게시판 글 작성"""
    try:
        table_client = get_table_client(TABLE_BOARD)
        row_key = str(_uuid.uuid4())
        now = datetime.utcnow().isoformat()
        table_client.upsert_entity({
            "PartitionKey": "post",
            "RowKey": row_key,
            "Author": request.author,
            "Title": request.title,
            "Category": request.category,
            "Content": request.content,
            "PasswordHash": hash_password(request.password),
            "CreatedAt": now,
            "UpdatedAt": now,
        })
        return {"success": True, "row_key": row_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/board/verify-password")
async def verify_post_password(request: VerifyPostPasswordRequest):
    """게시글 비밀번호 확인"""
    try:
        table_client = get_table_client(TABLE_BOARD)
        entity = table_client.get_entity(partition_key="post", row_key=request.row_key)
        if entity.get("PasswordHash") == hash_password(request.password):
            return {"success": True}
        return {"success": False}
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/board/{row_key}")
async def update_board_post(row_key: str, request: UpdatePostRequest):
    """게시판 글 수정"""
    try:
        table_client = get_table_client(TABLE_BOARD)
        entity = table_client.get_entity(partition_key="post", row_key=row_key)
        if entity.get("PasswordHash") != hash_password(request.password):
            raise HTTPException(status_code=403, detail="비밀번호가 올바르지 않습니다.")
        entity["Title"] = request.title
        entity["Category"] = request.category
        entity["Content"] = request.content
        entity["UpdatedAt"] = datetime.utcnow().isoformat()
        table_client.upsert_entity(entity)
        return {"success": True}
    except HTTPException:
        raise
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/board/{row_key}")
async def delete_board_post(row_key: str, password: str):
    """게시판 글 삭제"""
    try:
        table_client = get_table_client(TABLE_BOARD)
        entity = table_client.get_entity(partition_key="post", row_key=row_key)
        if entity.get("PasswordHash") != hash_password(password):
            raise HTTPException(status_code=403, detail="비밀번호가 올바르지 않습니다.")
        table_client.delete_entity(partition_key="post", row_key=row_key)
        return {"success": True}
    except HTTPException:
        raise
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Vue.js 정적 파일 서빙 (프로덕션)
static_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')
if os.path.exists(static_dir):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    from fastapi import Request
    
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """SPA 라우팅을 위한 catch-all"""
        if full_path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        return FileResponse(os.path.join(static_dir, "index.html"))

# 앱 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
