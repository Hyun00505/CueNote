<template>
  <header class="main-header">
    <div class="header-left">
      <!-- 캘린더 뷰일 때 로고 표시 -->
      <div v-if="currentView === 'dashboard'" class="logo">
        <div class="logo-icon">
          <svg class="logo-svg" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="7" y="4" width="18" height="24" rx="2" fill="currentColor" opacity="0.15"/>
            <rect x="7" y="4" width="18" height="24" rx="2" stroke="currentColor" stroke-width="1.5" opacity="0.6"/>
            <line x1="11" y1="11" x2="21" y2="11" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.4"/>
            <line x1="11" y1="16" x2="18" y2="16" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.3"/>
            <line x1="11" y1="21" x2="19" y2="21" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.2"/>
          </svg>
        </div>
        <span class="logo-text">
          <span class="logo-cue">Cue</span><span class="logo-note">Note</span>
        </span>
      </div>
      <!-- 파일 선택 시 breadcrumb (폴더 경로만 표시) -->
      <div class="breadcrumb" v-else-if="activeFile">
        <span class="breadcrumb-vault">{{ vaultName }}</span>
        <template v-if="getFolderPath(activeFile)">
          <span class="breadcrumb-sep">/</span>
          <span class="breadcrumb-folder">{{ getFolderPath(activeFile) }}</span>
        </template>
      </div>
      <div v-else class="welcome-text">
        <span>{{ t('header.selectNote') }}</span>
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
          <span>{{ t('header.editor') }}</span>
        </button>
        <button
          class="tab-btn"
          :class="{ active: currentView === 'dashboard' }"
          @click="$emit('change-view', 'dashboard')"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <span>{{ t('header.calendar') }}</span>
        </button>
        <button
          class="tab-btn"
          :class="{ active: currentView === 'graph' }"
          @click="$emit('change-view', 'graph')"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <circle cx="4" cy="8" r="2"/>
            <circle cx="20" cy="8" r="2"/>
            <circle cx="4" cy="16" r="2"/>
            <circle cx="20" cy="16" r="2"/>
            <line x1="6" y1="8" x2="9" y2="10"/>
            <line x1="18" y1="8" x2="15" y2="10"/>
            <line x1="6" y1="16" x2="9" y2="14"/>
            <line x1="18" y1="16" x2="15" y2="14"/>
          </svg>
          <span>{{ t('header.graph') }}</span>
        </button>
      </div>

      <button class="settings-btn" @click="$emit('open-settings')" title="설정">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import type { ViewType } from '../types';
import { useI18n } from '../composables';

const { t } = useI18n();

const props = defineProps<{
  activeFile: string | null;
  vaultName: string | null;
  currentView: ViewType;
}>();

const emit = defineEmits<{
  'change-view': [view: ViewType];
  'open-settings': [];
}>();

// 폴더 경로 추출 (파일명 제외)
function getFolderPath(path: string): string | null {
  const parts = path.split('/');
  if (parts.length <= 1) return null; // 루트에 있는 파일
  return parts.slice(0, -1).join('/');
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

/* 로고 스타일 */
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

.logo-icon:hover {
  color: var(--text-primary);
}

.logo-svg {
  width: 24px;
  height: 24px;
}

.logo-text {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.3px;
  display: flex;
  align-items: baseline;
}

.logo-cue {
  color: var(--text-primary);
  font-family: var(--font-sans);
}

.logo-note {
  color: var(--text-muted);
  font-family: var(--font-sans);
  font-weight: 400;
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

.breadcrumb-folder {
  color: var(--text-secondary);
  font-weight: 450;
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
  color: var(--text-primary);
  background: var(--bg-hover);
}

.tab-btn svg {
  opacity: 0.7;
}

.tab-btn.active svg {
  opacity: 1;
}

.settings-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
  margin-left: 8px;
}

.settings-btn:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
}

.settings-btn:active {
  transform: scale(0.95);
}
</style>
