"""
CueNote Core - OpenAI API 클라이언트
OpenAI API를 통한 텍스트 생성 (GPT-4, GPT-3.5 등)
"""
import asyncio
import json
import logging
from typing import Any, AsyncIterator, Optional
from urllib import request

try:
    from .json_extract import extract_first_json
except ImportError:
    from json_extract import extract_first_json

logger = logging.getLogger("cuenote.core")

# OpenAI API 기본 설정
OPENAI_API_BASE = "https://api.openai.com/v1"

# 사용 가능한 OpenAI 모델 목록 (공식 문서 기준 2025)
# https://platform.openai.com/docs/models
OPENAI_MODELS = [
    # ─────────────────────────────────────────────────────────────────────────
    # o-시리즈 (추론 모델, 2025 최신)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "o3",
        "name": "o3",
        "description": "최고 추론 모델, 복잡한 분석/코딩/연구용",
        "free": False,
        "context_window": 200000,
    },
    {
        "id": "o4-mini",
        "name": "o4-mini",
        "description": "빠르고 효율적인 추론 모델, STEM/코딩 최적화",
        "free": False,
        "context_window": 200000,
    },
    {
        "id": "o3-pro",
        "name": "o3-pro",
        "description": "o3 고성능 버전, 더 많은 컴퓨팅 파워",
        "free": False,
        "context_window": 200000,
    },
    {
        "id": "o3-mini",
        "name": "o3-mini",
        "description": "o3 경량 버전, 빠른 추론",
        "free": False,
        "context_window": 200000,
    },
    # ─────────────────────────────────────────────────────────────────────────
    # GPT-4.1 시리즈 (2025 최신)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "gpt-4.1",
        "name": "GPT-4.1",
        "description": "최고 비추론 모델, 1M 컨텍스트 (추천)",
        "free": False,
        "context_window": 1000000,
    },
    {
        "id": "gpt-4.1-mini",
        "name": "GPT-4.1 Mini",
        "description": "GPT-4.1 경량 버전, 빠르고 저렴",
        "free": False,
        "context_window": 1000000,
    },
    {
        "id": "gpt-4.1-nano",
        "name": "GPT-4.1 Nano",
        "description": "GPT-4.1 초경량 버전, 가장 빠름",
        "free": False,
        "context_window": 1000000,
    },
    # ─────────────────────────────────────────────────────────────────────────
    # GPT-4o 시리즈 (범용)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "description": "범용 플래그십 모델, 멀티모달 지원",
        "free": False,
        "context_window": 128000,
    },
    {
        "id": "gpt-4o-mini",
        "name": "GPT-4o Mini",
        "description": "범용 경량 모델, 가성비 좋음",
        "free": False,
        "context_window": 128000,
    },
    # ─────────────────────────────────────────────────────────────────────────
    # 레거시 모델
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "gpt-4-turbo",
        "name": "GPT-4 Turbo",
        "description": "GPT-4 향상 버전 (레거시)",
        "free": False,
        "context_window": 128000,
    },
    {
        "id": "gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "description": "빠르고 경제적 (레거시)",
        "free": False,
        "context_window": 16385,
    },
]

# 기본 모델 (가성비 좋은 최신 모델)
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"


def get_available_models() -> list[dict]:
    """사용 가능한 OpenAI 모델 목록 반환"""
    return OPENAI_MODELS


def generate(
    prompt: str,
    api_key: str,
    model: Optional[str] = None,
    temperature: float = 0.0,
) -> str:
    """OpenAI API를 통해 텍스트 생성"""
    if model is None:
        model = DEFAULT_OPENAI_MODEL

    url = f"{OPENAI_API_BASE}/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
    }

    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=120) as response:
            body = response.read().decode("utf-8")
        data = json.loads(body)

        # OpenAI API 응답에서 텍스트 추출
        choices = data.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            return message.get("content", "")
        return ""
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise


def call_json(
    prompt: str,
    schema_hint: str,
    api_key: str,
    model: Optional[str] = None
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
# 스트리밍 지원
# ─────────────────────────────────────────────────────────────────────────────

async def stream_generate(
    prompt: str,
    api_key: str,
    model: Optional[str] = None,
    chunk_delay: float = 0.0,
) -> AsyncIterator[str]:
    """스트리밍 방식으로 텍스트 생성"""
    try:
        import httpx
    except ImportError:
        logger.error("httpx is required for streaming. Install with: pip install httpx")
        raise ImportError("httpx is required for OpenAI streaming")

    if model is None:
        model = DEFAULT_OPENAI_MODEL

    url = f"{OPENAI_API_BASE}/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
        "stream": True,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                }
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            choices = data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                                    if chunk_delay > 0:
                                        await asyncio.sleep(chunk_delay)
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        logger.error(f"OpenAI streaming error: {e}")
        raise


def validate_api_key(api_key: str) -> bool:
    """API 키 유효성 검사"""
    if not api_key or len(api_key) < 10:
        return False

    try:
        url = f"{OPENAI_API_BASE}/models"
        req = request.Request(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            method="GET"
        )
        with request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        logger.warning(f"OpenAI API key validation failed: {e}")
        return False
