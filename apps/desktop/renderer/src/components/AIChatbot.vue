<template>
  <Teleport to="body">
    <!-- 플로팅 뱃지 -->
    <button
      class="chatbot-badge"
      :class="{ 'is-open': isOpen, 'has-messages': messages.length > 0 }"
      @click="togglePanel"
      title="AI 챗봇"
    >
      <svg v-if="!isOpen" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        <circle cx="9" cy="10" r="1" fill="currentColor" />
        <circle cx="12" cy="10" r="1" fill="currentColor" />
        <circle cx="15" cy="10" r="1" fill="currentColor" />
      </svg>
      <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
      <span v-if="!isOpen && messages.length > 0" class="badge-dot" />
    </button>

    <!-- 채팅 패널 -->
    <Transition name="chatpanel">
      <div v-if="isOpen" class="chatbot-panel" :style="panelStyle">
        <!-- 리사이즈 핸들 (좌상단 모서리) -->
        <div class="resize-handle" @mousedown.prevent="startResize" />
        <!-- 헤더 (드래그 핸들) -->
        <div class="chatbot-header" @mousedown="startDrag">
          <div class="header-left">
            <div class="header-avatar">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a7 7 0 0 1 7 7c0 3-2 5.5-4 7l-3 3-3-3c-2-1.5-4-4-4-7a7 7 0 0 1 7-7z" />
                <circle cx="12" cy="9" r="2" fill="currentColor" />
              </svg>
            </div>
            <div class="header-info">
              <span class="header-title">CueNote AI</span>
              <span class="header-status">{{ isLoading ? '응답 중...' : '온라인' }}</span>
            </div>
          </div>
          <div class="header-actions">
            <!-- 투명도 슬라이더 -->
            <div class="opacity-control" @mousedown.stop>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 2a10 10 0 0 1 0 20" fill="currentColor" opacity="0.3" />
              </svg>
              <input
                type="range"
                class="opacity-slider"
                v-model.number="panelOpacity"
                min="30"
                max="100"
                step="5"
                title="투명도"
              />
              <span class="opacity-value">{{ panelOpacity }}%</span>
            </div>
            <button class="header-action" @click.stop="handleClear" title="대화 초기화">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18" /><path d="M8 6V4h8v2" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 메시지 영역 -->
        <div class="chatbot-messages" ref="messagesContainer">
          <!-- 빈 상태 -->
          <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <p class="empty-title">무엇을 도와드릴까요?</p>
            <div class="quick-actions">
              <button @click="quickAction('이 글 요약해줘')">📝 현재 노트 요약</button>
              <button @click="quickAction('오늘 일정 보여줘')">📅 오늘 일정</button>
              <button @click="quickAction('노트 목록 보여줘')">📋 노트 목록</button>
              <button @click="quickAction('TODO 보여줘')">✅ TODO 조회</button>
            </div>
          </div>

          <!-- 메시지 목록 -->
          <template v-for="msg in messages" :key="msg.id">
            <!-- 사용자 메시지 -->
            <div v-if="msg.role === 'user'" class="message message-user">
              <div class="message-bubble user-bubble">{{ msg.content }}</div>
            </div>

            <!-- 도구 호출 표시 -->
            <div v-else-if="msg.role === 'tool_call'" class="message message-tool">
              <div class="tool-badge">
                <span class="tool-icon">{{ msg.content.slice(0, 2) }}</span>
                <span class="tool-label">{{ msg.content.slice(2).trim() }}</span>
              </div>
            </div>

            <!-- 도구 결과 표시 -->
            <div v-else-if="msg.role === 'tool_result'" class="message message-tool-result">
              <div class="tool-result-badge">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <span>{{ msg.content }}</span>
              </div>
            </div>

            <!-- AI 메시지 -->
            <div v-else-if="msg.role === 'assistant'" class="message message-assistant">
              <div class="message-bubble assistant-bubble" v-html="renderMarkdown(msg.content)" />
            </div>
          </template>

          <!-- 로딩 인디케이터 -->
          <div v-if="isLoading && (!messages.length || messages[messages.length - 1]?.content === '')" class="message message-assistant">
            <div class="message-bubble assistant-bubble typing-indicator">
              <span /><span /><span />
            </div>
          </div>
        </div>

        <!-- 입력 영역 -->
        <div class="chatbot-input">
          <input
            ref="inputRef"
            v-model="inputText"
            type="text"
            placeholder="메시지를 입력하세요..."
            :disabled="isLoading"
            @keydown.enter="handleSend"
          />
          <button
            class="send-button"
            :disabled="!inputText.trim() || isLoading"
            @click="handleSend"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import { useChatbot } from '../composables/useChatbot';
