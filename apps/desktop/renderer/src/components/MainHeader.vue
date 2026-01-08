<template>
  <header class="main-header">
    <div class="header-left">
      <div class="breadcrumb" v-if="activeFile">
        <span class="breadcrumb-vault">{{ vaultName }}</span>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-file">{{ getFileName(activeFile) }}</span>
      </div>
      <div v-else class="welcome-text">
        <span>Select a note to begin</span>
      </div>
    </div>

    <div class="header-actions">
      <div class="view-tabs">
        <button
          class="tab-btn"
          :class="{ active: currentView === 'editor' }"
          @click="$emit('change-view', 'editor')"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          <span>Editor</span>
        </button>
        <button
          class="tab-btn"
          :class="{ active: currentView === 'dashboard' }"
          @click="$emit('change-view', 'dashboard')"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
          </svg>
          <span>Dashboard</span>
        </button>
      </div>
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
  padding: 0 24px;
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
  gap: 6px;
  font-size: 13px;
}

.breadcrumb-vault {
  color: var(--text-muted);
  font-weight: 450;
}

.breadcrumb-sep {
  color: var(--text-muted);
  opacity: 0.4;
}

.breadcrumb-file {
  color: var(--text-primary);
  font-weight: 500;
}

.welcome-text {
  font-size: 13px;
  color: var(--text-muted);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.view-tabs {
  display: flex;
  gap: 2px;
  padding: 3px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.03);
}

.tab-btn.active {
  color: #e8d5b7;
  background: rgba(232, 213, 183, 0.1);
}

.tab-btn svg {
  opacity: 0.7;
}

.tab-btn.active svg {
  opacity: 1;
}
</style>
