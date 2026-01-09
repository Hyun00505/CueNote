<template>
  <Teleport to="body">
    <Transition name="menu-fade">
      <div
        v-if="visible"
        ref="menuRef"
        class="ai-context-menu"
        :style="menuStyle"
        @click.stop
      >
        <div class="menu-header">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H6a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 8 6a4 4 0 0 1 4-4z"/>
          </svg>
          <span>{{ t('ai.assistant') }}</span>
        </div>

        <div class="menu-scroll-container">
        <div class="menu-section">
          <div class="section-label">{{ t('ai.proofread') }}</div>
          <button class="menu-item" @click="handleAction('proofread')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 11l3 3L22 4"/>
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
            </svg>
            <span>{{ t('ai.proofreading') }}</span>
            <span class="badge">KO/EN</span>
          </button>
        </div>

        <div class="menu-section">
          <div class="section-label">{{ t('ai.transform') }}</div>
          <button class="menu-item" @click="handleAction('improve')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 20h9"/>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
            </svg>
            <span>{{ t('ai.improve') }}</span>
          </button>
          <button class="menu-item" @click="handleAction('expand')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
            </svg>
            <span>{{ t('ai.expand') }}</span>
          </button>
          <button class="menu-item" @click="handleAction('shorten')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7"/>
            </svg>
            <span>{{ t('ai.shorten') }}</span>
          </button>
          <button class="menu-item" @click="handleAction('summarize')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <path d="M14 2v6h6"/>
              <path d="M16 13H8M16 17H8M10 9H8"/>
            </svg>
            <span>{{ t('ai.summarize') }}</span>
          </button>
        </div>

        <div class="menu-section">
          <div class="section-label">{{ t('ai.translate') }}</div>
          <button class="menu-item" @click="handleAction('translate', 'ko')" :disabled="loading">
            <span class="lang-flag">🇰🇷</span>
            <span>{{ t('ai.toKorean') }}</span>
          </button>
          <button class="menu-item" @click="handleAction('translate', 'en')" :disabled="loading">
            <span class="lang-flag">🇺🇸</span>
            <span>{{ t('ai.toEnglish') }}</span>
          </button>
          <button class="menu-item" @click="handleAction('translate', 'ja')" :disabled="loading">
            <span class="lang-flag">🇯🇵</span>
            <span>{{ t('ai.toJapanese') }}</span>
          </button>
          <button class="menu-item" @click="handleAction('translate', 'zh')" :disabled="loading">
            <span class="lang-flag">🇨🇳</span>
            <span>{{ t('ai.toChinese') }}</span>
          </button>
        </div>

        <div class="menu-section">
          <div class="section-label">{{ t('ai.style') }}</div>
          <button class="menu-item" @click="handleAction('improve', 'professional')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
            </svg>
            <span>{{ t('ai.professional') }}</span>
          </button>
          <button class="menu-item" @click="handleAction('improve', 'casual')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
              <line x1="9" y1="9" x2="9.01" y2="9"/>
              <line x1="15" y1="9" x2="15.01" y2="9"/>
            </svg>
            <span>{{ t('ai.casual') }}</span>
          </button>
          <button class="menu-item" @click="handleAction('improve', 'academic')" :disabled="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
              <path d="M6 12v5c3 3 9 3 12 0v-5"/>
            </svg>
            <span>{{ t('ai.academic') }}</span>
          </button>
        </div>

        <!-- 직접 요청하기 섹션 -->
        <div class="menu-section custom-section">
          <div class="section-label">{{ t('ai.customRequest') }}</div>
          
          <!-- 선택된 텍스트 미리보기 -->
          <div v-if="selectedText" class="selected-preview">
            <div class="preview-label">{{ t('ai.selectedText') }}</div>
            <div class="preview-text">{{ truncatedSelectedText }}</div>
          </div>
          <div v-else class="no-selection-hint">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 16v-4"/>
              <path d="M12 8h.01"/>
            </svg>
            {{ t('ai.noSelectionHint') }}
          </div>
          
          <div class="custom-input-wrapper">
            <textarea
              ref="customInputRef"
              v-model="customPrompt"
              class="custom-input"
              :placeholder="t('ai.customPlaceholder')"
              rows="2"
              @keydown.enter.ctrl="handleCustomRequest"
              @keydown.enter.meta="handleCustomRequest"
              :disabled="loading"
            ></textarea>
            <button 
              class="custom-submit-btn" 
              @click="handleCustomRequest"
              :disabled="!customPrompt.trim() || loading"
              :title="t('ai.submitCustom')"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
          <div class="custom-hint">{{ t('ai.customHint') }}</div>
        </div>
        </div>

        <!-- 로딩 상태 -->
        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner"></div>
          <span>{{ t('ai.processing') }}</span>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