import { useSettings } from '../composables/useSettings';
import { getActiveNoteInfo } from '../composables/useEditor';

const { messages, isLoading, sendMessage, clearMessages } = useChatbot();
const { settings } = useSettings();

const isOpen = ref(false);
const inputText = ref('');
const inputRef = ref<HTMLInputElement | null>(null);
const messagesContainer = ref<HTMLElement | null>(null);

// 리사이즈 관련
const panelWidth = ref(380);
const panelHeight = ref(520);
const isResizing = ref(false);

// 드래그 관련
const isDragging = ref(false);
const panelX = ref<number | null>(null); // null = 기본 위치 (right:24px)
const panelY = ref<number | null>(null); // null = 기본 위치 (bottom:90px)

// 투명도
const panelOpacity = ref(100);

const MIN_W = 320;
const MAX_W = 700;
const MIN_H = 400;
const MAX_H = 800;

const panelStyle = computed(() => {
  const base: Record<string, string> = {
    width: `${panelWidth.value}px`,
    height: `${panelHeight.value}px`,
    opacity: `${panelOpacity.value / 100}`,
  };
  if (panelX.value !== null && panelY.value !== null) {
    // 드래그된 위치 사용
    base.left = `${panelX.value}px`;
    base.top = `${panelY.value}px`;
    base.right = 'auto';
    base.bottom = 'auto';
  }
  return base;
});

function startResize(e: MouseEvent) {
  isResizing.value = true;
  const startX = e.clientX;
  const startY = e.clientY;
  const startW = panelWidth.value;
  const startH = panelHeight.value;

  // 드래그된 상태라면 현재 위치를 기준으로 우하단 고정점 계산
  const hasDraggedPos = panelX.value !== null && panelY.value !== null;
  const startPanelX = panelX.value ?? 0;
  const startPanelY = panelY.value ?? 0;
  // 우하단 고정점 (리사이즈 시 이 점이 고정됨)
  const anchorRight = startPanelX + startW;
  const anchorBottom = startPanelY + startH;

  function onMove(ev: MouseEvent) {
    // 좌상단 핸들: 왼쪽으로 드래그 → 넓어짐, 위로 드래그 → 높아짐
    const dx = startX - ev.clientX;
    const dy = startY - ev.clientY;
    const newW = Math.min(MAX_W, Math.max(MIN_W, startW + dx));
    const newH = Math.min(MAX_H, Math.max(MIN_H, startH + dy));
    panelWidth.value = newW;
    panelHeight.value = newH;

    // 드래그된 상태(left/top 사용)면 우하단 고정점 유지를 위해 위치 업데이트
    if (hasDraggedPos) {
      panelX.value = anchorRight - newW;
      panelY.value = anchorBottom - newH;
    }
  }

  function onUp() {
    isResizing.value = false;
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('mouseup', onUp);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }

  document.body.style.cursor = 'nwse-resize';
  document.body.style.userSelect = 'none';
  document.addEventListener('mousemove', onMove);
  document.addEventListener('mouseup', onUp);
}

// ─── 드래그로 위치 이동 ───
function startDrag(e: MouseEvent) {
  // 버튼이나 인터랙티브 요소 클릭 시 드래그 무시
  const target = e.target as HTMLElement;
  if (target.closest('button') || target.closest('input') || target.closest('.opacity-control')) return;

  isDragging.value = true;

  // 현재 패널의 실제 위치 계산
  const panelEl = document.querySelector('.chatbot-panel') as HTMLElement;
  if (!panelEl) return;
  const rect = panelEl.getBoundingClientRect();

  const offsetX = e.clientX - rect.left;
  const offsetY = e.clientY - rect.top;

  function onMove(ev: MouseEvent) {
    const x = ev.clientX - offsetX;
    const y = ev.clientY - offsetY;
    // 화면 밖으로 나가지 않도록 제한
    panelX.value = Math.max(0, Math.min(window.innerWidth - panelWidth.value, x));
    panelY.value = Math.max(0, Math.min(window.innerHeight - 60, y));
  }

  function onUp() {
    isDragging.value = false;
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('mouseup', onUp);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }

  document.body.style.cursor = 'grabbing';
  document.body.style.userSelect = 'none';
  document.addEventListener('mousemove', onMove);
  document.addEventListener('mouseup', onUp);
}

function togglePanel() {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    nextTick(() => inputRef.value?.focus());
  }
}

