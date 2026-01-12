"""
CueNote Core - Pydantic 스키마
"""
from typing import Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Vault 스키마
# ─────────────────────────────────────────────────────────────────────────────

class VaultOpenPayload(BaseModel):
    path: Optional[str] = None


class VaultFilePayload(BaseModel):
    path: str
    content: str


class DeleteFilePayload(BaseModel):
    path: str


class RenameFilePayload(BaseModel):
    old_path: str
    new_path: str


class RestoreFilePayload(BaseModel):
    filename: str


class PermanentDeletePayload(BaseModel):
    filename: str


class ImageUploadPayload(BaseModel):
    """Base64 이미지 업로드"""
    data: str  # Base64 인코딩된 이미지 데이터 (data:image/png;base64,... 형식)
    filename: Optional[str] = None  # 원본 파일명 (선택)
    note_name: Optional[str] = None  # 현재 편집 중인 노트 이름 (이미지 파일명에 사용)


# ─────────────────────────────────────────────────────────────────────────────
# TODO 스키마
# ─────────────────────────────────────────────────────────────────────────────

class TodoItem(BaseModel):
    id: str
    text: str
    checked: bool
    notePath: str
    lineNo: int


class TodayPlan(BaseModel):
    tldr: str
    overdue: list[TodoItem]
    dueSoon: list[TodoItem]
    nextActions: list[str]
    quickWins: list[str]


# ─────────────────────────────────────────────────────────────────────────────
# AI 스키마
# ─────────────────────────────────────────────────────────────────────────────

class SummarizePayload(BaseModel):
    content: str = Field(..., description="노트 내용 (마크다운)")
    language: str = Field(default="ko", description="요약 언어 (ko, en 등)")
    # LLM 제공자 설정
    provider: str = Field(default="ollama", description="LLM 제공자 (ollama, gemini)")
    api_key: str = Field(default="", description="Gemini API 키 (gemini 선택 시)")
    model: str = Field(default="", description="사용할 모델명")


class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="노트 요약")
    keyPoints: list[str] = Field(default_factory=list, description="핵심 포인트 목록")
    wordCount: int = Field(..., description="원본 단어 수")


class TranslatePayload(BaseModel):
    content: str = Field(..., description="번역할 텍스트")
    target_language: str = Field(default="en", description="대상 언어")
    # LLM 제공자 설정
    provider: str = Field(default="ollama", description="LLM 제공자 (ollama, gemini)")
    api_key: str = Field(default="", description="Gemini API 키 (gemini 선택 시)")
    model: str = Field(default="", description="사용할 모델명")


class TranslateResponse(BaseModel):
    translated: str = Field(..., description="번역된 텍스트")
    source_language: str = Field(..., description="감지된 원본 언어")


class ImprovePayload(BaseModel):
    content: str = Field(..., description="개선할 텍스트")
    style: str = Field(default="professional", description="스타일")
    language: str = Field(default="ko", description="응답 언어")
    # LLM 제공자 설정
    provider: str = Field(default="ollama", description="LLM 제공자 (ollama, gemini)")
    api_key: str = Field(default="", description="Gemini API 키 (gemini 선택 시)")
    model: str = Field(default="", description="사용할 모델명")


class ImproveResponse(BaseModel):
    improved: str = Field(..., description="개선된 텍스트")
    changes: list[str] = Field(default_factory=list, description="주요 변경 사항")


class ExpandPayload(BaseModel):
    content: str = Field(..., description="확장할 텍스트")
    language: str = Field(default="ko", description="응답 언어")
    # LLM 제공자 설정
    provider: str = Field(default="ollama", description="LLM 제공자 (ollama, gemini)")
    api_key: str = Field(default="", description="Gemini API 키 (gemini 선택 시)")
    model: str = Field(default="", description="사용할 모델명")


class ExpandResponse(BaseModel):
    expanded: str = Field(..., description="확장된 텍스트")


class ShortenPayload(BaseModel):
    content: str = Field(..., description="축약할 텍스트")
    language: str = Field(default="ko", description="응답 언어")
    # LLM 제공자 설정
    provider: str = Field(default="ollama", description="LLM 제공자 (ollama, gemini)")
    api_key: str = Field(default="", description="Gemini API 키 (gemini 선택 시)")
    model: str = Field(default="", description="사용할 모델명")


