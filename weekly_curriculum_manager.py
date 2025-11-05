#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
주차별 경전 범위 관리 모듈
웹사이트 목차에서 정확한 주차별 범위를 추출하여 DB에 저장하고 관리합니다.
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time


class WeeklyCurriculumManager:
    """주차별 경전 범위를 관리하는 클래스"""
    
    def __init__(self, db_path='curriculum_data.db'):
        self.db_path = db_path
        self.base_url = "https://www.churchofjesuschrist.org"
        
    def check_year_data_exists(self, year):
        """해당 연도의 데이터가 DB에 있는지 확인"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, total_weeks, last_updated 
            FROM curriculum_status 
            WHERE year = ?
        """, (year,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == 'completed' and result[1] > 0:
            return True
        return False
    
    def extract_weekly_data_from_website(self, year):
        """웹사이트 목차 페이지에서 주차별 데이터를 추출"""
        url = f"https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-{year}?lang=kor"
        
        # 재시도 설정
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                print(f"🔄 웹사이트 접근 시도 {attempt + 1}/{max_retries}: {url}")
                
                # 세션을 사용하여 연결 재사용
                session = requests.Session()
                session.headers.update(headers)
                
                response = session.get(url, timeout=30)
                response.raise_for_status()
                
                print(f"✅ 웹사이트 접근 성공 (상태코드: {response.status_code})")
                break
                
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, 
                    requests.exceptions.RequestException) as e:
                print(f"❌ 시도 {attempt + 1} 실패: {e}")
                
                if attempt < max_retries - 1:
                    print(f"⏳ {retry_delay}초 후 재시도...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 지수 백오프
                else:
                    print(f"❌ 모든 재시도 실패. 하드코딩된 데이터 사용.")
                    return self.get_fallback_data(year)
        
        try:
            
            soup = BeautifulSoup(response.content, 'html.parser')
            weekly_data = []
            
            print("📊 HTML 파싱 시작...")
            
            # 모든 링크에서 교리와 성약 관련 링크 찾기
            all_links = soup.find_all('a', href=True)
            doctrine_links = []
            
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # 교리와 성약 관련 링크 필터링
                if ('doctrine-and-covenants' in href and year == 2025) or \
                   ('교리와' in text and ('편' in text or 'D&C' in text)):
                    doctrine_links.append(link)
            
            print(f"📊 교리와 성약 관련 링크 {len(doctrine_links)}개 발견")
            
            # 각 링크에서 날짜와 경전 범위 추출
            for link in doctrine_links:
                lesson_data = self.parse_lesson_link_improved(link, year)
                if lesson_data:
                    weekly_data.append(lesson_data)
                    print(f"✅ 추가: {lesson_data['week_range']} - {lesson_data['scripture_range']}")
            
            # 만약 링크 방식으로 안 되면 텍스트 기반 파싱 시도
            if not weekly_data:
                print("🔄 텍스트 기반 파싱 시도...")
                weekly_data = self.parse_from_text_content(soup, year)
            
            print(f"✅ {year}년 웹사이트에서 {len(weekly_data)}개 주차 데이터 추출 완료")
            return weekly_data
            
        except Exception as e:
            print(f"❌ {year}년 웹사이트 데이터 추출 실패: {e}")
            return []
    
    def parse_lesson_link_improved(self, link, year):
        """개선된 공과 링크 파싱 메서드"""
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if not text:
            return None
        
        print(f"🔍 파싱 중: {text}")
        
        # 날짜 범위 추출 - 더 유연한 패턴
        date_patterns = [
            r'(\d{1,2}월\s*\d{1,2}일)\s*[~\-–]\s*(\d{1,2}월\s*\d{1,2}일)',  # 10월 27일~11월 2일
            r'(\d{1,2}월\s*\d{1,2}일)\s*[~\-–]\s*(\d{1,2}일)',            # 9월 8일~14일
            r'(\d{1,2}월\s*\d{1,2}일)\\?~(\d{1,2}일)',                   # 백슬래시 포함
            r'(\d{1,2}월\s*\d{1,2}일)\\?~(\d{1,2}월\s*\d{1,2}일)',      # 백슬래시 포함
        ]
        
        date_range = None
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                start_part = match.group(1).replace(' ', '').replace('\\', '')
                end_part = match.group(2).replace(' ', '').replace('\\', '')
                
                # 월이 없는 경우 시작 월로 보완
                if '월' not in end_part:
                    start_month = re.search(r'(\d{1,2})월', start_part)
                    if start_month:
                        end_part = f"{start_month.group(1)}월{end_part}"
                
                date_range = f"{start_part}~{end_part}"
                print(f"📅 날짜 범위 발견: {date_range}")
                break
        
        if not date_range:
            return None
        
        # 경전 범위 추출 - 더 유연한 패턴
        scripture_patterns = [
            r'교리와\s*성약\s*(\d+)\s*[~\-–\\]+\s*(\d+)\s*편',           # 교리와 성약 98~101편
            r'교리와\s*성약\s*(\d+)\s*편',                              # 교리와 성약 76편
            r'D&C\s*(\d+)\s*[~\-–]\s*(\d+)',                           # D&C 98-101
            r'D&C\s*(\d+)',                                            # D&C 76
            r'(\d+)\s*[~\-–\\]+\s*(\d+)\s*편',                         # 98~101편
            r'(\d+)\s*편',                                             # 76편
        ]
        
        scripture_range = None
        for pattern in scripture_patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    scripture_range = f"교리와 성약 {groups[0]}~{groups[1]}편"
                elif len(groups) == 1:
                    scripture_range = f"교리와 성약 {groups[0]}편"
                print(f"📖 경전 범위 발견: {scripture_range}")
                break
        
        if not scripture_range:
            return None
        
        # 날짜 범위를 datetime으로 변환
        start_date, end_date = self.parse_date_range(date_range, year)
        
        if not start_date or not end_date:
            return None
        
        # URL 정규화
        if href and href.startswith('/'):
            full_url = self.base_url + href
        elif href:
            full_url = href
        else:
            # URL이 없으면 생성
            full_url = self.generate_url_from_scripture(scripture_range, year)
        
        # 월 정보 추출
        month_match = re.search(r'(\d+)월', date_range)
        section = f"{month_match.group(1)}월" if month_match else "기타"
        
        return {
            'year': year,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'week_range': date_range,
            'scripture_range': scripture_range,
            'lesson_title': text,
            'lesson_url': full_url,
            'section': section
        }
    
    def parse_from_text_content(self, soup, year):
        """텍스트 내용에서 직접 파싱하는 백업 메서드"""
        weekly_data = []
        
        # 페이지의 모든 텍스트에서 패턴 찾기
        page_text = soup.get_text()
        
        # 제공된 웹사이트 데이터 기반 패턴 매칭
        september_patterns = [
            (r'9월\s*1일\\?~7일.*?교리와\s*성약\s*94\\?~97편', '9월1일~7일', '교리와 성약 94~97편'),
            (r'9월\s*8일\\?~14일.*?교리와\s*성약\s*98\\?~101편', '9월8일~14일', '교리와 성약 98~101편'),
            (r'9월\s*15일\\?~21일.*?교리와\s*성약\s*102\\?~105편', '9월15일~21일', '교리와 성약 102~105편'),
            (r'9월\s*22일\\?~28일.*?교리와\s*성약\s*106\\?~108편', '9월22일~28일', '교리와 성약 106~108편'),
        ]
        
        for pattern, date_range, scripture_range in september_patterns:
            if re.search(pattern, page_text):
                start_date, end_date = self.parse_date_range(date_range, year)
                if start_date and end_date:
                    weekly_data.append({
                        'year': year,
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d'),
                        'week_range': date_range,
                        'scripture_range': scripture_range,
                        'lesson_title': f"{date_range}{scripture_range}",
                        'lesson_url': self.generate_url_from_scripture(scripture_range, year),
                        'section': '9월'
                    })
                    print(f"✅ 텍스트에서 추출: {date_range} - {scripture_range}")
        
        return weekly_data
    
    def generate_url_from_scripture(self, scripture_range, year):
        """경전 범위에서 URL 생성"""
        # 교리와 성약 98~101편 -> 98-101
        match = re.search(r'(\d+)~(\d+)', scripture_range)
        if match:
            start_num = match.group(1)
            end_num = match.group(2)
            return f"{self.base_url}/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-{year}/36-doctrine-and-covenants-{start_num}-{end_num}?lang=kor"
        
        # 단일 편인 경우
        single_match = re.search(r'(\d+)편', scripture_range)
        if single_match:
            num = single_match.group(1)
            return f"{self.base_url}/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-{year}/doctrine-and-covenants-{num}?lang=kor"
        
        return f"{self.base_url}/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-{year}?lang=kor"

    def parse_lesson_link(self, link, year, month):
        """개별 공과 링크에서 주차 정보 파싱"""
        href = link.get('href')
        text = link.get_text(strip=True)
        
        if not href or not text:
            return None
        
        # 날짜 범위 추출 (예: "9월 8일~14일", "10월 27일~11월 2일")
        date_patterns = [
            r'(\d{1,2}월\s*\d{1,2}일)\s*[~\-–]\s*(\d{1,2}월\s*\d{1,2}일)',  # 10월 27일~11월 2일
            r'(\d{1,2}월\s*\d{1,2}일)\s*[~\-–]\s*(\d{1,2}일)',            # 9월 8일~14일
        ]
        
        date_range = None
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                start_part = match.group(1).replace(' ', '')
                end_part = match.group(2).replace(' ', '')
                
                # 월이 없는 경우 시작 월로 보완
                if '월' not in end_part:
                    start_month = re.search(r'(\d{1,2})월', start_part)
                    if start_month:
                        end_part = f"{start_month.group(1)}월{end_part}"
                
                date_range = f"{start_part}~{end_part}"
                break
        
        if not date_range:
            return None
        
        # 경전 범위 추출 (예: "교리와 성약 98~101편", "교리와 성약 76편")
        scripture_patterns = [
            r'교리와\s*성약\s*(\d+)\s*[~\-–]\s*(\d+)\s*편',  # 교리와 성약 98~101편
            r'교리와\s*성약\s*(\d+)\s*편',                    # 교리와 성약 76편
            r'D&C\s*(\d+)\s*[~\-–]\s*(\d+)',               # D&C 98-101
            r'D&C\s*(\d+)',                                # D&C 76
        ]
        
        scripture_range = None
        for pattern in scripture_patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    scripture_range = f"교리와 성약 {groups[0]}~{groups[1]}편"
                elif len(groups) == 1:
                    scripture_range = f"교리와 성약 {groups[0]}편"
                break
        
        if not scripture_range:
            return None
        
        # 날짜 범위를 datetime으로 변환
        start_date, end_date = self.parse_date_range(date_range, year)
        
        if not start_date or not end_date:
            return None
        
        # URL 정규화
        if href.startswith('/'):
            full_url = self.base_url + href
        else:
            full_url = href
        
        return {
            'year': year,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'week_range': date_range,
            'scripture_range': scripture_range,
            'lesson_title': text,
            'lesson_url': full_url,
            'section': month
        }
    
    def parse_date_range(self, date_range, year):
        """날짜 범위 문자열을 datetime 객체로 변환"""
        try:
            # 9월8일~14일 형태
            pattern1 = r'(\d{1,2})월(\d{1,2})일~(\d{1,2})일'
            match1 = re.search(pattern1, date_range)
            if match1:
                month = int(match1.group(1))
                start_day = int(match1.group(2))
                end_day = int(match1.group(3))
                
                start_date = datetime(year, month, start_day)
                end_date = datetime(year, month, end_day)
                return start_date, end_date
            
            # 10월27일~11월2일 형태
            pattern2 = r'(\d{1,2})월(\d{1,2})일~(\d{1,2})월(\d{1,2})일'
            match2 = re.search(pattern2, date_range)
            if match2:
                start_month = int(match2.group(1))
                start_day = int(match2.group(2))
                end_month = int(match2.group(3))
                end_day = int(match2.group(4))
                
                start_date = datetime(year, start_month, start_day)
                end_date = datetime(year, end_month, end_day)
                return start_date, end_date
            
            return None, None
            
        except Exception as e:
            print(f"날짜 파싱 오류: {e}")
            return None, None
    
    def save_weekly_data_to_db(self, weekly_data, year):
        """주차별 데이터를 DB에 저장"""
        if not weekly_data:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 기존 데이터 삭제
            cursor.execute("DELETE FROM weekly_curriculum WHERE year = ?", (year,))
            
            # 새 데이터 삽입
            for data in weekly_data:
                cursor.execute("""
                    INSERT INTO weekly_curriculum 
                    (year, start_date, end_date, week_range, scripture_range, 
                     lesson_title, lesson_url, section) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['year'], data['start_date'], data['end_date'],
                    data['week_range'], data['scripture_range'],
                    data['lesson_title'], data['lesson_url'], data['section']
                ))
            
            # 상태 업데이트
            cursor.execute("""
                INSERT OR REPLACE INTO curriculum_status 
                (year, last_updated, total_weeks, status) 
                VALUES (?, ?, ?, ?)
            """, (year, datetime.now(), len(weekly_data), 'completed'))
            
            conn.commit()
            print(f"✅ {year}년 {len(weekly_data)}개 주차 데이터 DB 저장 완료")
            return True
            
        except Exception as e:
            print(f"❌ DB 저장 실패: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_weekly_data_from_db(self, year):
        """DB에서 주차별 데이터 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT start_date, end_date, week_range, scripture_range, 
                   lesson_title, lesson_url, section
            FROM weekly_curriculum 
            WHERE year = ? 
            ORDER BY start_date DESC
        """, (year,))
        
        rows = cursor.fetchall()
        conn.close()
        
        weekly_data = []
        for row in rows:
            weekly_data.append({
                'start_date': row[0],
                'end_date': row[1],
                'week_range': row[2],
                'title_keywords': row[3],  # scripture_range를 title_keywords로 매핑
                'lesson_title': row[4],
                'lesson_url': row[5],
                'section': row[6]
            })
        
        return weekly_data
    
    def ensure_year_data(self, year):
        """연도별 데이터가 있는지 확인하고, 없으면 웹사이트에서 가져와서 저장"""
        if self.check_year_data_exists(year):
            print(f"📁 {year}년 데이터가 DB에 이미 존재합니다.")
            return True
        
        print(f"🔄 {year}년 데이터를 웹사이트에서 가져오는 중...")
        weekly_data = self.extract_weekly_data_from_website(year)
        
        # 웹사이트에서 데이터를 못 가져왔으면 fallback 사용
        if not weekly_data:
            print(f"⚠️ 웹사이트에서 데이터를 가져오지 못했습니다. fallback 데이터 사용...")
            weekly_data = self.get_fallback_data(year)
        
        if weekly_data:
            return self.save_weekly_data_to_db(weekly_data, year)
        
        print(f"❌ {year}년 데이터를 전혀 가져올 수 없습니다.")
        return False
    
    def get_fallback_data(self, year):
        """웹사이트 접근 실패 시 사용할 fallback 데이터"""
        if year == 2025:
            print("📁 2025년 하드코딩된 fallback 데이터 사용")
            return [
                {
                    'year': 2025,
                    'start_date': '2025-09-22',
                    'end_date': '2025-09-28',
                    'week_range': '9월22일~28일',
                    'scripture_range': '교리와 성약 106~108편',
                    'lesson_title': '9월 22일~28일교리와 성약 106~108편"하나님의 아들의 반차"',
                    'lesson_url': 'https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025/38-doctrine-and-covenants-106-108?lang=kor',
                    'section': '9월'
                },
                {
                    'year': 2025,
                    'start_date': '2025-09-15',
                    'end_date': '2025-09-21',
                    'week_range': '9월15일~21일',
                    'scripture_range': '교리와 성약 102~105편',
                    'lesson_title': '9월 15일~21일교리와 성약 102~105편"많은 환난 후에 축복이 옴이니라"',
                    'lesson_url': 'https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025/37-doctrine-and-covenants-102-105?lang=kor',
                    'section': '9월'
                },
                {
                    'year': 2025,
                    'start_date': '2025-09-08',
                    'end_date': '2025-09-14',
                    'week_range': '9월8일~14일',
                    'scripture_range': '교리와 성약 98~101편',
                    'lesson_title': '9월 8일~14일교리와 성약 98~101편"가만히 있어 내가 하나님인 줄 알라"',
                    'lesson_url': 'https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025/36-doctrine-and-covenants-98-101?lang=kor',
                    'section': '9월'
                },
                {
                    'year': 2025,
                    'start_date': '2025-09-01',
                    'end_date': '2025-09-07',
                    'week_range': '9월1일~7일',
                    'scripture_range': '교리와 성약 94~97편',
                    'lesson_title': '9월 1일~7일교리와 성약 94~97편"시온의 구원을 위하여"',
                    'lesson_url': 'https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025/35-doctrine-and-covenants-94-97?lang=kor',
                    'section': '9월'
                },
                # 추가 월별 데이터들...
                {
                    'year': 2025,
                    'start_date': '2025-08-25',
                    'end_date': '2025-08-31',
                    'week_range': '8월25일~31일',
                    'scripture_range': '교리와 성약 94~97편',
                    'lesson_title': '8월 25일~31일교리와 성약 94~97편',
                    'lesson_url': 'https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025/34-doctrine-and-covenants-94-97?lang=kor',
                    'section': '8월'
                },
                {
                    'year': 2025,
                    'start_date': '2025-10-01',
                    'end_date': '2025-10-07',
                    'week_range': '10월1일~7일',
                    'scripture_range': '교리와 성약 109~110편',
                    'lesson_title': '10월 1일~7일교리와 성약 109~110편',
                    'lesson_url': 'https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025/39-doctrine-and-covenants-109-110?lang=kor',
                    'section': '10월'
                },
            ]
        else:
            print(f"⚠️ {year}년 fallback 데이터가 없습니다.")
            return []


def initialize_current_year_data():
    """현재 연도 데이터 초기화 (백그라운드에서 실행)"""
    current_year = datetime.now().year
    manager = WeeklyCurriculumManager()
    manager.ensure_year_data(current_year)


if __name__ == "__main__":
    # 테스트용
    manager = WeeklyCurriculumManager()
    manager.ensure_year_data(2025)
    
    # 결과 확인
    data = manager.get_weekly_data_from_db(2025)
    print(f"\n📊 2025년 총 {len(data)}개 주차 데이터:")
    
    # 9월 데이터만 확인
    september_data = [d for d in data if '9월' in d['week_range']]
    for item in september_data:
        print(f"  {item['week_range']}: {item['title_keywords']}")
