"""
CueNote Core - AI 라우터
요약, 번역, 다듬기, 스트리밍 등 AI 기능
Ollama 및 Gemini API 지원
"""
from typing import Optional, cast, Literal
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from ..config import logger
from .. import ollama_client
from .. import gemini_client
from ..schemas import (
    SummarizePayload, SummarizeResponse,
    TranslatePayload, TranslateResponse,
    ImprovePayload, ImproveResponse,
    ExpandPayload, ExpandResponse,
    ShortenPayload, ShortenResponse,
    ProofreadPayload, ProofreadResponse, CorrectionItem,
    StreamPayload,
    DocumentExtractPayload, DocumentExtractResponse,
    OCRModelStatus, OCRDownloadResponse,
)

# 기존 호환성을 위한 import
from ..ollama_client import process_long_text, MAX_INPUT_CHARS


def call_json_with_provider(
    prompt: str,
    schema_hint: str,
    provider: str = "ollama",
    api_key: str = "",
    model: Optional[str] = None
):
    """LLM 제공자에 따라 적절한 클라이언트로 JSON 호출"""
    if provider == "gemini" and api_key:
        return gemini_client.call_json(prompt, schema_hint, api_key, model)
    else:
        return ollama_client.call_json(prompt, schema_hint, model)

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
    
    # 언어 설정: auto이면 원문과 같은 언어로 응답
    if payload.language == "auto":
        lang_instruction = "in the SAME language as the input text"
    elif payload.language == "ko":
        lang_instruction = "한국어로"
    else:
        lang_instruction = f"in {payload.language}"
    
    prompt = (
        f"You are a helpful assistant that summarizes notes. Respond {lang_instruction}.\n"
        "Output MUST be JSON only and match the schema.\n\n"
        "Rules:\n"
        "- summary: A concise 2-3 sentence summary of the main content\n"
        "- keyPoints: Up to 5 bullet points highlighting the most important information\n"
        "- Be accurate and preserve the key meaning\n"
        "- IMPORTANT: Match the language of the input text when language is 'auto'\n\n"
        f"Note content:\n{content}\n\n"
        "Schema:\n"
        '{\n  "summary": "string",\n  "keyPoints": ["string"]\n}\n'
        "Return JSON only."
    )
    
    try:
        result = call_json_with_provider(
            prompt,
            "SummarizeResult with fields summary, keyPoints",
            provider=payload.provider,
            api_key=payload.api_key,
            model=payload.model if payload.model else None
        )
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
        result = call_json_with_provider(
            prompt,
            "TranslateResult with fields translated, source_language",
            provider=payload.provider,
            api_key=payload.api_key,
            model=payload.model if payload.model else None
        )
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
    
    # 언어 설정: auto이면 원문과 같은 언어로 응답
    if payload.language == "auto":
        lang_instruction = "Write in the SAME language as the input text"
    elif payload.language == "ko":
        lang_instruction = "한국어로 작성"
    else:
        lang_instruction = f"Write in {payload.language}"
    
    prompt = (
        f"Improve the following text. {style_inst}. {lang_instruction}.\n"
        "Output MUST be JSON only and match the schema.\n\n"
        "CRITICAL RULES:\n"
        "- PRESERVE ALL MARKDOWN FORMATTING exactly as-is\n"
        "- Improve grammar, clarity, and flow\n"
        "- Preserve the original meaning\n"
        "- List 2-3 key changes made\n"
        "- IMPORTANT: Match the language of the input text when language is 'auto'\n\n"
        f"Text to improve:\n{content}\n\n"
        "Schema:\n"
        '{\n  "improved": "string",\n  "changes": ["string"]\n}\n'
        "Return JSON only."
    )
    
    try:
        result = call_json_with_provider(
            prompt,
            "ImproveResult with fields improved, changes",
            provider=payload.provider,
            api_key=payload.api_key,
            model=payload.model if payload.model else None
        )
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
    
    # 언어 설정: auto이면 원문과 같은 언어로 응답
    if payload.language == "auto":
        lang_instruction = "Write in the SAME language as the input text"
    elif payload.language == "ko":
        lang_instruction = "한국어로 작성"
    else:
        lang_instruction = f"Write in {payload.language}"
    
    prompt = (
        f"Expand and elaborate on the following text. {lang_instruction}.\n"
        "Output MUST be JSON only and match the schema.\n\n"
        "CRITICAL RULES:\n"
        "- PRESERVE ALL MARKDOWN FORMATTING exactly as-is\n"
        "- Add more detail and explanation\n"
        "- Keep the same tone and style\n"
        "- Make it about 2-3x longer\n"
        "- IMPORTANT: Match the language of the input text when language is 'auto'\n\n"
        f"Text to expand:\n{content}\n\n"
        "Schema:\n"
        '{\n  "expanded": "string"\n}\n'
        "Return JSON only."
    )
    
    try:
        result = call_json_with_provider(
            prompt,
            "ExpandResult with field expanded",
            provider=payload.provider,
            api_key=payload.api_key,
            model=payload.model if payload.model else None
        )
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
    
    # 언어 설정: auto이면 원문과 같은 언어로 응답
    if payload.language == "auto":
        lang_instruction = "Write in the SAME language as the input text"
    elif payload.language == "ko":
        lang_instruction = "한국어로 작성"
    else:
        lang_instruction = f"Write in {payload.language}"
    
    prompt = (
        f"Shorten and condense the following text. {lang_instruction}.\n"
        "Output MUST be JSON only and match the schema.\n\n"
        "CRITICAL RULES:\n"
        "- PRESERVE ALL MARKDOWN FORMATTING exactly as-is\n"
        "- Keep the essential meaning\n"
        "- Remove redundancy\n"
        "- Make it about half the length\n"
        "- IMPORTANT: Match the language of the input text when language is 'auto'\n\n"
        f"Text to shorten:\n{content}\n\n"
        "Schema:\n"
        '{\n  "shortened": "string"\n}\n'
        "Return JSON only."
    )
    
    try:
        result = call_json_with_provider(
            prompt,
            "ShortenResult with field shortened",
            provider=payload.provider,
            api_key=payload.api_key,
            model=payload.model if payload.model else None
        )
        shortened = result.get("shortened", content)
        if truncation_warning:
            shortened = f"{shortened}\n\n{truncation_warning}"
        return ShortenResponse(shortened=shortened)
    except Exception as e:
        logger.error("Shorten failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to shorten text")


