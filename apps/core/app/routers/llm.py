"""
CueNote Core - LLM 설정 라우터
LLM 제공자 및 모델 목록 조회, API 키 검증
"""
from fastapi import APIRouter, HTTPException

from ..config import logger
from ..schemas import ValidateApiKeyPayload
from .. import gemini_client
from .. import ollama_client
from .. import openai_client
from .. import anthropic_client

router = APIRouter(prefix="/llm", tags=["llm"])


# ─────────────────────────────────────────────────────────────────────────────
# LLM 제공자 목록
# ─────────────────────────────────────────────────────────────────────────────

LLM_PROVIDERS = [
    {
        "id": "ollama",
        "name": "Ollama (로컬)",
        "description": "로컬에서 실행되는 오픈소스 LLM",
        "requiresApiKey": False,
        "apiKeyUrl": ""
    },
    {
        "id": "gemini",
        "name": "Google Gemini",
        "description": "Google의 최신 AI 모델",
        "requiresApiKey": True,
        "apiKeyUrl": "https://aistudio.google.com/app/apikey"
    },
    {
        "id": "openai",
        "name": "OpenAI",
        "description": "GPT-4, GPT-3.5 등 OpenAI 모델",
        "requiresApiKey": True,
        "apiKeyUrl": "https://platform.openai.com/api-keys"
    },
    {
        "id": "anthropic",
        "name": "Anthropic Claude",
        "description": "Claude 3.5, Claude 3 등 Anthropic 모델",
        "requiresApiKey": True,
        "apiKeyUrl": "https://console.anthropic.com/settings/keys"
    }
]


@router.get("/providers")
async def get_providers():
    """사용 가능한 LLM 제공자 목록 반환"""
    return {"providers": LLM_PROVIDERS}


# ─────────────────────────────────────────────────────────────────────────────
# Gemini 모델 목록
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/gemini/models")
async def get_gemini_models():
    """Gemini API에서 사용 가능한 모델 목록 반환"""
    models = gemini_client.get_available_models()
    return {"models": models}


# ─────────────────────────────────────────────────────────────────────────────
# Ollama 모델 목록
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/ollama/models")
async def get_ollama_models():
    """로컬 Ollama에서 설치된 모델 목록 반환"""
    models = ollama_client.get_installed_models()
    
    if not models:
        # Ollama가 실행 중이 아니거나 모델이 없는 경우
        return {
            "models": [],
            "error": "Ollama가 실행 중이 아니거나 설치된 모델이 없습니다. 'ollama pull <모델명>'으로 모델을 설치하세요."
        }
    
    return {"models": models}


# ─────────────────────────────────────────────────────────────────────────────
# API 키 검증
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/gemini/validate-key")
async def validate_gemini_key(payload: ValidateApiKeyPayload):
    """Gemini API 키 유효성 검사"""
    is_valid = gemini_client.validate_api_key(payload.api_key)
    return {"valid": is_valid}


# ─────────────────────────────────────────────────────────────────────────────
# OpenAI 모델 목록 및 키 검증
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/openai/models")
async def get_openai_models():
    """OpenAI API에서 사용 가능한 모델 목록 반환"""
    models = openai_client.get_available_models()
    return {"models": models}


@router.post("/openai/validate-key")
async def validate_openai_key(payload: ValidateApiKeyPayload):
    """OpenAI API 키 유효성 검사"""
    is_valid = openai_client.validate_api_key(payload.api_key)
    return {"valid": is_valid}


# ─────────────────────────────────────────────────────────────────────────────
# Anthropic (Claude) 모델 목록 및 키 검증
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/anthropic/models")
async def get_anthropic_models():
    """Anthropic API에서 사용 가능한 모델 목록 반환"""
    models = anthropic_client.get_available_models()
    return {"models": models}


@router.post("/anthropic/validate-key")
async def validate_anthropic_key(payload: ValidateApiKeyPayload):
    """Anthropic API 키 유효성 검사"""
    is_valid = anthropic_client.validate_api_key(payload.api_key)
    return {"valid": is_valid}
