<template>
  <div class="editor-toolbar">
    <!-- Formatting Group -->
    <ToolbarFormatGroup :editor="editor" />

    <div class="toolbar-divider" />

    <!-- Image Group -->
    <ToolbarImageGroup :editor="editor" />

    <!-- Table Group -->
    <ToolbarTableGroup :editor="editor" />

    <div class="toolbar-divider" />

    <!-- Undo/Redo is now in ToolbarFormatGroup, but maybe it should be separate? 
         The plan put it in FormatGroup, but structure wise it might be better here or in its own group.
         Looking at previous implementation, it was at the end. 
         Let's keep it in FormatGroup as implemented for now or move it if needed.
         Wait, I put it in ToolbarFormatGroup.vue.
    -->

    <!-- Cluster Badge -->
    <ToolbarClusterBadge :active-file="activeFile" />

    <div
      v-if="activeFile"
      class="toolbar-divider"
    />

    <!-- AI Group -->
    <ToolbarAIGroup
      :editor="editor"
      :summarizing="summarizing"
      :note-name="noteName"
      :llm-settings="llmSettings"
      @summarize="handleSummarize"
      @extract-result="handleExtractResult"
    />

    <div class="toolbar-divider" />

    <!-- Source View Toggle -->
    <button
      class="toolbar-btn"
      :class="{ active: showSourceView }"
      title="마크다운 원본 보기"
      @click="$emit('toggle-source-view')"
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polyline points="16 18 22 12 16 6" />
        <polyline points="8 6 2 12 8 18" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import type { Editor } from '@tiptap/vue-3';
import ToolbarFormatGroup from './toolbar/ToolbarFormatGroup.vue';
import ToolbarImageGroup from './toolbar/ToolbarImageGroup.vue';
import ToolbarTableGroup from './toolbar/ToolbarTableGroup.vue';
import ToolbarAIGroup from './toolbar/ToolbarAIGroup.vue';
import ToolbarClusterBadge from './toolbar/ToolbarClusterBadge.vue';

const props = defineProps<{
  editor: Editor | null;
  summarizing?: boolean;
  noteName?: string;
  activeFile?: string | null;
  showSourceView?: boolean;
  llmSettings?: {
    provider: string;
    apiKey: string;
    model: string;
  };
}>();

const emit = defineEmits<{
  (e: 'summarize'): void;
  (e: 'extract-result', markdown: string): void;
  (e: 'toggle-source-view'): void;
}>();

function handleSummarize() {
  emit('summarize');
}

function handleExtractResult(markdown: string) {
  emit('extract-result', markdown);
}
</script>

<style scoped>
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  flex-wrap: wrap;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border-subtle);
  margin: 0 8px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  background: transparent;
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.12s ease;
}

.toolbar-btn:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}

.toolbar-btn.active {
  background: var(--bg-active);
  color: var(--accent);
}
</style>
