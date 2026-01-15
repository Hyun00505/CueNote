<template>
  <div 
    v-if="show" 
    class="context-menu"
    :style="{ left: pos.x + 'px', top: pos.y + 'px' }"
    @click.stop
  >
    <div class="context-menu-header">
      <div class="context-header-row">
        <span class="context-note-name">{{ node?.label }}</span>
        <span 
          v-if="node && isLocked" 
          class="lock-badge"
          title="클러스터 잠금됨"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
        </span>
      </div>
      <span class="context-hint">클러스터 이동</span>
    </div>
    <div class="context-menu-items">
      <button
        v-for="cluster in clusters"
        :key="cluster.id"
        class="context-menu-item"
        :class="{ current: node?.cluster === cluster.id }"
        @click="emit('move-to-cluster', cluster.id)"
      >
        <span class="cluster-dot" :style="{ background: cluster.color }"></span>
        <span class="cluster-label">{{ cluster.label }}</span>
        <svg 
          v-if="node?.cluster === cluster.id" 
          width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
        >
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </button>
    </div>
    <div class="context-menu-divider"></div>
    
    <!-- 연결 관리 -->
    <div class="context-menu-section">
      <span class="context-section-label">연결 관리</span>
      <div class="context-link-buttons">
        <button class="link-btn add" @click="emit('start-link-add')">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          연결 추가
        </button>
        <button class="link-btn remove" @click="emit('start-link-remove')">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          연결 삭제
        </button>
      </div>
    </div>
    
    <div class="context-menu-divider"></div>
    
    <div class="context-menu-footer">
      <!-- 잠금/해제 버튼 -->
      <button 
        class="lock-btn"
        :class="{ locked: isLocked }"
        @click="emit('toggle-lock')"
      >
        <!-- 잠금된 상태: 닫힌 자물쇠 -->
        <svg v-if="isLocked" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
        <!-- 잠금 안 된 상태: 열린 자물쇠 -->
        <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
          <path d="M7 11V7a5 5 0 0 1 9.9-1" />
        </svg>
        {{ isLocked ? '잠금 해제' : 'AI 분류 잠금' }}
      </button>
      <!-- AI 복원 버튼 -->
      <button 
        class="reset-btn" 
        @click="emit('reset-cluster')"
        :disabled="isLocked"
        :title="isLocked ? '잠금 해제 후 사용 가능' : ''"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
          <path d="M3 3v5h5" />
        </svg>
        AI 자동 분류로 복원
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GraphNode } from '../../types';

defineProps<{
  show: boolean;
  node: GraphNode | null;
  pos: { x: number; y: number };
  clusters: any[];
  isLocked: boolean;
}>();

const emit = defineEmits<{
  (e: 'move-to-cluster', clusterId: number): void;
  (e: 'start-link-add'): void;
  (e: 'start-link-remove'): void;
  (e: 'toggle-lock'): void;
  (e: 'reset-cluster'): void;
}>();
</script>

<style scoped>
.context-menu {
  position: fixed;
  z-index: 1000;
  min-width: 200px;
  max-width: 280px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  animation: contextMenuFadeIn 0.15s ease;
}

@keyframes contextMenuFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.context-menu-header {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
}

.context-note-name {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.context-hint {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.context-menu-items {
  max-height: 240px;
  overflow-y: auto;
  padding: 6px;
}

.context-menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.12s ease;
  text-align: left;
}

.context-menu-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.context-menu-item.current {
  background: rgba(139, 92, 246, 0.12);
  color: var(--accent-primary, #8b5cf6);
}

.context-menu-item .cluster-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.context-menu-item .cluster-label {
  flex: 1;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.context-menu-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 4px 0;
}

.context-menu-section {
  padding: 8px 12px;
}

.context-section-label {
  display: block;
  font-size: 10px;
  color: var(--text-muted);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.context-link-buttons {
  display: flex;
  gap: 6px;
}

.link-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px 8px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  font-size: 10px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.link-btn.add:hover {
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
  color: #22c55e;
}

.link-btn.remove:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
  color: #ef4444;
}

.context-menu-footer {
  padding: 8px;
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.context-header-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.lock-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  background: rgba(139, 92, 246, 0.2);
  border-radius: 4px;
  color: var(--accent-primary, #8b5cf6);
}

.lock-btn,
.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.lock-btn:hover,
.reset-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--accent-primary, #8b5cf6);
  color: var(--accent-primary, #8b5cf6);
}

.lock-btn.locked {
  background: rgba(139, 92, 246, 0.15);
  border-color: rgba(139, 92, 246, 0.3);
  color: var(--accent-primary, #8b5cf6);
}

.lock-btn.locked:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.reset-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
