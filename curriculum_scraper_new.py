import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import json

class CurriculumScraper:
    def __init__(self):
        self.base_url = "https://www.churchofjesuschrist.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_current_week_curriculum(self):
        """현재 주의 공과 정보를 가져옵니다."""
        return self.get_curriculum_by_date(datetime.now())
    
    def get_curriculum_by_date(self, target_date):
        """특정 날짜의 공과 정보를 가져옵니다."""
        try:
            # DB에서 주차별 데이터 가져오기
            year = target_date.year
            week_mapping = self.get_week_mapping_from_db(year)
            
            # 해당 날짜의 주차 찾기
            target_week = None
            for week_info in week_mapping:
                start_date = datetime.strptime(week_info['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(week_info['end_date'], '%Y-%m-%d')
                
                # 날짜만 비교 (시간 제외)
                target_date_only = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
                
                if start_date <= target_date_only <= end_date:
                    target_week = week_info
                    break
            
            if target_week:
                # 직접 URL 생성 (더 안정적)
                lesson_url = self.generate_direct_url(target_week)
                lesson_title = f"{target_week['week_range']}: {target_week['title_keywords']}"
                
                # 해당 주의 상세 내용 가져오기
                lesson_content = self.get_lesson_content(lesson_url)
                
                return {
                    "title": lesson_title,
                    "content": lesson_content,
                    "url": lesson_url,
                    "week_info": target_week
                }
            
            # 매칭되지 않은 경우 기본 정보 반환
            return {
                "title": f"2025년 {target_date.strftime('%m월 %d일')} 주차 공과",
                "content": "이번 주 공과는 교리와 성약의 가르침에 관한 내용입니다.",
                "url": url
            }
                
        except Exception as e:
            print(f"공과 정보 스크래핑 중 오류: {e}")
            # 오류 시 기본 정보 반환
            return {
                "title": f"2025년 {target_date.strftime('%m월 %d일')} 주차 공과",
                "content": "이번 주 공과는 교리와 성약의 가르침에 관한 내용입니다.",
                "url": "https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025?lang=kor"
            }
    
    def get_available_weeks(self):
        """사용 가능한 주차 목록을 반환합니다."""
        # 현재 연도의 DB 데이터 사용
        current_year = datetime.now().year
        week_mapping = self.get_week_mapping_from_db(current_year)
        available_weeks = []
        
        for week_info in week_mapping:
            start_date = datetime.strptime(week_info['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(week_info['end_date'], '%Y-%m-%d')
            
            available_weeks.append({
                'week_range': week_info['week_range'],
                'title_keywords': week_info['title_keywords'],
                'start_date': week_info['start_date'],
                'end_date': week_info['end_date'],
                'section': week_info['section'],
                'display_text': f"{week_info['week_range']} - {week_info['title_keywords']}"
            })
        
        return available_weeks

    def get_week_mapping_2025(self):
        """2025년 주차별 공과 매핑 정보"""
        return [
            # 12월
            {
                'start_date': '2025-12-29',
                'end_date': '2025-12-31',
                'week_range': '12월 29일-31일',
                'title_keywords': '교리와 성약 137-138편',
                'section': '12월'
            },
            {
                'start_date': '2025-12-22',
                'end_date': '2025-12-28',
                'week_range': '12월 22일-28일',
                'title_keywords': '교리와 성약 135-136편',
                'section': '12월'
            },
            {
                'start_date': '2025-12-15',
                'end_date': '2025-12-21',
                'week_range': '12월 15일-21일',
                'title_keywords': '교리와 성약 133-134편',
                'section': '12월'
            },
            {
                'start_date': '2025-12-08',
                'end_date': '2025-12-14',
                'week_range': '12월 8일-14일',
                'title_keywords': '교리와 성약 131-132편',
                'section': '12월'
            },
            {
                'start_date': '2025-12-01',
                'end_date': '2025-12-07',
                'week_range': '12월 1일-7일',
                'title_keywords': '교리와 성약 129-130편',
                'section': '12월'
            },
            # 11월
            {
                'start_date': '2025-11-24',
                'end_date': '2025-11-30',
                'week_range': '11월 24일-30일',
                'title_keywords': '교리와 성약 127-128편',
                'section': '11월'
            },
            {
                'start_date': '2025-11-17',
                'end_date': '2025-11-23',
                'week_range': '11월 17일-23일',
                'title_keywords': '교리와 성약 125-126편',
                'section': '11월'
            },
            {
                'start_date': '2025-11-10',
                'end_date': '2025-11-16',
                'week_range': '11월 10일-16일',
                'title_keywords': '교리와 성약 123-124편',
                'section': '11월'
            },
            {
                'start_date': '2025-11-03',
                'end_date': '2025-11-09',
                'week_range': '11월 3일-9일',
                'title_keywords': '교리와 성약 121-122편',
                'section': '11월'
            },
            # 10월
            {
                'start_date': '2025-10-27',
                'end_date': '2025-11-02',
                'week_range': '10월 27일-11월 2일',
                'title_keywords': '교리와 성약 119-120편',
                'section': '10월'
            },
            {
                'start_date': '2025-10-20',
                'end_date': '2025-10-26',
                'week_range': '10월 20일-26일',
                'title_keywords': '교리와 성약 117-118편',
                'section': '10월'
            },
            {
                'start_date': '2025-10-13',
                'end_date': '2025-10-19',
                'week_range': '10월 13일-19일',
                'title_keywords': '교리와 성약 115-116편',
                'section': '10월'
            },
            {
                'start_date': '2025-10-06',
                'end_date': '2025-10-12',
                'week_range': '10월 6일-12일',
                'title_keywords': '교리와 성약 113-114편',
                'section': '10월'
            },
            # 9월
            {
                'start_date': '2025-09-29',
                'end_date': '2025-10-05',
                'week_range': '9월 29일-10월 5일',
                'title_keywords': '교리와 성약 111-112편',
                'section': '9월'
            },
            {
                'start_date': '2025-09-22',
                'end_date': '2025-09-28',
                'week_range': '9월 22일-28일',
                'title_keywords': '교리와 성약 106-108편',
                'section': '9월'
            },
            {
                'start_date': '2025-09-15',
                'end_date': '2025-09-21',
                'week_range': '9월 15일-21일',
                'title_keywords': '교리와 성약 102-105편',
                'section': '9월'
            },
            {
                'start_date': '2025-09-08',
                'end_date': '2025-09-14',
                'week_range': '9월 8일-14일',
                'title_keywords': '교리와 성약 98-101편',
                'section': '9월'
            },
            {
                'start_date': '2025-09-01',
                'end_date': '2025-09-07',
                'week_range': '9월 1일-7일',
                'title_keywords': '교리와 성약 94-97편',
                'section': '9월'
            },
            # 8월
            {
                'start_date': '2025-08-25',
                'end_date': '2025-08-31',
                'week_range': '8월 25일-31일',
                'title_keywords': '교리와 성약 101-102편',
                'section': '8월'
            },
            {
                'start_date': '2025-08-18',
                'end_date': '2025-08-24',
                'week_range': '8월 18일-24일',
                'title_keywords': '교리와 성약 99-100편',
                'section': '8월'
            },
            {
                'start_date': '2025-08-11',
                'end_date': '2025-08-17',
                'week_range': '8월 11일-17일',
                'title_keywords': '교리와 성약 97-98편',
                'section': '8월'
            },
            {
                'start_date': '2025-08-04',
                'end_date': '2025-08-10',
                'week_range': '8월 4일-10일',
                'title_keywords': '교리와 성약 95-96편',
                'section': '8월'
            },
            # 7월
            {
                'start_date': '2025-07-28',
                'end_date': '2025-08-03',
                'week_range': '7월 28일-8월 3일',
                'title_keywords': '교리와 성약 84-86편',
                'section': '7월'
            },
            {
                'start_date': '2025-07-21',
                'end_date': '2025-07-27',
                'week_range': '7월 21일-27일',
                'title_keywords': '교리와 성약 81-83편',
                'section': '7월'
            },
            {
                'start_date': '2025-07-14',
                'end_date': '2025-07-20',
                'week_range': '7월 14일-20일',
                'title_keywords': '교리와 성약 77-80편',
                'section': '7월'
            },
            {
                'start_date': '2025-07-07',
                'end_date': '2025-07-13',
                'week_range': '7월 7일-13일',
                'title_keywords': '교리와 성약 76편',
                'section': '7월'
            },
            {
                'start_date': '2025-06-30',
                'end_date': '2025-07-06',
                'week_range': '6월 30일-7월 6일',
                'title_keywords': '교리와 성약 71-75편',
                'section': '7월'
            },
            # 6월
            {
                'start_date': '2025-06-23',
                'end_date': '2025-06-29',
                'week_range': '6월 23일-29일',
                'title_keywords': '교리와 성약 67-70편',
                'section': '6월'
            },
            {
                'start_date': '2025-06-16',
                'end_date': '2025-06-22',
                'week_range': '6월 16일-22일',
                'title_keywords': '교리와 성약 65-66편',
                'section': '6월'
            },
            {
                'start_date': '2025-06-09',
                'end_date': '2025-06-15',
                'week_range': '6월 9일-15일',
                'title_keywords': '교리와 성약 63-64편',
                'section': '6월'
            },
            {
                'start_date': '2025-06-02',
                'end_date': '2025-06-08',
                'week_range': '6월 2일-8일',
                'title_keywords': '교리와 성약 60-62편',
                'section': '6월'
            },
            # 5월
            {
                'start_date': '2025-05-26',
                'end_date': '2025-06-01',
                'week_range': '5월 26일-6월 1일',
                'title_keywords': '교리와 성약 58-59편',
                'section': '5월'
            },
            {
                'start_date': '2025-05-19',
                'end_date': '2025-05-25',
                'week_range': '5월 19일-25일',
                'title_keywords': '교리와 성약 56-57편',
                'section': '5월'
            },
            {
                'start_date': '2025-05-12',
                'end_date': '2025-05-18',
                'week_range': '5월 12일-18일',
                'title_keywords': '교리와 성약 54-55편',
                'section': '5월'
            },
            {
                'start_date': '2025-05-05',
                'end_date': '2025-05-11',
                'week_range': '5월 5일-11일',
                'title_keywords': '교리와 성약 51-53편',
                'section': '5월'
            },
            # 4월
            {
                'start_date': '2025-04-28',
                'end_date': '2025-05-04',
                'week_range': '4월 28일-5월 4일',
                'title_keywords': '교리와 성약 49-50편',
                'section': '4월'
            },
            {
                'start_date': '2025-04-21',
                'end_date': '2025-04-27',
                'week_range': '4월 21일-27일',
                'title_keywords': '교리와 성약 46-48편',
                'section': '4월'
            },
            {
                'start_date': '2025-04-14',
                'end_date': '2025-04-20',
                'week_range': '4월 14일-20일',
                'title_keywords': '교리와 성약 43-45편',
                'section': '4월'
            },
            {
                'start_date': '2025-04-07',
                'end_date': '2025-04-13',
                'week_range': '4월 7일-13일',
                'title_keywords': '교리와 성약 41-42편',
                'section': '4월'
            },
            {
                'start_date': '2025-03-31',
                'end_date': '2025-04-06',
                'week_range': '3월 31일-4월 6일',
                'title_keywords': '교리와 성약 38-40편',
                'section': '4월'
            },
            # 3월
            {
                'start_date': '2025-03-24',
                'end_date': '2025-03-30',
                'week_range': '3월 24일-30일',
                'title_keywords': '교리와 성약 37편',
                'section': '3월'
            },
            {
                'start_date': '2025-03-17',
                'end_date': '2025-03-23',
                'week_range': '3월 17일-23일',
                'title_keywords': '교리와 성약 35-36편',
                'section': '3월'
            },
            {
                'start_date': '2025-03-10',
                'end_date': '2025-03-16',
                'week_range': '3월 10일-16일',
                'title_keywords': '교리와 성약 33-34편',
                'section': '3월'
            },
            {
                'start_date': '2025-03-03',
                'end_date': '2025-03-09',
                'week_range': '3월 3일-9일',
                'title_keywords': '교리와 성약 30-32편',
                'section': '3월'
            },
            # 2월
            {
                'start_date': '2025-02-24',
                'end_date': '2025-03-02',
                'week_range': '2월 24일-3월 2일',
                'title_keywords': '교리와 성약 27-29편',
                'section': '2월'
            },
            {
                'start_date': '2025-02-17',
                'end_date': '2025-02-23',
                'week_range': '2월 17일-23일',
                'title_keywords': '교리와 성약 25-26편',
                'section': '2월'
            },
            {
                'start_date': '2025-02-10',
                'end_date': '2025-02-16',
                'week_range': '2월 10일-16일',
                'title_keywords': '교리와 성약 23-24편',
                'section': '2월'
            },
            {
                'start_date': '2025-02-03',
                'end_date': '2025-02-09',
                'week_range': '2월 3일-9일',
                'title_keywords': '교리와 성약 20-22편',
                'section': '2월'
            },
            # 1월
            {
                'start_date': '2025-01-27',
                'end_date': '2025-02-02',
                'week_range': '1월 27일-2월 2일',
                'title_keywords': '교리와 성약 17-19편',
                'section': '1월'
            },
            {
                'start_date': '2025-01-20',
                'end_date': '2025-01-26',
                'week_range': '1월 20일-26일',
                'title_keywords': '교리와 성약 14-16편',
                'section': '1월'
            },
            {
                'start_date': '2025-01-13',
                'end_date': '2025-01-19',
                'week_range': '1월 13일-19일',
                'title_keywords': '교리와 성약 11-13편',
                'section': '1월'
            },
            {
                'start_date': '2025-01-06',
                'end_date': '2025-01-12',
                'week_range': '1월 6일-12일',
                'title_keywords': '교리와 성약 8-10편',
                'section': '1월'
            },
            {
                'start_date': '2025-01-01',
                'end_date': '2025-01-05',
                'week_range': '1월 1일-5일',
                'title_keywords': '교리와 성약 1-7편',
                'section': '1월'
            }
        ]

    def generate_direct_url(self, week_info):
        """주차 정보를 바탕으로 직접 URL 생성"""
        # 2025년 교리와 성약 공과 URL 패턴
        base_url = "https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025"
        
        # 주차별 URL 매핑 (실제 교회 웹사이트 구조 기반)
        url_mapping = {
            # 12월
            '12월 29일-31일': '52-doctrine-and-covenants-137-138',
            '12월 22일-28일': '51-doctrine-and-covenants-135-136',
            '12월 15일-21일': '50-doctrine-and-covenants-133-134',
            '12월 8일-14일': '49-doctrine-and-covenants-131-132',
            '12월 1일-7일': '48-doctrine-and-covenants-129-130',
            # 11월
            '11월 24일-30일': '47-doctrine-and-covenants-127-128',
            '11월 17일-23일': '46-doctrine-and-covenants-125-126',
            '11월 10일-16일': '45-doctrine-and-covenants-123-124',
            '11월 3일-9일': '44-doctrine-and-covenants-121-122',
            # 10월
            '10월 27일-11월 2일': '43-doctrine-and-covenants-119-120',
            '10월 20일-26일': '42-doctrine-and-covenants-117-118',
            '10월 13일-19일': '41-doctrine-and-covenants-115-116',
            '10월 6일-12일': '40-doctrine-and-covenants-113-114',
            # 9월
            '9월 29일-10월 5일': '39-doctrine-and-covenants-111-112',
            '9월 22일-28일': '38-doctrine-and-covenants-106-108',
            '9월 15일-21일': '37-doctrine-and-covenants-102-105',
            '9월 8일-14일': '36-doctrine-and-covenants-98-101',
            '9월 1일-7일': '35-doctrine-and-covenants-94-97',
            # 8월
            '8월 25일-31일': '34-doctrine-and-covenants-101-102',
            '8월 18일-24일': '33-doctrine-and-covenants-99-100',
            '8월 11일-17일': '32-doctrine-and-covenants-97-98',
            '8월 4일-10일': '31-doctrine-and-covenants-95-96',
            # 7월
            '7월 28일-8월 3일': '31-doctrine-and-covenants-84-86',
            '7월 21일-27일': '30-doctrine-and-covenants-81-83',
            '7월 14일-20일': '29-doctrine-and-covenants-77-80',
            '7월 7일-13일': '28-doctrine-and-covenants-76',
            '6월 30일-7월 6일': '27-doctrine-and-covenants-71-75',
            # 6월
            '6월 23일-29일': '26-doctrine-and-covenants-67-70',
            '6월 16일-22일': '25-doctrine-and-covenants-65-66',
            '6월 9일-15일': '24-doctrine-and-covenants-63-64',
            '6월 2일-8일': '23-doctrine-and-covenants-60-62',
            # 5월
            '5월 26일-6월 1일': '22-doctrine-and-covenants-58-59',
            '5월 19일-25일': '21-doctrine-and-covenants-56-57',
            '5월 12일-18일': '20-doctrine-and-covenants-54-55',
            '5월 5일-11일': '19-doctrine-and-covenants-51-53',
            # 4월
            '4월 28일-5월 4일': '18-doctrine-and-covenants-49-50',
            '4월 21일-27일': '17-doctrine-and-covenants-46-48',
            '4월 14일-20일': '16-doctrine-and-covenants-43-45',
            '4월 7일-13일': '15-doctrine-and-covenants-41-42',
            '3월 31일-4월 6일': '14-doctrine-and-covenants-38-40',
            # 3월
            '3월 24일-30일': '13-doctrine-and-covenants-37',
            '3월 17일-23일': '12-doctrine-and-covenants-35-36',
            '3월 10일-16일': '11-doctrine-and-covenants-33-34',
            '3월 3일-9일': '10-doctrine-and-covenants-30-32',
            # 2월
            '2월 24일-3월 2일': '09-doctrine-and-covenants-27-29',
            '2월 17일-23일': '08-doctrine-and-covenants-25-26',
            '2월 10일-16일': '07-doctrine-and-covenants-23-24',
            '2월 3일-9일': '06-doctrine-and-covenants-20-22',
            # 1월
            '1월 27일-2월 2일': '05-doctrine-and-covenants-17-19',
            '1월 20일-26일': '04-doctrine-and-covenants-14-16',
            '1월 13일-19일': '03-doctrine-and-covenants-11-13',
            '1월 6일-12일': '02-doctrine-and-covenants-8-10',
            '1월 1일-5일': '01-doctrine-and-covenants-1-7'
        }
        
        week_range = week_info['week_range']
        if week_range in url_mapping:
            return f"{base_url}/{url_mapping[week_range]}?lang=kor"
        else:
            # 매핑되지 않은 경우 기본 URL 반환
            return f"{base_url}?lang=kor"

    def get_lesson_content(self, lesson_url):
        """특정 주의 상세 내용을 가져옵니다."""
        try:
            response = self.session.get(lesson_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 주요 내용 추출
            content_sections = []
            
            # 제목 찾기 (h1 태그)
            title = soup.find('h1')
            if title:
                content_sections.append(f"제목: {title.get_text(strip=True)}")
            
            # 부제목 찾기 (h2 태그)
            subtitle = soup.find('h2')
            if subtitle:
                content_sections.append(f"부제목: {subtitle.get_text(strip=True)}")
            
            # 주요 내용 찾기 (p 태그들)
            paragraphs = soup.find_all('p')
            for p in paragraphs[:15]:  # 처음 15개 단락만
                text = p.get_text(strip=True)
                if text and len(text) > 20:  # 의미있는 텍스트만
                    content_sections.append(text)
            
            # 소제목들 찾기 (h3 태그들)
            subheadings = soup.find_all('h3')
            for h3 in subheadings[:10]:  # 처음 10개 소제목만
                text = h3.get_text(strip=True)
                if text and len(text) > 5:
                    content_sections.append(f"\n## {text}")
            
            # 내용이 없으면 기본 메시지
            if not content_sections:
                content_sections.append("이번 주 공과의 상세 내용을 가져올 수 없습니다.")
            
            return "\n\n".join(content_sections)
            
        except Exception as e:
            print(f"상세 내용 가져오기 중 오류: {e}")
            return "이번 주 공과의 상세 내용을 가져올 수 없습니다."

    def get_week_mapping_from_db(self, year):
        """DB에서 주차별 매핑 데이터를 가져옵니다."""
        try:
            from weekly_curriculum_manager import WeeklyCurriculumManager
            
            manager = WeeklyCurriculumManager()
            
            # 해당 연도 데이터가 DB에 있는지 확인하고, 없으면 웹사이트에서 가져와서 저장
            manager.ensure_year_data(year)
            
            # DB에서 데이터 조회
            return manager.get_weekly_data_from_db(year)
            
        except Exception as e:
            print(f"DB에서 주차 매핑 가져오기 실패: {e}")
            # fallback으로 하드코딩된 2025년 데이터 사용
            if year == 2025:
                return self.get_week_mapping_2025()
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
    current_curriculum = scraper.get_current_week_curriculum()
    print("현재 주 공과:", json.dumps(current_curriculum, ensure_ascii=False, indent=2))