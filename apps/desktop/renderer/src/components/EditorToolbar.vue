<template>
  <div class="editor-toolbar">
    <div class="toolbar-group">
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('heading', { level: 1 }) }"
        @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
        title="제목 1"
      >
        <span class="heading-icon">H1</span>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('heading', { level: 2 }) }"
        @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
        title="제목 2"
      >
        <span class="heading-icon">H2</span>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('heading', { level: 3 }) }"
        @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
        title="제목 3"
      >
        <span class="heading-icon">H3</span>
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('bold') }"
        @click="editor?.chain().focus().toggleBold().run()"
        title="굵게 (Ctrl+B)"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/>
          <path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/>
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('italic') }"
        @click="editor?.chain().focus().toggleItalic().run()"
        title="기울임 (Ctrl+I)"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="19" y1="4" x2="10" y2="4"/>
          <line x1="14" y1="20" x2="5" y2="20"/>
          <line x1="15" y1="4" x2="9" y2="20"/>
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('underline') }"
        @click="editor?.chain().focus().toggleUnderline().run()"
        title="밑줄 (Ctrl+U)"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 3v7a6 6 0 0 0 6 6 6 6 0 0 0 6-6V3"/>
          <line x1="4" y1="21" x2="20" y2="21"/>
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('strike') }"
        @click="editor?.chain().focus().toggleStrike().run()"
        title="취소선"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M16 4H9a3 3 0 0 0-2.83 4"/>
          <path d="M14 12a4 4 0 0 1 0 8H6"/>
          <line x1="4" y1="12" x2="20" y2="12"/>
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('highlight') }"
        @click="editor?.chain().focus().toggleHighlight().run()"
        title="형광펜"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m9 11-6 6v3h9l3-3"/>
          <path d="m22 12-4.6 4.6a2 2 0 0 1-2.8 0l-5.2-5.2a2 2 0 0 1 0-2.8L14 4"/>
        </svg>
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('bulletList') }"
        @click="editor?.chain().focus().toggleBulletList().run()"
        title="글머리 기호"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="8" y1="6" x2="21" y2="6"/>
          <line x1="8" y1="12" x2="21" y2="12"/>
          <line x1="8" y1="18" x2="21" y2="18"/>
          <circle cx="4" cy="6" r="1" fill="currentColor"/>
          <circle cx="4" cy="12" r="1" fill="currentColor"/>
          <circle cx="4" cy="18" r="1" fill="currentColor"/>
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('orderedList') }"
        @click="editor?.chain().focus().toggleOrderedList().run()"
        title="번호 매기기"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="10" y1="6" x2="21" y2="6"/>
          <line x1="10" y1="12" x2="21" y2="12"/>
          <line x1="10" y1="18" x2="21" y2="18"/>
          <text x="3" y="7" font-size="6" fill="currentColor">1</text>
          <text x="3" y="13" font-size="6" fill="currentColor">2</text>
          <text x="3" y="19" font-size="6" fill="currentColor">3</text>
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('taskList') }"
        @click="editor?.chain().focus().toggleTaskList().run()"
        title="할 일 목록"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="5" width="6" height="6" rx="1"/>
          <path d="m5 8 1 1 2-2"/>
          <line x1="12" y1="8" x2="21" y2="8"/>
          <rect x="3" y="13" width="6" height="6" rx="1"/>
          <line x1="12" y1="16" x2="21" y2="16"/>
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('blockquote') }"
        @click="editor?.chain().focus().toggleBlockquote().run()"
        title="인용문"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21z"/>
          <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3z"/>
        </svg>
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('code') }"
        @click="editor?.chain().focus().toggleCode().run()"
        title="인라인 코드"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="16 18 22 12 16 6"/>
          <polyline points="8 6 2 12 8 18"/>
        </svg>
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: editor?.isActive('codeBlock') }"
        @click="editor?.chain().focus().toggleCodeBlock().run()"
        title="코드 블록"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <polyline points="9 9 6 12 9 15"/>
          <polyline points="15 9 18 12 15 15"/>
        </svg>
      </button>
      <button
        class="toolbar-btn"
        @click="setLink"
        :class="{ active: editor?.isActive('link') }"
        title="링크 삽입"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
        </svg>
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <div class="dropdown-wrapper">
        <button
          class="toolbar-btn"
          @click="showImageModal = true"
          title="이미지 삽입"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="M21 15l-5-5L5 21"/>
          </svg>
        </button>
      </div>
      <div class="dropdown-wrapper">
        <button
          ref="tableBtnRef"
          class="toolbar-btn"
          @click="showTablePicker = !showTablePicker"
          title="표 삽입"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <line x1="3" y1="9" x2="21" y2="9"/>
            <line x1="3" y1="15" x2="21" y2="15"/>
            <line x1="9" y1="3" x2="9" y2="21"/>
            <line x1="15" y1="3" x2="15" y2="21"/>
          </svg>
        </button>
        <!-- 표 크기 선택 드롭다운 -->
        <Transition name="dropdown">
          <div v-if="showTablePicker" class="table-picker" @mouseleave="showTablePicker = false">
            <div class="table-picker-header">{{ tableRows }} × {{ tableCols }} 표</div>
            <div class="table-grid">
              <div
                v-for="row in 6"
                :key="row"
                class="table-row"
              >
                <div
                  v-for="col in 6"
                  :key="col"
                  class="table-cell"
                  :class="{ selected: row <= tableRows && col <= tableCols }"
                  @mouseenter="tableRows = row; tableCols = col"
                  @click="insertTableWithSize(row, col)"
                ></div>
              </div>
            </div>
          </div>
        </Transition>
      </div>
      <button
        class="toolbar-btn"
        @click="editor?.chain().focus().setHorizontalRule().run()"
        title="구분선"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="2" y1="12" x2="22" y2="12"/>
        </svg>
      </button>
    </div>

    <!-- 이미지 삽입 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showImageModal" class="image-modal-overlay" @click.self="closeImageModal">
          <div class="image-modal">
            <div class="image-modal-header">
              <h3>이미지 삽입</h3>
              <button class="close-btn" @click="closeImageModal">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
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
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                  </svg>
                  파일 업로드
                </button>
                <button 
                  class="tab-btn" 
                  :class="{ active: imageTab === 'url' }"
                  @click="imageTab = 'url'"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                  </svg>
                  URL 입력
                </button>
              </div>

              <!-- 파일 업로드 탭 -->
              <div v-if="imageTab === 'upload'" class="upload-section">
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
                  />
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                  </svg>
                  <span>클릭하거나 이미지를 드래그하세요</span>
                  <span class="upload-hint">PNG, JPG, GIF, WebP 지원</span>
                </div>
              </div>

              <!-- URL 입력 탭 -->
              <div v-if="imageTab === 'url'" class="input-group">
                <label>이미지 URL</label>
                <input
                  v-model="imageUrl"
                  type="text"
                  placeholder="https://example.com/image.jpg"
                  @input="onImageUrlChange"
                  @keydown.enter="confirmInsertImage"
                />
              </div>

              <!-- 미리보기 -->
              <div class="image-preview-container">
                <div v-if="imageLoading || isUploading" class="image-loading">
                  <span class="spinner"></span>
                  {{ isUploading ? '업로드 중...' : '이미지 로딩 중...' }}
                </div>
                <div v-else-if="imageError" class="image-error">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                  </svg>
                  이미지를 불러올 수 없습니다
                </div>
                <img
                  v-else-if="imagePreviewUrl"
                  :src="imagePreviewUrl"
                  class="image-preview"
                  @load="onImageLoad"
                  @error="onImageError"
                />
                <div v-else class="image-placeholder">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <path d="M21 15l-5-5L5 21"/>
                  </svg>
                  <span>{{ imageTab === 'upload' ? '이미지를 업로드하면 미리보기가 표시됩니다' : 'URL을 입력하면 미리보기가 표시됩니다' }}</span>
                </div>
              </div>
              <div class="insert-position-hint">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 16v-4"/>
                  <path d="M12 8h.01"/>
                </svg>
                현재 커서 위치에 이미지가 삽입됩니다
              </div>
            </div>
            <div class="image-modal-footer">
              <button class="btn-cancel" @click="closeImageModal">취소</button>
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

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button
        class="toolbar-btn"
        @click="editor?.chain().focus().undo().run()"
        :disabled="!editor?.can().undo()"
        title="실행 취소 (Ctrl+Z)"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 7v6h6"/>
          <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"/>
        </svg>
      </button>
      <button
        class="toolbar-btn"
        @click="editor?.chain().focus().redo().run()"
        :disabled="!editor?.can().redo()"
        title="다시 실행 (Ctrl+Y)"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 7v6h-6"/>
          <path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7"/>
        </svg>
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button
        class="toolbar-btn ai-btn"
        :class="{ loading: summarizing }"
        :disabled="summarizing"
        @click="handleSummarize"
        title="AI 요약"
      >
        <svg v-if="!summarizing" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H6a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 8 6a4 4 0 0 1 4-4z"/>
          <circle cx="9" cy="6" r="1" fill="currentColor"/>
          <circle cx="15" cy="6" r="1" fill="currentColor"/>
        </svg>
        <span v-else class="spinner"></span>
        <span class="ai-label">요약</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Editor } from '@tiptap/vue-3';

