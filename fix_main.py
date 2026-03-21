import re
import os

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
content = re.sub(
    r'# Azure Table Storage\nfrom azure\.data\.tables import TableServiceClient, TableClient\nfrom azure\.core\.exceptions import ResourceExistsError, ResourceNotFoundError',
    r'import sqlite3',
    content
)

# 2. Add DB config and get_db_connection
db_conn_str = """# 데이터베이스 설정
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'curriculum_data.db')

def get_db_connection():
    return sqlite3.connect(DB_PATH)
"""
content = re.sub(
    r'(?s)# Azure Table Storage 설정.*?AZURE_STORAGE_CONNECTION_STRING = os\.getenv\("AZURE_STORAGE_CONNECTION_STRING"\).*?# 테이블 이름.*?TABLE_MATERIALS = "CurriculumMaterials".*?TABLE_QA = "CurriculumQA"',
    db_conn_str,
    content
)

# 3. Remove init_tables and keys
content = re.sub(
    r'(?s)\ndef get_table_client.*?def create_partition_key.*?"""PartitionKey 생성 \(주차_대상그룹\)""".*?return f"\{safe_week\}_\{safe_audience\}"\n',
    '\n',
    content
)

# 4. startup_event
startup_replacement = """@app.on_event("startup")
async def startup_event():
    \"\"\"앱 시작 시 데이터 확인\"\"\"
    if not os.path.exists(DB_PATH):
        print("⚠️  경고: curriculum_data.db 파일을 찾을 수 없습니다.")
    else:
        print("✅ SQLite 데이터베이스 연결됨")"""
content = re.sub(
    r'(?s)@app\.on_event\("startup"\).*?async def startup_event\(\):.*?storage_ok = init_tables\(\).*?print\("   AZURE_STORAGE_CONNECTION_STRING=your_connection_string"\).*?print\("=" \* 60\).*?print\(""\)',
    startup_replacement,
    content
)

# 5. root and health endpoints
content = re.sub(r'storage_status = "connected" if AZURE_STORAGE_CONNECTION_STRING else "not configured"', 'storage_status = "local_sqlite"', content)

# 6. generate_curriculum_material - Check cache
check_cache_old = """        # Azure Table Storage에서 캐시 확인
        try:
            table_client = get_table_client(TABLE_MATERIALS)
            partition_key = create_partition_key(request.week_range, request.target_audience)
            
            # 제목으로 검색
            filter_query = f"PartitionKey eq '{partition_key}' and LessonTitle eq '{request.lesson_title}'"
            entities = list(table_client.query_entities(filter_query, results_per_page=1))
            
            if entities:
                return {"material": entities[0]['Content'], "is_cached": True}
        except HTTPException:
            raise
        except Exception as e:
            print(f"캐시 조회 실패: {e}")"""
check_cache_new = """        # 먼저 저장된 자료가 있는지 확인
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
        except Exception as e:
            print(f"캐시 조회 실패: {e}")"""
content = content.replace(check_cache_old, check_cache_new)

# 7. generate_curriculum_material - Save
save_mat_old = """        # Azure Table Storage에 저장
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
            print(f"✅ 교재 저장 완료: {request.lesson_title}")
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ 교재 저장 실패: {e}")"""
save_mat_new = """        # 데이터베이스에 저장
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO curriculum_materials (lesson_title, target_audience, content, week_range)
                VALUES (?, ?, ?, ?)
            ''', (request.lesson_title, request.target_audience, generated_material, request.week_range))
            conn.commit()
            conn.close()
            print(f"✅ 교재 저장 완료: {request.lesson_title}")
        except Exception as e:
            print(f"❌ 교재 저장 실패: {e}")"""
content = content.replace(save_mat_old, save_mat_new)

# 8. get_cached_material
get_cache_old = """try:
        try:
            table_client = get_table_client(TABLE_MATERIALS)
            partition_key = create_partition_key(week_range, target_audience)
            
            # 제목으로 검색
            filter_query = f"PartitionKey eq '{partition_key}' and LessonTitle eq '{lesson_title}'"
            entities = list(table_client.query_entities(filter_query, results_per_page=1))
            
            if entities:
                return {"material": entities[0]['Content'], "is_cached": True}
        except ValueError:
            # Storage connection is not set up
            pass
        except Exception as e:
            print(f"캐시 조회 실패: {e}")
            
        return {"material": None, "is_cached": False}
        
    except Exception as e:
        return {"material": None, "is_cached": False}"""
get_cache_new = """try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT content FROM curriculum_materials 
            WHERE lesson_title = ? AND target_audience = ? AND week_range = ?
            ORDER BY created_at DESC LIMIT 1
        ''', (lesson_title, target_audience, week_range))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"material": result[0], "is_cached": True}
        return {"material": None, "is_cached": False}
    except Exception as e:
        print(f"캐시 조회 실패: {e}")
        return {"material": None, "is_cached": False}"""
content = content.replace(get_cache_old, get_cache_new)

# 9. chat_response - save QA
save_qa_old = """        # Azure Table Storage에 Q&A 저장
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
            print(f"✅ Q&A 저장 완료")
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Q&A 저장 실패: {e}")"""
save_qa_new = """        # Q&A 저장
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO curriculum_qa (week_range, target_audience, question, answer)
                VALUES (?, ?, ?, ?)
            ''', (request.week_range, request.target_audience, request.user_question, response_text))
            conn.commit()
            conn.close()
            print(f"✅ Q&A 저장 완료")
        except Exception as e:
            print(f"❌ Q&A 저장 실패: {e}")"""
content = content.replace(save_qa_old, save_qa_new)

# 10. get_qa_list
get_qa_list_old = """    try:
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
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Q&A 조회 실패: {e}")
        return []"""
get_qa_list_new = """    try:
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
        print(f"Q&A 조회 실패: {e}")
        return []"""
content = content.replace(get_qa_list_old, get_qa_list_new)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(content)
