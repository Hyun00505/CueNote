<template>
  <div class="toolbar-group">
    <div class="dropdown-wrapper">
      <button
        class="toolbar-btn"
        title="이미지 삽입"
        @click="showImageModal = true"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
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
      </button>
    </div>

    <!-- 이미지 삽입 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showImageModal"
          class="image-modal-overlay"
          @click.self="closeImageModal"
        >
          <div class="image-modal">
            <div class="image-modal-header">
              <h3>이미지 삽입</h3>
              <button
                class="close-btn"
                @click="closeImageModal"
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
                  :class="{ active: imageTab === 'upload' }"
                  @click="imageTab = 'upload'"
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
                  :class="{ active: imageTab === 'url' }"
                  @click="imageTab = 'url'"
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
                v-if="imageTab === 'upload'"
                class="upload-section"
              >
                <div
                  class="upload-dropzone"
                  :class="{ 'drag-over': isUploadDragging }"
                  @dragenter="isUploadDragging = true"
                  @dragleave="isUploadDragging = false"
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
                v-if="imageTab === 'url'"
                class="input-group"
              >
                <label>이미지 URL</label>
                <input
                  v-model="imageUrl"
                  type="text"
                  placeholder="https://example.com/image.jpg"
                  @input="onImageUrlChange"
                  @keydown.enter="confirmInsertImage"
                >
              </div>

              <!-- 미리보기 -->
              <div class="image-preview-container">
                <div
                  v-if="imageLoading || isUploading"
                  class="image-loading"
                >
                  <span class="spinner" />
                  {{ isUploading ? '업로드 중...' : '이미지 로딩 중...' }}
                </div>
                <div
                  v-else-if="imageError"
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
                  v-else-if="imagePreviewUrl"
                  :src="imagePreviewUrl"
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
                  <span>{{ imageTab === 'upload' ? '이미지를 업로드하면 미리보기가 표시됩니다' : 'URL을 입력하면 미리보기가 표시됩니다' }}</span>
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
                @click="closeImageModal"
              >
                취소
              </button>
              <button
                class="btn-insert"
                :disabled="!finalImageUrl || imageError || isUploading"
                @click="confirmInsertImage"
              >
                삽입
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useEditor } from '../../composables/useEditor';
import { API_BASE_URL } from '../../config/api';
import type { Editor } from '@tiptap/vue-3';

const props = defineProps<{
  editor: Editor | null;
}>();

const { editorView } = useEditor();
const fileInputRef = ref<HTMLInputElement | null>(null);

const uploadUrl = `${API_BASE_URL}/images/upload`;

// 이미지 모달 상태
const showImageModal = ref(false);
const imageUrl = ref('');
const imagePreviewUrl = ref('');
const imageLoading = ref(false);
const imageError = ref(false);
const imageTab = ref<'upload' | 'url'>('upload');
const isUploadDragging = ref(false);
const isUploading = ref(false);
const uploadedImageUrl = ref('');

// 최종 이미지 URL
const finalImageUrl = computed(() => {
  if (imageTab.value === 'upload') {
    return uploadedImageUrl.value;
  }
  return imagePreviewUrl.value;
});

// 이미지 URL 변경 처리
let imageDebounceTimer: ReturnType<typeof setTimeout> | null = null;
function onImageUrlChange() {
  imageError.value = false;
  imagePreviewUrl.value = '';

  if (imageDebounceTimer) {
    clearTimeout(imageDebounceTimer);
  }

  if (!imageUrl.value.trim()) {
    return;
  }

  imageLoading.value = true;
  imageDebounceTimer = setTimeout(() => {
    imagePreviewUrl.value = imageUrl.value.trim();
  }, 300);
}

function onImageLoad() {
  imageLoading.value = false;
  imageError.value = false;
}

function onImageError() {
  imageLoading.value = false;
  imageError.value = true;
}

function closeImageModal() {
  showImageModal.value = false;
  imageUrl.value = '';
  imagePreviewUrl.value = '';
  imageError.value = false;
  imageLoading.value = false;
  imageTab.value = 'upload';
  uploadedImageUrl.value = '';
  isUploading.value = false;
}

function confirmInsertImage() {
  if (!props.editor || !finalImageUrl.value || imageError.value || isUploading.value) return;

  props.editor.chain().focus().setImage({ src: finalImageUrl.value }).run();
  closeImageModal();
}

// 파일 업로드 관련 함수들
function triggerFileInput() {
  fileInputRef.value?.click();
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement;
  if (input.files?.length) {
    uploadFile(input.files[0]);
  }
}

function handleFileDrop(e: DragEvent) {
  isUploadDragging.value = false;
  const files = e.dataTransfer?.files;
  if (files?.length) {
    const imageFile = Array.from(files).find(f => f.type.startsWith('image/'));
    if (imageFile) {
      uploadFile(imageFile);
    }
  }
}

async function uploadFile(file: File) {
  if (!file.type.startsWith('image/')) {
    imageError.value = true;
    return;
  }

  isUploading.value = true;
  imageError.value = false;

  try {
    // 파일을 Base64로 변환
    const base64 = await fileToBase64(file);

    // 서버에 업로드
    const res = await fetch(`${API_BASE_URL}/images/upload`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: base64 })
    });

    if (!res.ok) {
      throw new Error('Upload failed');
    }

    const data = await res.json();
    uploadedImageUrl.value = `${CORE_BASE}${data.url}`;
    imagePreviewUrl.value = uploadedImageUrl.value;
  } catch (error) {
    console.error('Upload error:', error);
    imageError.value = true;
  } finally {
    isUploading.value = false;
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
</script>

<style scoped>
.toolbar-group {
  display: flex;
  align-items: center;
  gap: 1px;
}

.dropdown-wrapper {
  position: relative;
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

.toolbar-btn:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}

/* Image Modal */
.image-modal-overlay {
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

.image-modal {
  width: 480px;
  max-width: 90vw;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
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
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}

.image-modal-content {
  padding: 20px;
}

.image-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 10px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--surface-2);
  color: var(--accent-primary, #8b5cf6);
  font-weight: 500;
}

.upload-dropzone {
  border: 2px dashed var(--border-subtle);
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
}

.upload-dropzone:hover,
.upload-dropzone.drag-over {
  border-color: var(--accent-primary, #8b5cf6);
  background: var(--surface-2);
  color: var(--text-primary);
}

.upload-hint {
  font-size: 12px;
  color: var(--text-muted);
  opacity: 0.7;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.input-group input {
  padding: 10px 12px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
}

.input-group input:focus {
  border-color: var(--accent-primary, #8b5cf6);
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
}

.image-preview-container {
  margin-top: 20px;
  height: 200px;
  background: var(--surface-1);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-subtle);
  position: relative;
}

.image-preview {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.image-placeholder,
.image-loading,
.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
  padding: 20px;
}

.image-error {
  color: var(--error);
}

.insert-position-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.image-modal-footer {
  padding: 16px 20px;
  background: var(--surface-1);
  border-top: 1px solid var(--border-subtle);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-cancel {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: var(--surface-2);
  color: var(--text-primary);
  border-color: var(--text-muted);
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
  transition: all 0.2s;
}

.btn-insert:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-insert:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(139, 92, 246, 0.3);
  border-top-color: var(--accent-primary, #8b5cf6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
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

.modal-enter-from .image-modal,
.modal-leave-to .image-modal {
  transform: scale(0.95);
  opacity: 0;
}

.image-modal {
  transition: all 0.2s ease;
}
</style>
