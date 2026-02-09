<template>
  <div class="toolbar-group">
    <div class="dropdown-wrapper">
      <button
        ref="tableBtnRef"
        class="toolbar-btn"
        title="표 삽입"
        @click="showTablePicker = !showTablePicker"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <rect
            x="3"
            y="3"
            width="18"
            height="18"
            rx="2"
          />
          <line
            x1="3"
            y1="9"
            x2="21"
            y2="9"
          />
          <line
            x1="3"
            y1="15"
            x2="21"
            y2="15"
          />
          <line
            x1="9"
            y1="3"
            x2="9"
            y2="21"
          />
          <line
            x1="15"
            y1="3"
            x2="15"
            y2="21"
          />
        </svg>
      </button>
      <!-- 표 크기 선택 드롭다운 -->
      <Transition name="dropdown">
        <div
          v-if="showTablePicker"
          class="table-picker"
          @mouseleave="showTablePicker = false"
        >
          <div class="table-picker-header">
            {{ tableRows }} × {{ tableCols }} 표
          </div>
          <div class="table-grid">
            <div
              v-for="row in 6"
              :key="row"
              class="table-row"
            >
              <div
                v-for="col in 6"
                :key="col"
                class="table-cell"
                :class="{ selected: row <= tableRows && col <= tableCols }"
                @mouseenter="tableRows = row; tableCols = col"
                @click="insertTableWithSize(row, col)"
              />
            </div>
          </div>
        </div>
      </Transition>
    </div>
    <button
      class="toolbar-btn"
      title="구분선"
      @click="editor?.chain().focus().setHorizontalRule().run()"
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <line
          x1="2"
          y1="12"
          x2="22"
          y2="12"
        />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { Editor } from '@tiptap/vue-3';

const props = defineProps<{
  editor: Editor | null;
}>();

const showTablePicker = ref(false);
const tableRows = ref(3);
const tableCols = ref(3);
const tableBtnRef = ref<HTMLElement | null>(null);

function insertTableWithSize(rows: number, cols: number) {
  if (!props.editor) return;
  props.editor.chain().focus().insertTable({ rows, cols, withHeaderRow: true }).run();
  showTablePicker.value = false;
  tableRows.value = 3;
  tableCols.value = 3;
}
</script>

<style scoped>
.toolbar-group {
  display: flex;
  align-items: center;
  gap: 1px;
}

.dropdown-wrapper {
  position: relative;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.12s ease;
}

.toolbar-btn:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}

/* Table Picker */
.table-picker {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  padding: 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  z-index: 100;
}

.table-picker-header {
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
  margin-bottom: 8px;
}

.table-grid {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.table-row {
  display: flex;
  gap: 3px;
}

.table-cell {
  width: 20px;
  height: 20px;
  background: var(--surface-2);
  border: 1px solid var(--border-subtle);
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.1s ease;
}

.table-cell:hover {
  background: var(--surface-4);
}

.table-cell.selected {
  background: var(--accent);
  border-color: var(--accent);
  opacity: 0.3;
}

/* Dropdown Transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