const CORE_BASE = 'http://127.0.0.1:8787';

const props = defineProps<{
  editor: Editor | null;
  summarizing?: boolean;
}>();

const emit = defineEmits<{
  (e: 'summarize'): void;
}>();

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
const fileInputRef = ref<HTMLInputElement | null>(null);

// 최종 이미지 URL (업로드된 이미지 또는 URL 입력)
const finalImageUrl = computed(() => {
  if (imageTab.value === 'upload') {
    return uploadedImageUrl.value;
  }
  return imagePreviewUrl.value;
});

// 표 피커 상태
const showTablePicker = ref(false);
const tableRows = ref(3);
const tableCols = ref(3);
const tableBtnRef = ref<HTMLElement | null>(null);

function handleSummarize() {
  emit('summarize');
}

function setLink() {
  if (!props.editor) return;

  const previousUrl = props.editor.getAttributes('link').href;
  const url = window.prompt('링크 URL을 입력하세요:', previousUrl);

  if (url === null) return;

  if (url === '') {
    props.editor.chain().focus().extendMarkRange('link').unsetLink().run();
    return;
  }

  props.editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
}

// 이미지 URL 변경 처리 (디바운스)
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
    const res = await fetch(`${CORE_BASE}/vault/image`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: base64 })
    });
    
    if (!res.ok) {
      throw new Error('Upload failed');
    }
    
    const data = await res.json();
    // 서버에서 반환한 URL 사용
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

