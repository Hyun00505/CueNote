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

# certifi CA 번들 + 패키지 데이터 파일 수집
import certifi
from PyInstaller.utils.hooks import collect_data_files

# 데이터 파일
datas = [
    # certifi CA 번들
    (certifi.where(), 'certifi'),
]
# trafilatura/tld/justext/dateparser 패키지 데이터 수집
datas += collect_data_files('trafilatura')
datas += collect_data_files('tld')
datas += collect_data_files('justext')
datas += collect_data_files('dateparser')

# 숨겨진 imports (동적으로 임포트되는 모듈들)
hiddenimports = [
    # FastAPI & Uvicorn (전체 모듈 포함)
    'fastapi',
    'fastapi.applications',
    'fastapi.routing',
    'fastapi.params',
    'fastapi.responses',
    'fastapi.requests',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'fastapi.staticfiles',
    'fastapi.templating',
    'fastapi.security',
    'fastapi.encoders',
    'fastapi.exceptions',
    
    # Starlette (FastAPI 의존성)
    'starlette',
    'starlette.applications',
    'starlette.routing',
    'starlette.responses',
    'starlette.requests',
    'starlette.middleware',
    'starlette.middleware.cors',
    'starlette.staticfiles',
    'starlette.templating',
    'starlette.exceptions',
    'starlette.background',
    'starlette.concurrency',
    'starlette.config',
    'starlette.datastructures',
    'starlette.formparsers',
    'starlette.status',
    'starlette.types',
    'starlette.websockets',
    
    # Uvicorn
    'uvicorn',
    'uvicorn.config',
    'uvicorn.main',
    'uvicorn.server',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    
    # Pydantic
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    'pydantic.networks',
    'pydantic.types',
    'pydantic_core',
    
    # SSE
    'sse_starlette',
    'sse_starlette.sse',
    
    # HTTP
    'httpx',
    'httpcore',
    'anyio',
    'anyio._backends',
    'anyio._backends._asyncio',
    'sniffio',
    
    # LangChain (전체 서브모듈 포함)
    'langchain',
    'langchain.schema',
    'langchain.llms',
    'langchain.chat_models',
    'langchain.prompts',
    'langchain.chains',
    
    # LangChain Ollama
    'langchain_ollama',
    'langchain_ollama.chat_models',
    'langchain_ollama.llms',
    
    # LangChain Core (중요!)
    'langchain_core',
    'langchain_core.callbacks',
    'langchain_core.callbacks.base',
    'langchain_core.callbacks.manager',
    'langchain_core.callbacks.streaming_stdout',
    'langchain_core.language_models',
    'langchain_core.language_models.base',
    'langchain_core.language_models.chat_models',
    'langchain_core.language_models.llms',
    'langchain_core.messages',
    'langchain_core.messages.base',
    'langchain_core.messages.human',
    'langchain_core.messages.ai',
    'langchain_core.messages.system',
    'langchain_core.outputs',
    'langchain_core.outputs.chat_generation',
    'langchain_core.outputs.generation',
    'langchain_core.outputs.llm_result',
    'langchain_core.prompts',
    'langchain_core.runnables',
    'langchain_core.runnables.base',
    'langchain_core.runnables.config',
    'langchain_core.load',
    'langchain_core.load.serializable',
    'langchain_core.pydantic_v1',
    'langchain_core.utils',
    
    # LangChain Text Splitters
    'langchain_text_splitters',
    
    # PDF
    'fitz',
    'pymupdf',
    
    # OCR (RapidOCR - ONNX Runtime 기반)
    'rapidocr_onnxruntime',
    'onnxruntime',
    'numpy',
    'cv2',
    
    # 기타
    'PIL',
    'PIL.Image',
    'sqlite3',
    'json',
    'asyncio',
    'multiprocessing',
    
    # 추가 의존성
    'email.mime.multipart',
    'email.mime.text',
    'email.mime.base',
    'typing_extensions',
    'annotated_types',

    # Web Extraction (URL 추출)
    'trafilatura',
    'trafilatura.settings',
    'trafilatura.core',
    'trafilatura.utils',
    'trafilatura.metadata',
    'trafilatura.external',
    'courlan',
    'htmldate',
    'justext',
    'lxml',
    'lxml.html',
    'lxml.etree',
    'tld',
    'charset_normalizer',
    'certifi',
    'urllib3',

    # Graph / Clustering (그래프 페이지)
    'sklearn',
    'sklearn.feature_extraction',
    'sklearn.feature_extraction.text',
    'sklearn.metrics',
    'sklearn.metrics.pairwise',
    'sklearn.cluster',
    'sklearn.utils',
    'sklearn.utils._cython_blas',
    'sklearn.neighbors',
    'sklearn.neighbors._typedefs',
    'sklearn.neighbors._partition_nodes',
    'sklearn.tree',
    'sklearn.tree._utils',
    'threadpoolctl',
]

# 제외할 모듈 (용량 줄이기)
excludes = [
    'tkinter',
    'matplotlib',
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
    console=False,  # 배포용: 콘솔 창 숨김
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
