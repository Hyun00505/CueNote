"""
CueNote Core - AI 라우터
요약, 번역, 다듬기, 스트리밍 등 AI 기능
"""
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from ..config import logger
from ..ollama_client import call_json, process_long_text, stream_generate, MAX_INPUT_CHARS
from ..schemas import (
    SummarizePayload, SummarizeResponse,
    TranslatePayload, TranslateResponse,
    ImprovePayload, ImproveResponse,
    ExpandPayload, ExpandResponse,
    ShortenPayload, ShortenResponse,
    StreamPayload
)

router = APIRouter(prefix="/ai", tags=["ai"])


# ─────────────────────────────────────────────────────────────────────────────
# 요약
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_note(payload: SummarizePayload):
    """노트 내용을 요약합니다."""
    content = payload.content.strip()
    
    if not content:
        raise HTTPException(status_code=400, detail="Content is empty")
    
    content, truncation_warning = process_long_text(content)
    word_count = len(content.split())
    
    if word_count < 20:
        return SummarizeResponse(summary=content, keyPoints=[], wordCount=word_count)
    
    lang_instruction = "한국어로" if payload.language == "ko" else f"in {payload.language}"
    
    prompt = (
        f"You are a helpful assistant that summarizes notes. Respond {lang_instruction}.\n"
        "Output MUST be JSON only and match the schema.\n\n"
        "Rules:\n"
        "- summary: A concise 2-3 sentence summary of the main content\n"
        "- keyPoints: Up to 5 bullet points highlighting the most important information\n"
        "- Be accurate and preserve the key meaning\n\n"
        f"Note content:\n{content}\n\n"
        "Schema:\n"
        '{\n  "summary": "string",\n  "keyPoints": ["string"]\n}\n'
        "Return JSON only."
    )
    
    try:
        result = call_json(prompt, "SummarizeResult with fields summary, keyPoints")
        summary = result.get("summary", "요약 생성 실패")
        if truncation_warning:
            summary = f"{summary}\n\n{truncation_warning}"
        return SummarizeResponse(
            summary=summary,
            keyPoints=result.get("keyPoints", []),
            wordCount=word_count
        )
    except Exception as e:
        logger.error("Summarize failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to generate summary")


# ─────────────────────────────────────────────────────────────────────────────
# 번역
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/translate", response_model=TranslateResponse)
async def translate_text(payload: TranslatePayload):
    """선택된 텍스트를 지정된 언어로 번역합니다."""
    content = payload.content.strip()
    
    if not content:
        raise HTTPException(status_code=400, detail="Content is empty")
    
    content, truncation_warning = process_long_text(content)
    
    language_names = {
        "ko": "Korean", "en": "English", "ja": "Japanese",
        "zh": "Chinese", "es": "Spanish", "fr": "French", "de": "German"
    }
    target_lang_name = language_names.get(payload.target_language, payload.target_language)
    
    prompt = (
        f"Translate the following text to {target_lang_name}.\n"
        "Output MUST be JSON only and match the schema.\n\n"
        "CRITICAL RULES:\n"
        "- PRESERVE ALL MARKDOWN FORMATTING exactly as-is\n"
        "- Only translate the actual text content, not URLs or special markers\n"
        "- Preserve the original meaning and tone\n"
        "- Detect the source language\n\n"
        f"Text to translate:\n{content}\n\n"
        "Schema:\n"
        '{\n  "translated": "string",\n  "source_language": "string"\n}\n'
        "Return JSON only."
    )
    
    try:
        result = call_json(prompt, "TranslateResult with fields translated, source_language")
        translated = result.get("translated", content)
        if truncation_warning:
            translated = f"{translated}\n\n{truncation_warning}"
        return TranslateResponse(
            translated=translated,
            source_language=result.get("source_language", "unknown")
        )
    except Exception as e:
        logger.error("Translate failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to translate text")