class ShortenResponse(BaseModel):
    shortened: str = Field(..., description="축약된 텍스트")


class ProofreadPayload(BaseModel):
    content: str = Field(..., description="맞춤법 검사할 텍스트")
    language: str = Field(default="auto", description="언어 (auto: 자동 감지, ko, en)")
    # LLM 제공자 설정
    provider: str = Field(default="ollama", description="LLM 제공자 (ollama, gemini)")
    api_key: str = Field(default="", description="Gemini API 키 (gemini 선택 시)")
    model: str = Field(default="", description="사용할 모델명")


class CorrectionItem(BaseModel):
    """개별 맞춤법 수정 항목"""
    original: str = Field(..., description="원본 텍스트")
    corrected: str = Field(..., description="수정된 텍스트")
    reason: str = Field(default="", description="수정 이유")
    type: str = Field(default="spelling", description="오류 유형 (spelling, grammar, punctuation, spacing)")


class ProofreadResponse(BaseModel):
    corrected: str = Field(..., description="전체 교정된 텍스트")
    items: list[CorrectionItem] = Field(default_factory=list, description="개별 수정 항목 목록")
    language_detected: str = Field(default="", description="감지된 언어")


class StreamPayload(BaseModel):
    content: str = Field(..., description="처리할 텍스트")
    action: str = Field(..., description="작업 종류 (translate, improve, expand, shorten, summarize, proofread, custom)")
    target_language: str = Field(default="en", description="번역 대상 언어")
    style: str = Field(default="professional", description="개선 스타일")
    language: str = Field(default="ko", description="응답 언어")
    custom_prompt: str = Field(default="", description="사용자 정의 프롬프트 (custom action 시 사용)")
    # LLM 제공자 설정
    provider: str = Field(default="ollama", description="LLM 제공자 (ollama, gemini)")
    api_key: str = Field(default="", description="Gemini API 키 (gemini 선택 시)")
    model: str = Field(default="", description="사용할 모델명")


# ─────────────────────────────────────────────────────────────────────────────
# LLM 설정 스키마
# ─────────────────────────────────────────────────────────────────────────────

class LLMProvider(BaseModel):
    id: str = Field(..., description="제공자 ID (ollama, gemini)")
    name: str = Field(..., description="표시 이름")
    requiresApiKey: bool = Field(..., description="API 키 필요 여부")


class LLMModel(BaseModel):
    id: str = Field(..., description="모델 ID")
    name: str = Field(..., description="모델 표시 이름")
    description: str = Field(default="", description="모델 설명")
    free: bool = Field(default=True, description="무료 여부")
    context_window: int = Field(default=4096, description="컨텍스트 윈도우 크기")


class LLMSettingsPayload(BaseModel):
    provider: str = Field(default="ollama", description="LLM 제공자")
    api_key: str = Field(default="", description="API 키")
    model: str = Field(default="", description="선택한 모델")


class ValidateApiKeyPayload(BaseModel):
    api_key: str = Field(..., description="검증할 API 키")


# ─────────────────────────────────────────────────────────────────────────────
# 문서 추출 스키마 (PDF/이미지 → 마크다운)
# ─────────────────────────────────────────────────────────────────────────────

class DocumentExtractPayload(BaseModel):
    """PDF 또는 이미지에서 마크다운 추출"""
    file_data: str = Field(..., description="Base64 인코딩된 파일 데이터 (data:...;base64,... 형식)")
    file_type: str = Field(..., description="파일 유형 (pdf, image)")
    language: str = Field(default="ko", description="출력 언어")
    raw_text_only: bool = Field(default=False, description="AI 없이 텍스트만 추출")
    # LLM 제공자 설정
    provider: str = Field(default="gemini", description="LLM 제공자 (gemini 권장)")
    api_key: str = Field(default="", description="Gemini API 키")
    model: str = Field(default="", description="사용할 모델명")
    # OCR 엔진 설정
    ocr_engine: str = Field(default="rapidocr", description="OCR 엔진 (gemini, rapidocr)")


