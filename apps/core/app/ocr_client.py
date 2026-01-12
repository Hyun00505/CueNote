"""
CueNote Core - OCR 클라이언트
사용자 선택 가능한 OCR 엔진:
- Gemini Vision: 클라우드 기반, 최고 정확도 (API 키 필요)
- RapidOCR: 로컬, 무료, ONNX Runtime 기반
"""
import base64
import io
import logging
from typing import Optional, Tuple, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    import fitz

logger = logging.getLogger("cuenote.core")

# OCR 엔진 타입
OCREngine = Literal["gemini", "rapidocr"]

# RapidOCR 인스턴스 (Lazy Loading)
_rapidocr_engine = None


def _get_rapidocr_engine():
    """RapidOCR 엔진 가져오기 (Lazy Loading)"""
    global _rapidocr_engine
    if _rapidocr_engine is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            _rapidocr_engine = RapidOCR()
            logger.info("RapidOCR engine initialized")
        except ImportError:
            logger.error("RapidOCR not installed. Run: pip install rapidocr-onnxruntime")
            raise ImportError("RapidOCR가 설치되어 있지 않습니다.")
    return _rapidocr_engine


# ─────────────────────────────────────────────────────────────────────────────
# OCR 엔진 정보
# ─────────────────────────────────────────────────────────────────────────────

def get_available_engines() -> list[dict]:
    """사용 가능한 OCR 엔진 목록 반환"""
    engines = []
    
    # Gemini Vision (항상 표시, API 키 필요)
    engines.append({
        "id": "gemini",
        "name": "Gemini Vision",
        "description": "Google AI 기반, 최고 정확도 (API 키 필요, 무료 티어 있음)",
        "available": True,  # API 키는 런타임에 확인
        "requires_api_key": True,
        "accuracy": "최상",
        "speed": "보통",
        "languages": ["한국어", "영어", "일본어", "중국어", "다국어"],
    })
    
    # RapidOCR
    try:
        from rapidocr_onnxruntime import RapidOCR
        rapidocr_available = True
    except ImportError:
        rapidocr_available = False
    
    engines.append({
        "id": "rapidocr",
        "name": "RapidOCR",
        "description": "로컬 OCR, 무료, 인터넷 불필요",
        "available": rapidocr_available,
        "requires_api_key": False,
        "accuracy": "보통",
        "speed": "빠름",
        "languages": ["한국어", "영어", "일본어", "중국어"],
    })
    
    return engines


def get_model_info(engine: OCREngine = "rapidocr") -> dict:
    """OCR 엔진 정보 반환"""
    engines = get_available_engines()
    
    for e in engines:
        if e["id"] == engine:
            return {
                "installed": e["available"],
                "model_downloaded": e["available"],
                "model_path": "",
                "languages": e["languages"],
                "engine": e["id"],
                "engine_name": e["name"],
                "engine_description": e["description"],
                "requires_api_key": e.get("requires_api_key", False),
            }
    
    return {
        "installed": False,
        "model_downloaded": False,
        "model_path": "",
        "languages": [],
        "engine": "none",
        "engine_name": "없음",
        "engine_description": "OCR을 사용할 수 없습니다",
        "requires_api_key": False,
    }


def is_ocr_available(engine: OCREngine = "rapidocr") -> bool:
    """OCR 기능 사용 가능 여부 확인"""
    if engine == "gemini":
        return True  # API 키는 호출 시 확인
    elif engine == "rapidocr":
        try:
            from rapidocr_onnxruntime import RapidOCR
            return True
        except ImportError:
            return False
    return False


# ─────────────────────────────────────────────────────────────────────────────
# RapidOCR 구현
# ─────────────────────────────────────────────────────────────────────────────

def _extract_with_rapidocr(image_bytes: bytes, languages: Optional[list[str]] = None) -> str:
    """RapidOCR로 텍스트 추출"""
    from PIL import Image
    import numpy as np
    
    # 이미지 열기
    image = Image.open(io.BytesIO(image_bytes))
    
    # RGB로 변환
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # numpy 배열로 변환
    img_array = np.array(image)
    
    # OCR 실행
    ocr = _get_rapidocr_engine()
    result, elapse = ocr(img_array)
    
    if result is None:
        return ""
    
    # 결과에서 텍스트만 추출
    text_lines = []
    for item in result:
        if len(item) >= 2:
            text_lines.append(item[1])
    
    return '\n'.join(text_lines)


# ─────────────────────────────────────────────────────────────────────────────
# Gemini Vision 구현
# ─────────────────────────────────────────────────────────────────────────────

def _extract_with_gemini(
    image_data: str,
    api_key: str,
    model: Optional[str] = None,
    language: str = "ko"
) -> str:
    """Gemini Vision API로 텍스트 추출"""
    try:
        from .gemini_client import extract_text_from_image
    except ImportError:
        from gemini_client import extract_text_from_image
    
    return extract_text_from_image(image_data, api_key, language, model)


# ─────────────────────────────────────────────────────────────────────────────
# 통합 OCR 인터페이스
# ─────────────────────────────────────────────────────────────────────────────