# ─────────────────────────────────────────────────────────────────────────────
# 글 다듬기
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/improve", response_model=ImproveResponse)
async def improve_text(payload: ImprovePayload):
    """선택된 텍스트의 문장을 개선합니다."""
    content = payload.content.strip()
    
    if not content:
        raise HTTPException(status_code=400, detail="Content is empty")
    
    content, truncation_warning = process_long_text(content)
    
    style_instructions = {
        "professional": "Make it more professional and polished",
        "casual": "Make it more casual and friendly",
        "academic": "Make it more formal and academic",
        "creative": "Make it more creative and engaging",
        "concise": "Make it more concise and clear",
        "detailed": "Add more detail and explanation"
    }
    style_inst = style_instructions.get(payload.style, style_instructions["professional"])
    lang_instruction = "한국어로 작성" if payload.language == "ko" else f"Write in {payload.language}"
    
    prompt = (
        f"Improve the following text. {style_inst}. {lang_instruction}.\n"
        "Output MUST be JSON only and match the schema.\n\n"
        "CRITICAL RULES:\n"
        "- PRESERVE ALL MARKDOWN FORMATTING exactly as-is\n"
        "- Improve grammar, clarity, and flow\n"
        "- Preserve the original meaning\n"
        "- List 2-3 key changes made\n\n"
        f"Text to improve:\n{content}\n\n"
        "Schema:\n"
        '{\n  "improved": "string",\n  "changes": ["string"]\n}\n'
        "Return JSON only."
    )
    
    try:
        result = call_json(prompt, "ImproveResult with fields improved, changes")
        improved = result.get("improved", content)
        if truncation_warning:
            improved = f"{improved}\n\n{truncation_warning}"
        return ImproveResponse(
            improved=improved,
            changes=result.get("changes", [])
        )
    except Exception as e:
        logger.error("Improve failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to improve text")


# ─────────────────────────────────────────────────────────────────────────────
# 확장
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/expand", response_model=ExpandResponse)
async def expand_text(payload: ExpandPayload):
    """선택된 텍스트를 더 자세하게 확장합니다."""
    content = payload.content.strip()
    
    if not content:
        raise HTTPException(status_code=400, detail="Content is empty")
    
    content, truncation_warning = process_long_text(content, max_chars=8000)
    lang_instruction = "한국어로 작성" if payload.language == "ko" else f"Write in {payload.language}"
    
    prompt = (
        f"Expand and elaborate on the following text. {lang_instruction}.\n"
        "Output MUST be JSON only and match the schema.\n\n"
        "CRITICAL RULES:\n"
        "- PRESERVE ALL MARKDOWN FORMATTING exactly as-is\n"
        "- Add more detail and explanation\n"
        "- Keep the same tone and style\n"
        "- Make it about 2-3x longer\n\n"
        f"Text to expand:\n{content}\n\n"
        "Schema:\n"
        '{\n  "expanded": "string"\n}\n'
        "Return JSON only."
    )
    
    try:
        result = call_json(prompt, "ExpandResult with field expanded")
        expanded = result.get("expanded", content)
        if truncation_warning:
            expanded = f"{expanded}\n\n{truncation_warning}"
        return ExpandResponse(expanded=expanded)
    except Exception as e:
        logger.error("Expand failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to expand text")


# ─────────────────────────────────────────────────────────────────────────────
# 축약
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/shorten", response_model=ShortenResponse)
async def shorten_text(payload: ShortenPayload):
    """선택된 텍스트를 더 간결하게 축약합니다."""
    content = payload.content.strip()
    
    if not content:
        raise HTTPException(status_code=400, detail="Content is empty")
    
    content, truncation_warning = process_long_text(content)
    lang_instruction = "한국어로 작성" if payload.language == "ko" else f"Write in {payload.language}"
    
    prompt = (
        f"Shorten and condense the following text. {lang_instruction}.\n"
        "Output MUST be JSON only and match the schema.\n\n"
        "CRITICAL RULES:\n"
        "- PRESERVE ALL MARKDOWN FORMATTING exactly as-is\n"
        "- Keep the essential meaning\n"
        "- Remove redundancy\n"
        "- Make it about half the length\n\n"
        f"Text to shorten:\n{content}\n\n"
        "Schema:\n"
        '{\n  "shortened": "string"\n}\n'
        "Return JSON only."
    )
    
    try:
        result = call_json(prompt, "ShortenResult with field shortened")
        shortened = result.get("shortened", content)
        if truncation_warning:
            shortened = f"{shortened}\n\n{truncation_warning}"
        return ShortenResponse(shortened=shortened)
    except Exception as e:
        logger.error("Shorten failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to shorten text")


