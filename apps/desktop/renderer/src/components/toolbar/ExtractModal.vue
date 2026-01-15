<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="extract-modal-overlay" @click.self="emit('close')">
        <div class="extract-modal">
          <div class="extract-modal-header">
            <h3>📄 PDF/이미지 → 마크다운 변환</h3>
            <button class="close-btn" @click="emit('close')">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <div class="extract-modal-content">
            <p class="extract-description">
              PDF 파일이나 이미지(스크린샷, 사진)를 업로드하면 AI가 내용을 분석하여 마크다운 문서로 변환합니다.
            </p>
            
            <!-- 파일 업로드 영역 -->
            <div 
              class="extract-dropzone"
              :class="{ 'drag-over': isDragging, 'has-file': file }"
              @dragenter="isDragging = true"
              @dragleave="isDragging = false"
              @dragover.prevent
              @drop.prevent="handleFileDrop"
              @click="triggerFileInput"
            >
              <input 
                ref="fileInputRef"
                type="file" 
                accept=".pdf,image/*" 
                style="display: none"
                @change="handleFileSelect"
              />
              <div v-if="!file" class="dropzone-empty">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <span>클릭하거나 파일을 드래그하세요</span>
                <span class="upload-hint">PDF, PNG, JPG, GIF, WebP 지원</span>
              </div>
              <div v-else class="dropzone-file">
                <div class="file-icon">
                  <svg v-if="fileType === 'pdf'" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <path d="M10 12h4"/>
                    <path d="M10 16h4"/>
                  </svg>
                  <svg v-else width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <path d="M21 15l-5-5L5 21"/>
                  </svg>
                </div>
                <div class="file-info">
                  <span class="file-name">{{ file?.name }}</span>
                  <span class="file-size">{{ formatFileSize(file?.size || 0) }}</span>
                </div>
                <button class="remove-file-btn" @click.stop="clearFile" title="파일 제거">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- OCR 엔진 상태 (사용 불가) -->
            <div v-if="ocrStatus && !ocrStatus.model_downloaded" class="ocr-model-status">
              <div class="model-status-header">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 8v4"/>
                  <path d="M12 16h.01"/>
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
            <div v-else-if="file" class="ocr-info ocr-ready">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <span>OCR 준비됨 - {{ ocrEngineName }}로 텍스트를 추출합니다.</span>
            </div>

            <!-- 텍스트만 가져오기 옵션 -->
            <div v-if="file" class="extract-options">
              <label class="checkbox-wrapper">
                <input 
                  type="checkbox" 
                  v-model="rawTextOnly"
                />
                <span class="checkbox-custom"></span>
                <span class="checkbox-label">
                  📄 텍스트만 가져오기
                  <span class="option-hint">(AI 없이 빠르게)</span>
                </span>
              </label>
              
              <div v-if="rawTextOnly" class="raw-text-info">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 16v-4"/>
                  <path d="M12 8h.01"/>
                </svg>
                <span>AI를 거치지 않고 OCR 결과를 그대로 가져옵니다. 마크다운 형식화가 필요하면 체크를 해제하세요.</span>
              </div>
            </div>

            <!-- 추출 결과 미리보기 -->
            <div v-if="result" class="extract-result">
              <div class="result-header">
                <span class="result-title">✨ 변환 완료</span>
                <div class="result-meta">
                  <span v-if="result.page_count > 1">{{ result.page_count }}페이지</span>
                  <span v-if="result.has_images">이미지 포함</span>
                </div>
              </div>
              <div class="result-preview">
                <pre>{{ result.markdown.slice(0, 500) }}{{ result.markdown.length > 500 ? '...' : '' }}</pre>
              </div>
            </div>

            <!-- 에러 메시지 -->
            <div v-if="error" class="extract-error">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span>{{ error }}</span>
            </div>
          </div>
          <div class="extract-modal-footer">
            <button class="btn-cancel" @click="emit('close')">취소</button>
            <button
              v-if="!result"
              class="btn-extract"
              :disabled="!file || loading"
              @click="handleExtract"
            >
              <span v-if="loading" class="spinner"></span>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
                <path d="M12 18v-6"/>
                <path d="m9 15 3 3 3-3"/>
              </svg>
              {{ loading ? '변환 중...' : '변환하기' }}
            </button>
            <button
              v-else
              class="btn-insert"
              @click="handleInsert"
            >
              에디터에 삽입
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useSettings } from '../../composables';

const CORE_BASE = 'http://127.0.0.1:8787';

interface ExtractResult {
  markdown: string;
  page_count: number;
  has_images: boolean;
}

interface OcrStatus {
  engine: string;
  engine_name: string;
  model_downloaded: boolean;
}

const props = defineProps<{
  visible: boolean;
}>();

const emit = defineEmits<{
  'close': [];
  'insert': [markdown: string];
}>();

const { settings } = useSettings();

const file = ref<File | null>(null);
const result = ref<ExtractResult | null>(null);
const ocrStatus = ref<OcrStatus | null>(null);
const loading = ref(false);
const error = ref('');
const isDragging = ref(false);
const rawTextOnly = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);

const fileType = computed(() => {
  if (!file.value) return '';
  return file.value.type === 'application/pdf' ? 'pdf' : 'image';
});

