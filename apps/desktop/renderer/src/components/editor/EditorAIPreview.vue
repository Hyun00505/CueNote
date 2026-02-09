<template>
  <Teleport to="body">
    <Transition name="panel-slide">
      <div
        v-if="isAIStreaming || showAIActionBar"
        class="ai-preview-panel"
      >
        <!-- 헤더 -->
        <div class="panel-header">
          <div class="panel-header-left">
            <div
              v-if="isAIStreaming"
              class="streaming-dots"
            >
              <span class="streaming-dot" />
              <span class="streaming-dot" />
              <span class="streaming-dot" />
            </div>
            <div
              v-else
              class="done-indicator"
            />
            <span class="panel-label">
              AI {{ getActionLabel(aiStreamingAction) }}{{ isAIStreaming ? '...' : ' 완료' }}
            </span>
          </div>
          <div
            v-if="showAIActionBar"
            class="panel-actions"
          >
            <button
              class="action-btn reject"
              @click="handleReject"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              되돌리기
            </button>
            <button
              class="action-btn accept"
              @click="handleAccept"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M20 6L9 17l-5-5" />
              </svg>
              적용하기
            </button>
          </div>
        </div>

        <!-- 프리뷰 콘텐츠 -->
        <div
          v-if="streamPreviewHtml"
          ref="contentRef"
          class="panel-content"
          v-html="streamPreviewHtml"
        />
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';

const props = defineProps<{
  isAIStreaming: boolean;
  aiStreamingAction: string;
  streamPreviewHtml: string;
  showAIActionBar: boolean;
}>();

const emit = defineEmits<{
  (e: 'reject'): void;
  (e: 'accept'): void;
}>();

const contentRef = ref<HTMLElement | null>(null);

function getActionLabel(action: string): string {
  if (!action) return '';
  const labels: Record<string, string> = {
    'summarize': '요약',
    'expand': '이어쓰기',
    'edit': '편집',
    'tone': '어조 변경',
    'translate': '번역'
  };
  return labels[action] || action;
}

// 스트리밍 중 자동 스크롤
watch(() => props.streamPreviewHtml, async () => {
  if (props.isAIStreaming && contentRef.value) {
    await nextTick();
    contentRef.value.scrollTop = contentRef.value.scrollHeight;
  }
});

function handleReject() {
  emit('reject');
}

function handleAccept() {
  emit('accept');
}
</script>

<style scoped>
.ai-preview-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: var(--bg-elevated, var(--bg-secondary));
  border-top: 1px solid var(--border-default);
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  max-height: 50vh;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 24px;
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.panel-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.streaming-dots {
  display: flex;
  gap: 3px;
}

.streaming-dot {
  width: 6px;
  height: 6px;
  background-color: var(--primary);
  border-radius: 50%;
  animation: pulse 1s infinite alternate;
}

.streaming-dot:nth-child(2) { animation-delay: 0.2s; }
.streaming-dot:nth-child(3) { animation-delay: 0.4s; }

.done-indicator {
  width: 8px;
  height: 8px;
  background: var(--success);
  border-radius: 50%;
  box-shadow: 0 0 0 3px var(--success-glow);
}

.panel-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn.reject {
  background: var(--bg-hover);
  color: var(--text-secondary);
}

.action-btn.reject:hover {
  background: var(--bg-active);
  color: var(--error);
}

.action-btn.accept {
  background: var(--success-glow);
  color: var(--success);
}

.action-btn.accept:hover {
  background: rgba(34, 197, 94, 0.3);
}

.panel-content {
  padding: 16px 24px;
  overflow-y: auto;
  flex: 1;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
}

.panel-content :deep(p) {
  margin-bottom: 0.8em;
}

.panel-content :deep(h1),
.panel-content :deep(h2),
.panel-content :deep(h3) {
  margin-top: 0.5em;
  margin-bottom: 0.3em;
}

.panel-content :deep(pre) {
  background: var(--bg-primary);
  border-radius: 6px;
  padding: 12px;
  overflow-x: auto;
  margin: 0.8em 0;
  border: 1px solid var(--border-default);
}

.panel-content :deep(code) {
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
}

.panel-content :deep(ul),
.panel-content :deep(ol) {
  padding-left: 1.5em;
  margin-bottom: 0.8em;
}

@keyframes pulse {
  from { opacity: 0.4; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

/* 패널 슬라이드 트랜지션 */
.panel-slide-enter-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.panel-slide-leave-active {
  transition: all 0.2s ease-in;
}

.panel-slide-enter-from,
.panel-slide-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
