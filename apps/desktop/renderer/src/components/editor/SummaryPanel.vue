<template>
  <Transition name="slide">
    <div
      v-if="visible"
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
          <span class="word-count">{{ result.wordCount }}자</span>
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
            @click="emit('insert')"
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
            @click="emit('close')"
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
          {{ result.summary }}
        </p>
        <div
          v-if="result.keyPoints.length > 0"
          class="key-points"
        >
          <h4>핵심 포인트</h4>
          <ul>
            <li
              v-for="(point, index) in result.keyPoints"
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

defineProps<{
  visible: boolean;
  result: SummaryResult;
}>();

const emit = defineEmits<{
  'close': [];
  'insert': [];
}>();

const copied = ref(false);

function handleCopy() {
  // Copy logic would be handled by parent
  copied.value = true;
  setTimeout(() => {
    copied.value = false;
  }, 2000);
}
</script>

<style scoped>
.summary-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 320px;
  max-height: 60%;
  background: var(--bg-primary);
  border-left: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  border-radius: 0 0 0 12px;
  box-shadow: -4px 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
  background: rgba(139, 92, 246, 0.05);
}

.summary-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #a78bfa;
}

.word-count {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  background: var(--surface-2);
  padding: 2px 8px;
  border-radius: 10px;
}

.summary-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-btn,
.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px 8px;
  background: none;
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn:hover,
.close-btn:hover {
  background: var(--surface-3);
  color: var(--text-primary);
}

.insert-btn {
  font-size: 12px;
  background: rgba(139, 92, 246, 0.1);
  color: #a78bfa;
}

.insert-btn:hover {
  background: rgba(139, 92, 246, 0.2);
}

.summary-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.summary-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
  margin: 0 0 16px;
}

.key-points h4 {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 10px;
}

.key-points ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.key-points li {
  position: relative;
  padding-left: 16px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.key-points li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  width: 6px;
  height: 6px;
  background: #a78bfa;
  border-radius: 50%;
}

/* Transition */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
