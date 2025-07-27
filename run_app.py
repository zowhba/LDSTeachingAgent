#!/usr/bin/env python3
"""
후기성도 예수그리스도 교회 공과 준비 도우미 AI Agent 실행 스크립트
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Python 버전 확인"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        print(f"현재 버전: {sys.version}")
        return False
    print(f"✅ Python 버전 확인 완료: {sys.version}")
    return True

def check_dependencies():
    """필요한 패키지 설치 확인 및 설치"""
    required_packages = [
        'streamlit',
        'openai',
        'python-dotenv',
        'requests',
        'beautifulsoup4',
        'lxml'
    ]
    
    print("📦 필요한 패키지 확인 중...")
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} 설치됨")
        except ImportError:
            print(f"❌ {package} 설치 필요")
            return False
    
    return True

def install_dependencies():
    """필요한 패키지 설치"""
    print("📦 필요한 패키지를 설치합니다...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 패키지 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 설치 실패: {e}")
        return False

def check_env_file():
    """환경변수 파일 확인"""
    if not os.path.exists('.env'):
        if os.path.exists('env_example.txt'):
            print("⚠️  .env 파일이 없습니다. env_example.txt를 복사하여 .env 파일을 생성하세요.")
            print("   그 후 Azure OpenAI 설정을 입력하세요.")
            return False
        else:
            print("❌ .env 파일과 env_example.txt 파일이 모두 없습니다.")
            return False
    
    print("✅ .env 파일 확인됨")
    return True

def run_streamlit():
    """Streamlit 애플리케이션 실행"""
    print("🚀 공과 준비 도우미를 시작합니다...")
    print("📖 브라우저에서 http://localhost:8501 로 접속하세요.")
    print("🛑 종료하려면 Ctrl+C를 누르세요.")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 애플리케이션이 종료되었습니다.")
    except Exception as e:
        print(f"❌ 애플리케이션 실행 중 오류 발생: {e}")

def main():
    """메인 함수"""
    print("=" * 60)
    print("📖 후기성도 예수그리스도 교회 공과 준비 도우미 AI Agent")
    print("=" * 60)
    
    # Python 버전 확인
    if not check_python_version():
        return
    
    # 환경변수 파일 확인
    if not check_env_file():
        return
    
    # 의존성 확인 및 설치
    if not check_dependencies():
        print("📦 필요한 패키지를 설치합니다...")
        if not install_dependencies():
            print("❌ 패키지 설치에 실패했습니다.")
            return
    
    # Streamlit 실행
    run_streamlit()

if __name__ == "__main__":
    main() 