def extract_text_from_image_bytes(
    image_bytes: bytes,
    languages: Optional[list[str]] = None,
    engine: OCREngine = "rapidocr",
    api_key: Optional[str] = None,
    gemini_model: Optional[str] = None,
) -> str:
    """
    이미지 바이트에서 텍스트 추출
    
    Args:
        image_bytes: 이미지 바이너리 데이터
        languages: OCR 언어 목록
        engine: OCR 엔진 ("gemini" 또는 "rapidocr")
        api_key: Gemini API 키 (engine="gemini"일 때 필요)
        gemini_model: Gemini 모델 (선택)
    
    Returns:
        추출된 텍스트
    """
    if engine == "gemini":
        if not api_key:
            raise ValueError("Gemini Vision을 사용하려면 API 키가 필요합니다.")
        
        # 바이트를 base64로 변환
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        image_data = f"data:image/png;base64,{base64_data}"
        
        lang = "ko" if not languages else languages[0]
        return _extract_with_gemini(image_data, api_key, gemini_model, lang)
    
    elif engine == "rapidocr":
        return _extract_with_rapidocr(image_bytes, languages)
    
    else:
        raise ValueError(f"지원하지 않는 OCR 엔진: {engine}")


def extract_text_from_base64_image(
    image_data: str,
    languages: Optional[list[str]] = None,
    engine: OCREngine = "rapidocr",
    api_key: Optional[str] = None,
    gemini_model: Optional[str] = None,
) -> str:
    """
    Base64 인코딩된 이미지에서 텍스트 추출
    
    Args:
        image_data: Base64 인코딩된 이미지 (data:image/...;base64,... 형식)
        languages: OCR 언어 목록
        engine: OCR 엔진
        api_key: Gemini API 키
        gemini_model: Gemini 모델
    
    Returns:
        추출된 텍스트
    """
    if engine == "gemini":
        if not api_key:
            raise ValueError("Gemini Vision을 사용하려면 API 키가 필요합니다.")
        
        lang = "ko" if not languages else languages[0]
        return _extract_with_gemini(image_data, api_key, gemini_model, lang)
    
    elif engine == "rapidocr":
        # Base64 디코딩
        if image_data.startswith("data:"):
            _, base64_content = image_data.split(",", 1)
        else:
            base64_content = image_data
        
        image_bytes = base64.b64decode(base64_content)
        return _extract_with_rapidocr(image_bytes, languages)
    
    else:
        raise ValueError(f"지원하지 않는 OCR 엔진: {engine}")


def extract_text_from_pdf_images(
    pdf_data: str,
    languages: Optional[list[str]] = None,
    dpi: int = 200,
    engine: OCREngine = "rapidocr",
    api_key: Optional[str] = None,
    gemini_model: Optional[str] = None,
) -> Tuple[str, int]:
    """
    PDF의 각 페이지를 이미지로 변환 후 OCR 수행
    
    Args:
        pdf_data: Base64 인코딩된 PDF 데이터
        languages: OCR 언어 목록
        dpi: 이미지 변환 해상도
        engine: OCR 엔진
        api_key: Gemini API 키
        gemini_model: Gemini 모델
    
    Returns:
        (추출된 텍스트, 페이지 수)
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF가 필요합니다. pip install PyMuPDF")
    
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
        # 페이지를 이미지로 변환
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        image_bytes = pix.tobytes("png")
        
        # OCR 수행
        page_text = extract_text_from_image_bytes(
            image_bytes, languages, engine, api_key, gemini_model
        )
        
        if page_text.strip():
            text_parts.append(f"<!-- 페이지 {page_num} -->\n{page_text}")
        
        logger.info(f"OCR completed for page {page_num}/{page_count}")
    
    doc.close()
    
    return '\n\n'.join(text_parts), page_count


def extract_text_with_layout(
    image_data: str,
    languages: Optional[list[str]] = None,
    engine: OCREngine = "rapidocr",
    api_key: Optional[str] = None,
    gemini_model: Optional[str] = None,
) -> dict:
    """
    이미지에서 텍스트와 레이아웃 정보 추출
    
    Returns:
        {"text": str, "blocks": list}
    """
    if engine == "gemini":
        # Gemini는 레이아웃 정보를 별도로 제공하지 않음
        text = extract_text_from_base64_image(
            image_data, languages, engine, api_key, gemini_model
        )
        return {"text": text, "blocks": [{"text": text, "confidence": 0.95, "bbox": []}]}
    
    elif engine == "rapidocr":
        from PIL import Image
        import numpy as np
        
        # Base64 디코딩
        if image_data.startswith("data:"):
            _, base64_content = image_data.split(",", 1)
        else:
            base64_content = image_data
        
        image_bytes = base64.b64decode(base64_content)
        image = Image.open(io.BytesIO(image_bytes))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        img_array = np.array(image)
        
        # OCR 실행
        ocr = _get_rapidocr_engine()
        result, elapse = ocr(img_array)
        
        if result is None:
            return {"text": "", "blocks": []}
        
        # 결과 파싱
        blocks = []
        text_lines = []
        
        for item in result:
            if len(item) >= 3:
                box, text, confidence = item[0], item[1], item[2]
                text_lines.append(text)
                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": box
                })
        
        return {"text": '\n'.join(text_lines), "blocks": blocks}
    
    return {"text": "", "blocks": []}


# ─────────────────────────────────────────────────────────────────────────────
# 호환성을 위한 함수들
# ─────────────────────────────────────────────────────────────────────────────

def is_model_downloaded(languages: Optional[list[str]] = None, use_cache: bool = True) -> bool:
    """OCR 모델이 준비되었는지 확인 (RapidOCR 기준)"""
    try:
        from rapidocr_onnxruntime import RapidOCR
        return True
    except ImportError:
        return False


def download_model(languages: Optional[list[str]] = None, progress_callback=None) -> bool:
    """OCR 모델 다운로드 (RapidOCR은 자동 다운로드)"""
    if progress_callback:
        progress_callback("RapidOCR이 이미 사용 가능합니다.")
    return is_model_downloaded()


def invalidate_model_cache():
    """모델 캐시 무효화"""
    global _rapidocr_engine
    _rapidocr_engine = None
