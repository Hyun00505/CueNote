<template>
  <div
    v-if="visible"
    class="modal-overlay"
    @click.self="emit('close')"
  >
    <div class="modal-content extract-modal">
      <div class="modal-header">
        <h3>{{ t('aiExtract.title') }}</h3>
        <button
          class="modal-close-btn"
          @click="emit('close')"
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

      <div class="modal-body">
        <!-- 입력 모드 선택 -->
        <div class="input-mode-tabs">
          <button 
            class="tab-btn" 
            :class="{ active: inputMode === 'file' }"
            @click="inputMode = 'file'; clearExtracted()"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            {{ t('aiExtract.selectFile') }}
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: inputMode === 'text' }"
            @click="inputMode = 'text'; clearExtracted()"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line
                x1="17"
                y1="10"
                x2="3"
                y2="10"
              />
              <line
                x1="21"
                y1="6"
                x2="3"
                y2="6"
              />
              <line
                x1="21"
                y1="14"
                x2="3"
                y2="14"
              />
              <line
                x1="17"
                y1="18"
                x2="3"
                y2="18"
              />
            </svg>
            {{ t('aiExtract.enterText') }}
          </button>
        </div>

        <!-- 파일 선택 모드 -->
        <div
          v-if="inputMode === 'file'"
          class="file-select-section"
        >
          <div class="file-search">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle
                cx="11"
                cy="11"
                r="8"
              />
              <line
                x1="21"
                y1="21"
                x2="16.65"
                y2="16.65"
              />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="t('aiExtract.searchPlaceholder')"
            >
          </div>
          <div class="file-list">
            <button
              v-for="file in filteredFiles"
              :key="file"
              class="file-item"
              :class="{ selected: selectedFile === file }"
              @click="selectFile(file)"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              <span>{{ getFileName(file) }}</span>
            </button>
            <div
              v-if="filteredFiles.length === 0"
              class="no-files"
            >
              {{ t('aiExtract.noFilesFound') }}
            </div>
          </div>
          <div
            v-if="fileLoading"
            class="file-loading"
          >
            <div class="spinner" />
            <span>{{ t('aiExtract.loadingFile') }}</span>
          </div>
        </div>

        <!-- 텍스트 입력 모드 -->
        <div
          v-else
          class="text-input-section"
        >
          <textarea
            v-model="content"
            :placeholder="t('aiExtract.textPlaceholder')"
            rows="8"
          />
        </div>

        <!-- 추출된 일정 목록 -->
        <div
          v-if="extractedSchedules.length > 0"
          class="extracted-schedules"
        >
          <div class="extracted-header">
            <h4>{{ t('aiExtract.extractedCount') }} ({{ extractedSchedules.length }})</h4>
            <span
              class="confidence-badge"
              :class="confidenceClass"
            >
              {{ t('aiExtract.confidence') }} {{ Math.round(confidence * 100) }}%
            </span>
          </div>
          <div class="extracted-list">
            <div
              v-for="(schedule, index) in extractedSchedules"
              :key="index"
              class="extracted-item"
              :style="{ '--item-color': schedule.color }"
            >
              <input
                :id="`schedule-${index}`"
                v-model="selectedIndexes"
                type="checkbox"
                :value="index"
              >
              <label
                :for="`schedule-${index}`"
                class="extracted-item-content"
              >
                <span class="item-title">{{ schedule.title }}</span>
                <span class="item-meta">
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <rect
                      x="3"
                      y="4"
                      width="18"
                      height="18"
                      rx="2"
                      ry="2"
                    />
                    <line
                      x1="16"
                      y1="2"
                      x2="16"
                      y2="6"
                    />
                    <line
                      x1="8"
                      y1="2"
                      x2="8"
                      y2="6"
                    />
                    <line
                      x1="3"
                      y1="10"
                      x2="21"
                      y2="10"
                    />
                  </svg>
                  {{ schedule.date }}
                  <template v-if="schedule.startTime">
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <circle
                        cx="12"
                        cy="12"
                        r="10"
                      />
                      <polyline points="12 6 12 12 16 14" />
                    </svg>
                    {{ schedule.startTime }}{{ schedule.endTime ? ` - ${schedule.endTime}` : '' }}
                  </template>
                </span>
              </label>
            </div>
          </div>
        </div>

        <!-- 추출 에러 -->
        <div
          v-if="error"
          class="extract-error"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle
              cx="12"
              cy="12"
              r="10"
            />
            <line
              x1="12"
              y1="8"
              x2="12"
              y2="12"
            />
            <line
              x1="12"
              y1="16"
              x2="12.01"
              y2="16"
            />
          </svg>
          {{ error }}
        </div>
      </div>

      <div class="modal-footer">
        <button
          class="cancel-btn"
          @click="emit('close')"
        >
          {{ t('common.cancel') }}
        </button>
        <button
          v-if="extractedSchedules.length === 0"
          class="extract-btn"
          :disabled="!content.trim() || loading"
          @click="emit('extract', content)"
        >
          <span
            v-if="loading"
            class="spinner"
          />
          <svg
            v-else
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H6a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 8 6a4 4 0 0 1 4-4z" />
          </svg>
          {{ loading ? t('aiExtract.extracting') : t('aiExtract.extractBtn') }}
        </button>
        <button
          v-else
          class="save-btn"
          :disabled="selectedIndexes.length === 0"
          @click="emit('save', selectedIndexes)"
        >
          {{ t('aiExtract.addSelected') }} ({{ selectedIndexes.length }})
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useI18n } from '../../composables';
import type { ScheduleItem } from '../../types';