function insertTableWithSize(rows: number, cols: number) {
  if (!props.editor) return;
  props.editor.chain().focus().insertTable({ rows, cols, withHeaderRow: true }).run();
  showTablePicker.value = false;
  tableRows.value = 3;
  tableCols.value = 3;
}
</script>

<style scoped>
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  flex-wrap: wrap;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 1px;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border-subtle);
  margin: 0 8px;
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

.toolbar-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.toolbar-btn:active:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
}

.toolbar-btn.active {
  background: rgba(201, 167, 108, 0.15);
  color: #e8d5b7;
}

.toolbar-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.heading-icon {
  font-size: 10px;
  font-weight: 700;
  font-family: var(--font-mono);
  letter-spacing: -0.5px;
}

.toolbar-btn svg {
  width: 15px;
  height: 15px;
  opacity: 0.85;
}

.toolbar-btn.active svg {
  opacity: 1;
}

/* AI Button Styles */
.ai-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  width: auto;
  padding: 0 10px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.ai-btn:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.4);
  color: #a78bfa;
}

.ai-btn.loading {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
}

.ai-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.ai-label {
  font-size: 11px;
  font-weight: 500;
}

.ai-btn .spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(139, 92, 246, 0.2);
  border-top-color: #a78bfa;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Dropdown Wrapper */
.dropdown-wrapper {
  position: relative;
}

/* Table Picker */
.table-picker {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  padding: 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  z-index: 100;
}

.table-picker-header {
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
  margin-bottom: 8px;
}

.table-grid {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.table-row {
  display: flex;
  gap: 3px;
}

.table-cell {
  width: 20px;
  height: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.1s ease;
}

.table-cell:hover {
  background: rgba(255, 255, 255, 0.1);
}

.table-cell.selected {
  background: rgba(201, 167, 108, 0.3);
  border-color: rgba(201, 167, 108, 0.5);
}

/* Dropdown Transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Image Modal */
.image-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
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
  border-radius: 16px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
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

.image-modal-header .close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.image-modal-header .close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.image-modal-content {
  padding: 20px;
}

/* 이미지 탭 */
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
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
}

.tab-btn.active {
  background: rgba(201, 167, 108, 0.1);
  border-color: rgba(201, 167, 108, 0.3);
  color: #e8d5b7;
}

/* 업로드 섹션 */
.upload-section {
  margin-bottom: 16px;
}

.upload-dropzone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 32px;
  background: rgba(255, 255, 255, 0.02);
  border: 2px dashed var(--border-subtle);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-dropzone:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(201, 167, 108, 0.3);
}

.upload-dropzone.drag-over {
  background: rgba(201, 167, 108, 0.1);
  border-color: rgba(201, 167, 108, 0.5);
}

.upload-dropzone svg {
  color: var(--text-muted);
  opacity: 0.5;
}

.upload-dropzone span {
  font-size: 14px;
  color: var(--text-secondary);
}

.upload-dropzone .upload-hint {
  font-size: 12px;
  color: var(--text-muted);
}

.input-group {
  margin-bottom: 16px;
}

.input-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.input-group input {
  width: 100%;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  transition: all 0.15s ease;
}

.input-group input:focus {
  border-color: rgba(201, 167, 108, 0.5);
  box-shadow: 0 0 0 3px rgba(201, 167, 108, 0.1);
}

.input-group input::placeholder {
  color: var(--text-muted);
}

.image-preview-container {
  height: 200px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px dashed var(--border-subtle);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.image-preview {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
}

.image-placeholder svg {
  opacity: 0.3;
}

.image-placeholder span {
  font-size: 13px;
}

.image-loading,
.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  font-size: 13px;
}

.image-error {
  color: #f87171;
}

.image-loading .spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(201, 167, 108, 0.2);
  border-top-color: #e8d5b7;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.insert-position-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(201, 167, 108, 0.1);
  border-radius: 8px;
  font-size: 12px;
  color: #e8d5b7;
}

.image-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-subtle);
}

.btn-cancel,
.btn-insert {
  padding: 8px 20px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--text-muted);
}

.btn-insert {
  background: linear-gradient(135deg, #c9a76c, #a68b4d);
  border: none;
  color: #1a1a1a;
}

.btn-insert:hover:not(:disabled) {
  background: linear-gradient(135deg, #d4b87d, #b8995e);
}

.btn-insert:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  transform: scale(0.95) translateY(-10px);
}
</style>
