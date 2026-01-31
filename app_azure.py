"""
LDS Teaching Agent - Azure Web App 배포용 통합 서버
FastAPI 백엔드 + Vue.js 정적 파일 서빙
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlite3
import os
import sys

from dotenv import load_dotenv
from openai import AzureOpenAI

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="LDS Teaching Agent API",
    description="후기성도 예수그리스도 교회 공과 준비 도우미 API",
    version="2.0"
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

# 데이터베이스 경로
DB_PATH = os.path.join(os.path.dirname(__file__), 'curriculum_data.db')


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
def get_db_connection():
    """데이터베이스 연결 반환"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_prompt_template(filename):
    """프롬프트 템플릿 로드"""
    prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
    with open(os.path.join(prompts_dir, filename), 'r', encoding='utf-8') as f:
        return f.read()


def init_db():
    """데이터베이스 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='curriculum_materials'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        cursor.execute("PRAGMA table_info(curriculum_materials)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'week_range' not in columns:
            cursor.execute('ALTER TABLE curriculum_materials ADD COLUMN week_range TEXT')
    else:
        cursor.execute('''
            CREATE TABLE curriculum_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_title TEXT,
                target_audience TEXT,
                content TEXT,
                week_range TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_curriculum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            week_range TEXT NOT NULL,
            scripture_range TEXT NOT NULL,
            lesson_title TEXT,
            lesson_url TEXT,
            section TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, start_date, end_date)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS curriculum_status (
            year INTEGER PRIMARY KEY,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_weeks INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS curriculum_qa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_range TEXT NOT NULL,
            target_audience TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


# === API 엔드포인트들 ===
@app.on_event("startup")
async def startup_event():
    """앱 시작 시 데이터베이스 초기화"""
    init_db()
    
    try:
        from weekly_curriculum_manager import WeeklyCurriculumManager
        current_year = datetime.now().year
        manager = WeeklyCurriculumManager(DB_PATH)
        
        if not manager.check_year_data_exists(current_year):
            try:
                manager.ensure_year_data(current_year)
            except Exception as e:
                print(f"웹사이트 접근 실패, fallback 데이터 사용: {e}")
                if current_year == 2025:
                    fallback_data = manager.get_fallback_data(current_year)
                    if fallback_data:
                        manager.save_weekly_data_to_db(fallback_data, current_year)
    except Exception as e:
        print(f"초기 데이터 로딩 실패: {e}")


@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "message": "LDS Teaching Agent API v2.0"}


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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT content FROM curriculum_materials 
            WHERE lesson_title = ? AND target_audience = ? AND week_range = ?
            ORDER BY created_at DESC LIMIT 1
        ''', (request.lesson_title, request.target_audience, request.week_range))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"material": result[0], "is_cached": True}
        
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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO curriculum_materials (lesson_title, target_audience, content, week_range)
            VALUES (?, ?, ?, ?)
        ''', (request.lesson_title, request.target_audience, generated_material, request.week_range))
        conn.commit()
        conn.close()
        
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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO curriculum_qa (week_range, target_audience, question, answer)
            VALUES (?, ?, ?, ?)
        ''', (request.week_range, request.target_audience, request.user_question, response_text))
        conn.commit()
        conn.close()
        
        return {"answer": response_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/qa/{week_range}/{target_audience}", response_model=List[QAItem])
async def get_qa_list(week_range: str, target_audience: str):
    """Q&A 목록 반환"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT question, answer, created_at 
            FROM curriculum_qa 
            WHERE week_range = ? AND target_audience = ?
            ORDER BY created_at DESC
        ''', (week_range, target_audience))
        results = cursor.fetchall()
        conn.close()
        
        return [{"question": r[0], "answer": r[1], "created_at": r[2]} for r in results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