const ocrEngineName = computed(() => {
  const engine = settings.value?.ocrEngine || 'gemini';
  const names: Record<string, string> = {
    'gemini': 'Gemini Vision',
    'easyocr': 'EasyOCR',
    'tesseract': 'Tesseract'
  };
  return names[engine] || engine;
});

watch(() => props.visible, async (val) => {
  if (val) {
    file.value = null;
    result.value = null;
    error.value = '';
    loading.value = false;
    rawTextOnly.value = false;
    isDragging.value = false;
    await checkOcrStatus();
  }
});

async function checkOcrStatus() {
  try {
    const res = await fetch(`${CORE_BASE}/ocr/status`);
    if (res.ok) {
      ocrStatus.value = await res.json();
    }
  } catch (e) {
    console.error('Failed to check OCR status:', e);
  }
}

function triggerFileInput() {
  fileInputRef.value?.click();
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement;
  const selectedFile = input.files?.[0];
  if (selectedFile) {
    file.value = selectedFile;
    result.value = null;
    error.value = '';
  }
  input.value = '';
}

function handleFileDrop(e: DragEvent) {
  isDragging.value = false;
  const droppedFile = e.dataTransfer?.files[0];
  if (droppedFile) {
    const isValidType = droppedFile.type === 'application/pdf' || droppedFile.type.startsWith('image/');
    if (isValidType) {
      file.value = droppedFile;
      result.value = null;
      error.value = '';
    }
  }
}

function clearFile() {
  file.value = null;
  result.value = null;
  error.value = '';
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

async function handleExtract() {
  if (!file.value) return;

  loading.value = true;
  error.value = '';
  result.value = null;

  try {
    const formData = new FormData();
    formData.append('file', file.value);
    formData.append('raw_text_only', String(rawTextOnly.value));

    const res = await fetch(`${CORE_BASE}/ocr/extract`, {
      method: 'POST',
      body: formData,
    });

    if (res.ok) {
      result.value = await res.json();
    } else {
      const data = await res.json().catch(() => ({}));
      error.value = data.detail || '문서 변환에 실패했습니다.';
    }
  } catch (e: any) {
    error.value = e.message || '문서 변환 중 오류가 발생했습니다.';
  } finally {
    loading.value = false;
  }
}

function handleInsert() {
  if (result.value?.markdown) {
    emit('insert', result.value.markdown);
  }
}
</script>

<style scoped>
.extract-modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.extract-modal {
  width: 520px;
  max-width: 90vw;
  max-height: 85vh;
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
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
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.close-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.12s ease;
}

.close-btn:hover {
  background: var(--surface-3);
  color: var(--text-primary);
}

.extract-modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.extract-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 16px;
  line-height: 1.5;
}

/* Dropzone */
.extract-dropzone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  border: 2px dashed var(--border-default);
  border-radius: 12px;
  background: var(--surface-1);
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 16px;
}

.extract-dropzone:hover,
.extract-dropzone.drag-over {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.05);
}

.extract-dropzone.has-file {
  border-style: solid;
  cursor: default;
}

.dropzone-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
}

.dropzone-empty svg {
  opacity: 0.5;
}

.upload-hint {
  font-size: 12px;
  opacity: 0.6;
}

.dropzone-file {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 10px;
  color: #22c55e;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.remove-file-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.12s ease;
}

.remove-file-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* OCR Status */
.ocr-model-status {
  padding: 14px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 10px;
  margin-bottom: 16px;
}

.model-status-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  color: #f59e0b;
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
  opacity: 0.8;
}

.ocr-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: rgba(34, 197, 94, 0.08);
  border-radius: 8px;
  font-size: 13px;
  color: #22c55e;
  margin-bottom: 16px;
}

/* Options */
.extract-options {
  margin-bottom: 16px;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
}

.checkbox-wrapper input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #22c55e;
}

.option-hint {
  font-size: 11px;
  color: var(--text-muted);
}

.raw-text-info {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 10px;
  padding: 10px 12px;
  background: rgba(139, 92, 246, 0.08);
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.raw-text-info svg {
  flex-shrink: 0;
  margin-top: 1px;
  color: #a78bfa;
}

/* Result */
.extract-result {
  background: rgba(34, 197, 94, 0.05);
  border: 1px solid rgba(34, 197, 94, 0.15);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 16px;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: rgba(34, 197, 94, 0.1);
}

.result-title {
  font-size: 13px;
  font-weight: 600;
  color: #22c55e;
}

.result-meta {
  display: flex;
  gap: 10px;
  font-size: 11px;
  color: var(--text-muted);
}

.result-preview {
  padding: 14px;
  max-height: 200px;
  overflow-y: auto;
}

.result-preview pre {
  margin: 0;
  font-size: 12px;
  font-family: var(--font-mono);
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
}

/* Error */
.extract-error {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: #ef4444;
  font-size: 13px;
}

/* Footer */
.extract-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-subtle);
}

.btn-cancel,
.btn-extract,
.btn-insert {
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.btn-cancel:hover {
  background: var(--surface-2);
}

.btn-extract {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.25);
  color: #22c55e;
}

.btn-extract:hover:not(:disabled) {
  background: rgba(34, 197, 94, 0.25);
}

.btn-extract:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-insert {
  background: #22c55e;
  border: none;
  color: white;
}

.btn-insert:hover {
  background: #16a34a;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border-strong);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.15s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