function handleSend(e?: KeyboardEvent | Event) {
  // 한글 IME 조합 중이면 전송하지 않음 (글자 잘림 방지)
  if (e && 'isComposing' in e && (e as KeyboardEvent).isComposing) return;
  if (!inputText.value.trim() || isLoading.value) return;
  const text = inputText.value;
  inputText.value = '';
  const noteInfo = getActiveNoteInfo();
  sendMessage(
    text,
    settings.value.llm.provider,
    settings.value.llm.apiKey || settings.value.llm.apiKeys?.[settings.value.llm.provider as keyof typeof settings.value.llm.apiKeys] || '',
    settings.value.llm.model,
    noteInfo.path,
    noteInfo.content,
  );
}

function quickAction(text: string) {
  inputText.value = text;
  handleSend();
}

function handleClear() {
  clearMessages();
}

function renderMarkdown(text: string): string {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');
}

// 자동 스크롤
watch(
  () => messages.value.length > 0 ? messages.value[messages.value.length - 1]?.content : '',
  () => {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    });
  },
  { flush: 'post' }
);

watch(
  () => messages.value.length,
  () => {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    });
  },
);
</script>

<style scoped>
/* ─── 플로팅 뱃지 ─── */
.chatbot-badge {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #89b4fa 0%, #b4befe 50%, #cba6f7 100%);
  color: #1e1e2e;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 4px 20px rgba(137, 180, 250, 0.35),
    0 0 40px rgba(203, 166, 247, 0.15);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 10001;
  animation: badge-pulse 3s ease-in-out infinite;
}

.chatbot-badge:hover {
  transform: scale(1.1);
  box-shadow:
    0 6px 28px rgba(137, 180, 250, 0.5),
    0 0 50px rgba(203, 166, 247, 0.25);
}