const props = defineProps<{
  visible: boolean;
  vaultFiles: string[];
  extractedSchedules: ScheduleItem[];
  confidence: number;
  loading: boolean;
  error: string;
}>();

const emit = defineEmits<{
  'close': [];
  'extract': [content: string];
  'save': [indexes: number[]];
  'load-file': [filePath: string];
}>();

const { t } = useI18n();

const CORE_BASE = 'http://127.0.0.1:8787';

const inputMode = ref<'file' | 'text'>('file');
const content = ref('');
const searchQuery = ref('');
const selectedFile = ref<string | null>(null);
const fileLoading = ref(false);
const selectedIndexes = ref<number[]>([]);

const filteredFiles = computed(() => {
  const mdFiles = props.vaultFiles.filter(f => f.endsWith('.md'));
  if (!searchQuery.value.trim()) return mdFiles;
  const query = searchQuery.value.toLowerCase();
  return mdFiles.filter(f => f.toLowerCase().includes(query));
});

const confidenceClass = computed(() => {
  if (props.confidence >= 0.8) return 'high';
  if (props.confidence >= 0.5) return 'medium';
  return 'low';
});

watch(() => props.visible, (val) => {
  if (val) {
    clearExtracted();
    content.value = '';
    selectedFile.value = null;
    searchQuery.value = '';
    inputMode.value = 'file';
    selectedIndexes.value = [];
  }
});

watch(() => props.extractedSchedules, (schedules) => {
  if (schedules.length > 0) {
    selectedIndexes.value = schedules.map((_, i) => i);
  }
});

function clearExtracted() {
  selectedIndexes.value = [];
}

function getFileName(path: string): string {
  const name = path.split(/[/\\]/).pop() || path;
  return name.replace(/\.md$/i, '');
}

async function selectFile(filePath: string) {
  if (selectedFile.value === filePath) {
    selectedFile.value = null;
    content.value = '';
    return;
  }

  selectedFile.value = filePath;
  fileLoading.value = true;

  try {
    const res = await fetch(`${CORE_BASE}/vault/file?path=${encodeURIComponent(filePath)}`);
    if (res.ok) {
      const data = await res.json();
      content.value = data.content || '';
    } else {
      content.value = '';
    }
  } catch (e) {
    content.value = '';
  } finally {
    fileLoading.value = false;
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.extract-modal {
  width: 520px;
  max-width: 90vw;
  max-height: 80vh;
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalIn 0.2s ease;
}

@keyframes modalIn {
  from { 
    opacity: 0;
    transform: scale(0.96) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.modal-close-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.12s ease;
}

.modal-close-btn:hover {
  background: var(--surface-3);
  color: var(--text-primary);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 22px;
}

/* Input mode tabs */
.input-mode-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  background: var(--surface-3);
  border-color: var(--border-default);
}

.tab-btn.active {
  background: rgba(201, 167, 108, 0.1);
  border-color: rgba(201, 167, 108, 0.35);
  color: #c9a76c;
}

/* File select */
.file-select-section {
  margin-bottom: 16px;
}

.file-search {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  margin-bottom: 12px;
}

.file-search svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.file-search input {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  outline: none;
}

.file-search input::placeholder {
  color: var(--text-muted);
}

.file-list {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  background: none;
  border: none;
  border-bottom: 1px solid var(--surface-2);
  color: var(--text-secondary);
  font-size: 13px;
  font-family: inherit;
  text-align: left;
  cursor: pointer;
  transition: all 0.12s ease;
}

.file-item:last-child {
  border-bottom: none;
}

.file-item:hover {
  background: var(--surface-2);
  color: var(--text-primary);
}

.file-item.selected {
  background: rgba(201, 167, 108, 0.12);
  color: #e8d5b7;
}

.file-item span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-files {
  padding: 20px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
}

.file-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px;
  color: var(--text-muted);
  font-size: 13px;
}

/* Text input */
.text-input-section textarea {
  width: 100%;
  padding: 14px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  resize: vertical;
  line-height: 1.6;
  transition: border-color 0.15s ease;
}

.text-input-section textarea:focus {
  outline: none;
  border-color: rgba(201, 167, 108, 0.5);
}

.text-input-section textarea::placeholder {
  color: var(--text-muted);
}

/* Extracted schedules */
.extracted-schedules {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-subtle);
}

.extracted-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.extracted-header h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.confidence-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 12px;
}

.confidence-badge.high {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.confidence-badge.medium {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.confidence-badge.low {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.extracted-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.extracted-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-left: 3px solid var(--item-color, #c9a76c);
  border-radius: 8px;
  transition: background 0.12s ease;
}

.extracted-item:hover {
  background: var(--surface-2);
}

.extracted-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  margin-top: 2px;
  accent-color: #c9a76c;
  cursor: pointer;
}

.extracted-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.item-meta svg {
  opacity: 0.6;
}

/* Extract error */
.extract-error {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  margin-top: 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: #ef4444;
  font-size: 13px;
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 22px;
  border-top: 1px solid var(--border-subtle);
  background: var(--surface-1);
}

.cancel-btn,
.extract-btn,
.save-btn {
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
}

.cancel-btn {
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.cancel-btn:hover {
  background: var(--surface-2);
  border-color: var(--border-default);
}

.extract-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #34d399;
}

.extract-btn:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.25);
}

.extract-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.save-btn {
  background: #c9a76c;
  border: none;
  color: #1a1a1a;
}

.save-btn:hover:not(:disabled) {
  background: #d4b67d;
}

.save-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border-strong);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

</style>