import { useSettings, useI18n } from '../composables';

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
  (e: 'proofread', text: string): void;
}>();

const loading = ref(false);
const { settings } = useSettings();
const { t } = useI18n();

// 직접 요청하기
const customPrompt = ref('');
const customInputRef = ref<HTMLTextAreaElement | null>(null);

// 메뉴 엘리먼트 참조
const menuRef = ref<HTMLElement | null>(null);
const adjustedPosition = ref({ x: 0, y: 0 });

// 메뉴 위치 계산 (화면 경계 고려)
function calculatePosition() {
  const padding = 10; // 화면 가장자리 여백
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  const menuWidth = 260; // 고정 너비
  const headerHeight = 45; // 헤더 높이 대략
  
  let x = props.position.x;
  let y = props.position.y;

  // 오른쪽 경계 체크
  if (x + menuWidth + padding > viewportWidth) {
    x = viewportWidth - menuWidth - padding;
  }
  
  // 왼쪽 경계 체크
  if (x < padding) {
    x = padding;
  }

  // 사용 가능한 아래쪽 공간
  const spaceBelow = viewportHeight - y - padding;
  // 사용 가능한 위쪽 공간  
  const spaceAbove = props.position.y - padding;
  
  // 최대 높이 결정 (아래 또는 위 공간 중 큰 쪽 사용)
  if (spaceBelow >= 300) {
    // 아래에 충분한 공간이 있으면 아래로 표시
    maxMenuHeight.value = Math.min(spaceBelow, 500);
  } else if (spaceAbove > spaceBelow) {
    // 위쪽 공간이 더 크면 위로 표시
    y = Math.max(padding, props.position.y - Math.min(spaceAbove, 500));
    maxMenuHeight.value = Math.min(spaceAbove, 500);
  } else {
    // 아래쪽으로 표시하되 높이 제한
    maxMenuHeight.value = Math.max(spaceBelow, 200);
  }
  
  // 위쪽 경계 체크
  if (y < padding) {
    y = padding;
    maxMenuHeight.value = viewportHeight - padding * 2;
  }

  adjustedPosition.value = { x, y };
}

// visible이 true가 되면 위치 계산
watch(() => props.visible, async (newVal) => {
  if (newVal) {
    // 초기 위치 설정
    adjustedPosition.value = { x: props.position.x, y: props.position.y };
    // DOM 업데이트 후 실제 크기로 재계산
    await nextTick();
    calculatePosition();
  }
});

// 사용 가능한 최대 높이 계산
const maxMenuHeight = ref(500);

// 메뉴 스타일
const menuStyle = computed(() => ({
  top: `${adjustedPosition.value.y}px`,
  left: `${adjustedPosition.value.x}px`,
  '--menu-max-height': `${maxMenuHeight.value}px`
}));

// 선택된 텍스트 미리보기 (100자 제한)
const truncatedSelectedText = computed(() => {
  const text = props.selectedText;
  if (text.length > 100) {
    return text.slice(0, 100) + '...';
  }
  return text;
});

async function handleAction(action: string, option?: string) {
  if (!props.selectedText.trim()) {
    emit('error', t('ai.noTextSelected'));
    return;
  }

  // 맞춤법 검사는 별도 처리 (패널 사용)
  if (action === 'proofread') {
    emit('proofread', props.selectedText);
    emit('close');
    return;
  }

  loading.value = true;

  // 스트리밍 API 사용 - LLM 설정 포함
  // language: 'auto'로 설정하여 원문과 같은 언어로 응답
  const body = {
    content: props.selectedText,
    action,
    target_language: action === 'translate' ? (option || 'en') : 'en',
    style: action === 'improve' ? (option || 'professional') : 'professional',
    language: 'auto',
    // LLM 설정 추가
    provider: settings.value.llm.provider,
    api_key: settings.value.llm.apiKey,
    model: settings.value.llm.model
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
    const providerName = settings.value.llm.provider === 'gemini' ? 'Gemini API' : 'Ollama';
    emit('error', `AI 처리에 실패했습니다. ${providerName}가 올바르게 설정되었는지 확인하세요.`);
    emit('stream-end');
  } finally {
    loading.value = false;
  }
}

