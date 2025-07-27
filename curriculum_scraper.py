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
        """?„ì¬ ì£¼ì˜ ê³µê³¼ ?•ë³´ë¥?ê°€?¸ì˜µ?ˆë‹¤."""
        return self.get_curriculum_by_date(datetime.now())
    
    def get_curriculum_by_date(self, target_date):
        """?¹ì • ? ì§œ??ê³µê³¼ ?•ë³´ë¥?ê°€?¸ì˜µ?ˆë‹¤."""
        try:
            # 2025??êµë¦¬?€ ?±ì•½ ê³µê³¼ ?˜ì´ì§€
            url = "https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025?lang=kor"
            
            # 2025??ì£¼ì°¨ë³?ê³µê³¼ ë§¤í•‘ (?¤ì œ êµíšŒ ?¬ë ¥ ê¸°ì?)
            week_mapping = self.get_week_mapping_2025()
            
            # ?´ë‹¹ ? ì§œ??ì£¼ì°¨ ì°¾ê¸°
            target_week = None
            for week_info in week_mapping:
                start_date = datetime.strptime(week_info['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(week_info['end_date'], '%Y-%m-%d')
                
                # ? ì§œë§?ë¹„êµ (?œê°„ ?œì™¸)
                target_date_only = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
                
                if start_date <= target_date_only <= end_date:
                    target_week = week_info
                    break
            
            if target_week:
                # ì§ì ‘ URL ?ì„± (???ˆì •??
                lesson_url = self.generate_direct_url(target_week)
                lesson_title = f"{target_week['week_range']}: {target_week['title_keywords']}"
                
                # ?´ë‹¹ ì£¼ì˜ ?ì„¸ ?´ìš© ê°€?¸ì˜¤ê¸?
                lesson_content = self.get_lesson_content(lesson_url)
                
                return {
                    "title": lesson_title,
                    "content": lesson_content,
                    "url": lesson_url,
                    "week_info": target_week
                }
            
            # ë§¤ì¹­?˜ì? ?Šì? ê²½ìš° ê¸°ë³¸ ?•ë³´ ë°˜í™˜
            return {
                "title": f"2025??{target_date.strftime('%m??%d??)} ì£¼ì°¨ ê³µê³¼",
                "content": "?´ë²ˆ ì£?ê³µê³¼??êµë¦¬?€ ?±ì•½??ê°€ë¥´ì¹¨??ê´€???´ìš©?…ë‹ˆ??",
                "url": url
            }
                
        except Exception as e:
            print(f"ê³µê³¼ ?•ë³´ ?¤í¬?˜í•‘ ì¤??¤ë¥˜: {e}")
            # ?¤ë¥˜ ??ê¸°ë³¸ ?•ë³´ ë°˜í™˜
            return {
                "title": f"2025??{target_date.strftime('%m??%d??)} ì£¼ì°¨ ê³µê³¼",
                "content": "?´ë²ˆ ì£?ê³µê³¼??êµë¦¬?€ ?±ì•½??ê°€ë¥´ì¹¨??ê´€???´ìš©?…ë‹ˆ??",
                "url": "https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025?lang=kor"
            }
    
    def get_available_weeks(self):
        """?¬ìš© ê°€?¥í•œ ì£¼ì°¨ ëª©ë¡??ë°˜í™˜?©ë‹ˆ??"""
        week_mapping = self.get_week_mapping_2025()
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
        """2025??ì£¼ì°¨ë³?ê³µê³¼ ë§¤í•‘ ?•ë³´"""
        return [
            # 12??
            {
                'start_date': '2025-12-29',
                'end_date': '2025-12-31',
                'week_range': '12??29??31??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 137-138??,
                'section': '12??
            },
            {
                'start_date': '2025-12-22',
                'end_date': '2025-12-28',
                'week_range': '12??22??28??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 135-136??,
                'section': '12??
            },
            {
                'start_date': '2025-12-15',
                'end_date': '2025-12-21',
                'week_range': '12??15??21??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 133-134??,
                'section': '12??
            },
            {
                'start_date': '2025-12-08',
                'end_date': '2025-12-14',
                'week_range': '12??8??14??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 131-132??,
                'section': '12??
            },
            {
                'start_date': '2025-12-01',
                'end_date': '2025-12-07',
                'week_range': '12??1??7??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 129-130??,
                'section': '12??
            },
            # 11??
            {
                'start_date': '2025-11-24',
                'end_date': '2025-11-30',
                'week_range': '11??24??30??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 127-128??,
                'section': '11??
            },
            {
                'start_date': '2025-11-17',
                'end_date': '2025-11-23',
                'week_range': '11??17??23??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 125-126??,
                'section': '11??
            },
            {
                'start_date': '2025-11-10',
                'end_date': '2025-11-16',
                'week_range': '11??10??16??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 123-124??,
                'section': '11??
            },
            {
                'start_date': '2025-11-03',
                'end_date': '2025-11-09',
                'week_range': '11??3??9??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 121-122??,
                'section': '11??
            },
            # 10??
            {
                'start_date': '2025-10-27',
                'end_date': '2025-11-02',
                'week_range': '10??27??11??2??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 119-120??,
                'section': '10??
            },
            {
                'start_date': '2025-10-20',
                'end_date': '2025-10-26',
                'week_range': '10??20??26??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 117-118??,
                'section': '10??
            },
            {
                'start_date': '2025-10-13',
                'end_date': '2025-10-19',
                'week_range': '10??13??19??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 115-116??,
                'section': '10??
            },
            {
                'start_date': '2025-10-06',
                'end_date': '2025-10-12',
                'week_range': '10??6??12??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 113-114??,
                'section': '10??
            },
            # 9??
            {
                'start_date': '2025-09-29',
                'end_date': '2025-10-05',
                'week_range': '9??29??10??5??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 111-112??,
                'section': '9??
            },
            {
                'start_date': '2025-09-22',
                'end_date': '2025-09-28',
                'week_range': '9??22??28??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 109-110??,
                'section': '9??
            },
            {
                'start_date': '2025-09-15',
                'end_date': '2025-09-21',
                'week_range': '9??15??21??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 107-108??,
                'section': '9??
            },
            {
                'start_date': '2025-09-08',
                'end_date': '2025-09-14',
                'week_range': '9??8??14??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 105-106??,
                'section': '9??
            },
            {
                'start_date': '2025-09-01',
                'end_date': '2025-09-07',
                'week_range': '9??1??7??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 103-104??,
                'section': '9??
            },
            # 8??
            {
                'start_date': '2025-08-25',
                'end_date': '2025-08-31',
                'week_range': '8??25??31??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 101-102??,
                'section': '8??
            },
            {
                'start_date': '2025-08-18',
                'end_date': '2025-08-24',
                'week_range': '8??18??24??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 99-100??,
                'section': '8??
            },
            {
                'start_date': '2025-08-11',
                'end_date': '2025-08-17',
                'week_range': '8??11??17??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 97-98??,
                'section': '8??
            },
            {
                'start_date': '2025-08-04',
                'end_date': '2025-08-10',
                'week_range': '8??4??10??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 95-96??,
                'section': '8??
            },
            # 7??
            {
                'start_date': '2025-07-28',
                'end_date': '2025-08-03',
                'week_range': '7??28??8??3??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 84-86??,
                'section': '7??
            },
            {
                'start_date': '2025-07-21',
                'end_date': '2025-07-27',
                'week_range': '7??21??27??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 81-83??,
                'section': '7??
            },
            {
                'start_date': '2025-07-14',
                'end_date': '2025-07-20',
                'week_range': '7??14??20??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 77-80??,
                'section': '7??
            },
            {
                'start_date': '2025-07-07',
                'end_date': '2025-07-13',
                'week_range': '7??7??13??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 76??,
                'section': '7??
            },
            {
                'start_date': '2025-06-30',
                'end_date': '2025-07-06',
                'week_range': '6??30??7??6??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 71-75??,
                'section': '7??
            },
            # 6??
            {
                'start_date': '2025-06-23',
                'end_date': '2025-06-29',
                'week_range': '6??23??29??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 67-70??,
                'section': '6??
            },
            {
                'start_date': '2025-06-16',
                'end_date': '2025-06-22',
                'week_range': '6??16??22??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 65-66??,
                'section': '6??
            },
            {
                'start_date': '2025-06-09',
                'end_date': '2025-06-15',
                'week_range': '6??9??15??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 63-64??,
                'section': '6??
            },
            {
                'start_date': '2025-06-02',
                'end_date': '2025-06-08',
                'week_range': '6??2??8??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 60-62??,
                'section': '6??
            },
            # 5??
            {
                'start_date': '2025-05-26',
                'end_date': '2025-06-01',
                'week_range': '5??26??6??1??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 58-59??,
                'section': '5??
            },
            {
                'start_date': '2025-05-19',
                'end_date': '2025-05-25',
                'week_range': '5??19??25??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 56-57??,
                'section': '5??
            },
            {
                'start_date': '2025-05-12',
                'end_date': '2025-05-18',
                'week_range': '5??12??18??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 54-55??,
                'section': '5??
            },
            {
                'start_date': '2025-05-05',
                'end_date': '2025-05-11',
                'week_range': '5??5??11??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 51-53??,
                'section': '5??
            },
            # 4??
            {
                'start_date': '2025-04-28',
                'end_date': '2025-05-04',
                'week_range': '4??28??5??4??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 49-50??,
                'section': '4??
            },
            {
                'start_date': '2025-04-21',
                'end_date': '2025-04-27',
                'week_range': '4??21??27??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 46-48??,
                'section': '4??
            },
            {
                'start_date': '2025-04-14',
                'end_date': '2025-04-20',
                'week_range': '4??14??20??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 43-45??,
                'section': '4??
            },
            {
                'start_date': '2025-04-07',
                'end_date': '2025-04-13',
                'week_range': '4??7??13??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 41-42??,
                'section': '4??
            },
            {
                'start_date': '2025-03-31',
                'end_date': '2025-04-06',
                'week_range': '3??31??4??6??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 38-40??,
                'section': '4??
            },
            # 3??
            {
                'start_date': '2025-03-24',
                'end_date': '2025-03-30',
                'week_range': '3??24??30??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 37??,
                'section': '3??
            },
            {
                'start_date': '2025-03-17',
                'end_date': '2025-03-23',
                'week_range': '3??17??23??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 35-36??,
                'section': '3??
            },
            {
                'start_date': '2025-03-10',
                'end_date': '2025-03-16',
                'week_range': '3??10??16??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 33-34??,
                'section': '3??
            },
            {
                'start_date': '2025-03-03',
                'end_date': '2025-03-09',
                'week_range': '3??3??9??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 30-32??,
                'section': '3??
            },
            # 2??
            {
                'start_date': '2025-02-24',
                'end_date': '2025-03-02',
                'week_range': '2??24??3??2??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 27-29??,
                'section': '2??
            },
            {
                'start_date': '2025-02-17',
                'end_date': '2025-02-23',
                'week_range': '2??17??23??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 25-26??,
                'section': '2??
            },
            {
                'start_date': '2025-02-10',
                'end_date': '2025-02-16',
                'week_range': '2??10??16??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 23-24??,
                'section': '2??
            },
            {
                'start_date': '2025-02-03',
                'end_date': '2025-02-09',
                'week_range': '2??3??9??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 20-22??,
                'section': '2??
            },
            # 1??
            {
                'start_date': '2025-01-27',
                'end_date': '2025-02-02',
                'week_range': '1??27??2??2??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 17-19??,
                'section': '1??
            },
            {
                'start_date': '2025-01-20',
                'end_date': '2025-01-26',
                'week_range': '1??20??26??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 14-16??,
                'section': '1??
            },
            {
                'start_date': '2025-01-13',
                'end_date': '2025-01-19',
                'week_range': '1??13??19??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 11-13??,
                'section': '1??
            },
            {
                'start_date': '2025-01-06',
                'end_date': '2025-01-12',
                'week_range': '1??6??12??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 8-10??,
                'section': '1??
            },
            {
                'start_date': '2025-01-01',
                'end_date': '2025-01-05',
                'week_range': '1??1??5??,
                'title_keywords': 'êµë¦¬?€ ?±ì•½ 1-7??,
                'section': '1??
            }
        ]

    def generate_direct_url(self, week_info):
        """ì£¼ì°¨ ?•ë³´ë¥?ë°”íƒ•?¼ë¡œ ì§ì ‘ URL ?ì„±"""
        # 2025??êµë¦¬?€ ?±ì•½ ê³µê³¼ URL ?¨í„´
        base_url = "https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-doctrine-and-covenants-2025"
        
        # ì£¼ì°¨ë³?URL ë§¤í•‘ (?¤ì œ êµíšŒ ?¹ì‚¬?´íŠ¸ êµ¬ì¡° ê¸°ë°˜)
        url_mapping = {
            # 12??
            '12??29??31??: '52-doctrine-and-covenants-137-138',
            '12??22??28??: '51-doctrine-and-covenants-135-136',
            '12??15??21??: '50-doctrine-and-covenants-133-134',
            '12??8??14??: '49-doctrine-and-covenants-131-132',
            '12??1??7??: '48-doctrine-and-covenants-129-130',
            # 11??
            '11??24??30??: '47-doctrine-and-covenants-127-128',
            '11??17??23??: '46-doctrine-and-covenants-125-126',
            '11??10??16??: '45-doctrine-and-covenants-123-124',
            '11??3??9??: '44-doctrine-and-covenants-121-122',
            # 10??
            '10??27??11??2??: '43-doctrine-and-covenants-119-120',
            '10??20??26??: '42-doctrine-and-covenants-117-118',
            '10??13??19??: '41-doctrine-and-covenants-115-116',
            '10??6??12??: '40-doctrine-and-covenants-113-114',
            # 9??
            '9??29??10??5??: '39-doctrine-and-covenants-111-112',
            '9??22??28??: '38-doctrine-and-covenants-109-110',
            '9??15??21??: '37-doctrine-and-covenants-107-108',
            '9??8??14??: '36-doctrine-and-covenants-105-106',
            '9??1??7??: '35-doctrine-and-covenants-103-104',
            # 8??
            '8??25??31??: '34-doctrine-and-covenants-101-102',
            '8??18??24??: '33-doctrine-and-covenants-99-100',
            '8??11??17??: '32-doctrine-and-covenants-97-98',
            '8??4??10??: '31-doctrine-and-covenants-95-96',
            # 7??
            '7??28??8??3??: '31-doctrine-and-covenants-84-86',
            '7??21??27??: '30-doctrine-and-covenants-81-83',
            '7??14??20??: '29-doctrine-and-covenants-77-80',
            '7??7??13??: '28-doctrine-and-covenants-76',
            '6??30??7??6??: '27-doctrine-and-covenants-71-75',
            # 6??
            '6??23??29??: '26-doctrine-and-covenants-67-70',
            '6??16??22??: '25-doctrine-and-covenants-65-66',
            '6??9??15??: '24-doctrine-and-covenants-63-64',
            '6??2??8??: '23-doctrine-and-covenants-60-62',
            # 5??
            '5??26??6??1??: '22-doctrine-and-covenants-58-59',
            '5??19??25??: '21-doctrine-and-covenants-56-57',
            '5??12??18??: '20-doctrine-and-covenants-54-55',
            '5??5??11??: '19-doctrine-and-covenants-51-53',
            # 4??
            '4??28??5??4??: '18-doctrine-and-covenants-49-50',
            '4??21??27??: '17-doctrine-and-covenants-46-48',
            '4??14??20??: '16-doctrine-and-covenants-43-45',
            '4??7??13??: '15-doctrine-and-covenants-41-42',
            '3??31??4??6??: '14-doctrine-and-covenants-38-40',
            # 3??
            '3??24??30??: '13-doctrine-and-covenants-37',
            '3??17??23??: '12-doctrine-and-covenants-35-36',
            '3??10??16??: '11-doctrine-and-covenants-33-34',
            '3??3??9??: '10-doctrine-and-covenants-30-32',
            # 2??
            '2??24??3??2??: '09-doctrine-and-covenants-27-29',
            '2??17??23??: '08-doctrine-and-covenants-25-26',
            '2??10??16??: '07-doctrine-and-covenants-23-24',
            '2??3??9??: '06-doctrine-and-covenants-20-22',
            # 1??
            '1??27??2??2??: '05-doctrine-and-covenants-17-19',
            '1??20??26??: '04-doctrine-and-covenants-14-16',
            '1??13??19??: '03-doctrine-and-covenants-11-13',
            '1??6??12??: '02-doctrine-and-covenants-8-10',
            '1??1??5??: '01-doctrine-and-covenants-1-7'
        }
        
        week_range = week_info['week_range']
        if week_range in url_mapping:
            return f"{base_url}/{url_mapping[week_range]}?lang=kor"
        else:
            # ë§¤í•‘?˜ì? ?Šì? ê²½ìš° ê¸°ë³¸ URL ë°˜í™˜
            return f"{base_url}?lang=kor"

    def get_lesson_content(self, lesson_url):
        """?¹ì • ì£¼ì˜ ?ì„¸ ?´ìš©??ê°€?¸ì˜µ?ˆë‹¤."""
        try:
            response = self.session.get(lesson_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ì£¼ìš” ?´ìš© ì¶”ì¶œ
            content_sections = []
            
            # ?œëª© ì°¾ê¸° (h1 ?œê·¸)
            title = soup.find('h1')
            if title:
                content_sections.append(f"?œëª©: {title.get_text(strip=True)}")
            
            # ë¶€?œëª© ì°¾ê¸° (h2 ?œê·¸)
            subtitle = soup.find('h2')
            if subtitle:
                content_sections.append(f"ë¶€?œëª©: {subtitle.get_text(strip=True)}")
            
            # ì£¼ìš” ?´ìš© ì°¾ê¸° (p ?œê·¸??
            paragraphs = soup.find_all('p')
            for p in paragraphs[:15]:  # ì²˜ìŒ 15ê°??¨ë½ë§?
                text = p.get_text(strip=True)
                if text and len(text) > 20:  # ?˜ë??ˆëŠ” ?ìŠ¤?¸ë§Œ
                    content_sections.append(text)
            
            # ?Œì œëª©ë“¤ ì°¾ê¸° (h3 ?œê·¸??
            subheadings = soup.find_all('h3')
            for h3 in subheadings[:10]:  # ì²˜ìŒ 10ê°??Œì œëª©ë§Œ
                text = h3.get_text(strip=True)
                if text and len(text) > 5:
                    content_sections.append(f"\n## {text}")
            
            # ?´ìš©???†ìœ¼ë©?ê¸°ë³¸ ë©”ì‹œì§€
            if not content_sections:
                content_sections.append("?´ë²ˆ ì£?ê³µê³¼???ì„¸ ?´ìš©??ê°€?¸ì˜¬ ???†ìŠµ?ˆë‹¤.")
            
            return "\n\n".join(content_sections)
            
        except Exception as e:
            print(f"?ì„¸ ?´ìš© ê°€?¸ì˜¤ê¸?ì¤??¤ë¥˜: {e}")
            return "?´ë²ˆ ì£?ê³µê³¼???ì„¸ ?´ìš©??ê°€?¸ì˜¬ ???†ìŠµ?ˆë‹¤."

    def get_weekly_curriculum_list(self):
        """?„ì²´ ì£¼ì°¨ë³?ê³µê³¼ ëª©ë¡??ê°€?¸ì˜µ?ˆë‹¤."""
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
            print(f"ê³µê³¼ ëª©ë¡ ê°€?¸ì˜¤ê¸?ì¤??¤ë¥˜: {e}")
            return []

# ?¬ìš© ?ˆì‹œ
if __name__ == "__main__":
    scraper = CurriculumScraper()
    current_curriculum = scraper.get_current_week_curriculum()
    print("?„ì¬ ì£?ê³µê³¼:", json.dumps(current_curriculum, ensure_ascii=False, indent=2)) 
