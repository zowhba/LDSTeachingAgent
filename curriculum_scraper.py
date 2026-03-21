import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import json
import os
from weekly_curriculum_manager import WeeklyCurriculumManager

class CurriculumScraper:
    def __init__(self):
        self.base_url = "https://www.churchofjesuschrist.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # 매니저 초기화 (Azure 연결 문자열 포함)
        self.manager = WeeklyCurriculumManager()

    def get_current_week_curriculum(self):
        """현재 주의 공과 정보를 가져옵니다."""
        return self.get_curriculum_by_date(datetime.now())
    
    def get_curriculum_by_date(self, target_date):
        """특정 날짜의 공과 정보를 가져옵니다."""
        try:
            year = target_date.year
            week_mapping = self.get_week_mapping_from_db(year)
            
            # 해당 날짜의 주차 찾기
            target_week = None
            target_date_only = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            for week_info in week_mapping:
                start_date = datetime.strptime(week_info['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(week_info['end_date'], '%Y-%m-%d')
                
                if start_date <= target_date_only <= end_date:
                    target_week = week_info
                    break
            
            if target_week:
                # 1. 이미 캐시된 내용이 있는지 확인
                cached_content = target_week.get('lesson_content')
                
                # lesson_url 확인
                lesson_url = target_week.get('lesson_url')
                if not lesson_url:
                    lesson_url = self.generate_direct_url(target_week, year)
                
                lesson_title = f"{target_week['week_range']}: {target_week['title_keywords']}"
                
                if cached_content and len(cached_content) > 100:
                    print(f"📦 저장된 공과 내용을 사용합니다: {target_week['week_range']}")
                    lesson_content = cached_content
                else:
                    # 2. 캐시가 없으면 스크래핑 시도
                    print(f"🌐 실시간 스크래핑 시도: {lesson_url}")
                    lesson_content = self.get_lesson_content(lesson_url)
                    
                    # 3. 스크래핑 성공 시 캐시 업데이트
                    if lesson_content and "가져올 수 없습니다" not in lesson_content:
                        self.manager.update_lesson_content(year, target_week['week_range'], lesson_content)
                
                return {
                    "title": lesson_title,
                    "content": lesson_content,
                    "url": lesson_url,
                    "week_info": target_week
                }
            
            return {
                "title": f"{year}년 {target_date.strftime('%m월 %d일')} 주차 공과",
                "content": "해당 날짜의 공과 정보를 찾을 수 없습니다.",
                "url": f"{self.base_url}/study/manual/come-follow-me-for-home-and-church?lang=kor"
            }
                
        except Exception as e:
            print(f"공과 정보 가져오기 중 오류: {e}")
            return {
                "title": "공과 정보 오류",
                "content": "공과 정보를 가져오는 중 시스템 오류가 발생했습니다.",
                "url": ""
            }
    
    def get_available_weeks(self):
        """사용 가능한 주차 목록을 반환합니다."""
        current_year = datetime.now().year
        week_mapping = self.get_week_mapping_from_db(current_year)
        available_weeks = []
        
        for week_info in week_mapping:
            title_clean = week_info.get('title_keywords', '')
            formatted_week_range = week_info['week_range'].replace('일-', '일~')

            available_weeks.append({
                'week_range': week_info['week_range'],
                'title_keywords': week_info.get('title_keywords', ''),
                'start_date': week_info['start_date'],
                'end_date': week_info['end_date'],
                'section': week_info['section'],
                'display_text': f"{formatted_week_range} ({title_clean})" if title_clean else formatted_week_range
            })
        
        available_weeks.sort(key=lambda x: x['end_date'])
        return available_weeks

    def generate_direct_url(self, week_info, year):
        """주차 정보를 바탕으로 직접 URL 생성"""
        known_mappings = {2025: 'doctrine-and-covenants', 2026: 'old-testament'}
        scripture_type = known_mappings.get(year, 'doctrine-and-covenants')
        base_url = f"https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-{scripture_type}-{year}"
        
        try:
            all_weeks = self.manager.get_weekly_data_from_db(year)
            week_index = None
            for i, week in enumerate(all_weeks):
                if week.get('week_range') == week_info.get('week_range'):
                    week_index = i + 1
                    break
            
            if week_index:
                return f"{base_url}/{week_index:02d}?lang=kor"
            return f"{base_url}/01?lang=kor"
        except:
            return f"{base_url}/01?lang=kor"

    def get_lesson_content(self, lesson_url):
        """특정 주의 상세 내용을 가져옵니다."""
        try:
            response = self.session.get(lesson_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content_sections = []
            # 제목/부제목
            for tag in ['h1', 'h2']:
                el = soup.find(tag)
                if el: content_sections.append(el.get_text(strip=True))
            
            # 본문
            paragraphs = soup.find_all(['p', 'li'])
            for p in paragraphs[:60]:
                text = p.get_text(strip=True)
                if len(text) > 20: content_sections.append(text)
            
            if not content_sections:
                return "이번 주 공과의 상세 내용을 가져올 수 없습니다. (웹사이트 구조 변경 또는 접근 제한)"
            
            return "\n\n".join(content_sections)
        except Exception as e:
            print(f"상세 내용 가져오기 실패: {e}")
            return "이번 주 공과의 상세 내용을 가져올 수 없습니다. (웹사이트 접속 불가)"

    def get_week_mapping_from_db(self, year):
        """DB/Storage에서 주차별 매핑 데이터를 가져옵니다."""
        try:
            self.manager.ensure_year_data(year)
            return self.manager.get_weekly_data_from_db(year)
        except Exception as e:
            print(f"주차 매핑 가져오기 실패: {e}")
            return []

    def get_weekly_curriculum_list(self):
        """전체 주차별 공과 목록을 가져옵니다."""
        try:
            url = "https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025?lang=kor"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            curriculum_list = []
            lesson_links = soup.find_all('a', href=re.compile(r'/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025/'))
            
            for link in lesson_links:
                title = link.get_text(strip=True)
                href = link.get('href')
                if title and href:
                    curriculum_list.append({
                        "title": title,
                        "url": self.base_url + href
                    })
            
            return curriculum_list
            
        except Exception as e:
            print(f"공과 목록 가져오기 중 오류: {e}")
            return []

# 사용 예시
if __name__ == "__main__":
    scraper = CurriculumScraper()
    
    # 1년치 커리큘럼 전체 가져오기
    current_year = datetime.now().year
    print(f"🔄 {current_year}년 커리큘럼 전체 데이터 수집 중...")
    
    # DB에서 모든 주차 데이터 가져오기
    week_mapping = scraper.get_week_mapping_from_db(current_year)
    
    print(f"✅ {current_year}년 총 {len(week_mapping)}개 주차 데이터 수집 완료")
    print("\n📋 주차별 목록:")
    for i, week in enumerate(week_mapping, 1):
        print(f"  {i}. {week['week_range']} - {week['title_keywords']}")
    
    # 현재 주 공과 정보도 출력
    print("\n📖 현재 주 공과:")
    current_curriculum = scraper.get_current_week_curriculum()
    print(json.dumps(current_curriculum, ensure_ascii=False, indent=2)) 