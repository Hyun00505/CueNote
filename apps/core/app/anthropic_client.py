"""
CueNote Core - Anthropic API 클라이언트
Claude API를 통한 텍스트 생성
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

# Anthropic API 기본 설정
ANTHROPIC_API_BASE = "https://api.anthropic.com/v1"
ANTHROPIC_API_VERSION = "2023-06-01"

# 사용 가능한 Claude 모델 목록 (공식 문서 기준 2025)
# https://docs.anthropic.com/en/docs/about-claude/models
CLAUDE_MODELS = [
    # ─────────────────────────────────────────────────────────────────────────
    # Claude 4 시리즈 (2025 최신)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "claude-opus-4-6",
        "name": "Claude Opus 4.6",
        "description": "최고 지능, 코딩/에이전트에 최적화 (200K/1M 컨텍스트)",
        "free": False,
        "context_window": 200000,
    },
    {
        "id": "claude-sonnet-4-5-20250929",
        "name": "Claude Sonnet 4.5",
        "description": "속도와 지능의 균형, 컴퓨터 사용 지원 (200K/1M 컨텍스트)",
        "free": False,
        "context_window": 200000,
    },
    {
        "id": "claude-haiku-4-5-20251001",
        "name": "Claude Haiku 4.5",
        "description": "가장 빠른 모델, 준프론티어 지능 (200K 컨텍스트)",
        "free": False,
        "context_window": 200000,
    },
    # ─────────────────────────────────────────────────────────────────────────
    # Claude 4 레거시 (여전히 사용 가능)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "claude-opus-4-5-20251101",
        "name": "Claude Opus 4.5",
        "description": "이전 세대 Opus, 복잡한 작업용",
        "free": False,
        "context_window": 200000,
    },
    {
        "id": "claude-sonnet-4-20250514",
        "name": "Claude Sonnet 4",
        "description": "균형 잡힌 성능 (추천)",
        "free": False,
        "context_window": 200000,
    },
    {
        "id": "claude-3-7-sonnet-20250219",
        "name": "Claude 3.7 Sonnet",
        "description": "안정적인 성능, 128K 출력 지원",
        "free": False,
        "context_window": 200000,
    },
    # ─────────────────────────────────────────────────────────────────────────
    # Claude 3 시리즈 (레거시)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "claude-3-haiku-20240307",
        "name": "Claude 3 Haiku",
        "description": "빠르고 저렴한 레거시 모델",
        "free": False,
        "context_window": 200000,
    },
]

# 기본 모델 (최신 균형 모델)
DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-5-20250929"


def get_available_models() -> list[dict]:
    """사용 가능한 Claude 모델 목록 반환"""
    return CLAUDE_MODELS


def generate(
    prompt: str,
    api_key: str,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 4096,
) -> str:
    """Anthropic API를 통해 텍스트 생성"""
    if model is None:
        model = DEFAULT_CLAUDE_MODEL

    url = f"{ANTHROPIC_API_BASE}/messages"

    payload = {
        "model": model,
        "max_tokens": max_tokens,
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
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_API_VERSION,
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=120) as response:
            body = response.read().decode("utf-8")
        data = json.loads(body)

        # Anthropic API 응답에서 텍스트 추출
        content = data.get("content", [])
        if content:
            for block in content:
                if block.get("type") == "text":
                    return block.get("text", "")
        return ""
    except Exception as e:
        logger.error(f"Anthropic API error: {e}")
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
    max_tokens: int = 4096,
) -> AsyncIterator[str]:
    """스트리밍 방식으로 텍스트 생성"""
    try:
        import httpx
    except ImportError:
        logger.error("httpx is required for streaming. Install with: pip install httpx")
        raise ImportError("httpx is required for Anthropic streaming")

    if model is None:
        model = DEFAULT_CLAUDE_MODEL

    url = f"{ANTHROPIC_API_BASE}/messages"

    payload = {
        "model": model,
        "max_tokens": max_tokens,
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
                    "x-api-key": api_key,
                    "anthropic-version": ANTHROPIC_API_VERSION,
                }
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            event_type = data.get("type", "")

                            if event_type == "content_block_delta":
                                delta = data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    text = delta.get("text", "")
                                    if text:
                                        yield text
                                        if chunk_delay > 0:
                                            await asyncio.sleep(chunk_delay)
                            elif event_type == "message_stop":
                                break
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        logger.error(f"Anthropic streaming error: {e}")
        raise


def validate_api_key(api_key: str) -> bool:
    """API 키 유효성 검사"""
    if not api_key or len(api_key) < 10:
        return False

    # 간단한 테스트 요청 (최소 토큰으로)
    try:
        url = f"{ANTHROPIC_API_BASE}/messages"
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "Hi"}],
        }
        req = request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": ANTHROPIC_API_VERSION,
            },
            method="POST",
        )
        with request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        logger.warning(f"Anthropic API key validation failed: {e}")
        return False