// 직접 요청하기 처리
async function handleCustomRequest() {
  const promptText = customPrompt.value.trim();
  
  if (!promptText) {
    emit('error', t('ai.enterPrompt'));
    return;
  }

  loading.value = true;

  // 선택된 텍스트가 없으면 빈 문자열로 처리 (AI가 지시만 수행)
  const content = props.selectedText.trim() || '';
  
  const body = {
    content: content,
    action: 'custom',
    custom_prompt: promptText,
    language: 'auto',
    provider: settings.value.llm.provider,
    api_key: settings.value.llm.apiKey,
    model: settings.value.llm.model
  };

  try {
    emit('stream-start', {
      action: 'custom',
      original: content,
      hasSelection: !!content
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
      
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data:')) {
          let data = line.slice(5);
          if (data.startsWith(' ')) {
            data = data.slice(1);
          }
          data = data.replace(/\\n/g, '\n');
          if (data !== '') {
            emit('stream-chunk', data);
          }
        } else if (line.startsWith('event:')) {
          const event = line.slice(6).trim();
          if (event === 'done') {
            emit('stream-end');
          }
        }
      }
    }

    // 요청 완료 후 입력창 초기화
    customPrompt.value = '';

  } catch (error) {
    console.error('Custom AI request failed:', error);
    const providerName = settings.value.llm.provider === 'gemini' ? 'Gemini API' : 'Ollama';
    emit('error', `AI 처리에 실패했습니다. ${providerName}가 올바르게 설정되었는지 확인하세요.`);
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
  width: 260px;
  max-height: var(--menu-max-height, 500px);
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary, #16161a);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 12px;
  box-shadow: 
    0 4px 24px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.05),
    0 0 40px rgba(139, 92, 246, 0.15);
  backdrop-filter: blur(12px);
  overflow: hidden;
}

/* 스크롤 컨테이너 */
.menu-scroll-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.4) transparent;
}

/* 스크롤바 스타일 (Webkit) */
.menu-scroll-container::-webkit-scrollbar {
  width: 8px;
}

.menu-scroll-container::-webkit-scrollbar-track {
  background: transparent;
}

.menu-scroll-container::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.4);
  border-radius: 4px;
}

.menu-scroll-container::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.6);
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

/* 직접 요청하기 섹션 */
.custom-section {
  padding-bottom: 12px !important;
}

.custom-input-wrapper {
  display: flex;
  gap: 8px;
  padding: 0 8px;
  align-items: flex-end;
}

.custom-input {
  flex: 1;
  padding: 10px 12px;
  background: rgba(139, 92, 246, 0.08);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  line-height: 1.4;
  resize: none;
  transition: all 0.15s ease;
}

.custom-input:focus {
  outline: none;
  border-color: rgba(139, 92, 246, 0.5);
  background: rgba(139, 92, 246, 0.12);
}

.custom-input::placeholder {
  color: var(--text-muted);
}

.custom-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.custom-submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.8), rgba(99, 102, 241, 0.8));
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.custom-submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(139, 92, 246, 1), rgba(99, 102, 241, 1));
  transform: scale(1.05);
}

.custom-submit-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.custom-submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.custom-hint {
  padding: 6px 8px 0;
  font-size: 10px;
  color: var(--text-muted);
  opacity: 0.7;
}

/* 선택된 텍스트 미리보기 */
.selected-preview {
  margin: 0 8px 10px;
  padding: 8px 10px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 6px;
}

.preview-label {
  font-size: 10px;
  font-weight: 600;
  color: #a78bfa;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.preview-text {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
  word-break: break-word;
  white-space: pre-wrap;
  max-height: 60px;
  overflow-y: auto;
}

.no-selection-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 8px 10px;
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text-muted);
}

.no-selection-hint svg {
  opacity: 0.6;
}

.badge {
  margin-left: auto;
  padding: 2px 6px;
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(16, 185, 129, 0.2));
  color: #4ade80;
  border-radius: 4px;
  border: 1px solid rgba(34, 197, 94, 0.3);
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
  background: var(--bg-secondary, #16161a);
  opacity: 0.98;
  backdrop-filter: blur(4px);
  color: #a78bfa;
  font-size: 12px;
  border-radius: 12px;
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
