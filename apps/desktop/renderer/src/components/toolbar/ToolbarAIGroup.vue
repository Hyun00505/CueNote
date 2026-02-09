<template>
  <div class="toolbar-group">
    <button class="toolbar-btn ai-btn" :class="{ loading: summarizing }" :disabled="summarizing" title="AI 요약"
      @click="handleSummarize">
      <svg v-if="!summarizing" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2">
        <path
          d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H6a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 8 6a4 4 0 0 1 4-4z" />
        <circle cx="9" cy="6" r="1" fill="currentColor" />
        <circle cx="15" cy="6" r="1" fill="currentColor" />
      </svg>
      <span v-else class="spinner" />
      <span class="ai-label">요약</span>
    </button>
    <button class="toolbar-btn ai-btn extract-btn" :class="{ loading: extracting }" :disabled="extracting"
      title="PDF/이미지 → 마크다운 변환" @click="showExtractModal = true">
      <svg v-if="!extracting" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <path d="M12 18v-6" />
        <path d="m9 15 3-3 3 3" />
      </svg>
      <span v-else class="spinner" />
      <span class="ai-label">문서 변환</span>
    </button>
    <button class="toolbar-btn ai-btn url-btn" :class="{ loading: urlExtracting }" :disabled="urlExtracting"
      title="URL → 마크다운 변환" @click="showUrlExtractModal = true">
      <svg v-if="!urlExtracting" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2">
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
      </svg>
      <span v-else class="spinner" />
      <span class="ai-label">URL 추출</span>
    </button>
    <button class="toolbar-btn ai-btn pdf-btn" :class="{ loading: exportingPdf }" :disabled="exportingPdf"
      title="PDF로 저장" @click="exportToPdf">
      <svg v-if="!exportingPdf" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <path d="M12 12v6" />
        <path d="m15 15-3 3-3-3" />
      </svg>
      <span v-else class="spinner" />
      <span class="ai-label">PDF 저장</span>
    </button>

    <!-- 문서 추출 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showExtractModal" class="extract-modal-overlay" @click.self="closeExtractModal">
          <div class="extract-modal">
            <div class="extract-modal-header">
              <h3>📄 PDF/이미지 → 마크다운 변환</h3>
              <button class="close-btn" @click="closeExtractModal">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <div class="extract-modal-content">
              <p class="extract-description">
                PDF 파일이나 이미지(스크린샷, 사진)를 업로드하면 AI가 내용을 분석하여 마크다운 문서로 변환합니다.
              </p>

              <!-- 파일 업로드 영역 -->
              <div class="extract-dropzone" :class="{ 'drag-over': isExtractDragging, 'has-file': extractFile }"
                @dragenter="isExtractDragging = true" @dragleave="isExtractDragging = false" @dragover.prevent
                @drop.prevent="handleExtractFileDrop" @click="triggerExtractFileInput">
                <input ref="extractFileInputRef" type="file" accept=".pdf,image/*" style="display: none"
                  @change="handleExtractFileSelect">
                <div v-if="!extractFile" class="dropzone-empty">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  <span>클릭하거나 파일을 드래그하세요</span>
                  <span class="upload-hint">PDF, PNG, JPG, GIF, WebP 지원</span>
                </div>
                <div v-else class="dropzone-file">
                  <div class="file-icon">
                    <svg v-if="extractFileType === 'pdf'" width="32" height="32" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" stroke-width="1.5">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                      <path d="M10 12h4" />
                      <path d="M10 16h4" />
                    </svg>
                    <svg v-else width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                      stroke-width="1.5">
                      <rect x="3" y="3" width="18" height="18" rx="2" />
                      <circle cx="8.5" cy="8.5" r="1.5" />
                      <path d="M21 15l-5-5L5 21" />
                    </svg>
                  </div>
                  <div class="file-info">
                    <span class="file-name">{{ extractFile?.name }}</span>
                    <span class="file-size">{{ formatFileSize(extractFile?.size || 0) }}</span>
                  </div>
                  <button class="remove-file-btn" title="파일 제거" @click.stop="clearExtractFile">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- OCR 엔진 상태 (사용 불가) -->
              <div v-if="ocrStatus && !ocrStatus.model_downloaded" class="ocr-model-status">
                <div class="model-status-header">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 8v4" />
                    <path d="M12 16h.01" />
                  </svg>
                  <div class="model-status-text">
                    <span class="model-title">{{ ocrStatus?.engine_name || 'OCR' }} 사용 불가</span>
                    <span class="model-desc">
                      {{ ocrStatus?.engine === 'gemini' ? 'Gemini API 키를 설정해주세요' : '설정에서 OCR 엔진을 확인해주세요' }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- OCR 안내 (모델 준비됨) -->
              <div v-else-if="extractFile" class="ocr-info ocr-ready">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                <span>OCR 준비됨 - {{ selectedOcrEngineName }}로 텍스트를 추출합니다.</span>
              </div>

              <!-- 텍스트만 가져오기 옵션 -->
              <div v-if="extractFile" class="extract-options">
                <label class="checkbox-wrapper">
                  <input v-model="rawTextOnly" type="checkbox">
                  <span class="checkbox-custom" />
                  <span class="checkbox-label">
                    📄 텍스트만 가져오기
                    <span class="option-hint">(AI 없이 빠르게)</span>
                  </span>
                </label>

                <div v-if="rawTextOnly" class="raw-text-info">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 16v-4" />
                    <path d="M12 8h.01" />
                  </svg>
                  <span>AI를 거치지 않고 OCR 결과를 그대로 가져옵니다. 마크다운 형식화가 필요하면 체크를 해제하세요.</span>
                </div>
              </div>

              <!-- 추출 결과 미리보기 -->
              <div v-if="extractResult" class="extract-result">
                <div class="result-header">
                  <span class="result-title">✨ 변환 완료</span>
                  <div class="result-meta">
                    <span v-if="extractResult.page_count > 1">{{ extractResult.page_count }}페이지</span>
                    <span v-if="extractResult.has_images">이미지 포함</span>
                  </div>
                </div>
                <div class="result-preview">
                  <pre>{{ extractResult.markdown.slice(0, 500) }}{{ extractResult.markdown.length > 500 ? '...' : '' }}</pre>
                </div>
              </div>

              <!-- 에러 메시지 -->
              <div v-if="extractError" class="extract-error">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                <span>{{ extractError }}</span>
              </div>
            </div>
            <div class="extract-modal-footer">
              <button class="btn-cancel" @click="closeExtractModal">
                취소
              </button>
              <button v-if="!extractResult" class="btn-extract" :disabled="!extractFile || extracting"
                @click="handleExtract">
                <span v-if="extracting" class="spinner" />
                <span>{{ extracting ? '변환 중...' : '변환하기' }}</span>
              </button>
              <button v-else class="btn-insert" @click="insertExtractResult">
                에디터에 삽입
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- URL 추출 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showUrlExtractModal" class="extract-modal-overlay" @click.self="closeUrlExtractModal">
          <div class="extract-modal">
            <div class="extract-modal-header">
              <h3>🔗 URL → 마크다운 변환</h3>
              <button class="close-btn" @click="closeUrlExtractModal">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <div class="extract-modal-content">
              <p class="extract-description">
                웹 페이지 URL을 입력하면 AI가 내용을 분석하여 마크다운 문서로 변환합니다.
              </p>

              <!-- URL 입력 -->
              <div class="url-input-group">
                <label>웹 페이지 URL</label>
                <div class="url-input-wrapper">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                    class="url-input-icon">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                  </svg>
                  <input v-model="urlInput" type="text" placeholder="https://example.com/article"
                    :disabled="urlExtracting" @keydown.enter="handleUrlExtract">
                </div>
              </div>

              <!-- 텍스트만 가져오기 옵션 -->
              <div class="extract-options">
                <label class="checkbox-wrapper">
                  <input v-model="urlRawTextOnly" type="checkbox">
                  <span class="checkbox-custom" />
                  <span class="checkbox-label">
                    📄 텍스트만 가져오기
                    <span class="option-hint">(AI 없이 빠르게)</span>
                  </span>
                </label>
              </div>

              <!-- 추출 결과 미리보기 -->
              <div v-if="urlExtractResult" class="extract-result">
                <div class="result-header">
                  <span class="result-title">✨ 변환 완료</span>
                  <div class="result-meta">
                    <span v-if="urlExtractResult.title">{{ urlExtractResult.title }}</span>
                  </div>
                </div>
                <div class="result-preview">
                  <pre>{{ urlExtractResult.markdown.slice(0, 500) }}{{ urlExtractResult.markdown.length > 500 ? '...' : '' }}</pre>
                </div>
              </div>

              <!-- 에러 메시지 -->
              <div v-if="urlExtractError" class="extract-error">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                <span>{{ urlExtractError }}</span>
              </div>
            </div>
            <div class="extract-modal-footer">
              <button class="btn-cancel" @click="closeUrlExtractModal">
                취소
              </button>
              <button v-if="!urlExtractResult" class="btn-extract" :disabled="!urlInput.trim() || urlExtracting"
                @click="handleUrlExtract">
                <span v-if="urlExtracting" class="spinner" />
                <span>{{ urlExtracting ? '추출 중...' : '추출하기' }}</span>
              </button>
              <button v-else class="btn-insert" @click="insertUrlExtractResult">
                에디터에 삽입
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { Editor } from '@tiptap/vue-3';
import { useSettings } from '../../composables';
import { useEditor } from '../../composables/useEditor';
import { API_ENDPOINTS } from '../../config/api';
import { GEMINI_VISION_MODELS } from '../../composables/useSettings';

const props = defineProps<{
  editor: Editor | null;
  summarizing?: boolean;
  noteName?: string;
  llmSettings?: {
    provider: string;
    apiKey: string;
    model: string;
  };
}>();

const emit = defineEmits<{
  (e: 'summarize'): void;
  (e: 'extract-result', markdown: string): void;
}>();

const CORE_BASE = 'http://127.0.0.1:8787';

// 문서 추출 상태
const showExtractModal = ref(false);
const extracting = ref(false);
const extractFile = ref<File | null>(null);
const extractFileType = ref<'pdf' | 'image' | ''>('');
const extractFileData = ref('');
const isExtractDragging = ref(false);
const extractFileInputRef = ref<HTMLInputElement | null>(null);
const extractResult = ref<{ markdown: string; page_count: number; has_images: boolean } | null>(null);
const extractError = ref('');

// OCR 모델 상태
interface OCRStatus {
  installed: boolean;
  model_downloaded: boolean;
  model_path: string;
  languages: string[];
  downloading: boolean;
  engine: string;
  engine_name: string;
  engine_description: string;
}
const ocrStatus = ref<OCRStatus | null>(null);
const ocrDownloading = ref(false);
const rawTextOnly = ref(false);

// PDF 내보내기 상태
const exportingPdf = ref(false);

// LLM 설정 가져오기
const { settings: llmSettingsStore } = useSettings();

// 선택된 OCR 엔진 이름 (설정 기반)
const selectedOcrEngineName = computed(() => {
  const engine = llmSettingsStore.value.ocr?.engine || 'rapidocr';

  if (engine === 'gemini') {
    const modelId = llmSettingsStore.value.ocr?.geminiModel || 'gemini-2.0-flash';
    const model = GEMINI_VISION_MODELS.find(m => m.id === modelId);
    return model ? model.name : 'Gemini Vision';
  }

  return 'RapidOCR';
});

function handleSummarize() {
  emit('summarize');
}

// PDF로 내보내기
async function exportToPdf() {
  if (!window.cuenote?.printToPDF) {
    alert('PDF 내보내기 기능을 사용할 수 없습니다.');
    return;
  }

  if (!props.editor) {
    alert('에디터가 준비되지 않았습니다.');
    return;
  }

  exportingPdf.value = true;

  try {
    // 파일명 생성 (노트 이름 기반, 확장자를 .pdf로 변경)
    const noteName = props.noteName || 'document';
    const pdfFilename = noteName.replace(/\.md$/i, '') + '.pdf';

    // 에디터에서 HTML 콘텐츠 가져오기
    const htmlContent = props.editor.getHTML();

    // 스타일을 포함하기 위해 현재 문서의 스타일을 인라인으로 추가하거나 별도로 처리해야 함
    // 여기서는 기본 기능만 구현

    const result = await window.cuenote.printToPDF({
      filename: pdfFilename,
      title: noteName.replace(/\.md$/i, ''),
      htmlContent: htmlContent
    });

    if (result.success) {
      console.log('PDF saved to:', result.filePath);
    } else if (!result.canceled) {
      alert('PDF 저장에 실패했습니다: ' + (result.error || '알 수 없는 오류'));
    }
  } catch (error) {
    console.error('PDF export error:', error);
    alert('PDF 저장 중 오류가 발생했습니다.');
  } finally {
    exportingPdf.value = false;
  }
}

// 문서 추출 관련 함수들
function triggerExtractFileInput() {
  extractFileInputRef.value?.click();
}

function handleExtractFileSelect(e: Event) {
  const input = e.target as HTMLInputElement;
  if (input.files?.length) {
    setExtractFile(input.files[0]);
  }
}

function handleExtractFileDrop(e: DragEvent) {
  isExtractDragging.value = false;
  const files = e.dataTransfer?.files;
  if (files?.length) {
    const file = files[0];
    if (file.type === 'application/pdf' || file.type.startsWith('image/')) {
      setExtractFile(file);
    } else {
      extractError.value = 'PDF 또는 이미지 파일만 지원합니다.';
    }
  }
}

async function setExtractFile(file: File) {
  extractFile.value = file;
  extractError.value = '';
  extractResult.value = null;

  // 파일 타입 판단
  if (file.type === 'application/pdf') {
    extractFileType.value = 'pdf';
  } else if (file.type.startsWith('image/')) {
    extractFileType.value = 'image';
  } else {
    extractFileType.value = '';
    extractError.value = 'PDF 또는 이미지 파일만 지원합니다.';
    return;
  }

  // Base64로 변환
  try {
    extractFileData.value = await fileToBase64(file);
  } catch (error) {
    extractError.value = '파일을 읽을 수 없습니다.';
  }
}

function clearExtractFile() {
  extractFile.value = null;
  extractFileType.value = '';
  extractFileData.value = '';
  extractResult.value = null;
  extractError.value = '';
}

function closeExtractModal() {
  showExtractModal.value = false;
  clearExtractFile();
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

async function handleExtract() {
  if (!extractFile.value || !extractFileData.value) return;

  extracting.value = true;
  extractError.value = '';
  extractResult.value = null;

  try {
    const ocrEngine = llmSettingsStore.value.ocr?.engine || 'rapidocr';
    const ocrModel = ocrEngine === 'gemini'
      ? (llmSettingsStore.value.ocr?.geminiModel || 'gemini-2.0-flash')
      : undefined;

    const res = await fetch(API_ENDPOINTS.AI.SUMMARIZE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_data: extractFileData.value,
        file_type: extractFileType.value,
        language: 'auto',
        raw_text_only: rawTextOnly.value,
        provider: llmSettingsStore.value.llm.provider,
        api_key: llmSettingsStore.value.llm.apiKey,
        model: ocrEngine === 'gemini' ? ocrModel : llmSettingsStore.value.llm.model,
        ocr_engine: ocrEngine
      })
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: '알 수 없는 오류' }));
      throw new Error(errorData.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    extractResult.value = {
      markdown: data.markdown,
      page_count: data.page_count || 1,
      has_images: data.has_images || false
    };
  } catch (error) {
    console.error('Extract error:', error);
    extractError.value = error instanceof Error ? error.message : '문서 변환에 실패했습니다.';
  } finally {
    extracting.value = false;
  }
}

