import json
import logging
from typing import Any
from urllib import request

try:
    from .json_extract import extract_first_json
except ImportError:
    from json_extract import extract_first_json

OLLAMA_BASE_URL = "http://127.0.0.1:11434"

# 모델 설정
OLLAMA_MODEL_TEXT = "qwen2.5:7b"  # 글 편집/번역/요약용 (한국어 지원 우수)
OLLAMA_MODEL_PLAN = "qwen2.5:7b"   # 일반 계획 생성용 (가벼운 작업)

# 컨텍스트 설정
MAX_CONTEXT_TOKENS = 8192  # Phi-3.5-mini의 최대 컨텍스트
DEFAULT_CONTEXT_TOKENS = 4096
MAX_INPUT_CHARS = 12000  # 입력 텍스트 최대 길이 (약 3000 토큰)

logger = logging.getLogger("cuenote.core")


def estimate_tokens(text: str) -> int:
    """텍스트의 대략적인 토큰 수 추정 (영어 기준 4자 = 1토큰, 한글 기준 1자 = 1토큰)"""
    # 한글 문자 수
    korean_chars = sum(1 for c in text if '\uac00' <= c <= '\ud7af')
    # 영어/기타 문자 수
    other_chars = len(text) - korean_chars
    return korean_chars + (other_chars // 4)


def truncate_text(text: str, max_chars: int = MAX_INPUT_CHARS) -> tuple[str, bool]:
    """긴 텍스트를 안전한 길이로 자르고, 잘렸는지 여부 반환"""
    if len(text) <= max_chars:
        return text, False
    
    # 문장 단위로 자르기 시도
    truncated = text[:max_chars]
    
    # 마지막 완전한 문장 찾기
    last_period = max(
        truncated.rfind('.'),
        truncated.rfind('。'),
        truncated.rfind('!'),
        truncated.rfind('?'),
        truncated.rfind('\n\n')
    )
    
    if last_period > max_chars * 0.7:  # 70% 이상 위치에 문장 끝이 있으면
        truncated = truncated[:last_period + 1]
    
    return truncated, True


def calculate_context_size(text: str) -> int:
    """텍스트 길이에 따른 적절한 컨텍스트 크기 계산"""
    estimated_tokens = estimate_tokens(text)
    # 입력 + 출력을 위한 여유 공간 (입력의 2배 정도)
    needed_ctx = estimated_tokens * 3
    return min(max(needed_ctx, DEFAULT_CONTEXT_TOKENS), MAX_CONTEXT_TOKENS)


def generate(
    prompt: str, 
    temperature: float = 0.0, 
    num_ctx: int = None,
    model: str = None
) -> str:
    """Ollama API를 통해 텍스트 생성"""
    if model is None:
        model = OLLAMA_MODEL_TEXT
    
    if num_ctx is None:
        num_ctx = calculate_context_size(prompt)
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": num_ctx},
    }
    req = request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=120) as response:  # 긴 텍스트를 위해 타임아웃 증가
        body = response.read().decode("utf-8")
    data = json.loads(body)
    return data.get("response", "")


def call_json(prompt: str, schema_hint: str, model: str = None) -> Any:
    """JSON 응답을 생성하고 파싱"""
    text = generate(prompt, model=model)
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
        text = generate(repair_prompt, model=model)
        json_text = extract_first_json(text)
        return json.loads(json_text)


def process_long_text(text: str, max_chars: int = MAX_INPUT_CHARS) -> tuple[str, str]:
    """
    긴 텍스트 처리: 자르고 경고 메시지 반환
    Returns: (처리된 텍스트, 경고 메시지 또는 빈 문자열)
    """
    truncated, was_truncated = truncate_text(text, max_chars)
    warning = ""
    if was_truncated:
        warning = f"(원본 텍스트가 너무 길어 일부만 처리되었습니다. 처리된 길이: {len(truncated)}자)"
        logger.warning(f"Text truncated from {len(text)} to {len(truncated)} chars")
    return truncated, warning


# ─────────────────────────────────────────────────────────────────────────────
# LangChain 스트리밍 지원
# ─────────────────────────────────────────────────────────────────────────────

from typing import AsyncIterator
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# LangChain Ollama 모델 (스트리밍용)
_streaming_llm = None

def get_streaming_llm(model: str = None) -> ChatOllama:
    """스트리밍 지원 LLM 인스턴스 반환"""
    global _streaming_llm
    if model is None:
        model = OLLAMA_MODEL_TEXT
    
    # 모델이 변경되었거나 초기화되지 않은 경우 새로 생성
    if _streaming_llm is None or _streaming_llm.model != model:
        _streaming_llm = ChatOllama(
            model=model,
            base_url=OLLAMA_BASE_URL,
            num_ctx=MAX_CONTEXT_TOKENS,
            temperature=0.0,
        )
    return _streaming_llm


async def stream_generate(prompt: str, model: str = None) -> AsyncIterator[str]:
    """
    스트리밍 방식으로 텍스트 생성
    실시간으로 토큰을 하나씩 yield합니다.
    """
    llm = get_streaming_llm(model)
    
    try:
        async for chunk in llm.astream([HumanMessage(content=prompt)]):
            if chunk.content:
                yield chunk.content
    except Exception as e:
        logger.error(f"Streaming generation failed: {e}")
        raise


async def stream_generate_json(
    prompt: str, 
    model: str = None
) -> AsyncIterator[str]:
    """
    JSON 응답을 스트리밍으로 생성
    완료 후 JSON 파싱은 클라이언트에서 처리
    """
    full_response = ""
    async for chunk in stream_generate(prompt, model):
        full_response += chunk
        yield chunk
    
    # 스트리밍 완료 후 JSON 유효성 검사 (로깅용)
    try:
        extract_first_json(full_response)
        logger.info("Streaming JSON generation completed successfully")
    except Exception as e:
        logger.warning(f"Streamed content may not be valid JSON: {e}")
