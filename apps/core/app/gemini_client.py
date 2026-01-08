"""
CueNote Core - Gemini API 클라이언트
Google Gemini API를 통한 텍스트 생성
"""
import asyncio
import json
import logging
from typing import Any, AsyncIterator
from urllib import request

try:
    from .json_extract import extract_first_json
except ImportError:
    from json_extract import extract_first_json

logger = logging.getLogger("cuenote.core")

# Gemini API 기본 설정
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# 사용 가능한 Gemini 모델 목록 (공식 가격표 기준)
# https://ai.google.dev/gemini-api/docs/pricing
GEMINI_MODELS = [
    # ─────────────────────────────────────────────────────────────────────────
    # Gemini 2.5 시리즈
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "description": "최신 고속 모델, 균형 잡힌 성능 (15 RPM)",
        "free": True,
        "context_window": 1048576,
    },
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "description": "최고 성능 모델, 복잡한 작업에 적합",
        "free": False,
        "context_window": 1048576,
    },
    # ─────────────────────────────────────────────────────────────────────────
    # Gemini 2.0 시리즈
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "gemini-2.0-flash",
        "name": "Gemini 2.0 Flash",
        "description": "차세대 고속 모델 (15 RPM)",
        "free": True,
        "context_window": 1048576,
    },
    {
        "id": "gemini-2.0-flash-lite",
        "name": "Gemini 2.0 Flash Lite",
        "description": "초경량 모델, 간단한 작업용 (30 RPM)",
        "free": True,
        "context_window": 1048576,
    },
    # ─────────────────────────────────────────────────────────────────────────
    # Gemini 1.5 시리즈 (가장 안정적)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "gemini-1.5-flash",
        "name": "Gemini 1.5 Flash",
        "description": "안정적인 고속 모델 (15 RPM, 추천)",
        "free": True,
        "context_window": 1048576,
    },
    {
        "id": "gemini-1.5-flash-8b",
        "name": "Gemini 1.5 Flash 8B",
        "description": "경량 모델, 빠른 처리 (15 RPM, 4M TPM)",
        "free": True,
        "context_window": 1048576,
    },
    {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro",
        "description": "고성능 모델, 복잡한 분석 (2 RPM, 50 RPD)",
        "free": True,  # 무료 등급 있음 (제한적)
        "context_window": 2097152,
    },
    # ─────────────────────────────────────────────────────────────────────────
    # Gemini 3 시리즈 (프리뷰)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "gemini-3-pro-preview",
        "name": "Gemini 3 Pro Preview",
        "description": "최신 프리뷰 모델, 가장 강력 (유료 전용)",
        "free": False,
        "context_window": 1048576,
    },
]

# 기본 모델 (가장 안정적이고 무료인 모델)
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"


def get_available_models() -> list[dict]:
    """사용 가능한 Gemini 모델 목록 반환"""
    return GEMINI_MODELS


def generate(
    prompt: str,
    api_key: str,
    model: str = None,
    temperature: float = 0.0,
) -> str:
    """Gemini API를 통해 텍스트 생성"""
    if model is None:
        model = DEFAULT_GEMINI_MODEL

    url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
        }
    }

    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=120) as response:
            body = response.read().decode("utf-8")
        data = json.loads(body)
        
        # Gemini API 응답에서 텍스트 추출
        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "")
        return ""
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise


def call_json(
    prompt: str,
    schema_hint: str,
    api_key: str,
    model: str = None
) -> Any:
    """JSON 응답을 생성하고 파싱"""
    text = generate(prompt, api_key, model)
    try:
        json_text = extract_first_json(text)
        return json.loads(json_text)
    except Exception as exc:
        logger.warning("JSON parse failed, retrying once: %s", exc)
        repair_prompt = (
            "Return ONLY valid JSON that matches this schema hint.\n"
            f"Schema hint: {schema_hint}\n"
            "If you need to correct formatting, do so silently.\n\n"
            f"Original prompt:\n{prompt}"
        )
        text = generate(repair_prompt, api_key, model)
        json_text = extract_first_json(text)
        return json.loads(json_text)


# ─────────────────────────────────────────────────────────────────────────────
# 스트리밍 지원 (httpx 사용)
# ─────────────────────────────────────────────────────────────────────────────

async def stream_generate(
    prompt: str,
    api_key: str,
    model: str = None,
    chunk_delay: float = 0.01,  # 청크 간 딜레이 (초)
) -> AsyncIterator[str]:
    """
    스트리밍 방식으로 텍스트 생성
    Gemini는 빠른 응답을 보내므로, 약간의 딜레이를 추가하여 자연스럽게 표시합니다.
    """
    try:
        import httpx
    except ImportError:
        logger.error("httpx is required for streaming. Install with: pip install httpx")
        raise ImportError("httpx is required for Gemini streaming")

    if model is None:
        model = DEFAULT_GEMINI_MODEL

    url = f"{GEMINI_API_BASE}/models/{model}:streamGenerateContent?key={api_key}&alt=sse"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.0,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            candidates = data.get("candidates", [])
                            if candidates:
                                content = candidates[0].get("content", {})
                                parts = content.get("parts", [])
                                if parts:
                                    text = parts[0].get("text", "")
                                    if text:
                                        # 텍스트를 그대로 전송 (공백, 줄바꿈 보존)
                                        # Gemini가 한번에 많이 보내도 SSE로 잘 전달됨
                                        yield text
                                        if chunk_delay > 0:
                                            await asyncio.sleep(chunk_delay)
                        except json.JSONDecodeError:
                            continue
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Gemini streaming error: {e}")
        raise


async def stream_generate_json(
    prompt: str,
    api_key: str,
    model: str = None
) -> AsyncIterator[str]:
    """
    JSON 응답을 스트리밍으로 생성
    완료 후 JSON 파싱은 클라이언트에서 처리
    """
    full_response = ""
    async for chunk in stream_generate(prompt, api_key, model):
        full_response += chunk
        yield chunk
    
    # 스트리밍 완료 후 JSON 유효성 검사 (로깅용)
    try:
        extract_first_json(full_response)
        logger.info("Gemini streaming JSON generation completed successfully")
    except Exception as e:
        logger.warning(f"Streamed content may not be valid JSON: {e}")


def validate_api_key(api_key: str) -> bool:
    """API 키 유효성 검사"""
    if not api_key or len(api_key) < 10:
        return False
    
    # 간단한 테스트 요청
    try:
        url = f"{GEMINI_API_BASE}/models?key={api_key}"
        req = request.Request(url, method="GET")
        with request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        logger.warning(f"API key validation failed: {e}")
        return False
