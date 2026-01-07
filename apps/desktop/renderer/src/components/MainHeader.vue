<template>
  <header class="main-header">
    <div class="header-left">
      <div class="breadcrumb" v-if="activeFile">
        <span class="breadcrumb-item">{{ vaultName }}</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
        <span class="breadcrumb-item current">{{ getFileName(activeFile) }}</span>
      </div>
      <div v-else class="welcome-text">
        <span>Welcome to CueNote</span>
      </div>
    </div>
    <div class="header-actions">
      <button 
        class="action-btn" 
        :class="{ active: currentView === 'editor' }"
        @click="$emit('change-view', 'editor')"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
        <span>Editor</span>
      </button>
      <button 
        class="action-btn" 
        :class="{ active: currentView === 'dashboard' }"
        @click="$emit('change-view', 'dashboard')"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"/>
          <rect x="14" y="3" width="7" height="7"/>
          <rect x="14" y="14" width="7" height="7"/>
          <rect x="3" y="14" width="7" height="7"/>
        </svg>
        <span>Dashboard</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import type { ViewType } from '../types';

defineProps<{
  activeFile: string | null;
  vaultName: string | null;
  currentView: ViewType;
}>();

defineEmits<{
  'change-view': [view: ViewType];
}>();

function getFileName(path: string): string {
  return path.split(/[/\\]/).pop() || path;
}
</script>

<style scoped>
.main-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  min-height: var(--header-height);
}

.header-left {
  display: flex;
  align-items: center;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.breadcrumb-item {
  color: var(--text-muted);
}

.breadcrumb-item.current {
  color: var(--text-primary);
  font-weight: 500;
}

.welcome-text {
  font-size: 14px;
  color: var(--text-secondary);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: transparent;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.action-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: white;
}
</style>


