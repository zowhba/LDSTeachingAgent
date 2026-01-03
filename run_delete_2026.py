import sqlite3

# 2026년도 데이터 삭제
conn = sqlite3.connect('curriculum_data.db')
cursor = conn.cursor()

try:
    # 1. curriculum_materials 삭제 (구약전서 관련)
    cursor.execute("""
        DELETE FROM curriculum_materials 
        WHERE (week_range LIKE '12월%' OR week_range LIKE '1월%')
           AND (lesson_title LIKE '%구약전서%' OR lesson_title LIKE '%모세서%' 
                OR lesson_title LIKE '%창세기%' OR lesson_title LIKE '%아브라함서%'
                OR lesson_title LIKE '%출애굽기%' OR lesson_title LIKE '%레위기%'
                OR lesson_title LIKE '%민수기%' OR lesson_title LIKE '%신명기%')
    """)
    deleted_materials = cursor.rowcount
    print(f"✅ curriculum_materials: {deleted_materials}개 삭제")
    
    # 2. curriculum_qa 삭제
    cursor.execute("""
        DELETE FROM curriculum_qa 
        WHERE (week_range LIKE '12월%' OR week_range LIKE '1월%')
    """)
    deleted_qa = cursor.rowcount
    print(f"✅ curriculum_qa: {deleted_qa}개 삭제")
    
    # 3. weekly_curriculum 삭제
    cursor.execute("DELETE FROM weekly_curriculum WHERE year = 2026")
    deleted_weekly = cursor.rowcount
    print(f"✅ weekly_curriculum: {deleted_weekly}개 삭제")
    
    # 4. curriculum_status 삭제
    cursor.execute("DELETE FROM curriculum_status WHERE year = 2026")
    deleted_status = cursor.rowcount
    print(f"✅ curriculum_status: {deleted_status}개 삭제")
    
    conn.commit()
    print(f"\n🎉 2026년도 데이터 삭제 완료!")
    
except Exception as e:
    print(f"❌ 오류: {e}")
    conn.rollback()
finally:
    conn.close()

