import os
import re

print("🛠️ app_azure.py 재생성 시작...")

with open("backend/main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. 경로 수정 (main.py는 backend/ 에 있지만, app_azure.py는 root에 있음)
content = content.replace("os.path.dirname(os.path.dirname(os.path.abspath(__file__)))", "os.path.dirname(os.path.abspath(__file__))")
content = content.replace("os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')", "os.path.join(os.path.dirname(__file__), '.env')")
content = content.replace("os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts')", "os.path.join(os.path.dirname(__file__), 'prompts')")

# 2. 정적 파일 서빙 코드 추가
static_serving_code = """
# Vue.js 정적 파일 서빙 (프로덕션)
static_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')
if os.path.exists(static_dir):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    from fastapi import Request
    
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        \"\"\"SPA 라우팅을 위한 catch-all\"\"\"
        if full_path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        return FileResponse(os.path.join(static_dir, "index.html"))

# 앱 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

# 마지막 `if __name__ == "__main__":` 부분을 교체
content = re.sub(r'# 앱 실행\nif __name__ == "__main__":\n.*', static_serving_code, content, flags=re.DOTALL)

with open("app_azure.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ app_azure.py 생성 완료!")
