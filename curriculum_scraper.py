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
                # URL 동적 생성 (주차 번호 기반 /01, /02 형식)
                # week_info에 필요한 모든 필드가 있는지 확인
                if 'start_date' not in target_week or 'end_date' not in target_week:
                    print(f"⚠️ target_week에 필요한 필드가 없습니다: {target_week}")
                    # 기본값으로 설정
                    if 'start_date' not in target_week:
                        target_week['start_date'] = week_mapping[0]['start_date'] if week_mapping else f"{year}-01-01"
                    if 'end_date' not in target_week:
                        target_week['end_date'] = week_mapping[0]['end_date'] if week_mapping else f"{year}-01-07"
                
                # DB에 저장된 lesson_url이 있으면 우선 사용, 없으면 생성
                lesson_url = target_week.get('lesson_url')
                if not lesson_url:
                    lesson_url = self.generate_direct_url(target_week, year)
                    print(f"🔗 생성된 URL: {lesson_url}")
                else:
                    print(f"🔗 DB에서 가져온 URL: {lesson_url}")
                
                lesson_title = f"{target_week['week_range']}: {target_week['title_keywords']}"
                
                # 해당 주의 상세 내용 가져오기 (동일한 URL 사용)
                lesson_content = self.get_lesson_content(lesson_url)
                
                return {
                    "title": lesson_title,
                    "content": lesson_content,
                    "url": lesson_url,  # 원본 링크와 동일한 URL 사용
                    "week_info": target_week
                }
            
            # 매칭되지 않은 경우 기본 정보 반환
            # 연도별 경전 종류 결정
            known_mappings = {
                2025: 'doctrine-and-covenants',
                2026: 'old-testament',
            }
            scripture_type = known_mappings.get(year, 'doctrine-and-covenants')
            base_url = f"{self.base_url}/study/manual/come-follow-me-for-home-and-church-{scripture_type}-{year}"
            
            return {
                "title": f"{year}년 {target_date.strftime('%m월 %d일')} 주차 공과",
                "content": f"{year}년 공과 내용을 찾을 수 없습니다.",
                "url": f"{base_url}/01?lang=kor"
            }
                
        except Exception as e:
            print(f"공과 정보 스크래핑 중 오류: {e}")
            # 오류 시 기본 정보 반환
            year = target_date.year
            known_mappings = {
                2025: 'doctrine-and-covenants',
                2026: 'old-testament',
            }
            scripture_type = known_mappings.get(year, 'doctrine-and-covenants')
            base_url = f"{self.base_url}/study/manual/come-follow-me-for-home-and-church-{scripture_type}-{year}"
            
            return {
                "title": f"{year}년 {target_date.strftime('%m월 %d일')} 주차 공과",
                "content": "이번 주 공과 내용을 가져올 수 없습니다.",
                "url": f"{base_url}/01?lang=kor"
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
            
            # title_keywords에서 날짜 패턴 제거 (중복 방지)
            title_clean = week_info['title_keywords']
            # 날짜 패턴 제거 (예: "12월 29일~1월 4일", "12월29일~1월4일" 등)
            date_patterns = [
                r'\d{1,2}월\s*\d{1,2}일\s*[~\-–]\s*\d{1,2}월\s*\d{1,2}일',  # 12월 29일~1월 4일
                r'\d{1,2}월\s*\d{1,2}일\s*[~\-–]\s*\d{1,2}일',              # 12월 29일~4일
                r'\d{1,2}월\d{1,2}일\s*[~\-–]\s*\d{1,2}월\d{1,2}일',        # 12월29일~1월4일
                r'\d{1,2}월\d{1,2}일\s*[~\-–]\s*\d{1,2}일',                # 12월29일~4일
            ]
            for pattern in date_patterns:
                title_clean = re.sub(pattern, '', title_clean).strip()
            
            available_weeks.append({
                'week_range': week_info['week_range'],
                'title_keywords': week_info['title_keywords'],
                'start_date': week_info['start_date'],
                'end_date': week_info['end_date'],
                'section': week_info['section'],
                'display_text': f"{week_info['week_range']} - {title_clean}" if title_clean else week_info['week_range']
            })
        
        # end_date를 기준으로 오름차순 정렬
        available_weeks.sort(key=lambda x: x['end_date'])
        
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

    def generate_direct_url(self, week_info, year=None):
        """주차 정보를 바탕으로 직접 URL 생성"""
        if year is None:
            # week_info에서 연도 추출 시도
            if 'start_date' in week_info:
                start_date = datetime.strptime(week_info['start_date'], '%Y-%m-%d')
                year = start_date.year
            else:
                year = datetime.now().year
                print(f"⚠️ week_info에 start_date가 없어 현재 연도({year}) 사용")
        
        # 연도별 경전 종류 결정
        known_mappings = {
            2025: 'doctrine-and-covenants',
            2026: 'old-testament',
        }
        scripture_type = known_mappings.get(year, 'doctrine-and-covenants')
        
        # Base URL 생성 (반드시 scripture_type 포함)
        base_url = f"https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-{scripture_type}-{year}"
        print(f"🔍 Base URL 생성: {base_url}, year={year}, scripture_type={scripture_type}")
        
        # 주차 번호 계산: DB에서 가져온 모든 주차 목록에서의 순서 사용
        try:
            from weekly_curriculum_manager import WeeklyCurriculumManager
            manager = WeeklyCurriculumManager()
            all_weeks = manager.get_weekly_data_from_db(year)
            
            if not all_weeks:
                print(f"⚠️ {year}년 주차 데이터가 없습니다. 기본 URL 반환")
                return f"{base_url}/01?lang=kor"
            
            # end_date 기준으로 정렬된 목록에서 현재 주차의 인덱스 찾기
            week_index = None
            target_start = week_info.get('start_date')
            target_end = week_info.get('end_date')
            
            # week_range로도 매칭 시도
            target_week_range = week_info.get('week_range')
            
            for i, week in enumerate(all_weeks):
                # start_date와 end_date로 매칭
                if target_start and target_end:
                    if week.get('start_date') == target_start and week.get('end_date') == target_end:
                        week_index = i + 1  # 1부터 시작
                        break
                # week_range로 매칭 (백업)
                elif target_week_range and week.get('week_range') == target_week_range:
                    week_index = i + 1
                    break
            
            if week_index:
                # 주차 번호를 2자리 숫자로 포맷팅 (01, 02, ..., 52)
                week_num = f"{week_index:02d}"
                url = f"{base_url}/{week_num}?lang=kor"
                print(f"✅ URL 생성: {url} (주차 {week_index})")
                return url
            else:
                print(f"⚠️ 주차를 찾을 수 없습니다. week_info: {week_info}")
                # 첫 번째 주차로 기본값 설정
                return f"{base_url}/01?lang=kor"
        except Exception as e:
            print(f"❌ 주차 번호 계산 실패: {e}")
            import traceback
            traceback.print_exc()
            # 오류 시 첫 번째 주차로 기본값 설정
            return f"{base_url}/01?lang=kor"

    def get_lesson_content(self, lesson_url):
        """특정 주의 상세 내용을 가져옵니다."""
        try:
            print(f"🔍 공과 내용 가져오기 시도: {lesson_url}")
            response = self.session.get(lesson_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 주요 내용 추출
            content_sections = []
            
            # 제목 찾기 (h1 태그)
            title = soup.find('h1')
            if title:
                title_text = title.get_text(strip=True)
                if title_text:
                    content_sections.append(f"제목: {title_text}")
            
            # 부제목 찾기 (h2 태그)
            subtitle = soup.find('h2')
            if subtitle:
                subtitle_text = subtitle.get_text(strip=True)
                if subtitle_text:
                    content_sections.append(f"부제목: {subtitle_text}")
            
            # 주요 내용 찾기 (p 태그들) - 더 많은 단락 추출
            paragraphs = soup.find_all('p')
            for p in paragraphs[:50]:  # 처음 50개 단락으로 증가
                text = p.get_text(strip=True)
                if text and len(text) > 10:  # 최소 길이를 10으로 낮춤
                    content_sections.append(text)
            
            # li 태그 (리스트 항목)도 추출
            list_items = soup.find_all('li')
            for li in list_items[:30]:  # 처음 30개 리스트 항목
                text = li.get_text(strip=True)
                if text and len(text) > 10:
                    content_sections.append(f"- {text}")
            
            # div.content 또는 article 태그에서 내용 찾기 (우선순위 높임)
            content_div = soup.find('div', class_=lambda x: x and ('content' in x.lower() or 'article' in x.lower() or 'body' in x.lower()))
            if not content_div:
                content_div = soup.find('article')
            if not content_div:
                # main 태그 찾기
                content_div = soup.find('main')
            if content_div:
                # div 내부의 모든 텍스트 추출 (더 많은 내용)
                div_text = content_div.get_text(strip=True, separator='\n')
                if div_text and len(div_text) > 200:
                    # 중복 제거하면서 추가
                    existing_text = "\n\n".join(content_sections)
                    if div_text not in existing_text:
                        content_sections.append(div_text[:5000])  # 처음 5000자로 증가
            
            # 내용이 없으면 기본 메시지
            if not content_sections or len("\n\n".join(content_sections)) < 50:
                print(f"⚠️ 내용 추출 실패: {len(content_sections)}개 섹션")
                return "이번 주 공과의 상세 내용을 가져올 수 없습니다."
            
            result = "\n\n".join(content_sections)
            print(f"✅ 내용 추출 성공: {len(result)}자")
            return result
            
        except Exception as e:
            print(f"❌ 상세 내용 가져오기 중 오류: {e}")
            import traceback
            traceback.print_exc()
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