function insertExtractResult() {
  if (!props.editor || !extractResult.value) return;
  emit('extract-result', extractResult.value.markdown);
  closeExtractModal();
}

// OCR 모델 상태 확인
async function checkOcrStatus() {
  try {
    const engine = llmSettingsStore.value.ocr?.engine || 'rapidocr';
    const res = await fetch(`${CORE_BASE}/ai/ocr/status?engine=${engine}`);
    if (res.ok) {
      ocrStatus.value = await res.json();
    }
  } catch (error) {
    console.error('Failed to check OCR status:', error);
  }
}

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// 모달 열 때 OCR 상태 확인
watch(showExtractModal, (isOpen) => {
  if (isOpen) {
    checkOcrStatus();
    rawTextOnly.value = false;
  }
});

// ─── URL 추출 관련 ───
const showUrlExtractModal = ref(false);
const urlExtracting = ref(false);
const urlInput = ref('');
const urlRawTextOnly = ref(false);
const urlExtractResult = ref<{ markdown: string; title: string; images: string[]; source_url: string } | null>(null);
const urlExtractError = ref('');

function closeUrlExtractModal() {
  showUrlExtractModal.value = false;
  urlInput.value = '';
  urlExtractResult.value = null;
  urlExtractError.value = '';
  urlRawTextOnly.value = false;
}

