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

    <!-- 클러스터 배지 -->
    <div v-if="noteClusterInfo?.hasCluster && showClusterBadge" class="cluster-badge-group">
      <div 
        class="cluster-badge"
        :style="{ '--cluster-color': noteClusterInfo.cluster?.color || '#8b5cf6' }"
        :title="`클러스터: ${noteClusterInfo.cluster?.label}`"
      >
        <span class="cluster-dot" :style="{ background: noteClusterInfo.cluster?.color }"></span>
        <span class="cluster-label">{{ noteClusterInfo.cluster?.label }}</span>
        <!-- 잠금 상태 토글 버튼 -->
        <button 
          class="cluster-lock-btn" 
          :class="{ locked: noteClusterInfo.isLocked }"
          @click.stop="toggleNoteLock"
          :title="noteClusterInfo.isLocked ? '클러스터 잠금 해제' : '클러스터 잠금'"
        >
          <!-- 잠긴 상태: 닫힌 자물쇠 -->
          <svg v-if="noteClusterInfo.isLocked" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <!-- 열린 상태: 열린 자물쇠 -->
          <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 9.9-1" />
          </svg>
        </button>
        <!-- 닫기 버튼 -->
        <button class="cluster-close-btn" @click="showClusterBadge = false" title="클러스터 배지 숨기기">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
      <div v-if="noteClusterInfo.cluster?.keywords?.length" class="cluster-keywords">
        <span 
          v-for="keyword in noteClusterInfo.cluster.keywords.slice(0, 3)" 
          :key="keyword"
          class="keyword-tag"
          :title="`키워드: ${keyword}`"
        >
          {{ keyword }}
        </span>
      </div>
    </div>

    <!-- 클러스터 배지 숨겨진 상태 - 다시 보기 버튼 -->
    <button 
      v-else-if="noteClusterInfo?.hasCluster && !showClusterBadge" 
      class="toolbar-btn cluster-show-btn"
      :style="{ '--cluster-color': noteClusterInfo.cluster?.color || '#8b5cf6' }"
      @click="showClusterBadge = true"
      title="클러스터 정보 보기"
    >
      <span class="cluster-dot-mini" :style="{ background: noteClusterInfo.cluster?.color }"></span>
    </button>

    <!-- 클러스터 정보 없음 (그래프 미생성) -->
    <button 
      v-else-if="noteClusterInfo && !noteClusterInfo.hasCluster && showClusterBadge" 
      class="toolbar-btn cluster-hint-btn"
      @click="showClusterBadge = false"
      title="그래프 뷰에서 AI 분석을 실행하면 클러스터 정보가 표시됩니다"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="3" />
        <circle cx="4" cy="8" r="2" opacity="0.5" />
        <circle cx="20" cy="8" r="2" opacity="0.5" />
      </svg>
    </button>

    <div v-if="noteClusterInfo?.hasCluster || (noteClusterInfo && !noteClusterInfo.hasCluster && showClusterBadge)" class="toolbar-divider"></div>

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
      <button
        class="toolbar-btn ai-btn extract-btn"
        :class="{ loading: extracting }"
        :disabled="extracting"
        @click="showExtractModal = true"
        title="PDF/이미지 → 마크다운 변환"
      >
        <svg v-if="!extracting" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <path d="M12 18v-6"/>
          <path d="m9 15 3-3 3 3"/>
        </svg>
        <span v-else class="spinner"></span>
        <span class="ai-label">문서 변환</span>
      </button>
      <button
        class="toolbar-btn ai-btn pdf-btn"
        :class="{ loading: exportingPdf }"
        :disabled="exportingPdf"
        @click="exportToPdf"
        title="PDF로 저장"
      >
        <svg v-if="!exportingPdf" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <path d="M12 12v6"/>
          <path d="m15 15-3 3-3-3"/>
        </svg>
        <span v-else class="spinner"></span>
        <span class="ai-label">PDF 저장</span>
      </button>
    </div>

    <!-- 문서 추출 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showExtractModal" class="extract-modal-overlay" @click.self="closeExtractModal">
          <div class="extract-modal">
            <div class="extract-modal-header">
              <h3>📄 PDF/이미지 → 마크다운 변환</h3>
              <button class="close-btn" @click="closeExtractModal">
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
                :class="{ 'drag-over': isExtractDragging, 'has-file': extractFile }"
                @dragenter="isExtractDragging = true"
                @dragleave="isExtractDragging = false"
                @dragover.prevent
                @drop.prevent="handleExtractFileDrop"
                @click="triggerExtractFileInput"
              >
                <input 
                  ref="extractFileInputRef"
                  type="file" 
                  accept=".pdf,image/*" 
                  style="display: none"
                  @change="handleExtractFileSelect"
                />
                <div v-if="!extractFile" class="dropzone-empty">
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
                    <svg v-if="extractFileType === 'pdf'" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
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
                    <span class="file-name">{{ extractFile?.name }}</span>
                    <span class="file-size">{{ formatFileSize(extractFile?.size || 0) }}</span>
                  </div>
                  <button class="remove-file-btn" @click.stop="clearExtractFile" title="파일 제거">
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
              <div v-else-if="extractFile" class="ocr-info ocr-ready">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span>OCR 준비됨 - {{ selectedOcrEngineName }}로 텍스트를 추출합니다.</span>
              </div>

              <!-- 텍스트만 가져오기 옵션 -->
              <div v-if="extractFile" class="extract-options">
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
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>{{ extractError }}</span>
              </div>
            </div>
            <div class="extract-modal-footer">
              <button class="btn-cancel" @click="closeExtractModal">취소</button>
              <button
                v-if="!extractResult"
                class="btn-extract"
                :disabled="!extractFile || extracting"
                @click="handleExtract"
              >
                <span v-if="extracting" class="spinner"></span>
                <span>{{ extracting ? '변환 중...' : '변환하기' }}</span>
              </button>
              <button
                v-else
                class="btn-insert"
                @click="insertExtractResult"
              >
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
import { useSettings } from '../composables';
import { GEMINI_VISION_MODELS } from '../composables/useSettings';

