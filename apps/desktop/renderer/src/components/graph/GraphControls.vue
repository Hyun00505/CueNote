<template>
  <div class="zoom-controls">
    <!-- 전체 잠금 버튼 (클러스터 필터 시에만 표시) -->
    <button 
      v-if="showOnlyCluster !== null"
      class="lock-all-btn"
      :class="{ locked: areAllFilteredNodesLocked }"
      @click="emit('lock-all')"
      :title="areAllFilteredNodesLocked ? '전체 잠금 해제' : '전체 잠금'"
    >
      <!-- 잠금된 상태: 닫힌 자물쇠 -->
      <svg v-if="areAllFilteredNodesLocked" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
      </svg>
      <!-- 잠금 안 된 상태: 열린 자물쇠 -->
      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
        <path d="M7 11V7a5 5 0 0 1 9.9-1" />
      </svg>
    </button>
    <button @click="emit('zoom-in')" title="확대">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
        <line x1="11" y1="8" x2="11" y2="14" />
        <line x1="8" y1="11" x2="14" y2="11" />
      </svg>
    </button>
    <button @click="emit('zoom-out')" title="축소">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
        <line x1="8" y1="11" x2="14" y2="11" />
      </svg>
    </button>
    <button @click="emit('reset-zoom')" title="초기화">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
        <path d="M3 3v5h5" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  showOnlyCluster: number | null | 'unclustered';
  areAllFilteredNodesLocked: boolean;
}>();

const emit = defineEmits<{
  (e: 'zoom-in'): void;
  (e: 'zoom-out'): void;
  (e: 'reset-zoom'): void;
  (e: 'lock-all'): void;
}>();
</script>

<style scoped>
.zoom-controls {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.zoom-controls button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.zoom-controls button:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary, #8b5cf6);
  color: var(--accent-primary, #8b5cf6);
}

.zoom-controls .lock-all-btn {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
  color: var(--accent-primary, #8b5cf6);
  margin-bottom: 8px;
}

.zoom-controls .lock-all-btn:hover {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.5);
}

.zoom-controls .lock-all-btn.locked {
  background: var(--accent-primary, #8b5cf6);
  color: #fff;
}

.zoom-controls .lock-all-btn.locked:hover {
  background: rgba(239, 68, 68, 0.8);
  border-color: rgba(239, 68, 68, 0.8);
}
</style>