async function handleUrlExtract() {
  const url = urlInput.value.trim();
  if (!url) return;

  urlExtracting.value = true;
  urlExtractError.value = '';
  urlExtractResult.value = null;

  try {
    const res = await fetch(API_ENDPOINTS.AI.EXTRACT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url,
        language: 'auto',
        raw_text_only: urlRawTextOnly.value,
        provider: llmSettingsStore.value.llm.provider,
        api_key: llmSettingsStore.value.llm.apiKey,
        model: llmSettingsStore.value.llm.model,
      })
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: '알 수 없는 오류' }));
      throw new Error(errorData.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    urlExtractResult.value = {
      markdown: data.markdown,
      title: data.title || '',
      images: data.images || [],
      source_url: data.source_url || url,
    };
  } catch (error) {
    console.error('URL extract error:', error);
    urlExtractError.value = error instanceof Error ? error.message : 'URL 추출에 실패했습니다.';
  } finally {
    urlExtracting.value = false;
  }
}

function insertUrlExtractResult() {
  if (!props.editor || !urlExtractResult.value) return;
  emit('extract-result', urlExtractResult.value.markdown);
  closeUrlExtractModal();
}
</script>

<style scoped>
.toolbar-group {
  display: flex;
  align-items: center;
  gap: 1px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.12s ease;
}

