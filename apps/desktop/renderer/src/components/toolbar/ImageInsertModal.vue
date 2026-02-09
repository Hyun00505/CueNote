<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="visible"
        class="image-modal-overlay"
        @click.self="emit('close')"
      >
        <div class="image-modal">
          <div class="image-modal-header">
            <h3>이미지 삽입</h3>
            <button
              class="close-btn"
              @click="emit('close')"
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line
                  x1="18"
                  y1="6"
                  x2="6"
                  y2="18"
                />
                <line
                  x1="6"
                  y1="6"
                  x2="18"
                  y2="18"
                />
              </svg>
            </button>
          </div>
          <div class="image-modal-content">
            <!-- 탭 선택 -->
            <div class="image-tabs">
              <button
                class="tab-btn"
                :class="{ active: currentTab === 'upload' }"
                @click="currentTab = 'upload'"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line
                    x1="12"
                    y1="3"
                    x2="12"
                    y2="15"
                  />
                </svg>
                파일 업로드
              </button>
              <button
                class="tab-btn"
                :class="{ active: currentTab === 'url' }"
                @click="currentTab = 'url'"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                  <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                </svg>
                URL 입력
              </button>
            </div>

            <!-- 파일 업로드 탭 -->
            <div
              v-if="currentTab === 'upload'"
              class="upload-section"
            >
              <div
                class="upload-dropzone"
                :class="{ 'drag-over': isDragging }"
                @dragenter="isDragging = true"
                @dragleave="isDragging = false"
                @dragover.prevent
                @drop.prevent="handleFileDrop"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInputRef"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="handleFileSelect"
                >
                <svg
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line
                    x1="12"
                    y1="3"
                    x2="12"
                    y2="15"
                  />
                </svg>
                <span>클릭하거나 이미지를 드래그하세요</span>
                <span class="upload-hint">PNG, JPG, GIF, WebP 지원</span>
              </div>
            </div>

            <!-- URL 입력 탭 -->
            <div
              v-if="currentTab === 'url'"
              class="input-group"
            >
              <label>이미지 URL</label>
              <input
                v-model="imageUrl"
                type="text"
                placeholder="https://example.com/image.jpg"
                @input="onImageUrlChange"
                @keydown.enter="handleInsert"
              >
            </div>

            <!-- 미리보기 -->
            <div class="image-preview-container">
              <div
                v-if="loading || uploading"
                class="image-loading"
              >
                <span class="spinner" />
                {{ uploading ? '업로드 중...' : '이미지 로딩 중...' }}
              </div>
              <div
                v-else-if="error"
                class="image-error"
              >
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                  />
                  <line
                    x1="12"
                    y1="8"
                    x2="12"
                    y2="12"
                  />
                  <line
                    x1="12"
                    y1="16"
                    x2="12.01"
                    y2="16"
                  />
                </svg>
                이미지를 불러올 수 없습니다
              </div>
              <img
                v-else-if="previewUrl"
                :src="previewUrl"
                class="image-preview"
                @load="onImageLoad"
                @error="onImageError"
              >
              <div
                v-else
                class="image-placeholder"
              >
                <svg
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1"
                >
                  <rect
                    x="3"
                    y="3"
                    width="18"
                    height="18"
                    rx="2"
                  />
                  <circle
                    cx="8.5"
                    cy="8.5"
                    r="1.5"
                  />
                  <path d="M21 15l-5-5L5 21" />
                </svg>
                <span>{{ currentTab === 'upload' ? '이미지를 업로드하면 미리보기가 표시됩니다' : 'URL을 입력하면 미리보기가 표시됩니다' }}</span>
              </div>
            </div>
            <div class="insert-position-hint">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                />
                <path d="M12 16v-4" />
                <path d="M12 8h.01" />
              </svg>
              현재 커서 위치에 이미지가 삽입됩니다
            </div>
          </div>
          <div class="image-modal-footer">
            <button
              class="btn-cancel"
              @click="emit('close')"
            >
              취소
            </button>
            <button
              class="btn-insert"
              :disabled="!finalUrl || error || uploading"
              @click="handleInsert"
            >
              삽입
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

const CORE_BASE = 'http://127.0.0.1:8787';

