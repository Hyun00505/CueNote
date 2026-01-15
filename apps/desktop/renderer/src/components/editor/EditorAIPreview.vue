<template>
  <div class="ai-preview-container">
    <!-- AI 스트리밍 프리뷰 (실시간으로 생성 중인 텍스트 표시) -->
    <div v-if="isAIStreaming" class="ai-streaming-preview">
      <div class="streaming-header">
        <div class="streaming-dots">
          <span class="streaming-dot"></span>
          <span class="streaming-dot"></span>
          <span class="streaming-dot"></span>
        </div>
        <span class="streaming-label">AI {{ getActionLabel(aiStreamingAction) }}...</span>
      </div>
      <div class="streaming-content" v-html="streamPreviewHtml"></div>
    </div>
    
    <!-- AI 완료 후 액션 바 -->
    <Transition name="action-bar-slide">
      <div v-if="showAIActionBar" class="ai-action-bar">
        <div class="action-bar-indicator"></div>
        <span class="action-bar-label">AI {{ getActionLabel(aiStreamingAction) }} {{ t('ai.completed') }}</span>
        <div class="action-bar-buttons">
          <button class="action-btn reject" @click="handleReject">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
              <path d="M3 3v5h5"/>
            </svg>
            {{ t('ai.revert') }}
          </button>
          <button class="action-btn accept" @click="handleAccept">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 6L9 17l-5-5"/>
            </svg>
            {{ t('ai.keep') }}
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from '../../composables';

const { t } = useI18n();

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

function handleReject() {
  emit('reject');
}

function handleAccept() {
  emit('accept');
}
</script>

<style scoped>
.ai-preview-container {
  position: relative;
  z-index: 10;
}

.ai-streaming-preview {
  margin: 16px 0;
  border: 1px solid var(--primary-glow);
  border-radius: 8px;
  background: rgba(var(--primary-rgb), 0.03);
  overflow: hidden;
  animation: fadeIn 0.3s ease;
}

.streaming-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(var(--primary-rgb), 0.08);
  border-bottom: 1px solid rgba(var(--primary-rgb), 0.1);
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

.streaming-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
}

.streaming-content {
  padding: 12px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  min-height: 40px;
}

.ai-action-bar {
  position: absolute;
  bottom: -60px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: 100px;
  box-shadow: var(--shadow-lg);
  z-index: 100;
  white-space: nowrap;
}

.action-bar-indicator {
  width: 8px;
  height: 8px;
  background: var(--success);
  border-radius: 50%;
  box-shadow: 0 0 0 2px var(--success-glow);
}

.action-bar-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.action-bar-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 12px;
  border-left: 1px solid var(--border-subtle);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: none;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
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

@keyframes pulse {
  from { opacity: 0.4; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.action-bar-slide-enter-active,
.action-bar-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.action-bar-slide-enter-from,
.action-bar-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, 10px);
}
</style>
