<template>
  <div v-if="localNoteClusterInfo?.hasCluster && showClusterBadge" class="cluster-badge-group">
    <div 
      class="cluster-badge"
      :style="{ '--cluster-color': localNoteClusterInfo.cluster?.color || '#8b5cf6' }"
      :title="`클러스터: ${localNoteClusterInfo.cluster?.label}`"
    >
      <span class="cluster-dot" :style="{ background: localNoteClusterInfo.cluster?.color }"></span>
      <span class="cluster-label">{{ localNoteClusterInfo.cluster?.label }}</span>
      <!-- 잠금 상태 토글 버튼 -->
      <button 
        class="cluster-lock-btn" 
        :class="{ locked: localNoteClusterInfo.isLocked }"
        @click.stop="toggleNoteLock"
        :title="localNoteClusterInfo.isLocked ? '클러스터 잠금 해제' : '클러스터 잠금'"
      >
        <!-- 잠긴 상태: 닫힌 자물쇠 -->
        <svg v-if="localNoteClusterInfo.isLocked" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
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
  </div>

  <!-- 클러스터 배지 숨겨진 상태 - 다시 보기 버튼 -->
  <button 
    v-else-if="localNoteClusterInfo?.hasCluster && !showClusterBadge" 
    class="toolbar-btn cluster-show-btn"
    :style="{ '--cluster-color': localNoteClusterInfo.cluster?.color || '#8b5cf6' }"
    @click="showClusterBadge = true"
    title="클러스터 정보 보기"
  >
    <span class="cluster-dot-mini" :style="{ background: localNoteClusterInfo.cluster?.color }"></span>
  </button>

  <!-- 클러스터 정보 없음 (그래프 미생성) -->
  <button 
    v-else-if="localNoteClusterInfo && !localNoteClusterInfo.hasCluster && showClusterBadge" 
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
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';

const props = defineProps<{
  activeFile?: string | null;
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

const localNoteClusterInfo = ref<NoteClusterInfo | null>(null);
const showClusterBadge = ref(true);

// 클러스터 정보 로드
const loadNoteClusterInfo = async () => {
  if (!props.activeFile) {
    localNoteClusterInfo.value = null;
    return;
  }
  
  try {
    const filePath = props.activeFile.replace(/\\/g, '/');
    const response = await fetch(`http://127.0.0.1:8787/graph/note-info/${encodeURIComponent(filePath)}`);
    
    if (response.ok) {
      const data = await response.json();
      localNoteClusterInfo.value = data;
    } else {
      localNoteClusterInfo.value = null;
    }
  } catch (err) {
    console.error('[ClusterBadge] Failed to load note cluster info:', err);
    localNoteClusterInfo.value = null;
  }
};

watch(() => props.activeFile, () => {
  loadNoteClusterInfo();
}, { immediate: true });

// 노트 클러스터 잠금/해제 토글
const toggleNoteLock = async () => {
  if (!props.activeFile || !localNoteClusterInfo.value) return;
  
  try {
    const newLockState = !localNoteClusterInfo.value.isLocked;
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
      localNoteClusterInfo.value.isLocked = newLockState;
    }
  } catch (err) {
    console.error('Failed to toggle note lock:', err);
  }
};
</script>

<style scoped>
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

.cluster-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cluster-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
  max-width: 100px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cluster-lock-btn {
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

.cluster-lock-btn:hover {
  background: var(--glass-highlight);
  color: var(--text-primary);
}

.cluster-lock-btn.locked {
  color: var(--cluster-color, #8b5cf6);
}

.cluster-lock-btn.locked:hover {
  color: #ef4444;
}

.cluster-close-btn {
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

.cluster-close-btn:hover {
  background: var(--glass-highlight);
  color: var(--text-primary);
}

.cluster-show-btn {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
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

.cluster-hint-btn {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 28px !important;
  height: 28px !important;
  padding: 0 !important;
  background: var(--surface-1) !important;
  border: 1px dashed var(--border-subtle) !important;
  color: var(--text-muted) !important;
  opacity: 0.6;
}

.cluster-hint-btn:hover {
  opacity: 1;
  border-color: var(--accent-primary, #8b5cf6) !important;
  color: var(--accent-primary, #8b5cf6) !important;
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
</style>
