import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta
import json
import sqlite3
from openai import AzureOpenAI
from dotenv import load_dotenv
import re

# 환경변수 로드
load_dotenv()

# Azure OpenAI 설정
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview"
)

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('curriculum_data.db')
    cursor = conn.cursor()
    
    # 기존 테이블이 있는지 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='curriculum_materials'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        # 기존 테이블에 week_range 컬럼이 있는지 확인
        cursor.execute("PRAGMA table_info(curriculum_materials)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'week_range' not in columns:
            # week_range 컬럼 추가
            cursor.execute('ALTER TABLE curriculum_materials ADD COLUMN week_range TEXT')
    else:
        # 새 테이블 생성
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
    
    conn.commit()
    conn.close()

# 프롬프트 템플릿 로드
def load_prompt_template(filename):
    with open(f'prompts/{filename}', 'r', encoding='utf-8') as f:
        return f.read()

# 현재 주의 공과 정보 가져오기
def get_current_week_curriculum():
    try:
        from curriculum_scraper import CurriculumScraper
        scraper = CurriculumScraper()
        return scraper.get_current_week_curriculum()
    except Exception as e:
        st.error(f"공과 정보를 가져오는 중 오류가 발생했습니다: {e}")
        return None

# 특정 주차의 공과 정보 가져오기
def get_curriculum_by_week(selected_week):
    try:
        from curriculum_scraper import CurriculumScraper
        scraper = CurriculumScraper()
        
        # 선택된 주차의 시작 날짜로 공과 정보 가져오기
        start_date = datetime.strptime(selected_week['start_date'], '%Y-%m-%d')
        return scraper.get_curriculum_by_date(start_date)
    except Exception as e:
        st.error(f"공과 정보를 가져오는 중 오류가 발생했습니다: {e}")
        return None

# 사용 가능한 주차 목록 가져오기
def get_available_weeks():
    try:
        from curriculum_scraper import CurriculumScraper
        scraper = CurriculumScraper()
        return scraper.get_available_weeks()
    except Exception as e:
        st.error(f"주차 목록을 가져오는 중 오류가 발생했습니다: {e}")
        return []

# Azure OpenAI를 사용한 공과 자료 생성
def generate_curriculum_material(lesson_title, lesson_content, target_audience):
    try:
        template = load_prompt_template('curriculum_template.txt')
        prompt = template.format(
            target_audience=target_audience,
            lesson_title=lesson_title,
            lesson_content=lesson_content
        )
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOY_CURRICULUM"),
            messages=[
                {"role": "system", "content": "당신은 후기성도 예수그리스도 교회의 공과 준비 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"공과 자료 생성 중 오류가 발생했습니다: {e}")
        return None

# 채팅 응답 생성
def generate_chat_response(lesson_title, lesson_content, reference_material, user_question):
    try:
        template = load_prompt_template('chat_template.txt')
        prompt = template.format(
            lesson_title=lesson_title,
            lesson_content=lesson_content,
            reference_material=reference_material,
            user_question=user_question
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
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"채팅 응답 생성 중 오류가 발생했습니다: {e}")
        return None

# 데이터베이스에서 저장된 자료 가져오기
def get_saved_material(lesson_title, target_audience, week_range):
    conn = sqlite3.connect('curriculum_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT content FROM curriculum_materials 
        WHERE lesson_title = ? AND target_audience = ? AND week_range = ?
        ORDER BY created_at DESC LIMIT 1
    ''', (lesson_title, target_audience, week_range))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# 자료를 데이터베이스에 저장
def save_material(lesson_title, target_audience, content, week_range):
    conn = sqlite3.connect('curriculum_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO curriculum_materials (lesson_title, target_audience, content, week_range)
        VALUES (?, ?, ?, ?)
    ''', (lesson_title, target_audience, content, week_range))
    conn.commit()
    conn.close()

# 메인 애플리케이션
def main():
    st.set_page_config(
        page_title="공과 준비 도우미",
        page_icon="📖",
        layout="wide"
    )
    
    # 데이터베이스 초기화
    init_db()
    
    st.title("📖 후기성도 예수그리스도 교회 신갈와드 공과 준비 도우미 v1.0")
    st.markdown("---")
    
    # 사용 가능한 주차 목록 가져오기
    available_weeks = get_available_weeks()
    
    if available_weeks:
        # 메인 컨테이너
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("🎯 설정")
            
            # 주차 선택
            st.markdown("**📅 공과 주차 선택**")
            
            # 현재 주차 찾기
            current_date = datetime.now()
            current_week_index = 0
            
            for i, week in enumerate(available_weeks):
                start_date = datetime.strptime(week['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(week['end_date'], '%Y-%m-%d')
                current_date_only = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
                
                if start_date <= current_date_only <= end_date:
                    current_week_index = i
                    break
            
            # 현재 선택된 주차 이후의 주차들만 필터링
            current_date = datetime.now()
            filtered_weeks = []
            filtered_indices = []
            
            for i, week in enumerate(available_weeks):
                start_date = datetime.strptime(week['start_date'], '%Y-%m-%d')
                # 현재 선택된 주차의 시작일 이후의 주차들만 포함
                if start_date >= datetime.strptime(available_weeks[current_week_index]['start_date'], '%Y-%m-%d'):
                    filtered_weeks.append(week)
                    filtered_indices.append(i)
            
            # 필터링된 주차들 중에서 현재 주차의 인덱스 찾기
            current_filtered_index = 0
            for i, original_index in enumerate(filtered_indices):
                if original_index == current_week_index:
                    current_filtered_index = i
                    break
            
            # 주차 선택 드롭다운 (필터링된 목록 사용)
            selected_filtered_index = st.selectbox(
                "주차 선택",
                range(len(filtered_weeks)),
                index=current_filtered_index,
                format_func=lambda x: filtered_weeks[x]['display_text'],
                help="공과 준비 자료를 생성할 주차를 선택하세요.",
                key="week_selector"
            )
            
            # 필터링된 인덱스를 원래 인덱스로 변환
            selected_week_index = filtered_indices[selected_filtered_index]
            selected_week = available_weeks[selected_week_index]
            
            # 선택된 주차의 공과 정보 가져오기
            lesson_data = get_curriculum_by_week(selected_week)
            
            # 주차가 변경되면 기존 생성된 자료 초기화
            if 'current_week' not in st.session_state:
                st.session_state.current_week = selected_week['week_range']
            elif st.session_state.current_week != selected_week['week_range']:
                # 주차가 변경되었으므로 기존 자료 초기화
                if 'generated_material' in st.session_state:
                    del st.session_state.generated_material
                if 'chat_history' in st.session_state:
                    del st.session_state.chat_history
                st.session_state.current_week = selected_week['week_range']
            
            # 대상 선택
            target_audience = st.selectbox(
                "대상 선택",
                ["성인", "신회원", "청소년", "초등회"],
                help="공과 준비 자료를 생성할 대상 그룹을 선택하세요."
            )
            
            # 생성 버튼
            if st.button("📝 공과 자료 생성", type="primary"):
                if lesson_data:
                    with st.spinner("공과 자료를 생성하고 있습니다..."):
                        # 먼저 저장된 자료가 있는지 확인
                        saved_material = get_saved_material(lesson_data["title"], target_audience, selected_week['week_range'])
                        
                        if saved_material:
                            st.session_state.generated_material = saved_material
                            st.success("저장된 자료를 불러왔습니다!")
                        else:
                            # 새로운 자료 생성
                            generated_material = generate_curriculum_material(
                                lesson_data["title"],
                                lesson_data["content"],
                                target_audience
                            )
                            
                            if generated_material:
                                # 데이터베이스에 저장
                                save_material(lesson_data["title"], target_audience, generated_material, selected_week['week_range'])
                                st.session_state.generated_material = generated_material
                                st.success("새로운 공과 자료가 생성되었습니다!")
                            else:
                                st.error("공과 자료 생성에 실패했습니다.")
                else:
                    st.error("공과 정보를 가져올 수 없습니다.")
        
        with col2:
            st.subheader("📚 선택된 주차 공과")
            
            if lesson_data:
                # 주차 정보 표시
                if 'week_info' in lesson_data:
                    week_info = lesson_data['week_info']
                    st.markdown(f"**📅 주차:** {week_info['week_range']}")
                    st.markdown(f"**📖 교재:** {week_info['title_keywords']}")
                
                st.markdown(f"**제목:** {lesson_data['title']}")
                
                # 내용이 길면 접기/펼치기 기능 추가
                if len(lesson_data['content']) > 500:
                    with st.expander("📄 공과 내용 보기", expanded=False):
                        st.markdown(lesson_data['content'])
                else:
                    st.markdown(f"**내용:** {lesson_data['content']}")
                
                st.markdown(f"**🔗 원본 링크:** [교회 웹사이트]({lesson_data['url']})")
                
                # 생성된 자료 표시 (현재 선택된 주차의 자료만)
                if ('generated_material' in st.session_state and 
                    'current_week' in st.session_state and 
                    st.session_state.current_week == selected_week['week_range']):
                    
                    st.markdown("---")
                    st.subheader(f"📋 {target_audience}을 위한 공과 준비 자료")
                    st.markdown(st.session_state.generated_material)
                    
                    # 채팅 섹션
                    st.markdown("---")
                    st.subheader("💬 공과 자료에 대한 질문")
                    
                    # 채팅 히스토리 초기화
                    if 'chat_history' not in st.session_state:
                        st.session_state.chat_history = []
                    
                    # 채팅 히스토리 표시
                    for message in st.session_state.chat_history:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                    
                    # 사용자 입력
                    if prompt := st.chat_input("공과 자료에 대해 궁금한 점을 물어보세요..."):
                        # 사용자 메시지 추가
                        st.session_state.chat_history.append({"role": "user", "content": prompt})
                        
                        with st.chat_message("user"):
                            st.markdown(prompt)
                        
                        # AI 응답 생성
                        with st.chat_message("assistant"):
                            with st.spinner("답변을 생성하고 있습니다..."):
                                response = generate_chat_response(
                                    lesson_data["title"],
                                    lesson_data["content"],
                                    st.session_state.generated_material,
                                    prompt
                                )
                                
                                if response:
                                    st.markdown(response)
                                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                                else:
                                    st.error("답변 생성에 실패했습니다.")
                else:
                    # 생성된 자료가 없거나 다른 주차의 자료인 경우 안내 메시지
                    st.markdown("---")
                    st.info("📝 위의 '공과 자료 생성' 버튼을 클릭하여 이 주차의 공과 준비 자료를 생성하세요.")
            else:
                st.warning("공과 정보를 불러오는 중입니다...")
    else:
        st.error("주차 목록을 가져올 수 없습니다. 나중에 다시 시도해주세요.")

if __name__ == "__main__":
    main() 