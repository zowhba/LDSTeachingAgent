#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026년도 데이터 삭제 실행"""
import sqlite3
import sys
import os

# 작업 디렉토리 확인
print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"DB 파일 존재 여부: {os.path.exists('curriculum_data.db')}")

print("\n🗑️  2026년도 공과 자료 생성 기록 삭제 시작...\n")

# 2026년도 데이터 삭제
conn = sqlite3.connect('curriculum_data.db')
cursor = conn.cursor()

try:
    # 먼저 삭제할 데이터 확인
    cursor.execute("""
        SELECT id, lesson_title, week_range 
        FROM curriculum_materials 
        WHERE (week_range LIKE '12월%' OR week_range LIKE '1월%')
           OR (lesson_title LIKE '%구약전서%' OR lesson_title LIKE '%모세서%' 
               OR lesson_title LIKE '%창세기%' OR lesson_title LIKE '%아브라함서%'
               OR lesson_title LIKE '%출애굽기%' OR lesson_title LIKE '%레위기%'
               OR lesson_title LIKE '%민수기%' OR lesson_title LIKE '%신명기%'
               OR lesson_title LIKE '%2026%'
               OR lesson_title LIKE '%12월29일%' OR lesson_title LIKE '%12월 29일%')
    """)
    materials = cursor.fetchall()
    print(f"📋 curriculum_materials에서 {len(materials)}개 레코드 발견")
    for material in materials:
        print(f"  - {material[1]} ({material[2]})")
    
    # 1. curriculum_materials 삭제
    cursor.execute("""
        DELETE FROM curriculum_materials 
        WHERE (week_range LIKE '12월%' OR week_range LIKE '1월%')
           OR (lesson_title LIKE '%구약전서%' OR lesson_title LIKE '%모세서%' 
               OR lesson_title LIKE '%창세기%' OR lesson_title LIKE '%아브라함서%'
               OR lesson_title LIKE '%출애굽기%' OR lesson_title LIKE '%레위기%'
               OR lesson_title LIKE '%민수기%' OR lesson_title LIKE '%신명기%'
               OR lesson_title LIKE '%2026%'
               OR lesson_title LIKE '%12월29일%' OR lesson_title LIKE '%12월 29일%')
    """)
    deleted_materials = cursor.rowcount
    print(f"✅ curriculum_materials: {deleted_materials}개 삭제")
    
    # 2. curriculum_qa 삭제
    cursor.execute("""
        SELECT id, week_range, target_audience 
        FROM curriculum_qa 
        WHERE (week_range LIKE '12월%' OR week_range LIKE '1월%')
    """)
    qas = cursor.fetchall()
    print(f"\n📋 curriculum_qa에서 {len(qas)}개 레코드 발견")
    for qa in qas:
        print(f"  - {qa[1]} ({qa[2]})")
    
    cursor.execute("""
        DELETE FROM curriculum_qa 
        WHERE (week_range LIKE '12월%' OR week_range LIKE '1월%')
    """)
    deleted_qa = cursor.rowcount
    print(f"✅ curriculum_qa: {deleted_qa}개 삭제")
    
    # 3. weekly_curriculum 삭제
    cursor.execute("SELECT COUNT(*) FROM weekly_curriculum WHERE year = 2026")
    weekly_count = cursor.fetchone()[0]
    print(f"\n📋 weekly_curriculum에서 {weekly_count}개 레코드 발견")
    
    cursor.execute("DELETE FROM weekly_curriculum WHERE year = 2026")
    deleted_weekly = cursor.rowcount
    print(f"✅ weekly_curriculum: {deleted_weekly}개 삭제")
    
    # 4. curriculum_status 삭제
    cursor.execute("SELECT year, status, total_weeks FROM curriculum_status WHERE year = 2026")
    status = cursor.fetchone()
    if status:
        print(f"\n📋 curriculum_status에서 2026년도 상태 발견: {status}")
    
    cursor.execute("DELETE FROM curriculum_status WHERE year = 2026")
    deleted_status = cursor.rowcount
    print(f"✅ curriculum_status: {deleted_status}개 삭제")
    
    conn.commit()
    print(f"\n🎉 2026년도 데이터 삭제 완료!")
    print(f"   - 공과 자료: {deleted_materials}개")
    print(f"   - Q&A: {deleted_qa}개")
    print(f"   - 주차별 커리큘럼: {deleted_weekly}개")
    print(f"   - 상태 정보: {deleted_status}개")
    
except Exception as e:
    print(f"❌ 오류: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()

print("\n✅ 삭제 작업 완료!")