const props = defineProps<{
  visible: boolean;
}>();

const emit = defineEmits<{
  'close': [];
  'insert': [url: string];
}>();

const currentTab = ref<'upload' | 'url'>('upload');
const imageUrl = ref('');
const previewUrl = ref('');
const uploadedUrl = ref('');
const loading = ref(false);
const uploading = ref(false);
const error = ref(false);
const isDragging = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);

const finalUrl = computed(() => {
  if (currentTab.value === 'upload') {
    return uploadedUrl.value;
  }
  return imageUrl.value;
});

watch(() => props.visible, (val) => {
  if (val) {
    currentTab.value = 'upload';
    imageUrl.value = '';
    previewUrl.value = '';
    uploadedUrl.value = '';
    loading.value = false;
    uploading.value = false;
    error.value = false;
    isDragging.value = false;
  }
});

function triggerFileInput() {
  fileInputRef.value?.click();
}

async function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) {
    await uploadFile(file);
  }
  input.value = '';
}

async function handleFileDrop(e: DragEvent) {
  isDragging.value = false;
  const file = e.dataTransfer?.files[0];
  if (file && file.type.startsWith('image/')) {
    await uploadFile(file);
  }
}

async function uploadFile(file: File) {
  uploading.value = true;
  error.value = false;

  try {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE_URL}/images/upload`, {
      method: 'POST',
      body: formData,
    });

    if (res.ok) {
      const data = await res.json();
      uploadedUrl.value = data.url || data.path;
      previewUrl.value = uploadedUrl.value;
    } else {
      error.value = true;
    }
  } catch (e) {
    error.value = true;
  } finally {
    uploading.value = false;
  }
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null;
function onImageUrlChange() {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    if (imageUrl.value.trim()) {
      loading.value = true;
      error.value = false;
      previewUrl.value = imageUrl.value;
    } else {
      previewUrl.value = '';
    }
  }, 300);
}

function onImageLoad() {
  loading.value = false;
  error.value = false;
}

function onImageError() {
  loading.value = false;
  error.value = true;
}

function handleInsert() {
  if (finalUrl.value && !error.value && !uploading.value) {
    emit('insert', finalUrl.value);
  }
}
</script>

<style scoped>
.image-modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-modal {
  width: 480px;
  max-width: 90vw;
  max-height: 85vh;
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.image-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.image-modal-header h3 {
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

.image-modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* Tabs */
.image-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  background: var(--surface-3);
}

.tab-btn.active {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
  color: #a78bfa;
}

/* Upload */
.upload-dropzone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 32px;
  border: 2px dashed var(--border-default);
  border-radius: 12px;
  background: var(--surface-1);
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-muted);
}

.upload-dropzone:hover,
.upload-dropzone.drag-over {
  border-color: #a78bfa;
  background: rgba(139, 92, 246, 0.05);
}

.upload-dropzone svg {
  opacity: 0.5;
}

.upload-hint {
  font-size: 12px;
  opacity: 0.6;
}

/* URL Input */
.input-group {
  margin-bottom: 16px;
}

.input-group label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.input-group input {
  width: 100%;
  padding: 10px 12px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  transition: border-color 0.15s ease;
}

.input-group input:focus {
  outline: none;
  border-color: #a78bfa;
}

/* Preview */
.image-preview-container {
  margin-top: 16px;
  min-height: 150px;
  background: var(--bg-tertiary);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.image-loading,
.image-error,
.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  font-size: 13px;
  padding: 24px;
  text-align: center;
}

.image-loading .spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-default);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.image-error {
  color: #ef4444;
}

.image-preview {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
}

.insert-position-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(139, 92, 246, 0.08);
  border-radius: 8px;
  font-size: 12px;
  color: #a78bfa;
}

/* Footer */
.image-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-subtle);
}

.btn-cancel,
.btn-insert {
  padding: 9px 18px;
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

.btn-insert {
  background: #8b5cf6;
  border: none;
  color: white;
}

.btn-insert:hover:not(:disabled) {
  background: #7c3aed;
}

.btn-insert:disabled {
  opacity: 0.4;
  cursor: not-allowed;
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
