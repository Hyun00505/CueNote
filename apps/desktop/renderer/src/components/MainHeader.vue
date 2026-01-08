<template>
  <header class="main-header">
    <div class="header-left">
      <div class="breadcrumb" v-if="activeFile">
        <div class="breadcrumb-icon">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <span class="breadcrumb-item vault">{{ vaultName }}</span>
        <svg class="breadcrumb-separator" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
        <span class="breadcrumb-item current">{{ getFileName(activeFile) }}</span>
      </div>
      <div v-else class="welcome-text">
        <div class="welcome-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4M12 8h.01"/>
          </svg>
        </div>
        <span>Select a file to get started</span>
      </div>
    </div>

    <div class="header-actions">
      <div class="view-tabs">
        <button
          class="tab-btn"
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
          class="tab-btn"
          :class="{ active: currentView === 'dashboard' }"
          @click="$emit('change-view', 'dashboard')"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
          </svg>
          <span>Dashboard</span>
        </button>
        <div class="tab-indicator" :class="currentView"></div>
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
  padding: 0 28px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  min-height: var(--header-height);
  position: relative;
}

.main-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent-glow), transparent);
  opacity: 0.5;
}

.header-left {
  display: flex;
  align-items: center;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.breadcrumb-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--accent-secondary);
}

.breadcrumb-item {
  font-size: 13px;
  color: var(--text-muted);
  transition: color var(--transition-fast);
}

.breadcrumb-item.vault {
  padding: 4px 10px;
  background: var(--glass-bg);
  border-radius: var(--radius-xs);
  font-weight: 500;
}

.breadcrumb-item.vault:hover {
  color: var(--text-secondary);
}

.breadcrumb-item.current {
  color: var(--text-primary);
  font-weight: 600;
  padding: 4px 12px;
  background: var(--gradient-primary);
  border-radius: var(--radius-xs);
  color: white;
  box-shadow: var(--shadow-xs), 0 0 12px var(--accent-glow);
}

.breadcrumb-separator {
  color: var(--text-muted);
  opacity: 0.5;
}

.welcome-text {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: var(--text-muted);
  animation: slideDown 0.3s ease;
}

.welcome-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.view-tabs {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: var(--glass-bg);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  position: relative;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  z-index: 1;
}

.tab-btn:hover {
  color: var(--text-secondary);
}

.tab-btn.active {
  color: white;
}

.tab-btn svg {
  transition: transform var(--transition-fast);
}

.tab-btn:hover svg {
  transform: scale(1.1);
}

.tab-indicator {
  position: absolute;
  top: 4px;
  bottom: 4px;
  width: calc(50% - 4px);
  background: var(--gradient-primary);
  border-radius: var(--radius-sm);
  transition: transform var(--transition-smooth);
  box-shadow: var(--shadow-sm), 0 0 20px var(--accent-glow);
}

.tab-indicator.editor {
  transform: translateX(0);
}

.tab-indicator.dashboard {
  transform: translateX(calc(100% + 4px));
}
</style>