# ─────────────────────────────────────────────────────────────────────────────
# 스트리밍
# ─────────────────────────────────────────────────────────────────────────────

def build_stream_prompt(payload: StreamPayload) -> str:
    """스트리밍용 프롬프트 생성"""
    content = payload.content
    
    preserve_rules = (
        "CRITICAL RULES:\n"
        "- Output ONLY the result text, no explanations\n"
        "- Write words and sentences as continuous text\n"
        "- Do NOT add line breaks between characters or words\n"
        "- Do NOT add spaces between characters\n"
        "- Keep original paragraph structure (line breaks between paragraphs only)\n"
        "- PRESERVE markdown syntax: # headers, - lists, **bold**, *italic*\n"
    )
    
    if payload.action == "translate":
        language_names = {
            "ko": "Korean (한국어)", "en": "English", "ja": "Japanese (日本語)",
            "zh": "Chinese (中文)", "es": "Spanish (Español)", "fr": "French (Français)", "de": "German (Deutsch)"
        }
        target_lang = language_names.get(payload.target_language, payload.target_language)
        
        korean_instruction = ""
        if payload.target_language == "ko":
            korean_instruction = (
                "\nKOREAN TRANSLATION RULES:\n"
                "- Use ONLY Hangul (Korean alphabet) for the translation\n"
                "- Do NOT use Chinese characters (漢字/한자) - convert them to Hangul\n"
                "- Do NOT use Japanese characters (ひらがな/カタカナ) - translate to Korean\n"
                "- Common conversions: 日 → 일, 月 → 월, 年 → 년, 中 → 중\n"
                "- Write all Korean words in pure Hangul script\n"
            )
        
        return (
            f"Translate the following text to {target_lang}.\n"
            f"{preserve_rules}"
            f"{korean_instruction}\n"
            f"---INPUT---\n{content}\n---OUTPUT ({target_lang})---\n"
        )
    
    elif payload.action == "improve":
        style_instructions = {
            "professional": "more professional",
            "casual": "more casual and friendly",
            "academic": "more academic",
            "creative": "more creative",
            "concise": "more concise",
            "detailed": "more detailed"
        }
        style_inst = style_instructions.get(payload.style, style_instructions["professional"])
        return (
            f"Rewrite the following text to be {style_inst}. Keep the same language.\n"
            f"{preserve_rules}\n"
            f"---INPUT---\n{content}\n---OUTPUT---\n"
        )
    
    elif payload.action == "expand":
        return (
            f"Expand the following text with more details. Make it 2-3x longer. Keep the same language.\n"
            f"{preserve_rules}\n"
            f"---INPUT---\n{content}\n---OUTPUT---\n"
        )
    
    elif payload.action == "shorten":
        return (
            f"Shorten the following text to about half the length. Keep key points. Keep the same language.\n"
            f"{preserve_rules}\n"
            f"---INPUT---\n{content}\n---OUTPUT---\n"
        )
    
    elif payload.action == "summarize":
        return (
            f"Summarize the following text in 2-3 sentences. Keep the same language.\n"
            f"{preserve_rules}\n"
            f"---INPUT---\n{content}\n---SUMMARY---\n"
        )
    
    else:
        raise ValueError(f"Unknown action: {payload.action}")


@router.post("/stream")
async def ai_stream(payload: StreamPayload):
    """스트리밍 방식으로 AI 텍스트 생성 (SSE)"""
    content = payload.content.strip()
    
    if not content:
        raise HTTPException(status_code=400, detail="Content is empty")
    
    max_chars = 8000 if payload.action == "expand" else MAX_INPUT_CHARS
    content, truncation_warning = process_long_text(content, max_chars)
    payload.content = content
    
    try:
        prompt = build_stream_prompt(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    async def event_generator():
        try:
            async for chunk in stream_generate(prompt):
                escaped_chunk = chunk.replace('\n', '\\n')
                yield {"event": "message", "data": escaped_chunk}
            
            if truncation_warning:
                yield {"event": "warning", "data": truncation_warning}
            yield {"event": "done", "data": ""}
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {"event": "error", "data": str(e)}
    
    return EventSourceResponse(event_generator())