class DocumentExtractResponse(BaseModel):
    """문서 추출 결과"""
    markdown: str = Field(..., description="추출된 마크다운 텍스트")
    page_count: int = Field(default=1, description="페이지 수 (PDF의 경우)")
    has_images: bool = Field(default=False, description="이미지 포함 여부")


# ─────────────────────────────────────────────────────────────────────────────
# OCR 모델 스키마
# ─────────────────────────────────────────────────────────────────────────────

class OCRModelStatus(BaseModel):
    """OCR 모델 상태 (플랫폼별 자동 선택)"""
    installed: bool = Field(..., description="OCR 사용 가능 여부")
    model_downloaded: bool = Field(..., description="OCR 준비 완료 여부")
    model_path: str = Field(default="", description="모델/엔진 경로")
    languages: list[str] = Field(..., description="지원 언어 목록")
    downloading: bool = Field(default=False, description="다운로드 진행 중 여부")
    engine: str = Field(default="", description="OCR 엔진 (windows, macos, tesseract)")
    engine_name: str = Field(default="", description="OCR 엔진 이름")
    engine_description: str = Field(default="", description="OCR 엔진 설명")
    platform: str = Field(default="", description="현재 플랫폼")


class OCRDownloadResponse(BaseModel):
    """OCR 모델 다운로드 응답"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="결과 메시지")


# ─────────────────────────────────────────────────────────────────────────────
# 일정(Schedule) 스키마
# ─────────────────────────────────────────────────────────────────────────────

class ScheduleItem(BaseModel):
    """일정 항목"""
    id: str = Field(..., description="일정 고유 ID")
    title: str = Field(..., description="일정 제목")
    description: str = Field(default="", description="일정 설명")
    date: str = Field(..., description="일정 날짜 (YYYY-MM-DD)")
    startTime: str = Field(default="", description="시작 시간 (HH:MM)")
    endTime: str = Field(default="", description="종료 시간 (HH:MM)")
    color: str = Field(default="#c9a76c", description="일정 색상")
    completed: bool = Field(default=False, description="완료 여부")
    createdAt: str = Field(default="", description="생성 시간")
    updatedAt: str = Field(default="", description="수정 시간")


class ScheduleCreatePayload(BaseModel):
    """일정 생성 요청"""
    title: str = Field(..., description="일정 제목")
    description: str = Field(default="", description="일정 설명")
    date: str = Field(..., description="일정 날짜 (YYYY-MM-DD)")
    startTime: str = Field(default="", description="시작 시간 (HH:MM)")
    endTime: str = Field(default="", description="종료 시간 (HH:MM)")
    color: str = Field(default="#c9a76c", description="일정 색상")


class ScheduleUpdatePayload(BaseModel):
    """일정 수정 요청"""
    title: Optional[str] = Field(default=None, description="일정 제목")
    description: Optional[str] = Field(default=None, description="일정 설명")
    date: Optional[str] = Field(default=None, description="일정 날짜 (YYYY-MM-DD)")
    startTime: Optional[str] = Field(default=None, description="시작 시간 (HH:MM)")
    endTime: Optional[str] = Field(default=None, description="종료 시간 (HH:MM)")
    color: Optional[str] = Field(default=None, description="일정 색상")
    completed: Optional[bool] = Field(default=None, description="완료 여부")


class ScheduleCountByDate(BaseModel):
    """날짜별 일정 개수"""
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    count: int = Field(..., description="일정 개수")
    completedCount: int = Field(default=0, description="완료된 일정 개수")


class AIExtractSchedulePayload(BaseModel):
    """AI 일정 추출 요청"""
    content: str = Field(..., description="노트 내용")
    language: str = Field(default="ko", description="언어")
    provider: str = Field(default="ollama", description="LLM 제공자")
    api_key: str = Field(default="", description="API 키")
    model: str = Field(default="", description="모델명")


class AIExtractScheduleResponse(BaseModel):
    """AI 일정 추출 응답"""
    schedules: list[ScheduleItem] = Field(default_factory=list, description="추출된 일정 목록")
    confidence: float = Field(default=0.0, description="신뢰도")