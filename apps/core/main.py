"""
CueNote Core - Entry Point
PyInstaller 빌드 및 직접 실행 지원
"""
import os
import sys

# PyInstaller 환경에서 경로 설정
if getattr(sys, 'frozen', False):
    # PyInstaller로 패키징된 경우
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    os.chdir(os.path.dirname(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from app.main import app

__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    
    # 개발 모드 감지
    is_dev = not getattr(sys, 'frozen', False)
    
    uvicorn.run(
        "app.main:app" if is_dev else app,
        host="127.0.0.1",
        port=8787,
        reload=is_dev,  # 개발 모드에서만 reload 활성화
        reload_dirs=["app"] if is_dev else None,  # app 폴더만 감시 (node_modules 등 제외)
        log_level="info"
    )
