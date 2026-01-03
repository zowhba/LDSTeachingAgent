#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026년도 공과 자료 생성 기록 삭제 스크립트
"""

import sqlite3
import re

def delete_2026_curriculum_data():
    """2026년도 공과 자료 생성 기록 삭제"""
    conn = sqlite3.connect('curriculum_data.db')
    cursor = conn.cursor()
    
    try:
        # 먼저 2026년도 주차 목록 가져오기
        cursor.execute("""
            SELECT week_range FROM weekly_curriculum WHERE year = 2026
        """)
        week_ranges_2026 = [row[0] for row in cursor.fetchall()]
        print(f"📋 2026년도 주차 목록: {len(week_ranges_2026)}개")
        if week_ranges_2026:
            print("   예시:", week_ranges_2026[:5])
        
        # 1. curriculum_materials 테이블에서 2026년도 데이터 삭제
        deleted_materials = 0
        if week_ranges_2026:
            # 2026년도 주차 week_range와 일치하는 데이터 삭제
            placeholders = ','.join(['?' for _ in week_ranges_2026])
            cursor.execute(f"""
                SELECT id, lesson_title, week_range 
                FROM curriculum_materials 
                WHERE week_range IN ({placeholders})
            """, week_ranges_2026)
            materials = cursor.fetchall()
            print(f"\n📋 curriculum_materials에서 {len(materials)}개 레코드 발견")
            for material in materials:
                print(f"  - {material[1]} ({material[2]})")
            
            cursor.execute(f"""
                DELETE FROM curriculum_materials 
                WHERE week_range IN ({placeholders})
            """, week_ranges_2026)
            deleted_materials = cursor.rowcount
        else:
            # weekly_curriculum에 2026년도 데이터가 없으면 구약전서 관련 키워드로 삭제
            cursor.execute("""
                SELECT id, lesson_title, week_range 
                FROM curriculum_materials 
                WHERE (week_range LIKE '12월%' OR week_range LIKE '1월%')
                   AND (lesson_title LIKE '%구약전서%' OR lesson_title LIKE '%모세서%' 
                        OR lesson_title LIKE '%창세기%' OR lesson_title LIKE '%아브라함서%'
                        OR lesson_title LIKE '%출애굽기%' OR lesson_title LIKE '%레위기%'
                        OR lesson_title LIKE '%민수기%' OR lesson_title LIKE '%신명기%')
            """)
            materials = cursor.fetchall()
            print(f"\n📋 curriculum_materials에서 {len(materials)}개 레코드 발견")
            for material in materials:
                print(f"  - {material[1]} ({material[2]})")
            
            cursor.execute("""
                DELETE FROM curriculum_materials 
                WHERE (week_range LIKE '12월%' OR week_range LIKE '1월%')
                   AND (lesson_title LIKE '%구약전서%' OR lesson_title LIKE '%모세서%' 
                        OR lesson_title LIKE '%창세기%' OR lesson_title LIKE '%아브라함서%'
                        OR lesson_title LIKE '%출애굽기%' OR lesson_title LIKE '%레위기%'
                        OR lesson_title LIKE '%민수기%' OR lesson_title LIKE '%신명기%')
            """)
            deleted_materials = cursor.rowcount
        print(f"✅ curriculum_materials에서 {deleted_materials}개 레코드 삭제 완료")
        
        # 2. curriculum_qa 테이블에서 2026년도 데이터 삭제
        deleted_qa = 0
        if week_ranges_2026:
            placeholders = ','.join(['?' for _ in week_ranges_2026])
            cursor.execute(f"""
                SELECT id, week_range, target_audience 
                FROM curriculum_qa 
                WHERE week_range IN ({placeholders})
            """, week_ranges_2026)
            qas = cursor.fetchall()
            print(f"\n📋 curriculum_qa에서 {len(qas)}개 레코드 발견")
            for qa in qas:
                print(f"  - {qa[1]} ({qa[2]})")
            
            cursor.execute(f"""
                DELETE FROM curriculum_qa 
                WHERE week_range IN ({placeholders})
            """, week_ranges_2026)
            deleted_qa = cursor.rowcount
        else:
            # weekly_curriculum에 2026년도 데이터가 없으면 12월/1월 주차 삭제
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
        print(f"✅ curriculum_qa에서 {deleted_qa}개 레코드 삭제 완료")
        
        # 3. weekly_curriculum 테이블에서 2026년도 데이터 삭제
        cursor.execute("""
            SELECT COUNT(*) FROM weekly_curriculum WHERE year = 2026
        """)
        weekly_count = cursor.fetchone()[0]
        print(f"\n📋 weekly_curriculum에서 {weekly_count}개 레코드 발견")
        
        cursor.execute("DELETE FROM weekly_curriculum WHERE year = 2026")
        deleted_weekly = cursor.rowcount
        print(f"✅ weekly_curriculum에서 {deleted_weekly}개 레코드 삭제 완료")
        
        # 4. curriculum_status 테이블에서 2026년도 상태 삭제
        cursor.execute("""
            SELECT year, status, total_weeks 
            FROM curriculum_status 
            WHERE year = 2026
        """)
        status = cursor.fetchone()
        if status:
            print(f"\n📋 curriculum_status에서 2026년도 상태 발견: {status}")
        
        cursor.execute("DELETE FROM curriculum_status WHERE year = 2026")
        deleted_status = cursor.rowcount
        print(f"✅ curriculum_status에서 {deleted_status}개 레코드 삭제 완료")
        
        conn.commit()
        print(f"\n🎉 2026년도 데이터 삭제 완료!")
        print(f"   - 공과 자료: {deleted_materials}개")
        print(f"   - Q&A: {deleted_qa}개")
        print(f"   - 주차별 커리큘럼: {deleted_weekly}개")
        print(f"   - 상태 정보: {deleted_status}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🗑️  2026년도 공과 자료 생성 기록 삭제 시작...\n")
    delete_2026_curriculum_data()
