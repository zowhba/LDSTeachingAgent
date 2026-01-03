#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_tilde_in_file():
    """curriculum_scraper.py 파일에서 ~ 기호를 -로 변경"""
    
    # 파일 읽기
    with open('curriculum_scraper.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # ~를 -로 변경
    fixed_content = content.replace('~', '-')
    
    # 파일에 다시 쓰기
    with open('curriculum_scraper.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("~ 기호를 -로 변경 완료!")

if __name__ == "__main__":
    fix_tilde_in_file() 