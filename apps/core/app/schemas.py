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


class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="노트 요약")
    keyPoints: list[str] = Field(default_factory=list, description="핵심 포인트 목록")
    wordCount: int = Field(..., description="원본 단어 수")


class TranslatePayload(BaseModel):
    content: str = Field(..., description="번역할 텍스트")
    target_language: str = Field(default="en", description="대상 언어")


class TranslateResponse(BaseModel):
    translated: str = Field(..., description="번역된 텍스트")
    source_language: str = Field(..., description="감지된 원본 언어")


class ImprovePayload(BaseModel):
    content: str = Field(..., description="개선할 텍스트")
    style: str = Field(default="professional", description="스타일")
    language: str = Field(default="ko", description="응답 언어")


class ImproveResponse(BaseModel):
    improved: str = Field(..., description="개선된 텍스트")
    changes: list[str] = Field(default_factory=list, description="주요 변경 사항")


class ExpandPayload(BaseModel):
    content: str = Field(..., description="확장할 텍스트")
    language: str = Field(default="ko", description="응답 언어")


class ExpandResponse(BaseModel):
    expanded: str = Field(..., description="확장된 텍스트")


class ShortenPayload(BaseModel):
    content: str = Field(..., description="축약할 텍스트")
    language: str = Field(default="ko", description="응답 언어")


class ShortenResponse(BaseModel):
    shortened: str = Field(..., description="축약된 텍스트")


class StreamPayload(BaseModel):
    content: str = Field(..., description="처리할 텍스트")
    action: str = Field(..., description="작업 종류 (translate, improve, expand, shorten, summarize)")
    target_language: str = Field(default="en", description="번역 대상 언어")
    style: str = Field(default="professional", description="개선 스타일")
    language: str = Field(default="ko", description="응답 언어")