# ─────────────────────────────────────────────────────────────────────────────
# 맞춤법 교정
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/proofread", response_model=ProofreadResponse)
async def proofread_text(payload: ProofreadPayload):
    """선택된 텍스트의 맞춤법과 문법을 교정합니다. 한국어와 영어를 지원합니다."""
    content = payload.content.strip()
    
    if not content:
        raise HTTPException(status_code=400, detail="Content is empty")
    
    content, truncation_warning = process_long_text(content)
    
    prompt = (
        "You are a professional proofreader. Find and fix spelling, grammar, and punctuation errors.\n"
        "Output MUST be JSON only and match the schema.\n\n"
        "CRITICAL RULES:\n"
        "- PRESERVE ALL MARKDOWN FORMATTING exactly as-is (headers, lists, bold, italic, links, code)\n"
        "- Find ALL errors including:\n"
        "  * Spelling mistakes (e.g., '안녕하세욧' → '안녕하세요', 'teh' → 'the')\n"
        "  * Grammar errors (e.g., subject-verb agreement, tense)\n"
        "  * Punctuation (e.g., missing periods, incorrect comma usage)\n"
        "  * Spacing issues (e.g., '안녕 하세요' → '안녕하세요', 'helloworld' → 'hello world')\n"
        "- DO NOT change the meaning or style of the text\n"
        "- DO NOT translate - keep the original language\n"
        "- If text mixes Korean and English, fix each language according to its rules\n"
        "- Return EACH error as a separate item in the 'items' array\n"
        "- For each item, provide: original text, corrected text, reason, and type\n"
        "- Type must be one of: 'spelling', 'grammar', 'punctuation', 'spacing'\n"
        "- If there are no errors, return empty items array\n\n"
        f"Text to proofread:\n{content}\n\n"
        "Schema:\n"
        '{\n'
        '  "corrected": "string (the full corrected text)",\n'
        '  "items": [\n'
        '    {\n'
        '      "original": "wrong word or phrase",\n'
        '      "corrected": "correct word or phrase",\n'
        '      "reason": "brief explanation (in same language as the error)",\n'
        '      "type": "spelling|grammar|punctuation|spacing"\n'
        '    }\n'
        '  ],\n'
        '  "language_detected": "ko|en|mixed"\n'
        '}\n'
        "Return JSON only."
    )
    
    try:
        result = call_json_with_provider(
            prompt,
            "ProofreadResult with fields corrected, items, language_detected",
            provider=payload.provider,
            api_key=payload.api_key,
            model=payload.model if payload.model else None
        )
        corrected = result.get("corrected", content)
        if truncation_warning:
            corrected = f"{corrected}\n\n{truncation_warning}"
        
        # items 파싱
        raw_items = result.get("items", [])
        items = []
        for item in raw_items:
            if isinstance(item, dict) and "original" in item and "corrected" in item:
                items.append(CorrectionItem(
                    original=item.get("original", ""),
                    corrected=item.get("corrected", ""),
                    reason=item.get("reason", ""),
                    type=item.get("type", "spelling")
                ))
        
        return ProofreadResponse(
            corrected=corrected,
            items=items,
            language_detected=result.get("language_detected", "")
        )
    except Exception as e:
        logger.error("Proofread failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to proofread text")