const CORE_BASE = 'http://127.0.0.1:8787';

const props = defineProps<{
  editor: Editor | null;
  summarizing?: boolean;
  noteName?: string;  // 현재 노트 파일명
  activeFile?: string | null;  // 현재 활성 파일 경로
  llmSettings?: {
    provider: string;
    apiKey: string;
    model: string;
  };
}>();

// 클러스터 정보 타입
interface ClusterInfo {
  id: number;
  label: string;
  color: string;
  keywords: string[];
}

interface NoteClusterInfo {
  notePath: string;
  hasCluster: boolean;
  cluster: ClusterInfo | null;
  isLocked: boolean;
}

// 노트 클러스터 정보
const noteClusterInfo = ref<NoteClusterInfo | null>(null);
const showClusterBadge = ref(true);

// 클러스터 정보 로드
const loadNoteClusterInfo = async () => {
  if (!props.activeFile) {
    noteClusterInfo.value = null;
    return;
  }
  
  try {
    // 파일 경로에서 vault 경로를 제거하고 상대 경로만 사용
    const filePath = props.activeFile.replace(/\\/g, '/');
    console.log('[ClusterBadge] Loading info for:', filePath);
    
    const response = await fetch(`http://127.0.0.1:8787/graph/note-info/${encodeURIComponent(filePath)}`);
    console.log('[ClusterBadge] Response status:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('[ClusterBadge] Data:', data);
      noteClusterInfo.value = data;
    } else {
      const errorText = await response.text();
      console.warn('[ClusterBadge] Error response:', errorText);
      noteClusterInfo.value = null;
    }
  } catch (err) {
    console.error('[ClusterBadge] Failed to load note cluster info:', err);
    noteClusterInfo.value = null;
  }
};

// activeFile 변경 시 클러스터 정보 다시 로드
watch(() => props.activeFile, () => {
  loadNoteClusterInfo();
}, { immediate: true });

// 노트 클러스터 잠금/해제 토글
const toggleNoteLock = async () => {
  if (!props.activeFile || !noteClusterInfo.value) return;
  
  try {
    const newLockState = !noteClusterInfo.value.isLocked;
    const response = await fetch(`http://127.0.0.1:8787/graph/lock-note`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        notePath: props.activeFile, 
        locked: newLockState 
      })
    });
    
    if (response.ok) {
      // 로컬 상태 업데이트
      noteClusterInfo.value.isLocked = newLockState;
    }
  } catch (err) {
    console.error('Failed to toggle note lock:', err);
  }
};

const emit = defineEmits<{
  (e: 'summarize'): void;
  (e: 'extract-result', markdown: string): void;
}>();

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

// PDF 내보내기 상태
const exportingPdf = ref(false);


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

// LLM 설정 가져오기
const { settings: llmSettingsStore } = useSettings();

