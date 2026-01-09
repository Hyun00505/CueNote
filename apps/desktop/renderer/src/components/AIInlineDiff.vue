<template>
  <Transition name="diff-slide">
    <div 
      v-if="visible" 
      class="inline-diff-wrapper"
      :style="position ? { top: `${position.y}px`, left: `${position.x}px` } : {}"
    >
      <!-- Git Merge Conflict 스타일 헤더 -->
      <div class="conflict-header">
        <code class="conflict-marker">&lt;&lt;&lt;&lt;&lt;&lt;&lt; 원본</code>
        <div class="conflict-actions">
          <button 
            class="conflict-btn reject" 
            @click="$emit('reject')" 
            :disabled="isStreaming"
            title="원본 유지 (Esc)"
          >
            원본 유지
          </button>
          <button 
            class="conflict-btn accept" 
            @click="$emit('accept')" 
            :disabled="isStreaming"
            title="변경 적용 (Enter)"
          >
            변경 적용
          </button>
        </div>
      </div>

      <!-- 원본 (삭제될 내용) -->
      <div class="conflict-section original">
        <pre class="conflict-content"><code v-html="formatText(original)"></code></pre>
      </div>

      <!-- 구분선 -->
      <div class="conflict-divider">
        <code class="conflict-marker">=======</code>
        <span class="action-label">{{ actionLabel }}</span>
      </div>

      <!-- AI 제안 (추가될 내용) -->
      <div class="conflict-section incoming">
        <pre class="conflict-content"><code v-html="formatText(result)"></code><span v-if="isStreaming" class="streaming-cursor">▌</span></pre>
        <div v-if="isStreaming && !result" class="streaming-placeholder">
          <span class="streaming-dot"></span>
          <span class="streaming-dot"></span>
          <span class="streaming-dot"></span>
          <span class="streaming-text">AI가 생성 중...</span>
        </div>
      </div>

      <!-- Git Merge Conflict 스타일 푸터 -->
      <div class="conflict-footer">
        <code class="conflict-marker">&gt;&gt;&gt;&gt;&gt;&gt;&gt; AI 제안</code>
        <div class="conflict-meta">
          <span v-if="isStreaming" class="meta-info streaming-badge">
            <span class="pulse-dot"></span> 스트리밍 중
          </span>
          <span v-else-if="meta && meta.sourceLanguage" class="meta-info">
            {{ getLanguageName(meta.sourceLanguage) }} → {{ targetLanguage }}
          </span>
        </div>
      </div>

      <!-- 하단 액션 바 -->
      <div class="conflict-action-bar">
        <span v-if="isStreaming" class="hint streaming">
          스트리밍 완료까지 기다려주세요...
        </span>
        <span v-else class="hint">
          <kbd>Enter</kbd> 변경 적용 · <kbd>Esc</kbd> 원본 유지
        </span>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount } from 'vue';

const props = defineProps<{
  visible: boolean;
  action: string;
  original: string;
  result: string;
  meta?: Record<string, any>;
  position?: { x: number; y: number };
  isStreaming?: boolean;
}>();

const emit = defineEmits<{
  (e: 'accept'): void;
  (e: 'reject'): void;
}>();

const actionLabels: Record<string, string> = {
  improve: '글 다듬기',
  expand: '더 길게',
  shorten: '더 짧게',
  summarize: '요약',
  translate: '번역',
  proofread: '맞춤법',
};

const actionLabel = computed(() => actionLabels[props.action] || 'AI 변환');

const targetLanguage = computed(() => {
  if (props.action !== 'translate') return '';
  const hasKorean = /[가-힣]/.test(props.result);
  const hasJapanese = /[\u3040-\u309F\u30A0-\u30FF]/.test(props.result);
  const hasChinese = /[\u4E00-\u9FFF]/.test(props.result);
  
  if (hasKorean) return '한국어';
  if (hasJapanese) return '일본어';
  if (hasChinese) return '중국어';
  return '영어';
});

const hasMetaInfo = computed(() => {
  if (!props.meta) return false;
  return props.meta.sourceLanguage || (props.meta.changes && props.meta.changes.length > 0);
});

function getLanguageName(code: string): string {
  const names: Record<string, string> = {
    ko: '한국어', korean: '한국어',
    en: '영어', english: '영어',
    ja: '일본어', japanese: '일본어',
    zh: '중국어', chinese: '중국어',
  };
  return names[code.toLowerCase()] || code;
}

