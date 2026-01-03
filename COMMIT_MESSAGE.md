# 커밋 메시지

## 주요 변경사항

### 1. 2026년도 커리큘럼 지원
- `weekly_curriculum_manager.py`: 2026년도 구약전서 커리큘럼 동적 URL 패턴 감지 추가
- `curriculum_scraper.py`: 2026년도 URL 생성 로직 개선 (주차 번호 기반 /01, /02 형식)

### 2. URL 생성 개선
- `curriculum_scraper.py`: `generate_direct_url` 함수 개선
  - 연도별 경전 종류 자동 감지 (old-testament, doctrine-and-covenants 등)
  - 주차 번호 동적 계산 (01-52)
  - 원본 링크와 동일한 URL 사용 보장

### 3. 원문 내용 추출 개선
- `curriculum_scraper.py`: `get_lesson_content` 함수 개선
  - 더 많은 단락 추출 (20개 → 50개)
  - 리스트 항목(li 태그) 추출 추가
  - div.content, article, main 태그에서 더 많은 내용 추출 (2000자 → 5000자)
  - h3 태그 마크다운 제목 형식 제거

### 4. 프롬프트 템플릿 개선
- `prompts/curriculum_template.txt`: 원문 참조 강조
  - 원문의 핵심 교리와 경전 구절을 정확히 반영하도록 지시 추가
  - "공과 원문 내용"으로 명확히 표시

### 5. 공과 자료 생성 개선
- `app.py`: 원본 링크 URL을 직접 사용하여 내용 재가져오기
  - 자료 생성 시 원본 링크와 동일한 URL 사용 보장
  - 원문 내용이 제대로 전달되도록 개선

### 6. 데이터 삭제 스크립트
- `delete_2026_data.py`: 2026년도 공과 자료 생성 기록 삭제 스크립트
- `run_delete_2026.py`: 간소화된 삭제 스크립트
- `execute_delete.py`: 디버깅 정보 포함 삭제 스크립트

### 7. UI 개선
- `app.py`: 주차 선택 콤보박스 정렬 (end_date 기준 오름차순)
- `curriculum_scraper.py`: display_text에서 중복 날짜 패턴 제거

## 커밋 명령어

```bash
git add .
git commit -m "feat: 2026년도 구약전서 커리큘럼 지원 및 원문 추출 개선

- 2026년도 구약전서 커리큘럼 동적 URL 패턴 감지 추가
- 주차 번호 기반 URL 생성 로직 개선 (/01, /02 형식)
- 원문 내용 추출 개선 (더 많은 단락, 리스트 항목 추출)
- 프롬프트 템플릿에서 원문 참조 강조
- 원본 링크 URL 직접 사용하여 내용 재가져오기
- 2026년도 데이터 삭제 스크립트 추가
- UI 개선 (주차 정렬, 중복 날짜 패턴 제거)"
git push
```

