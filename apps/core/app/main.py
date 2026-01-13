"""
CueNote Core - FastAPI 메인 앱
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .routers import vault_router, todos_router, ai_router, llm_router, environment_router, schedules_router, graph_router

# 로거 설정
logger = logging.getLogger("cuenote.core")
logging.basicConfig(level=logging.INFO)

# FastAPI 앱 생성
app = FastAPI(
    title="CueNote Core",
    description="CueNote 마크다운 노트 앱의 백엔드 API",
    version="1.0.0"
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(vault_router)
app.include_router(todos_router)
app.include_router(ai_router)
app.include_router(llm_router)
app.include_router(environment_router)
app.include_router(schedules_router)
app.include_router(graph_router)


@app.on_event("startup")
async def on_startup() -> None:
    """앱 시작 시 초기화"""
    init_db()
    logger.info("CueNote core started")


@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "ok"}
