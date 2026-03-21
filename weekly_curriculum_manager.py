import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import os
from azure.data.tables import TableServiceClient, TableClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError


class WeeklyCurriculumManager:
    """주차별 경전 범위를 관리하는 클래스 (Azure/SQLite 지원)"""
    
    def __init__(self, db_path='curriculum_data.db', connection_string=None):
        self.db_path = db_path
        self.base_url = "https://www.churchofjesuschrist.org"
        self.connection_string = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        
        # 테이블 이름 정의
        self.TABLE_WEEKLY = "WeeklyCurriculum"
        self.TABLE_STATUS = "CurriculumStatus"
        
        # Azure 사용 시 테이블 초기화
        if self.connection_string:
            self._init_azure_tables()
            
    def _init_azure_tables(self):
        """Azure Table Storage 초기화"""
        try:
            service_client = TableServiceClient.from_connection_string(self.connection_string)
            for table_name in [self.TABLE_WEEKLY, self.TABLE_STATUS]:
                try:
                    service_client.create_table(table_name)
                    print(f"✅ Azure 테이블 생성됨: {table_name}")
                except ResourceExistsError:
                    pass
        except Exception as e:
            print(f"❌ Azure 테이블 초기화 실패: {e}")

    def check_year_data_exists(self, year):
        """해당 연도의 데이터가 DB/Storage에 있는지 확인"""
        if self.connection_string:
            try:
                table_client = TableClient.from_connection_string(self.connection_string, self.TABLE_STATUS)
                entity = table_client.get_entity(partition_key="status", row_key=str(year))
                if entity.get('Status') == 'completed' and entity.get('TotalWeeks', 0) > 0:
                    return True
            except ResourceNotFoundError:
                pass
            except Exception as e:
                print(f"Azure 데이터 확인 중 오류: {e}")
        
        # Local (SQLite)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS curriculum_status (
                    year INTEGER PRIMARY KEY,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_weeks INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending'
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
                    lesson_content TEXT,
                    section TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(year, start_date, end_date)
                )
            ''')
            conn.commit()
            
            # lesson_content 컬럼 확인
            cursor.execute("PRAGMA table_info(weekly_curriculum)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'lesson_content' not in columns:
                cursor.execute("ALTER TABLE weekly_curriculum ADD COLUMN lesson_content TEXT")
                conn.commit()
            
            cursor.execute("""
                SELECT status, total_weeks 
                FROM curriculum_status 
                WHERE year = ?
            """, (year,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == 'completed' and result[1] > 0:
                return True
            return False
        except Exception as e:
            print(f"로컬 데이터 확인 중 오류: {e}")
            return False
    
    def find_correct_url_pattern(self, year):
        known_mappings = {
            2025: 'doctrine-and-covenants',
            2026: 'old-testament',
        }
        if year in known_mappings:
            scripture_type = known_mappings[year]
            url = f"https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-{scripture_type}-{year}?lang=kor"
            return url, scripture_type
        return None, None
    
    def extract_weekly_data_from_website(self, year):
        url, scripture_type = self.find_correct_url_pattern(year)
        if not url: return self.get_fallback_data(year)
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            weekly_data = []
            
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                if 'come-follow-me' in href and str(year) in href:
                    lesson_data = self.parse_lesson_link_improved(link, year)
                    if lesson_data:
                        weekly_data.append(lesson_data)
            return weekly_data
        except Exception as e:
            print(f"웹사이트 추출 오류: {e}")
            return self.get_fallback_data(year)
    
    def parse_lesson_link_improved(self, link, year):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if not text: return None
        
        date_pattern = r'(\d{1,2}월\s*\d{1,2}일)\s*[~\-–\\]+\s*(\d{1,2}월\s*\d{1,2}일|\d{1,2}일)'
        match = re.search(date_pattern, text)
        if not match: return None
        
        start_part = match.group(1).replace(' ', '').replace('\\', '')
        end_part = match.group(2).replace(' ', '').replace('\\', '')
        if '월' not in end_part:
            st_month_match = re.search(r'(\d+)월', start_part)
            if st_month_match: end_part = f"{st_month_match.group(1)}월{end_part}"
        
        date_range = f"{start_part}~{end_part}"
        start_date, end_date = self.parse_date_range(date_range, year)
        if not start_date or not end_date: return None
        
        full_url = self.base_url + href if href.startswith('/') else href
        month_match = re.search(r'(\d+)월', start_part)
        section = f"{month_match.group(1)}월" if month_match else "기타"
        
        return {
            'year': year,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'week_range': date_range,
            'scripture_range': text.replace(date_range, '').strip() or f"{year}년 공과",
            'lesson_title': text,
            'lesson_url': full_url,
            'section': section,
            'lesson_content': None
        }

    def parse_date_range(self, date_range, year):
        try:
            m1 = re.search(r'(\d+)월(\d+)일~(\d+)일', date_range)
            if m1: return datetime(year, int(m1.group(1)), int(m1.group(2))), datetime(year, int(m1.group(1)), int(m1.group(3)))
            m2 = re.search(r'(\d+)월(\d+)일~(\d+)월(\d+)일', date_range)
            if m2: return datetime(year, int(m2.group(1)), int(m2.group(2))), datetime(year, int(m2.group(3)), int(m2.group(4)))
            return None, None
        except: return None, None

    def save_weekly_data_to_db(self, weekly_data, year):
        if not weekly_data: return False
        
        # 1. Azure Table Storage
        if self.connection_string:
            try:
                table_client = TableClient.from_connection_string(self.connection_string, self.TABLE_WEEKLY)
                for data in weekly_data:
                    row_key = data['week_range'].replace('~', '-').replace(' ', '_').replace('월', 'M').replace('일', 'D')
                    entity = {
                        "PartitionKey": str(year),
                        "RowKey": row_key,
                        "StartDate": data['start_date'],
                        "EndDate": data['end_date'],
                        "WeekRange": data['week_range'],
                        "ScriptureRange": data.get('scripture_range', ''),
                        "LessonTitle": data['lesson_title'],
                        "LessonUrl": data['lesson_url'],
                        "LessonContent": data.get('lesson_content', '') or "",
                        "Section": data['section'],
                        "CreatedAt": datetime.utcnow().isoformat()
                    }
                    table_client.upsert_entity(entity)
                
                status_client = TableClient.from_connection_string(self.connection_string, self.TABLE_STATUS)
                status_client.upsert_entity({
                    "PartitionKey": "status", "RowKey": str(year),
                    "LastUpdated": datetime.utcnow().isoformat(), "TotalWeeks": len(weekly_data), "Status": "completed"
                })
            except Exception as e:
                print(f"Azure 저장 오류: {e}")

        # 2. Local SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM weekly_curriculum WHERE year = ?", (year,))
            for data in weekly_data:
                cursor.execute("""
                    INSERT INTO weekly_curriculum 
                    (year, start_date, end_date, week_range, scripture_range, lesson_title, lesson_url, lesson_content, section) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['year'], data['start_date'], data['end_date'],
                    data['week_range'], data.get('scripture_range', ''),
                    data['lesson_title'], data['lesson_url'], data.get('lesson_content'), data['section']
                ))
            cursor.execute("INSERT OR REPLACE INTO curriculum_status (year, last_updated, total_weeks, status) VALUES (?, ?, ?, ?)", (year, datetime.now(), len(weekly_data), 'completed'))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"로컬 저장 오류: {e}")
            return False

    def get_weekly_data_from_db(self, year):
        if self.connection_string:
            try:
                table_client = TableClient.from_connection_string(self.connection_string, self.TABLE_WEEKLY)
                entities = table_client.query_entities(f"PartitionKey eq '{year}'")
                weekly_data = []
                for e in entities:
                    weekly_data.append({
                        'year': year, 'start_date': e.get('StartDate'), 'end_date': e.get('EndDate'),
                        'week_range': e.get('WeekRange'), 'title_keywords': e.get('ScriptureRange'),
                        'scripture_range': e.get('ScriptureRange'), 'lesson_title': e.get('LessonTitle'),
                        'lesson_url': e.get('LessonUrl'), 'lesson_content': e.get('LessonContent'), 'section': e.get('Section')
                    })
                if weekly_data:
                    weekly_data.sort(key=lambda x: x['end_date'])
                    return weekly_data
            except Exception as e:
                print(f"Azure 조회 오류: {e}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT start_date, end_date, week_range, scripture_range, lesson_title, lesson_url, lesson_content, section
                FROM weekly_curriculum WHERE year = ? ORDER BY end_date ASC
            """, (year,))
            rows = cursor.fetchall()
            conn.close()
            return [{
                'year': year, 'start_date': r[0], 'end_date': r[1], 'week_range': r[2], 
                'title_keywords': r[3], 'scripture_range': r[3],
                'lesson_title': r[4], 'lesson_url': r[5], 'lesson_content': r[6], 'section': r[7]
            } for r in rows]
        except: return []

    def update_lesson_content(self, year, week_range, content):
        if self.connection_string:
            try:
                table_client = TableClient.from_connection_string(self.connection_string, self.TABLE_WEEKLY)
                row_key = week_range.replace('~', '-').replace(' ', '_').replace('월', 'M').replace('일', 'D')
                entity = table_client.get_entity(partition_key=str(year), row_key=row_key)
                entity['LessonContent'] = content
                table_client.update_entity(entity)
            except Exception as e:
                print(f"Azure Content 업데이트 오류: {e}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE weekly_curriculum SET lesson_content = ? WHERE year = ? AND week_range = ?", (content, year, week_range))
            conn.commit()
            conn.close()
        except: pass

    def ensure_year_data(self, year):
        if self.check_year_data_exists(year): return True
        weekly_data = self.extract_weekly_data_from_website(year)
        if weekly_data: return self.save_weekly_data_to_db(weekly_data, year)
        return False

    def get_fallback_data(self, year):
        # 2025/2026 기본 데이터
        return []