# ─────────────────────────────────────────────────────────────────────────────
# 스트리밍
# ─────────────────────────────────────────────────────────────────────────────

def build_stream_prompt(payload: StreamPayload) -> str:
    """스트리밍용 프롬프트 생성"""
    content = payload.content
    
    preserve_rules = (
        "CRITICAL RULES:\n"
        "- Output ONLY the result text, no explanations or comments\n"
        "- PRESERVE ALL SPACES between words exactly as normal text\n"
        "- PRESERVE ALL LINE BREAKS and paragraph structure\n"
        "- PRESERVE ALL MARKDOWN FORMATTING exactly:\n"
        "  * Headers: # ## ### etc.\n"
        "  * Lists: - item or * item\n"
        "  * Checkboxes: - [ ] or - [x]\n"
        "  * Bold: **text**\n"
        "  * Italic: *text*\n"
        "  * Links: [text](url)\n"
        "  * Code: `code` or ```code```\n"
        "- Write naturally with proper spacing between words\n"
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
    
    elif payload.action == "proofread":
        return (
            f"Proofread and correct spelling, grammar, and punctuation errors in the following text.\n"
            f"{preserve_rules}"
            "- Fix spelling mistakes (e.g., '안녕하세욧' → '안녕하세요', 'teh' → 'the')\n"
            "- Fix grammatical errors while preserving meaning\n"
            "- Fix punctuation and spacing issues\n"
            "- DO NOT translate - keep the original language\n"
            "- If text mixes Korean and English, fix each language according to its rules\n\n"
            f"---INPUT---\n{content}\n---CORRECTED---\n"
        )
    
    elif payload.action == "custom":
        # 사용자 정의 프롬프트
        user_instruction = payload.custom_prompt or "Edit the text as requested"
        
        # 선택된 텍스트가 있는 경우와 없는 경우 구분
        if content.strip():
            return (
                f"You are a helpful writing assistant. Follow the user's instruction exactly.\n"
                f"{preserve_rules}\n"
                f"USER INSTRUCTION: {user_instruction}\n\n"
                f"Apply this instruction to the following text:\n"
                f"---INPUT TEXT---\n{content}\n---OUTPUT---\n"
            )
        else:
            # 선택된 텍스트 없이 새 글 생성
            return (
                f"You are a helpful writing assistant that writes high-quality content.\n"
                f"{preserve_rules}\n"
                f"IMPORTANT: Generate NEW content based on the user's request. Write naturally and creatively.\n"
                f"Match the language of the user's instruction (if Korean instruction, write in Korean).\n\n"
                f"USER REQUEST: {user_instruction}\n\n"
                f"---OUTPUT---\n"
            )
    
    else:
        raise ValueError(f"Unknown action: {payload.action}")


@router.post("/stream")
async def ai_stream(payload: StreamPayload):
    """스트리밍 방식으로 AI 텍스트 생성 (SSE)"""
    content = payload.content.strip()
    
    # custom action은 content 없이도 허용 (새 글 생성)
    if not content and payload.action != "custom":
        raise HTTPException(status_code=400, detail="Content is empty")
    
    max_chars = 8000 if payload.action == "expand" else MAX_INPUT_CHARS
    content, truncation_warning = process_long_text(content, max_chars)
    payload.content = content
    
    try:
        prompt = build_stream_prompt(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # LLM 제공자에 따른 스트리밍 함수 선택
    provider = payload.provider
    api_key = payload.api_key
    model = payload.model if payload.model else None
    
    async def event_generator():
        try:
            # Gemini 또는 Ollama 스트리밍 선택
            if provider == "gemini" and api_key:
                stream_func = gemini_client.stream_generate(prompt, api_key, model)
            else:
                stream_func = ollama_client.stream_generate(prompt, model)
            
            async for chunk in stream_func:
                escaped_chunk = chunk.replace('\n', '\\n')
                yield {"event": "message", "data": escaped_chunk}
            
            if truncation_warning:
                yield {"event": "warning", "data": truncation_warning}
            yield {"event": "done", "data": ""}
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {"event": "error", "data": str(e)}
    
    return EventSourceResponse(event_generator())


# ─────────────────────────────────────────────────────────────────────────────
# 문서 추출 (PDF/이미지 → 마크다운)
# ─────────────────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_data: str) -> tuple[str, int]:
    """
    PDF에서 텍스트 추출
    
    Args:
        pdf_data: Base64 인코딩된 PDF 데이터
    
    Returns:
        (추출된 텍스트, 페이지 수)
    """
    import base64
    import io
    
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF is required for PDF processing. Install with: pip install PyMuPDF")
    
    # Base64 디코딩
    if pdf_data.startswith("data:"):
        _, base64_content = pdf_data.split(",", 1)
    else:
        base64_content = pdf_data
    
    pdf_bytes = base64.b64decode(base64_content)
    
    # PDF 열기
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = len(doc)
    
    text_parts = []
    for page_num, page in enumerate(doc, 1):  # type: ignore[arg-type]
        text = page.get_text("text")
        if text.strip():
            text_parts.append(f"<!-- 페이지 {page_num} -->\n{text}")
    
    doc.close()
    
    return "\n\n".join(text_parts), page_count


def format_text_as_markdown(
    text: str,
    provider: str,
    api_key: str,
    language: str,
    model: Optional[str] = None
) -> str:
    """
    추출된 텍스트를 마크다운 형식으로 정리
    """
    # 언어 설정: auto이면 원문과 같은 언어로 응답
    if language == "auto":
        lang_instruction = "Write in the SAME language as the input text"
    elif language == "ko":
        lang_instruction = "한국어로 작성"
    else:
        lang_instruction = f"Write in {language}"
    
    prompt = f"""You are a document converter. Convert the following text into clean markdown format.

RULES (DO NOT output these rules, just follow them):
- Use appropriate headings (#, ##, ###)
- Convert lists to markdown lists (-, 1.)
- Convert tables to markdown tables
- Use **bold** for important content, *italic* for emphasis
- Wrap code in code blocks
- Remove unnecessary whitespace
- Output ONLY the converted markdown, nothing else
- {lang_instruction}

---INPUT TEXT---
{text}
---END INPUT---

Output the markdown below (no explanations, no instructions, just the converted content):"""
    
    if provider == "gemini" and api_key:
        return gemini_client.generate(prompt, api_key, model)
    else:
        return ollama_client.generate(prompt, model=model)


@router.post("/extract", response_model=DocumentExtractResponse)
async def extract_document(payload: DocumentExtractPayload):
    """
    PDF 또는 이미지에서 마크다운을 추출합니다.
    
    - PDF: PyMuPDF로 텍스트 추출 (실패 시 OCR) 후 LLM으로 마크다운 형식화
    - 이미지: EasyOCR로 텍스트 추출 후 LLM으로 마크다운 형식화
    """
    from .. import ocr_client
    
    file_data = payload.file_data.strip()
    
    if not file_data:
        raise HTTPException(status_code=400, detail="File data is empty")
    
    try:
        if payload.file_type == "pdf":
            # PDF 처리: 먼저 텍스트 추출 시도
            raw_text, page_count = extract_text_from_pdf(file_data)
            
            # 텍스트가 없으면 OCR로 fallback
            if not raw_text.strip():
                logger.info("PDF text extraction failed, falling back to OCR...")
                try:
                    # OCR 엔진 선택에 따라 처리
                    ocr_engine = payload.ocr_engine or "rapidocr"
                    raw_text, page_count = ocr_client.extract_text_from_pdf_images(
                        file_data,
                        engine=cast(Literal["gemini", "rapidocr"], ocr_engine),
                        api_key=payload.api_key if ocr_engine == "gemini" else None,
                        gemini_model=payload.model if ocr_engine == "gemini" else None,
                    )
                except ImportError as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"OCR 라이브러리가 필요합니다: {str(e)}"
                    )
                except ValueError as e:
                    raise HTTPException(
                        status_code=400,
                        detail=str(e)
                    )
                
                if not raw_text.strip():
                    raise HTTPException(
                        status_code=400, 
                        detail="PDF에서 텍스트를 추출할 수 없습니다."
                    )
            
            # 텍스트가 너무 길면 잘라내기
            if len(raw_text) > MAX_INPUT_CHARS * 2:
                raw_text = raw_text[:MAX_INPUT_CHARS * 2]
                logger.warning(f"PDF text truncated to {MAX_INPUT_CHARS * 2} chars")
            
            # raw_text_only 옵션: AI 없이 텍스트만 반환
            if payload.raw_text_only:
                # 기본적인 마크다운 형식화 (줄바꿈 유지)
                markdown = raw_text.strip()
                return DocumentExtractResponse(
                    markdown=markdown,
                    page_count=page_count,
                    has_images=False
                )
            
            # LLM으로 마크다운 형식화
            markdown = format_text_as_markdown(
                raw_text,
                payload.provider,
                payload.api_key,
                payload.language,
                payload.model if payload.model else None
            )
            
            return DocumentExtractResponse(
                markdown=markdown,
                page_count=page_count,
                has_images=False
            )
        
        elif payload.file_type == "image":
            # 이미지 처리 (선택된 OCR 엔진 사용)
            try:
                ocr_engine = payload.ocr_engine or "rapidocr"
                raw_text = ocr_client.extract_text_from_base64_image(
                    file_data,
                    engine=cast(Literal["gemini", "rapidocr"], ocr_engine),
                    api_key=payload.api_key if ocr_engine == "gemini" else None,
                    gemini_model=payload.model if ocr_engine == "gemini" else None,
                )
            except ImportError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"OCR 라이브러리가 필요합니다: {str(e)}"
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=str(e)
                )
            
            if not raw_text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="이미지에서 텍스트를 추출할 수 없습니다."
                )
            
            # 텍스트가 너무 길면 잘라내기
            if len(raw_text) > MAX_INPUT_CHARS * 2:
                raw_text = raw_text[:MAX_INPUT_CHARS * 2]
                logger.warning(f"Image text truncated to {MAX_INPUT_CHARS * 2} chars")
            
            # raw_text_only 옵션: AI 없이 텍스트만 반환
            if payload.raw_text_only:
                markdown = raw_text.strip()
                return DocumentExtractResponse(
                    markdown=markdown,
                    page_count=1,
                    has_images=False
                )
            
            # LLM으로 마크다운 형식화
            markdown = format_text_as_markdown(
                raw_text,
                payload.provider,
                payload.api_key,
                payload.language,
                payload.model if payload.model else None
            )
            
            return DocumentExtractResponse(
                markdown=markdown,
                page_count=1,
                has_images=False
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 파일 유형입니다: {payload.file_type}"
            )
    
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"문서 추출에 실패했습니다: {str(e)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# OCR 엔진 관리
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/ocr/engines")
async def get_ocr_engines():
    """사용 가능한 OCR 엔진 목록 반환"""
    from .. import ocr_client
    
    return ocr_client.get_available_engines()


@router.get("/ocr/status")
async def get_ocr_status(engine: str = "rapidocr"):
    """OCR 엔진 상태 확인"""
    from .. import ocr_client
    
    info = ocr_client.get_model_info(cast(Literal["gemini", "rapidocr"], engine))
    
    return {
        "installed": info["installed"],
        "model_downloaded": info["model_downloaded"],
        "model_path": info["model_path"],
        "languages": info["languages"],
        "engine": info["engine"],
        "engine_name": info["engine_name"],
        "engine_description": info["engine_description"],
        "requires_api_key": info.get("requires_api_key", False),
    }

