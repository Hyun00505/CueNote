<template>
  <div 
    v-if="show" 
    class="context-menu"
    :style="{ left: pos.x + 'px', top: pos.y + 'px' }"
    @click.stop
  >
    <div class="context-menu-header">
      <span class="context-note-name">{{ node?.label }}</span>
    </div>
    <div class="context-menu-items">
      <button
        class="context-menu-item"
        @click="emit('open-note', node?.id)"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
          <polyline points="15 3 21 3 21 9" />
          <line x1="10" y1="14" x2="21" y2="3" />
        </svg>
        노트 열기
      </button>
      <button
        class="context-menu-item"
        @click="emit('show-related')"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="12" cy="12" r="3" />
          <circle cx="4" cy="8" r="2" />
          <circle cx="20" cy="8" r="2" />
          <circle cx="4" cy="16" r="2" />
          <circle cx="20" cy="16" r="2" />
        </svg>
        관련 노트 보기
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
}>();

const emit = defineEmits<{
  (e: 'open-note', path?: string): void;
  (e: 'show-related'): void;
}>();
</script>

<style scoped>
.context-menu {
  position: fixed;
  z-index: 1000;
  min-width: 180px;
  max-width: 240px;
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
  padding: 10px 14px;
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
}

.context-menu-items {
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
  font-size: 13px;
}

.context-menu-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
</style>
