<template>
  <div class="editor-toolbar">
    <!-- Formatting Group -->
    <ToolbarFormatGroup :editor="editor" />

    <div class="toolbar-divider"></div>

    <!-- Image Group -->
    <ToolbarImageGroup :editor="editor" />

    <!-- Table Group -->
    <ToolbarTableGroup :editor="editor" />

    <div class="toolbar-divider"></div>

    <!-- Undo/Redo is now in ToolbarFormatGroup, but maybe it should be separate? 
         The plan put it in FormatGroup, but structure wise it might be better here or in its own group.
         Looking at previous implementation, it was at the end. 
         Let's keep it in FormatGroup as implemented for now or move it if needed.
         Wait, I put it in ToolbarFormatGroup.vue.
    -->

    <!-- Cluster Badge -->
    <ToolbarClusterBadge :activeFile="activeFile" />

    <div class="toolbar-divider" v-if="activeFile"></div>

    <!-- AI Group -->
    <ToolbarAIGroup 
      :editor="editor"
      :summarizing="summarizing"
      :noteName="noteName"
      :llmSettings="llmSettings"
      @summarize="handleSummarize"
      @extract-result="handleExtractResult"
    />
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
  llmSettings?: {
    provider: string;
    apiKey: string;
    model: string;
  };
}>();

const emit = defineEmits<{
  (e: 'summarize'): void;
  (e: 'extract-result', markdown: string): void;
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
</style>
