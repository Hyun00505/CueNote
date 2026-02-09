<template>
  <div
    v-if="trashFiles.length > 0"
    class="sidebar-section trash-section"
  >
    <div class="section-header-row">
      <div
        class="section-label trash-label"
        @click="toggleTrash"
      >
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          :class="{ rotated: !expanded }"
        >
          <path d="M6 9l6 6 6-6" />
        </svg>
        Trash
        <span class="trash-count">{{ trashFiles.length }}</span>
      </div>
      <button
        class="empty-trash-btn"
        title="Empty trash"
        @click="emit('empty-trash')"
      >
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14z" />
        </svg>
      </button>
    </div>

    <ul
      v-if="expanded"
      class="file-list trash-list"
    >
      <li
        v-for="file in trashFiles"
        :key="file"
        class="file-item trash-item"
      >
        <div class="trash-file-info">
          <svg
            class="file-icon"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
          <span class="file-name">{{ getFileName(file) }}</span>
        </div>
        <div class="trash-actions">
          <button 
            class="restore-btn" 
            title="Restore"
            @click="emit('restore-file', file)"
          >
            <svg
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
              <path d="M21 3v5h-5" />
              <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
            </svg>
          </button>
          <button 
            class="permanent-delete-btn" 
            title="Delete permanently"
            @click="emit('permanent-delete', file)"
          >
            <svg
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line
                x1="18"
                y1="6"
                x2="6"
                y2="18"
              />
              <line
                x1="6"
                y1="6"
                x2="18"
                y2="18"
              />
            </svg>
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

defineProps<{
  trashFiles: string[];
}>();

const emit = defineEmits<{
  'restore-file': [filename: string];
  'permanent-delete': [filename: string];
  'empty-trash': [];
}>();

const expanded = ref(true);

function toggleTrash() {
  expanded.value = !expanded.value;
}

function getFileName(path: string): string {
  const name = path.split(/[/\\]/).pop() || path;
  return name.replace(/\.md$/i, '');
}
</script>

<style scoped>
.trash-section {
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);
}

.section-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px 10px;
}

.section-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted);
  opacity: 0.7;
}

.trash-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
}

.trash-label svg {
  transition: transform 0.15s ease;
}

.trash-label svg.rotated {
  transform: rotate(-90deg);
}

.trash-count {
  background: var(--bg-hover);
  padding: 1px 6px;
  border-radius: 8px;
  font-size: 10px;
  margin-left: 4px;
}

.empty-trash-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  opacity: 0;
  transition: all 0.15s ease;
}

.trash-section:hover .empty-trash-btn {
  opacity: 1;
}

.empty-trash-btn:hover {
  background: var(--error-glow);
  color: var(--error);
}

.file-list {
  list-style: none;
}

.trash-list {
  max-height: 150px;
}

.file-item {
  display: flex;
  align-items: center;
  border-radius: 6px;
  margin-bottom: 2px;
}

.trash-item {
  opacity: 0.7;
}

.trash-item:hover {
  opacity: 1;
}

.trash-file-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  min-width: 0;
}

.trash-file-info .file-icon {
  opacity: 0.5;
}

.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 450;
  font-size: 12px;
  color: var(--text-muted);
}

.trash-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s ease;
  margin-right: 4px;
}

.trash-item:hover .trash-actions {
  opacity: 1;
}

.restore-btn,
.permanent-delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: none;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.restore-btn:hover {
  background: var(--success-glow);
  color: var(--success);
}

.permanent-delete-btn:hover {
  background: var(--error-glow);
  color: var(--error);
}
</style>
