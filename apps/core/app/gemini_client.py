"""
CueNote Core - Gemini API 클라이언트
Google Gemini API를 통한 텍스트 생성
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

# Gemini API 기본 설정
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# 사용 가능한 Gemini 모델 목록 (공식 문서 기준 2025)
# https://ai.google.dev/gemini-api/docs/models
GEMINI_MODELS = [
    # ─────────────────────────────────────────────────────────────────────────
    # Gemini 3 시리즈 (최신, Preview)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "gemini-3-pro-preview",
        "name": "Gemini 3 Pro Preview",
        "description": "최고 성능 멀티모달 모델, 고급 추론 (1M 컨텍스트)",
        "free": False,
        "context_window": 1048576,
    },
    {
        "id": "gemini-3-flash-preview",
        "name": "Gemini 3 Flash Preview",
        "description": "빠르고 강력한 균형 모델 (1M 컨텍스트)",
        "free": True,
        "context_window": 1048576,
    },
    # ─────────────────────────────────────────────────────────────────────────
    # Gemini 2.5 시리즈 (안정적)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "description": "복잡한 추론, 코딩, 수학에 최적화 (1M 컨텍스트)",
        "free": False,
        "context_window": 1048576,
    },
    {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "description": "가성비 최고, 범용 모델 (1M 컨텍스트, 추천)",
        "free": True,
        "context_window": 1048576,
    },
    {
        "id": "gemini-2.5-flash-lite",
        "name": "Gemini 2.5 Flash-Lite",
        "description": "가장 빠르고 저렴한 모델, 대용량 처리용",
        "free": True,
        "context_window": 1048576,
    },
    # ─────────────────────────────────────────────────────────────────────────
    # Gemini 2.0 시리즈 (2026년 3월 종료 예정)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "gemini-2.0-flash",
        "name": "Gemini 2.0 Flash",
        "description": "고속 모델 (2026년 3월 종료 예정)",
        "free": True,
        "context_window": 1048576,
    },
    {
        "id": "gemini-2.0-flash-lite",
        "name": "Gemini 2.0 Flash-Lite",
        "description": "초경량 모델 (2026년 3월 종료 예정)",
        "free": True,
        "context_window": 1048576,
    },
]

# 기본 모델 (안정적이고 무료인 최신 모델)
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


def get_available_models() -> list[dict]:
    """사용 가능한 Gemini 모델 목록 반환"""
    return GEMINI_MODELS


def generate(
    prompt: str,
    api_key: str,
    model: Optional[str] = None,
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
# 스트리밍 지원 (httpx 사용)
# ─────────────────────────────────────────────────────────────────────────────

async def stream_generate(
    prompt: str,
    api_key: str,
    model: Optional[str] = None,
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
    model: Optional[str] = None
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


# ─────────────────────────────────────────────────────────────────────────────
# Vision API 지원 (이미지 분석 및 OCR)
# ─────────────────────────────────────────────────────────────────────────────

def generate_with_image(
    prompt: str,
    image_data: str,
    api_key: str,
    model: Optional[str] = None,
    temperature: float = 0.0,
) -> str:
    """
    이미지와 함께 Gemini API를 통해 텍스트 생성 (Vision API)
    
    Args:
        prompt: 프롬프트 텍스트
        image_data: Base64 인코딩된 이미지 데이터 (data:image/...;base64,... 형식)
        api_key: Gemini API 키
        model: 사용할 모델 (기본: gemini-1.5-flash)
        temperature: 온도 설정
    
    Returns:
        생성된 텍스트
    """
    if model is None:
        model = DEFAULT_GEMINI_MODEL
    
    # Base64 데이터에서 MIME 타입과 실제 데이터 분리
    if image_data.startswith("data:"):
        # data:image/png;base64,... 형식
        header, base64_content = image_data.split(",", 1)
        mime_type = header.split(":")[1].split(";")[0]
    else:
        # 순수 base64 데이터인 경우
        base64_content = image_data
        mime_type = "image/jpeg"  # 기본값
    
    url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64_content
                        }
                    }
                ]
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
        with request.urlopen(req, timeout=180) as response:  # 이미지 처리에 시간이 더 걸릴 수 있음
            body = response.read().decode("utf-8")
        data = json.loads(body)
        
        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "")
        return ""
    except Exception as e:
        logger.error(f"Gemini Vision API error: {e}")
        raise


def extract_text_from_image(
    image_data: str,
    api_key: str,
    language: str = "ko",
    model: Optional[str] = None,
) -> str:
    """
    이미지에서 텍스트를 추출하고 마크다운으로 변환 (OCR)
    
    Args:
        image_data: Base64 인코딩된 이미지 데이터
        api_key: Gemini API 키
        language: 출력 언어 (auto: 원문 언어 유지)
        model: 사용할 모델
    
    Returns:
        마크다운 형식의 텍스트
    """
    if language == "auto":
        lang_instruction = "Write in the SAME language as the text in the image"
    elif language == "ko":
        lang_instruction = "한국어로 작성"
    else:
        lang_instruction = f"Write in {language}"
    
    prompt = f"""이미지를 분석하고 내용을 마크다운 형식으로 변환하세요. {lang_instruction}.

