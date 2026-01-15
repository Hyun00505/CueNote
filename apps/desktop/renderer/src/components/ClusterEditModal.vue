<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="handleClose">
      <div class="modal-container">
        <!-- 헤더 -->
        <div class="modal-header">
          <h2>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3" />
              <circle cx="4" cy="8" r="2" />
              <circle cx="20" cy="8" r="2" />
              <circle cx="4" cy="16" r="2" />
              <circle cx="20" cy="16" r="2" />
            </svg>
            {{ isCreateMode ? '새 클러스터 만들기' : '클러스터 편집' }}
          </h2>
          <button class="close-btn" @click="handleClose">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <!-- 바디 -->
        <div class="modal-body">
          <!-- 클러스터 정보 -->
          <div class="cluster-preview">
            <span 
              class="color-dot" 
              :style="{ background: editedColor }"
            ></span>
            <span class="cluster-name">{{ editedLabel || cluster?.label || (isCreateMode ? '새 클러스터' : '클러스터') }}</span>
            <span class="note-count" v-if="!isCreateMode">{{ cluster?.noteCount || 0 }}개 노트</span>
            <span class="note-count new" v-else>새로 생성</span>
          </div>

          <!-- 라벨 수정 -->
          <div class="form-group">
            <label>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 20h9" />
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
              </svg>
              라벨
            </label>
            <input 
              v-model="editedLabel" 
              type="text" 
              :placeholder="cluster?.label || '클러스터 이름'"
              @keydown.enter="handleSave"
            />
            <span class="hint">AI가 생성한 라벨을 수정할 수 있습니다</span>
          </div>

          <!-- 색상 선택 -->
          <div class="form-group">
            <label>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="13.5" cy="6.5" r="2.5" />
                <circle cx="19" cy="13" r="2.5" />
                <circle cx="13.5" cy="19.5" r="2.5" />
                <circle cx="6.5" cy="13" r="2.5" />
              </svg>
              색상
            </label>
            <div class="color-picker">
              <button
                v-for="color in colorPalette"
                :key="color"
                class="color-btn"
                :class="{ active: editedColor === color }"
                :style="{ background: color }"
                @click="editedColor = color"
                :title="color"
              >
                <svg v-if="editedColor === color" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </button>
              <!-- 커스텀 색상 (그라데이션 버튼) -->
              <div class="custom-color-btn">
                <input 
                  type="color" 
                  v-model="editedColor"
                  class="custom-color-input"
                  title="커스텀 색상 선택"
                />
                <div class="gradient-overlay"></div>
              </div>
            </div>
          </div>

          <!-- 키워드 수정 -->
          <div class="form-group">
            <label>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
                <line x1="7" y1="7" x2="7.01" y2="7" />
              </svg>
              키워드
            </label>
            <div class="keywords-input">
              <div class="keyword-tags">
                <span 
                  v-for="(keyword, index) in editedKeywords" 
                  :key="index"
                  class="keyword-tag"
                >
                  {{ keyword }}
                  <button class="remove-keyword" @click="removeKeyword(index)">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  </button>
                </span>
              </div>
              <input 
                v-model="newKeyword" 
                type="text" 
                placeholder="키워드 추가 (Enter)"
                @keydown.enter.prevent="addKeyword"
              />
            </div>
            <span class="hint">클러스터를 설명하는 키워드를 추가하세요</span>
          </div>
        </div>

        <!-- 푸터 -->
        <div class="modal-footer">
          <div class="footer-left" v-if="!isCreateMode">
            <!-- 삭제 버튼 (확인 전) -->
            <button 
              v-if="!showDeleteConfirm" 
              class="btn-danger-outline" 
              @click="toggleDeleteConfirm"
              title="클러스터 삭제"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                <line x1="10" y1="11" x2="10" y2="17"/>
                <line x1="14" y1="11" x2="14" y2="17"/>
              </svg>
              삭제
            </button>
            <!-- 삭제 확인 -->
            <div v-else class="delete-confirm-group">
              <span class="delete-confirm-text">정말 삭제?</span>
              <button class="btn-danger" @click="handleDelete">삭제</button>
              <button class="btn-cancel-sm" @click="toggleDeleteConfirm">취소</button>
            </div>
          </div>
          <div class="footer-left" v-else></div>
          
          <div class="btn-group" v-if="!showDeleteConfirm">
            <button v-if="!isCreateMode" class="btn-secondary" @click="handleReset">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              복원
            </button>
            <button class="btn-cancel" @click="handleClose">취소</button>
            <button 
              class="btn-primary" 
              @click="handleSave" 
              :disabled="isSaving || (isCreateMode && !editedLabel.trim())"
            >
              <svg v-if="isSaving" class="spinning" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
              {{ isSaving ? (isCreateMode ? '생성 중...' : '저장 중...') : (isCreateMode ? '생성' : '저장') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import type { ClusterInfo } from '../types';

const props = defineProps<{
  visible: boolean;
  cluster: ClusterInfo | null;
  isCreateMode?: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', data: { id: number; label: string; color: string; keywords: string[] }): void;
  (e: 'reset', clusterId: number): void;
  (e: 'create', data: { label: string; color: string; keywords: string[] }): void;
  (e: 'delete', clusterId: number): void;
}>();

// 삭제 확인 상태
const showDeleteConfirm = ref(false);

// 파스텔 톤 색상 팔레트 (무지개 순서)
const colorPalette = [
  '#fca5a5', // 빨강
  '#fdba74', // 주황
  '#fcd34d', // 노랑
  '#bef264', // 연두
  '#86efac', // 초록
  '#5eead4', // 청록
  '#67e8f9', // 하늘
  '#93c5fd', // 파랑
  '#a5b4fc', // 남색
  '#c4b5fd', // 보라
  '#f9a8d4', // 분홍
];

// 편집 상태
const editedLabel = ref('');
const editedColor = ref('#c4b5fd'); // 기본 파스텔 보라색
const editedKeywords = ref<string[]>([]);
const newKeyword = ref('');
const isSaving = ref(false);

// 클러스터 변경 시 또는 생성 모드일 때 초기값 설정
watch([() => props.cluster, () => props.visible, () => props.isCreateMode], ([newCluster, visible, isCreate]) => {
  if (visible) {
    if (isCreate) {
      // 생성 모드: 빈 값으로 초기화
      editedLabel.value = '';
      editedColor.value = colorPalette[Math.floor(Math.random() * colorPalette.length)];
      editedKeywords.value = [];
    } else if (newCluster) {
      // 편집 모드: 기존 값으로 초기화
      editedLabel.value = newCluster.label || '';
      editedColor.value = newCluster.color || '#8b5cf6';
      editedKeywords.value = [...(newCluster.keywords || [])];
    }
  }
}, { immediate: true });

// 키워드 추가
function addKeyword() {
  const keyword = newKeyword.value.trim();
  if (keyword && !editedKeywords.value.includes(keyword)) {
    editedKeywords.value.push(keyword);
    newKeyword.value = '';
  }
}

// 키워드 제거
function removeKeyword(index: number) {
  editedKeywords.value.splice(index, 1);
}

// 저장
async function handleSave() {
  isSaving.value = true;
  
  if (props.isCreateMode) {
    // 생성 모드
    if (!editedLabel.value.trim()) {
      isSaving.value = false;
      return;
    }
    
    emit('create', {
      label: editedLabel.value,
      color: editedColor.value,
      keywords: editedKeywords.value
    });
  } else if (props.cluster) {
    // 편집 모드
    emit('save', {
      id: props.cluster.id,
      label: editedLabel.value || props.cluster.label,
      color: editedColor.value,
      keywords: editedKeywords.value
    });
  }
  
  // 짧은 딜레이 후 닫기 (UX)
  setTimeout(() => {
    isSaving.value = false;
    emit('close');
  }, 300);
}

// AI 설정으로 복원
function handleReset() {
  if (!props.cluster) return;
  emit('reset', props.cluster.id);
  emit('close');
}

// 삭제 확인 토글
function toggleDeleteConfirm() {
  showDeleteConfirm.value = !showDeleteConfirm.value;
}

// 클러스터 삭제
function handleDelete() {
  if (!props.cluster) return;
  emit('delete', props.cluster.id);
  emit('close');
}

// 닫기
function handleClose() {
  showDeleteConfirm.value = false;
  emit('close');
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-container {
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  width: 420px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 헤더 */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-header h2 svg {
  color: var(--accent-primary, #8b5cf6);
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* 바디 */
.modal-body {
  padding: 24px;
  overflow-y: auto;
  max-height: calc(90vh - 180px);
}

/* 클러스터 프리뷰 */
.cluster-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  margin-bottom: 20px;
}

.color-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.cluster-name {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.note-count {
  font-size: 12px;
  color: var(--text-muted);
  background: var(--bg-primary);
  padding: 4px 10px;
  border-radius: 12px;
}

.note-count.new {
  color: var(--accent-primary, #8b5cf6);
  background: rgba(139, 92, 246, 0.1);
}

/* 폼 그룹 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.form-group label svg {
  color: var(--text-muted);
}

.form-group input[type="text"] {
  width: 100%;
  padding: 12px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.15s ease;
}

.form-group input[type="text"]:focus {
  outline: none;
  border-color: var(--accent-primary, #8b5cf6);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

.form-group input::placeholder {
  color: var(--text-muted);
}

.hint {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 6px;
}

/* 색상 선택 */
.color-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.color-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.color-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.color-btn.active {
  border-color: white;
  box-shadow: 0 0 0 2px var(--accent-primary, #8b5cf6);
}

/* 커스텀 색상 버튼 (그라데이션) */
.custom-color-btn {
  position: relative;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
}

.custom-color-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
  padding: 0;
  cursor: pointer;
  opacity: 0;
  z-index: 2;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: conic-gradient(
    from 0deg,
    #ff6b6b,
    #ffd93d,
    #6bcb77,
    #4d96ff,
    #9b59b6,
    #ff6b6b
  );
  border-radius: 8px;
  pointer-events: none;
}

.custom-color-btn:hover .gradient-overlay {
  filter: brightness(1.15);
  transform: scale(1.1);
}

.custom-color-btn:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* 키워드 입력 */
.keywords-input {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 8px;
  transition: all 0.15s ease;
}

.keywords-input:focus-within {
  border-color: var(--accent-primary, #8b5cf6);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.keyword-tags:empty {
  margin-bottom: 0;
}

.keyword-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: rgba(139, 92, 246, 0.15);
  border: 1px solid rgba(139, 92, 246, 0.25);
  border-radius: 12px;
  font-size: 12px;
  color: var(--accent-primary, #a78bfa);
}

.remove-keyword {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  transition: all 0.15s ease;
}

.remove-keyword:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.keywords-input input {
  width: 100%;
  padding: 6px 8px;
  background: transparent;
  border: none;
  font-size: 13px;
  color: var(--text-primary);
}

.keywords-input input:focus {
  outline: none;
}

/* 푸터 */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-group {
  display: flex;
  gap: 10px;
}

/* 삭제 버튼 스타일 */
.btn-danger-outline {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-danger-outline:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.5);
}

.delete-confirm-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.delete-confirm-text {
  font-size: 12px;
  color: #ef4444;
  font-weight: 500;
}

.btn-danger {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #ef4444;
  border: 1px solid #ef4444;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-danger:hover {
  background: #dc2626;
  border-color: #dc2626;
}

.btn-cancel-sm {
  display: flex;
  align-items: center;
  padding: 6px 10px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel-sm:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-secondary,
.btn-cancel,
.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-secondary {
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--text-muted);
}

.btn-secondary:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-cancel {
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.btn-cancel:hover {
  background: var(--bg-hover);
}

.btn-primary {
  background: var(--accent-primary, #8b5cf6);
  border: 1px solid var(--accent-primary, #8b5cf6);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  filter: brightness(1.1);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
