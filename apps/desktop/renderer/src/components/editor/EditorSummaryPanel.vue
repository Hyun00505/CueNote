<template>
  <Transition name="slide">
    <div
      v-if="summaryResult"
      class="summary-panel"
    >
      <div class="summary-header">
        <div class="summary-title">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H6a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 8 6a4 4 0 0 1 4-4z" />
          </svg>
          <span>AI 요약</span>
          <span class="word-count">{{ summaryResult.wordCount }}자</span>
        </div>
        <div class="summary-actions">
          <button
            class="action-btn"
            :title="copied ? '복사됨!' : '요약 복사'"
            @click="handleCopy"
          >
            <svg
              v-if="!copied"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <rect
                x="9"
                y="9"
                width="13"
                height="13"
                rx="2"
                ry="2"
              />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
            <svg
              v-else
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </button>
          <button
            class="action-btn insert-btn"
            title="노트 상단에 삽입"
            @click="handleInsert"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M12 5v14M5 12h14" />
            </svg>
            <span>삽입</span>
          </button>
          <button
            class="close-btn"
            title="닫기"
            @click="handleClose"
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
      </div>
      <div class="summary-content">
        <p class="summary-text">
          {{ summaryResult.summary }}
        </p>
        <div
          v-if="summaryResult.keyPoints.length > 0"
          class="key-points"
        >
          <h4>핵심 포인트</h4>
          <ul>
            <li
              v-for="(point, index) in summaryResult.keyPoints"
              :key="index"
            >
              {{ point }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface SummaryResult {
  summary: string;
  keyPoints: string[];
  wordCount: number;
}

const props = defineProps<{
  summaryResult: SummaryResult | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'copy'): void;
  (e: 'insert'): void;
}>();

const copied = ref(false);

function handleClose() {
  emit('close');
}

function handleCopy() {
  copied.value = true;
  emit('copy');
  setTimeout(() => {
    copied.value = false;
  }, 2000);
}

function handleInsert() {
  emit('insert');
}
</script>

<style scoped>
.summary-panel {
  margin: 16px 48px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border-subtle);
}

.summary-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
}

.word-count {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: normal;
  padding: 2px 8px;
  background: var(--bg-elevated);
  border-radius: 10px;
}

.summary-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 10px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-primary);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.insert-btn {
  color: var(--primary);
  border-color: var(--primary-glow);
  background: rgba(var(--primary-rgb), 0.05);
}

.insert-btn:hover {
  background: rgba(var(--primary-rgb), 0.1);
  border-color: var(--primary);
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--bg-active);
  color: var(--text-secondary);
}

.summary-content {
  padding: 20px;
}

.summary-text {
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.key-points {
  background: var(--bg-primary);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
}

.key-points h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.key-points ul {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.key-points li {
  position: relative;
  padding-left: 14px;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.key-points li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: var(--primary);
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  max-height: 500px;
  opacity: 1;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
  margin-bottom: 0;
  transform: translateY(-10px);
}
</style>
