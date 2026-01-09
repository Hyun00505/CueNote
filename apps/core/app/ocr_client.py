"""
CueNote Core - OCR 클라이언트
EasyOCR을 사용한 이미지/PDF 텍스트 추출
"""
import base64
import io
import logging
from typing import Optional

logger = logging.getLogger("cuenote.core")

# EasyOCR 리더 (lazy loading)
_ocr_reader = None


def get_ocr_reader(languages: list[str] = None):
    """
    EasyOCR 리더 인스턴스 반환 (싱글톤)
    첫 호출 시 모델 다운로드가 진행될 수 있음
    """
    global _ocr_reader
    
    if languages is None:
        languages = ['ko', 'en']  # 기본: 한국어 + 영어
    
    if _ocr_reader is None:
        try:
            import easyocr
            logger.info(f"Initializing EasyOCR with languages: {languages}")
            _ocr_reader = easyocr.Reader(languages, gpu=False)  # GPU 없이 CPU 사용
            logger.info("EasyOCR initialized successfully")
        except ImportError:
            raise ImportError(
                "EasyOCR is required for OCR. Install with: pip install easyocr"
            )
    
    return _ocr_reader


def extract_text_from_image_bytes(image_bytes: bytes, languages: list[str] = None) -> str:
    """
    이미지 바이트에서 텍스트 추출
    
    Args:
        image_bytes: 이미지 바이너리 데이터
        languages: OCR 언어 목록 (기본: ['ko', 'en'])
    
    Returns:
        추출된 텍스트
    """
    reader = get_ocr_reader(languages)
    
    # EasyOCR은 바이트 데이터를 직접 처리할 수 있음
    results = reader.readtext(image_bytes, detail=0)  # detail=0: 텍스트만 반환
    
    # 결과 합치기
    text = '\n'.join(results)
    return text


def extract_text_from_base64_image(
    image_data: str, 
    languages: list[str] = None
) -> str:
    """
    Base64 인코딩된 이미지에서 텍스트 추출
    
    Args:
        image_data: Base64 인코딩된 이미지 (data:image/...;base64,... 형식 또는 순수 base64)
        languages: OCR 언어 목록
    
    Returns:
        추출된 텍스트
    """
    # Base64 디코딩
    if image_data.startswith("data:"):
        _, base64_content = image_data.split(",", 1)
    else:
        base64_content = image_data
    
    image_bytes = base64.b64decode(base64_content)
    
    return extract_text_from_image_bytes(image_bytes, languages)


