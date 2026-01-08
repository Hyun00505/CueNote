<template>
  <Teleport to="body">
    <Transition name="menu-fade">
      <div
        v-if="visible"
        class="ai-context-menu"
        :style="{ top: `${position.y}px`, left: `${position.x}px` }"
        @click.stop
      >
        <div class="menu-header">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H6a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 8 6a4 4 0 0 1 4-4z"/>
          </svg>
          <span>AI 어시스턴트</span>
        </div>

        <div class="menu-section">
          <div class="section-label">변환</div>
          <button class="menu-item" @click="handleAction('improve')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 20h9"/>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
            </svg>
            <span>글 다듬기</span>
          </button>
          <button class="menu-item" @click="handleAction('expand')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
            </svg>
            <span>더 길게</span>
          </button>
          <button class="menu-item" @click="handleAction('shorten')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7"/>
            </svg>
            <span>더 짧게</span>
          </button>
          <button class="menu-item" @click="handleAction('summarize')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <path d="M14 2v6h6"/>
              <path d="M16 13H8M16 17H8M10 9H8"/>
            </svg>
            <span>요약하기</span>
          </button>
        </div>

        <div class="menu-section">
          <div class="section-label">번역</div>
          <button class="menu-item" @click="handleAction('translate', 'ko')" :disabled="loading">
            <span class="lang-flag">🇰🇷</span>
            <span>한국어로</span>
          </button>
          <button class="menu-item" @click="handleAction('translate', 'en')" :disabled="loading">
            <span class="lang-flag">🇺🇸</span>
            <span>영어로</span>
          </button>
          <button class="menu-item" @click="handleAction('translate', 'ja')" :disabled="loading">
            <span class="lang-flag">🇯🇵</span>
            <span>일본어로</span>
          </button>
          <button class="menu-item" @click="handleAction('translate', 'zh')" :disabled="loading">
            <span class="lang-flag">🇨🇳</span>
            <span>중국어로</span>
          </button>
        </div>

        <div class="menu-section">
          <div class="section-label">스타일</div>
          <button class="menu-item" @click="handleAction('improve', 'professional')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
            </svg>
            <span>전문적으로</span>
          </button>
          <button class="menu-item" @click="handleAction('improve', 'casual')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
              <line x1="9" y1="9" x2="9.01" y2="9"/>
              <line x1="15" y1="9" x2="15.01" y2="9"/>
            </svg>
            <span>친근하게</span>
          </button>
          <button class="menu-item" @click="handleAction('improve', 'academic')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
              <path d="M6 12v5c3 3 9 3 12 0v-5"/>
            </svg>
            <span>학술적으로</span>
          </button>
        </div>

        <!-- 로딩 상태 -->
        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner"></div>
          <span>AI가 처리 중...</span>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';

const CORE_BASE = 'http://127.0.0.1:8787';

const props = defineProps<{
  visible: boolean;
  position: { x: number; y: number };
  selectedText: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'result', data: { action: string; original: string; result: string; meta?: any }): void;
  (e: 'stream-start', data: { action: string; original: string }): void;
  (e: 'stream-chunk', chunk: string): void;
  (e: 'stream-end'): void;
  (e: 'error', message: string): void;
}>();

const loading = ref(false);

async function handleAction(action: string, option?: string) {
  if (!props.selectedText.trim()) {
    emit('error', '선택된 텍스트가 없습니다.');
    return;
  }

  loading.value = true;

  // 스트리밍 API 사용
  const body = {
    content: props.selectedText,
    action,
    target_language: action === 'translate' ? (option || 'en') : 'en',
    style: action === 'improve' ? (option || 'professional') : 'professional',
    language: 'ko'
  };

  try {
    // 스트리밍 시작 알림
    emit('stream-start', {
      action,
      original: props.selectedText
    });
    emit('close');

    const response = await fetch(`${CORE_BASE}/ai/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      
      // SSE 이벤트 파싱
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // 마지막 불완전한 라인 보관

      for (const line of lines) {
        if (line.startsWith('data:')) {
          // SSE 표준: data: 다음의 첫 공백만 제거 (trim 사용 X - 공백 보존)
          let data = line.slice(5);
          if (data.startsWith(' ')) {
            data = data.slice(1); // 첫 공백만 제거
          }
          // 이스케이프된 줄바꿈 복원: \\n -> \n
          data = data.replace(/\\n/g, '\n');
          // 빈 문자열이 아니면 emit (공백만 있어도 전달)
          if (data !== '') {
            emit('stream-chunk', data);
          }
        } else if (line.startsWith('event:')) {
          const event = line.slice(6).trim();
          if (event === 'done') {
            emit('stream-end');
          } else if (event === 'error') {
            // 다음 data 라인에서 에러 메시지를 읽음
          }
        }
      }
    }

  } catch (error) {
    console.error('AI streaming failed:', error);
    emit('error', 'AI 처리에 실패했습니다. Ollama가 실행 중인지 확인하세요.');
    emit('stream-end');
  } finally {
    loading.value = false;
  }
}

// 외부 클릭 시 메뉴 닫기
function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement;
  if (!target.closest('.ai-context-menu')) {
    emit('close');
  }
}

// ESC 키로 메뉴 닫기
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    emit('close');
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  document.addEventListener('keydown', handleKeydown);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
  document.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.ai-context-menu {
  position: fixed;
  z-index: 9999;
  min-width: 200px;
  max-width: 260px;
  background: #1a1a1f;
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 12px;
  box-shadow: 
    0 4px 24px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.05),
    0 0 40px rgba(139, 92, 246, 0.15);
  overflow: hidden;
  backdrop-filter: blur(12px);
}

.menu-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(99, 102, 241, 0.1));
  border-bottom: 1px solid rgba(139, 92, 246, 0.2);
  color: #c4b5fd;
  font-size: 12px;
  font-weight: 600;
}

.menu-section {
  padding: 8px 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.menu-section:last-child {
  border-bottom: none;
}

.section-label {
  padding: 4px 8px 6px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted);
  opacity: 0.6;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 13px;
  text-align: left;
  cursor: pointer;
  transition: all 0.12s ease;
}

.menu-item:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.15);
  color: #e9d5ff;
}

.menu-item:active:not(:disabled) {
  background: rgba(139, 92, 246, 0.25);
}

.menu-item:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.menu-item svg {
  flex-shrink: 0;
  opacity: 0.7;
}

.menu-item:hover svg {
  opacity: 1;
}

.lang-flag {
  font-size: 14px;
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(26, 26, 31, 0.95);
  backdrop-filter: blur(4px);
  color: #a78bfa;
  font-size: 12px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(139, 92, 246, 0.2);
  border-top-color: #a78bfa;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Transition */
.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: all 0.15s ease;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}
</style>