/* AI Button Styles */
.ai-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  width: auto;
  padding: 0 10px;
  margin-left: 6px;
  background: color-mix(in srgb, var(--accent-primary, #8b5cf6) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--accent-primary, #8b5cf6) 20%, transparent);
  color: var(--text-secondary);
  transition: all 0.15s ease;
}

.ai-btn:first-child {
  margin-left: 0;
}

.ai-btn:hover:not(:disabled) {
  background: color-mix(in srgb, var(--accent-primary, #8b5cf6) 20%, transparent);
  border-color: var(--accent-primary, #8b5cf6);
  color: var(--accent-primary, #8b5cf6);
}

.ai-btn.loading {
  background: color-mix(in srgb, var(--accent-primary, #8b5cf6) 15%, transparent);
  color: var(--accent-primary, #8b5cf6);
}

.ai-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.ai-btn .spinner {
  width: 12px;
  height: 12px;
  border: 2px solid color-mix(in srgb, var(--accent-primary, #8b5cf6) 20%, transparent);
  border-top-color: var(--accent-primary, #8b5cf6);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.ai-label {
  font-size: 11px;
  font-weight: 500;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* URL Input */
.url-input-group {
  margin-bottom: 16px;
}

.url-input-group label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.url-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.url-input-icon {
  position: absolute;
  left: 12px;
  color: var(--text-muted);
  pointer-events: none;
}

.url-input-wrapper input {
  width: 100%;
  padding: 10px 12px 10px 36px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
}

.url-input-wrapper input:focus {
  border-color: var(--accent-primary, #8b5cf6);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.url-input-wrapper input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Extract Modal */
.extract-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.extract-modal {
  width: 500px;
  max-width: 90vw;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.extract-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.extract-modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.close-btn:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}

.extract-modal-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.extract-description {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.extract-dropzone {
  border: 2px dashed var(--border-subtle);
  border-radius: 8px;
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--surface-1);
}

.extract-dropzone:hover,
.extract-dropzone.drag-over {
  border-color: var(--accent-primary, #8b5cf6);
  background: var(--surface-2);
}

.extract-dropzone.has-file {
  border-style: solid;
  padding: 16px;
  background: var(--surface-2);
}

.dropzone-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
}

.upload-hint {
  font-size: 12px;
  opacity: 0.7;
}

.dropzone-file {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  color: var(--accent-primary, #8b5cf6);
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  overflow: hidden;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.file-size {
  font-size: 12px;
  color: var(--text-muted);
}

.remove-file-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.remove-file-btn:hover {
  background: var(--surface-3);
  color: #ef4444;
}

.ocr-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--surface-2);
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.ocr-ready {
  background: rgba(139, 92, 246, 0.1);
  color: var(--accent-primary, #8b5cf6);
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.ocr-model-status {
  padding: 12px;
  background: var(--surface-2);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
}

.model-status-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: var(--error);
}

.model-status-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.model-title {
  font-weight: 600;
  font-size: 13px;
}

.model-desc {
  font-size: 12px;
  opacity: 0.9;
}

.extract-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.checkbox-wrapper input {
  display: none;
}

.checkbox-custom {
  width: 16px;
  height: 16px;
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  margin-right: 8px;
  position: relative;
  transition: all 0.2s;
}

.checkbox-wrapper input:checked+.checkbox-custom {
  background: var(--accent-primary, #8b5cf6);
  border-color: var(--accent-primary, #8b5cf6);
}

.checkbox-wrapper input:checked+.checkbox-custom::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 2px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-label {
  font-size: 13px;
  color: var(--text-primary);
}

.option-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 4px;
}

.raw-text-info {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  background: var(--surface-2);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.extract-result {
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  overflow: hidden;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--border-subtle);
  font-size: 12px;
}

.result-title {
  font-weight: 600;
  color: var(--accent-primary, #8b5cf6);
}

.result-meta {
  color: var(--text-muted);
}

.result-preview {
  padding: 12px;
  max-height: 150px;
  overflow-y: auto;
}

.result-preview pre {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 12px;
  white-space: pre-wrap;
  color: var(--text-secondary);
}

.extract-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 6px;
  color: #ef4444;
  font-size: 13px;
}

.extract-modal-footer {
  padding: 16px 20px;
  background: var(--surface-1);
  border-top: 1px solid var(--border-subtle);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-extract {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--accent-primary, #8b5cf6);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-extract:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-extract:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-insert {
  padding: 8px 16px;
  background: var(--accent-primary, #8b5cf6);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
}

.btn-insert:hover {
  opacity: 0.9;
}

.btn-cancel {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
}

.btn-cancel:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}

/* Modal Transition */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .extract-modal,
.modal-leave-to .extract-modal {
  transform: scale(0.95);
  opacity: 0;
}
</style>
