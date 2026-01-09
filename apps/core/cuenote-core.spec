# -*- mode: python ; coding: utf-8 -*-
"""
CueNote Core - PyInstaller Spec File
FastAPI 백엔드를 Windows exe로 패키징
"""

import sys
from pathlib import Path

block_cipher = None

# 현재 디렉토리
CORE_DIR = Path(SPECPATH)

# 데이터 파일 (DB, 설정 등)
datas = [
    # data 폴더 포함
    (str(CORE_DIR / 'data'), 'data'),
]

# 숨겨진 imports (동적으로 임포트되는 모듈들)
hiddenimports = [
    # FastAPI & Uvicorn
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'starlette',
    'pydantic',
    
    # SSE
    'sse_starlette',
    
    # HTTP
    'httpx',
    'httpcore',
    
    # LangChain
    'langchain',
    'langchain_ollama',
    'langchain_core',
    
    # PDF
    'fitz',
    'pymupdf',
    
    # OCR (선택사항 - 용량이 큼)
    # 'easyocr',
    # 'torch',
    # 'transformers',
    
    # 기타
    'PIL',
    'PIL.Image',
    'sqlite3',
    'json',
    'asyncio',
    'multiprocessing',
]

# 제외할 모듈 (용량 줄이기)
excludes = [
    'tkinter',
    'matplotlib',
    'scipy',
    'numpy.distutils',
    'test',
    'tests',
]

a = Analysis(
    ['main.py'],
    pathex=[str(CORE_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='cuenote-core',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 콘솔 창 표시 (디버깅용, 배포 시 False로)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 아이콘 경로 (있으면 추가)
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='cuenote-core',
)
