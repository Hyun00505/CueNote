<template>
  <div class="editor-view">
    <div v-if="!activeFile" class="empty-state">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <line x1="10" y1="9" x2="8" y2="9"/>
        </svg>
      </div>
      <h2>No file selected</h2>
      <p>Select a markdown file from the sidebar to start editing</p>
    </div>
    
    <div v-else class="editor-container">
      <div class="editor-toolbar">
        <div class="toolbar-left">
          <span class="file-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
            </svg>
            {{ getFileName(activeFile) }}
          </span>
        </div>
        <div class="toolbar-right">
          <button class="save-btn" :disabled="saving" @click="saveFile">
            <svg v-if="!saving" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              <polyline points="17 21 17 13 7 13 7 21"/>
              <polyline points="7 3 7 8 15 8"/>
            </svg>
            <span class="spinner" v-else></span>
            <span>{{ saving ? 'Saving...' : 'Save' }}</span>
          </button>
        </div>
      </div>
      <div ref="editorEl" class="editor-surface"></div>
      <p v-if="editorError" class="error-msg">{{ editorError }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useEditor } from '../composables';

const props = defineProps<{
  activeFile: string | null;
}>();

const editorEl = ref<HTMLDivElement | null>(null);
const { editorError, saving, openFile, saveFile } = useEditor(editorEl);

function getFileName(path: string): string {
  return path.split(/[/\\]/).pop() || path;
}

watch(() => props.activeFile, (newFile) => {
  if (newFile) {
    openFile(newFile);
  }
}, { immediate: true });
</script>

<style scoped>
.editor-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.empty-icon {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  border-radius: 50%;
  margin-bottom: 24px;
  color: var(--text-muted);
}

.empty-state h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--text-muted);
  font-size: 14px;
}

.editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px 24px;
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.file-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-elevated);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text-secondary);
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--accent-primary);
  border: none;
  border-radius: var(--radius-sm);
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.save-btn:hover:not(:disabled) {
  background: var(--accent-secondary);
  box-shadow: var(--shadow-glow);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.editor-surface {
  flex: 1;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.editor-surface :deep(.cm-editor) {
  height: 100%;
  font-family: var(--font-mono);
  font-size: 14px;
}

.editor-surface :deep(.cm-scroller) {
  padding: 16px;
}

.editor-surface :deep(.cm-gutters) {
  background: var(--bg-tertiary);
  border-right: 1px solid var(--border-subtle);
  color: var(--text-muted);
}

.editor-surface :deep(.cm-activeLineGutter) {
  background: var(--bg-hover);
}

.editor-surface :deep(.cm-activeLine) {
  background: var(--bg-hover);
}

.editor-surface :deep(.cm-selectionBackground) {
  background: var(--accent-glow) !important;
}

.editor-surface :deep(.cm-content) {
  caret-color: var(--accent-secondary);
}

.error-msg {
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-sm);
  color: var(--error);
  font-size: 13px;
  margin-top: 12px;
}
</style>