// Gemini API 키 확인
const hasGeminiApiKey = computed(() => {
  return llmSettingsStore.value.llm.provider === 'gemini' && !!llmSettingsStore.value.llm.apiKey;
});

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
    
    const res = await fetch(`${CORE_BASE}/ai/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_data: extractFileData.value,
        file_type: extractFileType.value,
        language: 'auto',  // 원문 언어 자동 감지
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
  
  // 마크다운을 에디터에 삽입
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

// OCR 모델 다운로드
async function downloadOcrModel() {
  ocrDownloading.value = true;
  extractError.value = '';
  
  try {
    const res = await fetch(`${CORE_BASE}/ai/ocr/download`, {
      method: 'POST'
    });
    
    const data = await res.json();
    
    if (data.success) {
      // 상태 갱신
      await checkOcrStatus();
    } else {
      extractError.value = data.message || '모델 다운로드에 실패했습니다.';
    }
  } catch (error) {
    console.error('OCR model download failed:', error);
    extractError.value = '모델 다운로드에 실패했습니다. 네트워크를 확인해주세요.';
  } finally {
    ocrDownloading.value = false;
  }
}

// 모달 열 때 OCR 상태 확인
watch(showExtractModal, (isOpen) => {
  if (isOpen) {
    checkOcrStatus();
    rawTextOnly.value = false; // 모달 열 때 초기화
  }
});
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

/* Cluster Badge Styles */
.cluster-badge-group {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 8px;
}

.cluster-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: color-mix(in srgb, var(--cluster-color, #8b5cf6) 15%, transparent);
  border: 1px solid color-mix(in srgb, var(--cluster-color, #8b5cf6) 30%, transparent);
  border-radius: 12px;
  cursor: default;
  transition: all 0.15s ease;
}

.cluster-badge:hover {
  background: color-mix(in srgb, var(--cluster-color, #8b5cf6) 20%, transparent);
  border-color: color-mix(in srgb, var(--cluster-color, #8b5cf6) 40%, transparent);
}

.cluster-badge .cluster-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cluster-badge .cluster-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
  max-width: 100px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cluster-badge .cluster-lock-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  margin-left: 4px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.cluster-badge .cluster-lock-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.cluster-badge .cluster-lock-btn.locked {
  color: var(--cluster-color, #8b5cf6);
}

.cluster-badge .cluster-lock-btn.locked:hover {
  color: #ef4444;
}

.cluster-badge .cluster-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-left: 4px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 50%;
  color: var(--text-muted);
  cursor: pointer;
  opacity: 0;
  transition: all 0.15s ease;
}

.cluster-badge:hover .cluster-close-btn {
  opacity: 1;
}

.cluster-badge .cluster-close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

/* 클러스터 배지 숨겨진 상태 - 다시 보기 버튼 */
.cluster-show-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px !important;
  height: 24px !important;
  padding: 0 !important;
  background: color-mix(in srgb, var(--cluster-color, #8b5cf6) 15%, transparent) !important;
  border: 1px solid color-mix(in srgb, var(--cluster-color, #8b5cf6) 30%, transparent) !important;
  border-radius: 50% !important;
}

.cluster-show-btn:hover {
  background: color-mix(in srgb, var(--cluster-color, #8b5cf6) 25%, transparent) !important;
  border-color: color-mix(in srgb, var(--cluster-color, #8b5cf6) 50%, transparent) !important;
}

.cluster-dot-mini {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

/* 클러스터 미생성 힌트 버튼 */
.cluster-hint-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px !important;
  height: 28px !important;
  padding: 0 !important;
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1px dashed var(--border-subtle) !important;
  color: var(--text-muted) !important;
  opacity: 0.6;
}

.cluster-hint-btn:hover {
  opacity: 1;
  border-color: var(--accent-primary, #8b5cf6) !important;
  color: var(--accent-primary, #8b5cf6) !important;
}

.cluster-keywords {
  display: flex;
  align-items: center;
  gap: 4px;
}

.keyword-tag {
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  font-size: 10px;
  color: var(--text-muted);
  cursor: default;
  transition: all 0.15s ease;
}

.keyword-tag:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-secondary);
}

/* AI Button Styles */
.ai-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  width: auto;
  padding: 0 10px;
  margin-left: 6px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.ai-btn:first-child {
  margin-left: 0;
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

/* Extract Button Style */
.extract-btn {
  background: rgba(16, 185, 129, 0.1) !important;
  border-color: rgba(16, 185, 129, 0.2) !important;
}

.extract-btn:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.2) !important;
  border-color: rgba(16, 185, 129, 0.4) !important;
  color: #34d399 !important;
}

/* Extract Modal */
.extract-modal-overlay {
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

.extract-modal {
  width: 520px;
  max-width: 90vw;
  max-height: 85vh;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.extract-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.extract-modal-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.extract-modal-header .close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.extract-modal-header .close-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
}

.extract-modal-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.extract-description {
  margin: 0 0 16px 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.extract-dropzone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 140px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.02);
  border: 2px dashed var(--border-subtle);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.extract-dropzone:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(16, 185, 129, 0.3);
}

.extract-dropzone.drag-over {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.5);
}

.extract-dropzone.has-file {
  border-style: solid;
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.05);
}

.dropzone-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.dropzone-empty svg {
  color: var(--text-muted);
  opacity: 0.5;
}

.dropzone-empty span {
  font-size: 14px;
  color: var(--text-secondary);
}

.dropzone-empty .upload-hint {
  font-size: 12px;
  color: var(--text-muted);
}

.dropzone-file {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.dropzone-file .file-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 10px;
  color: #34d399;
}

.dropzone-file .file-info {
  flex: 1;
  min-width: 0;
}

.dropzone-file .file-name {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropzone-file .file-size {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.remove-file-btn {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.remove-file-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

/* OCR 모델 상태 */
.ocr-model-status {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 16px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.1), rgba(245, 158, 11, 0.05));
  border: 1px solid rgba(234, 179, 8, 0.25);
  border-radius: 12px;
}

.model-status-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.model-status-header svg {
  flex-shrink: 0;
  color: #fbbf24;
  margin-top: 2px;
}

.model-status-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.model-title {
  font-size: 14px;
  font-weight: 600;
  color: #fbbf24;
}

.model-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

.btn-download-model {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-download-model:hover:not(:disabled) {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.btn-download-model:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-download-model .spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.ocr-info {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 16px;
  padding: 12px 14px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 10px;
  font-size: 13px;
  color: #60a5fa;
}

.ocr-info svg {
  flex-shrink: 0;
  margin-top: 1px;
}

.ocr-info.ocr-ready {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

/* 텍스트만 가져오기 옵션 */
.extract-options {
  margin-top: 16px;
  padding: 14px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 10px;
}

.extract-options .option-hint {
  font-size: 11px;
  font-weight: 400;
  color: var(--text-muted);
  margin-left: 4px;
}

.raw-text-info {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  font-size: 12px;
  color: #60a5fa;
  line-height: 1.5;
}

.raw-text-info svg {
  flex-shrink: 0;
  margin-top: 1px;
}

/* 손글씨 모드 옵션 */
.handwriting-option {
  margin-top: 16px;
  padding: 14px;
  background: rgba(139, 92, 246, 0.05);
  border: 1px solid rgba(139, 92, 246, 0.15);
  border-radius: 10px;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-wrapper input[type="checkbox"] {
  display: none;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(139, 92, 246, 0.4);
  border-radius: 4px;
  position: relative;
  transition: all 0.15s ease;
}

.checkbox-wrapper input:checked + .checkbox-custom {
  background: #8b5cf6;
  border-color: #8b5cf6;
}

.checkbox-wrapper input:checked + .checkbox-custom::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 2px;
  width: 5px;
  height: 9px;
  border: solid #fff;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-wrapper input:disabled + .checkbox-custom {
  opacity: 0.4;
  cursor: not-allowed;
}

.checkbox-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.checkbox-label .need-download {
  font-size: 11px;
  font-weight: 400;
  color: #fbbf24;
  margin-left: 6px;
}

.handwriting-warning {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(234, 179, 8, 0.1);
  border: 1px solid rgba(234, 179, 8, 0.2);
  border-radius: 8px;
  font-size: 12px;
  color: #fbbf24;
  line-height: 1.5;
}

.handwriting-warning svg {
  flex-shrink: 0;
  margin-top: 1px;
}

.handwriting-download {
  margin-top: 12px;
}

.btn-download-handwriting {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px 16px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-download-handwriting:hover:not(:disabled) {
  background: linear-gradient(135deg, #a78bfa, #8b5cf6);
}

.btn-download-handwriting:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-download-handwriting .spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.extract-result {
  margin-top: 16px;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 10px;
  overflow: hidden;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: rgba(16, 185, 129, 0.1);
  border-bottom: 1px solid rgba(16, 185, 129, 0.15);
}

.result-title {
  font-size: 13px;
  font-weight: 600;
  color: #34d399;
}

.result-meta {
  display: flex;
  gap: 12px;
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
  line-height: 1.6;
}

.extract-error {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 16px;
  padding: 12px 14px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 10px;
  font-size: 13px;
  color: #f87171;
}

.extract-error svg {
  flex-shrink: 0;
  margin-top: 1px;
}

.extract-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-subtle);
}

.btn-extract {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  color: #fff;
}

.btn-extract:hover:not(:disabled) {
  background: linear-gradient(135deg, #34d399, #10b981);
}

.btn-extract:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-extract .spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.modal-enter-from .extract-modal,
.modal-leave-to .extract-modal {
  transform: scale(0.95) translateY(-10px);
}
</style>