def extract_text_from_pdf_images(
    pdf_data: str,
    languages: list[str] = None,
    dpi: int = 200
) -> tuple[str, int]:
    """
    PDF의 각 페이지를 이미지로 변환 후 OCR 수행
    텍스트 추출이 안 되는 스캔 PDF에 유용
    
    Args:
        pdf_data: Base64 인코딩된 PDF 데이터
        languages: OCR 언어 목록
        dpi: 이미지 변환 해상도
    
    Returns:
        (추출된 텍스트, 페이지 수)
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError(
            "PyMuPDF is required for PDF processing. Install with: pip install PyMuPDF"
        )
    
    # Base64 디코딩
    if pdf_data.startswith("data:"):
        _, base64_content = pdf_data.split(",", 1)
    else:
        base64_content = pdf_data
    
    pdf_bytes = base64.b64decode(base64_content)
    
    # PDF 열기
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = len(doc)
    
    reader = get_ocr_reader(languages)
    text_parts = []
    
    for page_num, page in enumerate(doc, 1):
        # 페이지를 이미지로 변환
        mat = fitz.Matrix(dpi / 72, dpi / 72)  # 72 DPI 기준 스케일
        pix = page.get_pixmap(matrix=mat)
        image_bytes = pix.tobytes("png")
        
        # OCR 수행
        results = reader.readtext(image_bytes, detail=0)
        page_text = '\n'.join(results)
        
        if page_text.strip():
            text_parts.append(f"<!-- 페이지 {page_num} -->\n{page_text}")
        
        logger.info(f"OCR completed for page {page_num}/{page_count}")
    
    doc.close()
    
    return '\n\n'.join(text_parts), page_count


def extract_text_with_layout(
    image_data: str,
    languages: list[str] = None
) -> dict:
    """
    이미지에서 텍스트와 레이아웃 정보 추출
    
    Args:
        image_data: Base64 인코딩된 이미지
        languages: OCR 언어 목록
    
    Returns:
        {
            "text": str,  # 전체 텍스트
            "blocks": list,  # 텍스트 블록 정보 [{"text": str, "confidence": float, "bbox": tuple}]
        }
    """
    # Base64 디코딩
    if image_data.startswith("data:"):
        _, base64_content = image_data.split(",", 1)
    else:
        base64_content = image_data
    
    image_bytes = base64.b64decode(base64_content)
    
    reader = get_ocr_reader(languages)
    
    # detail=1: bbox 정보 포함
    results = reader.readtext(image_bytes, detail=1)
    
    blocks = []
    texts = []
    
    for bbox, text, confidence in results:
        blocks.append({
            "text": text,
            "confidence": confidence,
            "bbox": bbox  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        })
        texts.append(text)
    
    return {
        "text": '\n'.join(texts),
        "blocks": blocks
    }


def is_ocr_available() -> bool:
    """OCR 기능 사용 가능 여부 확인"""
    try:
        import easyocr
        return True
    except ImportError:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# 손글씨 OCR (TrOCR - Microsoft)
# ─────────────────────────────────────────────────────────────────────────────

# TrOCR 모델 (lazy loading)
_trocr_processor = None
_trocr_model = None
TROCR_MODEL_NAME = "microsoft/trocr-base-handwritten"


def is_handwriting_ocr_available() -> bool:
    """손글씨 OCR 기능 사용 가능 여부 확인"""
    try:
        import transformers
        return True
    except ImportError:
        return False


def _get_huggingface_cache_dir() -> str:
    """Hugging Face 캐시 디렉토리 경로 반환 (OS별 처리)"""
    import os
    
    # HF_HOME 환경변수가 설정되어 있으면 사용
    hf_home = os.environ.get("HF_HOME")
    if hf_home:
        return os.path.join(hf_home, "hub")
    
    # TRANSFORMERS_CACHE 환경변수 확인
    transformers_cache = os.environ.get("TRANSFORMERS_CACHE")
    if transformers_cache:
        return transformers_cache
    
    # 기본 경로 (Windows/Linux/Mac 모두 동일)
    home = os.path.expanduser("~")
    return os.path.join(home, ".cache", "huggingface", "hub")


# 손글씨 모델 다운로드 상태 캐시
_handwriting_model_cache = None
_handwriting_cache_time = 0


def is_handwriting_model_downloaded(use_cache: bool = True) -> bool:
    """손글씨 OCR 모델이 다운로드되어 있는지 확인"""
    import time
    global _handwriting_model_cache, _handwriting_cache_time
    
    # 캐시가 유효하면 캐시된 값 반환
    if use_cache and _handwriting_model_cache is not None:
        if time.time() - _handwriting_cache_time < _MODEL_CACHE_DURATION:
            return _handwriting_model_cache
    
    # 최대 3번 재시도
    for attempt in range(3):
        try:
            import os
            
            # Hugging Face 캐시 경로 확인
            cache_dir = _get_huggingface_cache_dir()
            logger.info(f"Checking HuggingFace cache dir: {cache_dir}")
            
            if not os.path.exists(cache_dir):
                logger.info(f"Cache directory does not exist: {cache_dir}")
                if attempt < 2:
                    time.sleep(0.1)
                    continue
                _handwriting_model_cache = False
                _handwriting_cache_time = time.time()
                return False
            
            # 모델 폴더 확인 (models--microsoft--trocr-base-handwritten)
            model_folder_name = f"models--{TROCR_MODEL_NAME.replace('/', '--')}"
            model_path = os.path.join(cache_dir, model_folder_name)
            
            logger.info(f"Looking for model at: {model_path}")
            
            if os.path.exists(model_path):
                # snapshots 폴더에 실제 모델 파일이 있는지 확인
                snapshots_path = os.path.join(model_path, "snapshots")
                if os.path.exists(snapshots_path):
                    snapshots = os.listdir(snapshots_path)
                    logger.info(f"Found snapshots: {snapshots}")
                    if snapshots:
                        # 스냅샷 폴더 내에 실제 파일이 있는지 확인
                        for snapshot in snapshots:
                            snapshot_full_path = os.path.join(snapshots_path, snapshot)
                            if os.path.isdir(snapshot_full_path):
                                files = os.listdir(snapshot_full_path)
                                logger.info(f"Snapshot {snapshot} files: {files}")
                                # model.safetensors 또는 pytorch_model.bin이 있으면 다운로드 완료
                                if any(f.endswith(('.safetensors', '.bin')) for f in files):
                                    logger.info("Handwriting model found!")
                                    _handwriting_model_cache = True
                                    _handwriting_cache_time = time.time()
                                    return True
            
            logger.info("Handwriting model not found")
            if attempt < 2:
                time.sleep(0.1)
                continue
            _handwriting_model_cache = False
            _handwriting_cache_time = time.time()
            return False
            
        except Exception as e:
            logger.warning(f"Error checking handwriting model status (attempt {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(0.1)
                continue
            _handwriting_model_cache = False
            _handwriting_cache_time = time.time()
            return False
    
    return False


def invalidate_handwriting_model_cache():
    """손글씨 모델 캐시 무효화"""
    global _handwriting_model_cache, _handwriting_cache_time
    _handwriting_model_cache = None
    _handwriting_cache_time = 0


def get_handwriting_model_info() -> dict:
    """손글씨 OCR 모델 정보 반환"""
    import os
    
    cache_dir = _get_huggingface_cache_dir()
    model_folder_name = f"models--{TROCR_MODEL_NAME.replace('/', '--')}"
    model_path = os.path.join(cache_dir, model_folder_name)
    
    # _trocr_model이 이미 로드되어 있으면 다운로드된 것
    global _trocr_model
    model_ready = _trocr_model is not None or is_handwriting_model_downloaded()
    
    logger.info(f"Handwriting model info - installed: {is_handwriting_ocr_available()}, downloaded: {model_ready}, path: {model_path}")
    
    return {
        "installed": is_handwriting_ocr_available(),
        "model_downloaded": model_ready,
        "model_name": TROCR_MODEL_NAME,
        "model_path": model_path,
    }


def download_handwriting_model(progress_callback=None) -> bool:
    """손글씨 OCR 모델 다운로드"""
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        
        logger.info(f"Downloading handwriting OCR model: {TROCR_MODEL_NAME}")
        
        if progress_callback:
            progress_callback("손글씨 모델 다운로드 시작...")
        
        # Processor 다운로드
        if progress_callback:
            progress_callback("Processor 다운로드 중...")
        processor = TrOCRProcessor.from_pretrained(TROCR_MODEL_NAME)
        
        # 모델 다운로드
        if progress_callback:
            progress_callback("모델 다운로드 중... (약 1GB)")
        model = VisionEncoderDecoderModel.from_pretrained(TROCR_MODEL_NAME)
        
        # 전역 변수에 저장
        global _trocr_processor, _trocr_model
        _trocr_processor = processor
        _trocr_model = model
        
        if progress_callback:
            progress_callback("손글씨 모델 다운로드 완료!")
        
        logger.info("Handwriting OCR model download completed")
        
        # 캐시 무효화 (새로 다운로드했으므로 상태 갱신 필요)
        invalidate_handwriting_model_cache()
        
        return True
        
    except Exception as e:
        logger.error(f"Handwriting model download failed: {e}")
        if progress_callback:
            progress_callback(f"다운로드 실패: {str(e)}")
        return False


def get_handwriting_ocr():
    """손글씨 OCR 모델 로드 (lazy loading)"""
    global _trocr_processor, _trocr_model
    
    if _trocr_processor is None or _trocr_model is None:
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            
            logger.info(f"Loading handwriting OCR model: {TROCR_MODEL_NAME}")
            _trocr_processor = TrOCRProcessor.from_pretrained(TROCR_MODEL_NAME)
            _trocr_model = VisionEncoderDecoderModel.from_pretrained(TROCR_MODEL_NAME)
            logger.info("Handwriting OCR model loaded")
            
        except Exception as e:
            logger.error(f"Failed to load handwriting OCR model: {e}")
            raise
    
    return _trocr_processor, _trocr_model


def extract_handwriting_from_image(image_data: str) -> str:
    """
    이미지에서 손글씨 텍스트 추출 (TrOCR 사용)
    
    Args:
        image_data: Base64 인코딩된 이미지 데이터
    
    Returns:
        추출된 텍스트
    """
    import base64
    from PIL import Image
    import io
    
    # Base64 디코딩
    if image_data.startswith("data:"):
        _, base64_content = image_data.split(",", 1)
    else:
        base64_content = image_data
    
    image_bytes = base64.b64decode(base64_content)
    
    # PIL Image로 변환
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # 모델 로드
    processor, model = get_handwriting_ocr()
    
    # 이미지 전처리
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    
    # 텍스트 생성
    generated_ids = model.generate(pixel_values, max_length=256)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return generated_text


def extract_handwriting_from_image_bytes(image_bytes: bytes) -> str:
    """이미지 바이트에서 손글씨 텍스트 추출"""
    from PIL import Image
    import io
    
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    processor, model = get_handwriting_ocr()
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values, max_length=256)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return generated_text


# 모델 다운로드 상태 캐시
_model_downloaded_cache = None
_model_cache_time = 0
_MODEL_CACHE_DURATION = 60  # 60초간 캐시 유지


def is_model_downloaded(languages: list[str] = None, use_cache: bool = True) -> bool:
    """
    OCR 모델이 다운로드되어 있는지 확인
    
    Args:
        languages: 확인할 언어 목록 (기본: ['ko', 'en'])
        use_cache: 캐시 사용 여부
    
    Returns:
        모델 다운로드 여부
    """
    import time
    global _model_downloaded_cache, _model_cache_time
    
    # 캐시가 유효하면 캐시된 값 반환
    if use_cache and _model_downloaded_cache is not None:
        if time.time() - _model_cache_time < _MODEL_CACHE_DURATION:
            return _model_downloaded_cache
    
    if languages is None:
        languages = ['ko', 'en']
    
    # 최대 3번 재시도
    for attempt in range(3):
        try:
            import os
            
            # EasyOCR 모델 저장 경로
            home = os.path.expanduser("~")
            model_dir = os.path.join(home, ".EasyOCR", "model")
            
            if not os.path.exists(model_dir):
                if attempt < 2:
                    time.sleep(0.1)  # 짧은 대기 후 재시도
                    continue
                _model_downloaded_cache = False
                _model_cache_time = time.time()
                return False
            
            # 모델 디렉토리에 있는 파일들 확인
            model_files = os.listdir(model_dir)
            logger.info(f"Model directory: {model_dir}")
            logger.info(f"Found model files: {model_files}")
            
            # Detection 모델 확인 (craft로 시작하는 파일)
            has_detection = any(f.startswith('craft') and f.endswith('.pth') for f in model_files)
            
            if not has_detection:
                logger.info("Detection model not found")
                if attempt < 2:
                    time.sleep(0.1)
                    continue
                _model_downloaded_cache = False
                _model_cache_time = time.time()
                return False
            
            # 한국어 모델 확인 (korean 포함된 파일)
            if 'ko' in languages:
                has_korean = any('korean' in f.lower() and f.endswith('.pth') for f in model_files)
                if not has_korean:
                    logger.info("Korean model not found")
                    if attempt < 2:
                        time.sleep(0.1)
                        continue
                    _model_downloaded_cache = False
                    _model_cache_time = time.time()
                    return False
            
            # 영어 모델 확인 (latin 또는 english 포함된 파일)
            if 'en' in languages:
                has_english = any(
                    ('latin' in f.lower() or 'english' in f.lower()) and f.endswith('.pth') 
                    for f in model_files
                )
                if not has_english:
                    logger.info("English model not found")
                    if attempt < 2:
                        time.sleep(0.1)
                        continue
                    _model_downloaded_cache = False
                    _model_cache_time = time.time()
                    return False
            
            logger.info("All required models found")
            _model_downloaded_cache = True
            _model_cache_time = time.time()
            return True
            
        except Exception as e:
            logger.warning(f"Error checking model status (attempt {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(0.1)
                continue
            _model_downloaded_cache = False
            _model_cache_time = time.time()
            return False
    
    return False


def invalidate_model_cache():
    """모델 캐시 무효화 (다운로드 후 호출)"""
    global _model_downloaded_cache, _model_cache_time
    _model_downloaded_cache = None
    _model_cache_time = 0


def get_model_info() -> dict:
    """
    OCR 모델 정보 반환
    
    Returns:
        {
            "installed": bool,  # easyocr 설치 여부
            "model_downloaded": bool,  # 모델 다운로드 여부
            "model_path": str,  # 모델 저장 경로
            "languages": list,  # 지원 언어
            "model_files": list,  # 다운로드된 모델 파일 목록
        }
    """
    import os
    
    home = os.path.expanduser("~")
    model_dir = os.path.join(home, ".EasyOCR", "model")
    
    # 모델 파일 목록 확인
    model_files = []
    if os.path.exists(model_dir):
        model_files = [f for f in os.listdir(model_dir) if f.endswith('.pth')]
    
    # _ocr_reader가 이미 초기화되어 있으면 모델이 있는 것
    global _ocr_reader
    model_ready = _ocr_reader is not None or is_model_downloaded()
    
    return {
        "installed": is_ocr_available(),
        "model_downloaded": model_ready,
        "model_path": model_dir,
        "languages": ["ko", "en"],
        "model_files": model_files,
    }


def download_model(languages: list[str] = None, progress_callback=None) -> bool:
    """
    OCR 모델 다운로드
    
    Args:
        languages: 다운로드할 언어 목록 (기본: ['ko', 'en'])
        progress_callback: 진행 상황 콜백 함수
    
    Returns:
        성공 여부
    """
    if languages is None:
        languages = ['ko', 'en']
    
    try:
        import easyocr
        
        logger.info(f"Downloading OCR model for languages: {languages}")
        
        if progress_callback:
            progress_callback("모델 다운로드 시작...")
        
        # Reader 생성 시 모델이 자동으로 다운로드됨
        global _ocr_reader
        _ocr_reader = easyocr.Reader(languages, gpu=False, verbose=True)
        
        if progress_callback:
            progress_callback("모델 다운로드 완료!")
        
        logger.info("OCR model download completed")
        
        # 캐시 무효화 (새로 다운로드했으므로 상태 갱신 필요)
        invalidate_model_cache()
        
        return True
        
    except Exception as e:
        logger.error(f"Model download failed: {e}")
        if progress_callback:
            progress_callback(f"다운로드 실패: {str(e)}")
        return False