function formatText(text: string): string {
  // HTML 특수문자 이스케이프
  let formatted = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  
  // 마크다운 포맷팅 하이라이트
  formatted = formatted
    // 헤더 (# 로 시작하는 줄)
    .replace(/^(#{1,6})\s+(.+)$/gm, '<span class="md-header">$1 $2</span>')
    // 리스트 (- 또는 * 로 시작하는 줄)
    .replace(/^(\s*[-*])\s+/gm, '<span class="md-list">$1</span> ')
    // 숫자 리스트
    .replace(/^(\s*\d+\.)\s+/gm, '<span class="md-list">$1</span> ')
    // 링크 [text](url)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<span class="md-link">[$1]($2)</span>')
    // 굵게 **text**
    .replace(/\*\*([^*]+)\*\*/g, '<span class="md-bold">**$1**</span>')
    // 기울임 *text*
    .replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<span class="md-italic">*$1*</span>')
    // 인라인 코드 `code`
    .replace(/`([^`]+)`/g, '<span class="md-code">`$1`</span>')
    // 줄바꿈
    .replace(/\n/g, '<br>');
  
  return formatted;
}

function handleKeydown(e: KeyboardEvent) {
  if (!props.visible) return;
  if (props.isStreaming) return; // 스트리밍 중에는 키보드 입력 무시
  
  if (e.key === 'Escape') {
    e.preventDefault();
    e.stopPropagation();
    emit('reject');
  } else if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    e.stopPropagation();
    emit('accept');
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown, true);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown, true);
});
</script>

<style scoped>
/* Git Merge Conflict 스타일 - 노션 AI 처럼 선택 위치에 표시 */
.inline-diff-wrapper {
  position: absolute;
  z-index: 100;
  width: calc(100% - 96px);
  max-width: 680px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(139, 92, 246, 0.4);
  background: var(--bg-secondary);
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.6;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(139, 92, 246, 0.2);
}

/* 헤더 (<<<<<<< 원본) */
.conflict-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.15);
  border-bottom: 1px solid rgba(239, 68, 68, 0.2);
}

.conflict-marker {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.conflict-header .conflict-marker {
  color: #f87171;
  background: rgba(239, 68, 68, 0.2);
}

.conflict-actions {
  display: flex;
  gap: 8px;
}

.conflict-btn {
  padding: 4px 12px;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.conflict-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.conflict-btn.reject {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.conflict-btn.reject:hover {
  background: rgba(239, 68, 68, 0.35);
}

.conflict-btn.accept {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

.conflict-btn.accept:hover {
  background: rgba(34, 197, 94, 0.35);
}

/* 원본 섹션 (삭제될 내용) */
.conflict-section.original {
  background: rgba(239, 68, 68, 0.05);
  border-left: 3px solid #ef4444;
}

.conflict-section.incoming {
  background: rgba(34, 197, 94, 0.05);
  border-left: 3px solid #22c55e;
}

.conflict-content {
  margin: 0;
  padding: 12px 16px;
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.conflict-section.original .conflict-content {
  color: var(--text-muted);
  text-decoration: line-through;
  text-decoration-color: rgba(239, 68, 68, 0.5);
}

.conflict-section.incoming .conflict-content {
  color: var(--text-primary);
}

/* 구분선 (=======) */
.conflict-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background: rgba(139, 92, 246, 0.1);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.conflict-divider .conflict-marker {
  color: #a78bfa;
  background: rgba(139, 92, 246, 0.2);
}

.action-label {
  font-size: 11px;
  font-weight: 500;
  color: #a78bfa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 푸터 (>>>>>>> AI 제안) */
.conflict-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(34, 197, 94, 0.15);
  border-top: 1px solid rgba(34, 197, 94, 0.2);
}

.conflict-footer .conflict-marker {
  color: #4ade80;
  background: rgba(34, 197, 94, 0.2);
}

.conflict-meta {
  display: flex;
  gap: 8px;
}

.meta-info {
  font-size: 10px;
  color: var(--text-muted);
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

/* 하단 액션 바 */
.conflict-action-bar {
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  text-align: center;
}

.hint {
  font-size: 11px;
  color: var(--text-muted);
}

.hint kbd {
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 10px;
  margin: 0 2px;
}

/* 마크다운 하이라이트 */
:deep(.md-link) {
  color: #60a5fa;
  background: rgba(96, 165, 250, 0.15);
  padding: 1px 4px;
  border-radius: 3px;
  text-decoration: none !important;
}

:deep(.md-bold) {
  color: #fbbf24;
  font-weight: 600;
  text-decoration: none !important;
}

:deep(.md-italic) {
  color: #c4b5fd;
  font-style: italic;
  text-decoration: none !important;
}

:deep(.md-code) {
  color: #34d399;
  background: rgba(52, 211, 153, 0.15);
  padding: 1px 6px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 0.9em;
  text-decoration: none !important;
}

:deep(.md-header) {
  color: #f472b6;
  font-weight: 600;
}

:deep(.md-list) {
  color: #fbbf24;
}

/* 스트리밍 커서 애니메이션 */
.streaming-cursor {
  color: #22c55e;
  animation: blink 0.8s infinite;
  font-weight: bold;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 스트리밍 플레이스홀더 */
.streaming-placeholder {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  color: var(--text-muted);
}

.streaming-dot {
  width: 6px;
  height: 6px;
  background: #22c55e;
  border-radius: 50%;
  animation: bounce 1.2s infinite;
}

.streaming-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.streaming-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-4px); }
}

.streaming-text {
  font-size: 12px;
  color: var(--text-muted);
}

/* 스트리밍 배지 */
.streaming-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #22c55e !important;
  background: rgba(34, 197, 94, 0.1) !important;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.hint.streaming {
  color: #22c55e;
  font-style: italic;
}

/* 트랜지션 */
.diff-slide-enter-active,
.diff-slide-leave-active {
  transition: all 0.2s ease;
}

.diff-slide-enter-from,
.diff-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