## 지침:
1. 이미지에 있는 모든 텍스트를 정확하게 추출하세요
2. 문서의 구조와 계층을 유지하세요 (제목, 부제목, 목록 등)
3. 표가 있으면 마크다운 표로 변환하세요
4. 수식이 있으면 LaTeX 형식으로 변환하세요
5. 이미지에 대한 설명이 필요하면 간단히 추가하세요
6. 출력은 순수 마크다운만 반환하세요 (코드 블록으로 감싸지 마세요)

마크다운으로 변환된 내용:"""
    
    return generate_with_image(prompt, image_data, api_key, model)


def analyze_document_image(
    image_data: str,
    api_key: str,
    language: str = "ko",
    model: Optional[str] = None,
) -> dict:
    """
    문서 이미지를 분석하여 구조화된 마크다운과 메타데이터 반환
    
    Args:
        image_data: Base64 인코딩된 이미지 데이터
        api_key: Gemini API 키
        language: 출력 언어 (auto: 원문 언어 유지)
        model: 사용할 모델
    
    Returns:
        {"markdown": str, "has_images": bool, "summary": str}
    """
    if language == "auto":
        lang_instruction = "Write in the SAME language as the text in the image"
    elif language == "ko":
        lang_instruction = "한국어로 작성"
    else:
        lang_instruction = f"Write in {language}"
    
    prompt = f"""이 이미지를 분석하고 다음 형식의 JSON으로 응답하세요. {lang_instruction}.

## 응답 형식 (JSON):
{{
  "markdown": "추출된 마크다운 내용",
  "has_images": true/false (이미지에 그림, 차트, 사진이 포함되어 있는지),
  "summary": "내용 요약 (1-2문장)"
}}

## 마크다운 변환 지침:
1. 모든 텍스트를 정확하게 추출
2. 문서 구조 유지 (제목은 #, 목록은 -, 등)
3. 표는 마크다운 표로 변환
4. 수식은 LaTeX로 변환 ($...$ 또는 $$...$$)
5. 코드는 코드 블록으로 감싸기

JSON 응답:"""
    
    result_text = ""
    try:
        result_text = generate_with_image(prompt, image_data, api_key, model)
        
        # JSON 파싱 시도
        from .json_extract import extract_first_json
        json_text = extract_first_json(result_text)
        result = json.loads(json_text)
        
        return {
            "markdown": result.get("markdown", result_text),
            "has_images": result.get("has_images", False),
            "summary": result.get("summary", "")
        }
    except Exception as e:
        logger.warning(f"JSON parsing failed, using raw text: {e}")
        # JSON 파싱 실패 시 텍스트만 반환
        return {
            "markdown": result_text,
            "has_images": False,
            "summary": ""
        }