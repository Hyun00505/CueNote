<template>
  <div class="editor-header">
    <div class="file-info">
      <div class="file-icon">
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
          <polyline points="14 2 14 8 20 8" />
        </svg>
      </div>
      <div class="file-details">
        <span class="file-name">{{ getSimpleFileName(activeFile) }}</span>
        <span class="file-ext">.md</span>
        <span
          v-if="isGithubFile"
          class="github-badge"
        >
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"
            />
          </svg>
          GitHub
        </span>
        <span
          v-if="isDirty"
          class="unsaved-dot"
          title="저장되지 않은 변경사항"
        />
      </div>
    </div>
    <!-- GitHub 파일 저장 버튼 -->
    <button
      v-if="isGithubFile"
      class="save-btn github-save-btn"
      :class="{ saving: stagingSaving, saved: stagingSaved }"
      :disabled="stagingSaving"
      @click="handleSaveGitHub"
    >
      <svg
        v-if="stagingSaved"
        class="check-icon"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
      >
        <path d="M20 6L9 17l-5-5" />
      </svg>
      <svg
        v-else-if="!stagingSaving"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
        <polyline points="17 21 17 13 7 13 7 21" />
        <polyline points="7 3 7 8 15 8" />
      </svg>
      <span
        v-else
        class="spinner"
      />
      <span v-if="stagingSaved">{{ t('common.save') }} ✓</span>
      <span v-else-if="stagingSaving">{{ t('common.loading') }}</span>
      <span v-else>{{ t('common.save') }}</span>
      <kbd v-if="!stagingSaved">Ctrl+S</kbd>
    </button>
    <!-- 로컬 파일 저장 버튼 -->
    <button
      v-else
      class="save-btn"
      :class="{ saving, saved }"
      :disabled="saving"
      @click="handleSave"
    >
      <svg
        v-if="saved"
        class="check-icon"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
      >
        <path d="M20 6L9 17l-5-5" />
      </svg>
      <svg
        v-else-if="!saving"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
        <polyline points="17 21 17 13 7 13 7 21" />
        <polyline points="7 3 7 8 15 8" />
      </svg>
      <span
        v-else
        class="spinner"
      />
      <span v-if="saved">{{ t('common.save') }} ✓</span>
      <span v-else-if="saving">{{ t('common.loading') }}</span>
      <span v-else>{{ t('common.save') }}</span>
      <kbd v-if="!saved">Ctrl+S</kbd>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from '../../composables';

const { t } = useI18n();

const props = defineProps<{
  activeFile: string | null;
  isGithubFile: boolean;
  isDirty: boolean;
  stagingSaving: boolean;
  stagingSaved: boolean;
  saving: boolean;
  saved: boolean;
}>();

const emit = defineEmits<{
  (e: 'save'): void;
  (e: 'save-github'): void;
}>();

function getSimpleFileName(path: string | null): string {
  if (!path) return '';
  const name = path.split(/[/\\]/).pop() || path;
  return name.replace(/\.md$/, '');
}

function handleSave() {
  emit('save');
}

function handleSaveGitHub() {
  emit('save-github');
}
</script>

<style scoped>
.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px 16px 52px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
  height: 64px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.file-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-hover);
  border-radius: 8px;
  color: var(--text-secondary);
}

.file-details {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  overflow: hidden;
}

.file-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-ext {
  color: var(--text-muted);
  font-size: 14px;
}

.github-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  font-size: 11px;
  color: var(--text-secondary);
}

.unsaved-dot {
  width: 8px;
  height: 8px;
  background-color: var(--primary);
  border-radius: 50%;
  margin-left: 4px;
  box-shadow: 0 0 0 2px var(--bg-primary);
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.save-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-hover);
}

.save-btn.saving {
  opacity: 0.8;
  cursor: wait;
}

.save-btn.saved {
  background: var(--success-glow);
  color: var(--success);
  border-color: var(--success);
}

.save-btn kbd {
  font-family: inherit;
  font-size: 11px;
  padding: 2px 6px;
  background: var(--bg-active);
  border-radius: 4px;
  color: var(--text-muted);
  border: 1px solid var(--border-subtle);
}

.check-icon {
  color: var(--success);
  animation: scaleIn 0.2s ease;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--text-muted);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }

  to {
    transform: scale(1);
  }
}
</style>