.chatbot-badge.is-open {
  background: var(--bg-tertiary, #313244);
  color: var(--text-secondary, #a6adc8);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  animation: none;
}

.chatbot-badge.is-open:hover {
  color: var(--text-primary, #cdd6f4);
}

.badge-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #a6e3a1;
  border: 2px solid #1e1e2e;
  animation: dot-pulse 2s ease-in-out infinite;
}

@keyframes badge-pulse {
  0%, 100% { box-shadow: 0 4px 20px rgba(137, 180, 250, 0.35), 0 0 40px rgba(203, 166, 247, 0.15); }
  50% { box-shadow: 0 4px 24px rgba(137, 180, 250, 0.5), 0 0 55px rgba(203, 166, 247, 0.25); }
}

@keyframes dot-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* ─── 채팅 패널 ─── */
.chatbot-panel {
  position: fixed;
  bottom: 90px;
  right: 24px;
  border-radius: 16px;
  background: var(--bg-secondary, #1e1e2e);
  border: 1px solid var(--border-primary, #313244);
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.4),
    0 0 1px rgba(255, 255, 255, 0.05) inset;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 10000;
  backdrop-filter: blur(20px);
}

/* ─── 리사이즈 핸들 ─── */
.resize-handle {
  position: absolute;
  top: 0;
  left: 0;
  width: 16px;
  height: 16px;
  cursor: nwse-resize;
  z-index: 10;
  border-top-left-radius: 16px;
}

.resize-handle::after {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  width: 8px;
  height: 8px;
  border-top: 2px solid var(--text-tertiary, #585b70);
  border-left: 2px solid var(--text-tertiary, #585b70);
  border-top-left-radius: 3px;
  opacity: 0;
  transition: opacity 0.2s;
}

.chatbot-panel:hover .resize-handle::after {
  opacity: 0.5;
}

.resize-handle:hover::after {
  opacity: 1 !important;
}

/* ─── 헤더 (드래그 핸들) ─── */
.chatbot-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: linear-gradient(180deg,
    rgba(137, 180, 250, 0.08) 0%,
    rgba(137, 180, 250, 0) 100%
  );
  border-bottom: 1px solid var(--border-primary, #313244);
  cursor: grab;
  user-select: none;
}

.chatbot-header:active {
  cursor: grabbing;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.header-avatar {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, #89b4fa, #cba6f7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1e1e2e;
}

.header-info {
  display: flex;
  flex-direction: column;
}

.header-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #cdd6f4);
}

.header-status {
  font-size: 11px;
  color: #a6e3a1;
}

/* ─── 투명도 컨트롤 ─── */
.opacity-control {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  cursor: default;
  color: var(--text-tertiary, #585b70);
}

.opacity-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 50px;
  height: 3px;
  background: rgba(137, 180, 250, 0.2);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.opacity-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #89b4fa;
  cursor: pointer;
  transition: transform 0.1s;
}

.opacity-slider::-webkit-slider-thumb:hover {
  transform: scale(1.3);
}

.opacity-value {
  font-size: 10px;
  min-width: 28px;
  text-align: right;
  color: var(--text-tertiary, #585b70);
}

.header-action {
  background: none;
  border: none;
  color: var(--text-tertiary, #585b70);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s;
}

.header-action:hover {
  background: var(--bg-tertiary, #313244);
  color: var(--text-secondary, #a6adc8);
}

/* ─── 메시지 영역 ─── */
.chatbot-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  scroll-behavior: smooth;
}

.chatbot-messages::-webkit-scrollbar {
  width: 4px;
}
.chatbot-messages::-webkit-scrollbar-thumb {
  background: var(--border-primary, #313244);
  border-radius: 4px;
}

/* ─── 빈 상태 ─── */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-tertiary, #585b70);
}

.empty-icon {
  opacity: 0.3;
}

.empty-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary, #a6adc8);
  margin: 0;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
  margin-top: 4px;
}

.quick-actions button {
  background: var(--bg-tertiary, #313244);
  border: 1px solid var(--border-primary, #45475a);
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 12px;
  color: var(--text-secondary, #a6adc8);
  cursor: pointer;
  transition: all 0.2s;
}

.quick-actions button:hover {
  background: rgba(137, 180, 250, 0.1);
  border-color: rgba(137, 180, 250, 0.3);
  color: #89b4fa;
}

/* ─── 메시지 버블 ─── */
.message {
  display: flex;
  max-width: 100%;
}

.message-user {
  justify-content: flex-end;
}

.message-assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.5;
  word-break: break-word;
}

.user-bubble {
  background: linear-gradient(135deg, #89b4fa, #74c7ec);
  color: #1e1e2e;
  border-bottom-right-radius: 4px;
}

.assistant-bubble {
  background: var(--bg-tertiary, #313244);
  color: var(--text-primary, #cdd6f4);
  border-bottom-left-radius: 4px;
}

.assistant-bubble :deep(code) {
  background: rgba(0, 0, 0, 0.2);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 12px;
}

.assistant-bubble :deep(strong) {
  color: #89b4fa;
}

/* ─── 도구 호출 표시 ─── */
.message-tool, .message-tool-result {
  justify-content: center;
}

.tool-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 20px;
  background: rgba(203, 166, 247, 0.1);
  border: 1px solid rgba(203, 166, 247, 0.2);
  font-size: 12px;
  color: #cba6f7;
  animation: tool-appear 0.3s ease;
}

.tool-icon {
  font-size: 13px;
}

.tool-label {
  font-weight: 500;
}

.tool-result-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 20px;
  background: rgba(166, 227, 161, 0.1);
  border: 1px solid rgba(166, 227, 161, 0.2);
  font-size: 11px;
  color: #a6e3a1;
  animation: tool-appear 0.3s ease;
}

@keyframes tool-appear {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}

/* ─── 타이핑 인디케이터 ─── */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 18px;
}

.typing-indicator span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-tertiary, #585b70);
  animation: typing-bounce 1.4s ease-in-out infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* ─── 입력 영역 ─── */
.chatbot-input {
  display: flex;
  gap: 8px;
  padding: 12px 14px;
  border-top: 1px solid var(--border-primary, #313244);
  background: var(--bg-secondary, #1e1e2e);
}

.chatbot-input input {
  flex: 1;
  background: var(--bg-tertiary, #313244);
  border: 1px solid var(--border-primary, #45475a);
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  color: var(--text-primary, #cdd6f4);
  outline: none;
  transition: all 0.2s;
}

.chatbot-input input::placeholder {
  color: var(--text-tertiary, #585b70);
}

.chatbot-input input:focus {
  border-color: rgba(137, 180, 250, 0.4);
  box-shadow: 0 0 0 2px rgba(137, 180, 250, 0.1);
}

.send-button {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #89b4fa, #b4befe);
  color: #1e1e2e;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.send-button:not(:disabled):hover {
  transform: scale(1.05);
  box-shadow: 0 2px 12px rgba(137, 180, 250, 0.3);
}

/* ─── 패널 트랜지션 ─── */
.chatpanel-enter-active {
  animation: panel-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.chatpanel-leave-active {
  animation: panel-in 0.2s ease reverse;
}

@keyframes panel-in {
  from {
    opacity: 0;
    transform: translateY(16px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
