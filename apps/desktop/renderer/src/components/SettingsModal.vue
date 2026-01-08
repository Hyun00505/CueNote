<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container">
          <!-- Header -->
          <div class="modal-header">
            <div class="header-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
              <span>설정</span>
            </div>
            <button class="close-btn" @click="$emit('close')">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- Content -->
          <div class="modal-content">
            <!-- LLM Provider Section -->
            <section class="settings-section">
              <h3 class="section-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
                AI 모델 제공자
              </h3>
              
              <div class="provider-cards">
                <button
                  v-for="provider in providers"
                  :key="provider.id"
                  class="provider-card"
                  :class="{ active: settings.llm.provider === provider.id }"
                  @click="onProviderChange(provider.id)"
                >
                  <div class="provider-icon">
                    <svg v-if="provider.id === 'ollama'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <circle cx="12" cy="12" r="10"/>
                      <path d="M12 6v6l4 2"/>
                    </svg>
                    <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                      <path d="M2 17l10 5 10-5"/>
                      <path d="M2 12l10 5 10-5"/>
                    </svg>
                  </div>
                  <div class="provider-info">
                    <span class="provider-name">{{ provider.name }}</span>
                    <span class="provider-desc">{{ provider.description }}</span>
                  </div>
                  <div class="provider-check" v-if="settings.llm.provider === provider.id">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  </div>
                </button>
              </div>
            </section>

            <!-- API Key Section (for Gemini) -->
            <section class="settings-section" v-if="settings.llm.provider === 'gemini'">
              <h3 class="section-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                API 키
              </h3>
              
              <div class="api-key-input-wrapper">
                <input
                  type="password"
                  v-model="settings.llm.apiKey"
                  placeholder="Gemini API 키를 입력하세요"
                  class="api-key-input"
                  :class="{ 
                    valid: keyValidationResult === true,
                    invalid: keyValidationResult === false
                  }"
                />
                <button 
                  class="validate-btn"
                  @click="handleValidateKey"
                  :disabled="isValidatingKey || !settings.llm.apiKey"
                >
                  <span v-if="isValidatingKey" class="loading-spinner"></span>
                  <span v-else>검증</span>
                </button>
              </div>
              
              <div class="validation-result" v-if="keyValidationResult !== null">
                <span v-if="keyValidationResult" class="valid-text">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                  API 키가 유효합니다
                </span>
                <span v-else class="invalid-text">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                  </svg>
                  API 키가 유효하지 않습니다
                </span>
              </div>

              <a href="https://aistudio.google.com/app/apikey" target="_blank" class="api-key-link">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
                Google AI Studio에서 API 키 발급받기
              </a>
            </section>

            <!-- Model Selection Section -->
            <section class="settings-section">
              <div class="section-header-with-action">
                <h3 class="section-title">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="12 2 2 7 12 12 22 7 12 2"/>
                    <polyline points="2 17 12 22 22 17"/>
                    <polyline points="2 12 12 17 22 12"/>
                  </svg>
                  모델 선택
                </h3>
                <button 
                  v-if="settings.llm.provider === 'ollama'"
                  class="refresh-btn" 
                  @click="handleRefreshOllama"
                  :disabled="isRefreshing"
                  title="모델 목록 새로고침"
                >
                  <svg 
                    width="14" height="14" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    stroke-width="2"
                    :class="{ spinning: isRefreshing }"
                  >
                    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
                    <path d="M21 3v5h-5"/>
                    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
                    <path d="M8 16H3v5"/>
                  </svg>
                </button>
              </div>

              <!-- Ollama 에러 메시지 -->
              <div v-if="settings.llm.provider === 'ollama' && ollamaError" class="ollama-error">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>{{ ollamaError }}</span>
              </div>
              
              <!-- 로딩 상태 -->
              <div v-if="settingsLoading && currentModels.length === 0" class="models-loading">
                <span class="loading-spinner"></span>
                <span>모델 목록 불러오는 중...</span>
              </div>

              <div v-else class="model-list">
                <button
                  v-for="model in currentModels"
                  :key="model.id"
                  class="model-card"
                  :class="{ active: settings.llm.model === model.id }"
                  @click="settings.llm.model = model.id"
                >
                  <div class="model-left">
                    <div class="model-radio">
                      <div class="radio-dot" :class="{ checked: settings.llm.model === model.id }"></div>
                    </div>
                    <div class="model-info">
                      <div class="model-header">
                        <span class="model-name">{{ model.name }}</span>
                        <!-- Gemini만 FREE/PAID 태그 표시 -->
                        <span v-if="settings.llm.provider === 'gemini' && model.free" class="free-badge">FREE</span>
                        <span v-if="settings.llm.provider === 'gemini' && !model.free" class="paid-badge">PAID</span>
                      </div>
                      <span class="model-desc">{{ model.description }}</span>
                      <span class="model-id">{{ model.id }}</span>
                    </div>
                  </div>
                </button>
              </div>

              <p v-if="currentModels.length === 0 && !ollamaError" class="no-models">
                {{ settings.llm.provider === 'ollama' ? '설치된 모델이 없습니다' : '모델을 불러오는 중...' }}
              </p>

              <!-- Ollama 모델 설치 안내 -->
              <div v-if="settings.llm.provider === 'ollama' && currentModels.length === 0" class="ollama-install-hint">
                <p>터미널에서 다음 명령어로 모델을 설치하세요:</p>
                <code>ollama pull qwen2.5:7b</code>
              </div>
            </section>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button class="reset-btn" @click="handleReset">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
                <path d="M21 3v5h-5"/>
                <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
                <path d="M8 16H3v5"/>
              </svg>
              초기화
            </button>
            <button class="save-btn" @click="$emit('close')">
              완료
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch, ref } from 'vue';
import { useSettings } from '../composables';

const props = defineProps<{
  isOpen: boolean;
}>();

defineEmits<{
  close: [];
}>();

const {
  settings,
  providers,
  ollamaModels,
  geminiModels,
  ollamaError,
  isValidatingKey,
  keyValidationResult,
  settingsLoading,
  initSettings,
  validateApiKey,
  onProviderChange,
  resetSettings,
  refreshOllamaModels
} = useSettings();

const isRefreshing = ref(false);
const hasInitialized = ref(false);

// 모달이 열릴 때만 데이터 로드 (이미 로드되어 있으면 스킵)
watch(() => props.isOpen, async (isOpen) => {
  if (isOpen && !hasInitialized.value) {
    await initSettings();
    hasInitialized.value = true;
  }
}, { immediate: true });

async function handleRefreshOllama() {
  isRefreshing.value = true;
  await refreshOllamaModels();
  isRefreshing.value = false;
}

const currentModels = computed(() => {
  if (settings.value.llm.provider === 'gemini') {
    return geminiModels.value;
  }
  return ollamaModels.value;
});

async function handleValidateKey() {
  await validateApiKey(settings.value.llm.apiKey);
}

function handleReset() {
  resetSettings();
}

// Provider 변경 시 모델 목록 갱신
watch(() => settings.value.llm.provider, () => {
  // 이미 composable에서 처리됨
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  width: 520px;
  max-height: 85vh;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-title svg {
  color: #e8d5b7;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-primary);
}

/* Content */
.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.settings-section {
  margin-bottom: 28px;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  margin-bottom: 14px;
}

.section-title svg {
  opacity: 0.7;
}

/* Provider Cards */
.provider-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.provider-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.provider-card:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
}

.provider-card.active {
  background: rgba(232, 213, 183, 0.08);
  border-color: rgba(232, 213, 183, 0.3);
}

.provider-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  color: var(--text-muted);
}

.provider-card.active .provider-icon {
  background: rgba(232, 213, 183, 0.1);
  color: #e8d5b7;
}

.provider-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.provider-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.provider-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.provider-check {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #e8d5b7;
  border-radius: 50%;
  color: #1a1a2e;
}

/* API Key Input */
.api-key-input-wrapper {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.api-key-input {
  flex: 1;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  transition: all 0.15s ease;
}

.api-key-input:focus {
  outline: none;
  border-color: rgba(232, 213, 183, 0.4);
  background: rgba(255, 255, 255, 0.04);
}

.api-key-input.valid {
  border-color: rgba(34, 197, 94, 0.5);
}

.api-key-input.invalid {
  border-color: rgba(239, 68, 68, 0.5);
}

.api-key-input::placeholder {
  color: var(--text-muted);
}

.validate-btn {
  padding: 12px 20px;
  background: rgba(232, 213, 183, 0.1);
  border: 1px solid rgba(232, 213, 183, 0.2);
  border-radius: 10px;
  color: #e8d5b7;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  min-width: 70px;
}

.validate-btn:hover:not(:disabled) {
  background: rgba(232, 213, 183, 0.15);
  border-color: rgba(232, 213, 183, 0.3);
}

.validate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(232, 213, 183, 0.3);
  border-top-color: #e8d5b7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.validation-result {
  margin-bottom: 12px;
}

.valid-text, .invalid-text {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
}

.valid-text {
  color: #22c55e;
}

.invalid-text {
  color: #ef4444;
}

.api-key-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.15s ease;
}

.api-key-link:hover {
  color: #e8d5b7;
}

/* Models Loading */
.models-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 32px;
  color: var(--text-muted);
  font-size: 13px;
}

/* Model List */
.model-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 280px;
  overflow-y: auto;
}

.model-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.model-card:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
}

.model-card.active {
  background: rgba(232, 213, 183, 0.06);
  border-color: rgba(232, 213, 183, 0.3);
}

.model-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.model-radio {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-subtle);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
  transition: all 0.15s ease;
}

.model-card:hover .model-radio {
  border-color: rgba(255, 255, 255, 0.2);
}

.model-card.active .model-radio {
  border-color: #e8d5b7;
}

.radio-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: transparent;
  transition: all 0.15s ease;
}

.radio-dot.checked {
  background: #e8d5b7;
}

.model-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.model-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.model-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.model-card.active .model-name {
  color: #e8d5b7;
}

.free-badge {
  padding: 2px 6px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(16, 185, 129, 0.2));
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 4px;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: #22c55e;
}

.paid-badge {
  padding: 2px 6px;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.2));
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 4px;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: #fbbf24;
}

.model-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.model-id {
  font-size: 11px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  color: var(--text-muted);
  opacity: 0.7;
}

.model-check {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: #e8d5b7;
  border-radius: 50%;
  color: #1a1a2e;
}

.no-models {
  padding: 24px;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}

/* Section Header with Action */
.section-header-with-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.section-header-with-action .section-title {
  margin-bottom: 0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn svg.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Ollama Error */
.ollama-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.2);
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #fbbf24;
}

.ollama-error svg {
  flex-shrink: 0;
}

/* Ollama Install Hint */
.ollama-install-hint {
  padding: 14px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed var(--border-subtle);
  border-radius: 8px;
  margin-top: 12px;
}

.ollama-install-hint p {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.ollama-install-hint code {
  display: block;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: #e8d5b7;
}

/* Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
}

.reset-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.reset-btn:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
}

.save-btn {
  padding: 10px 24px;
  background: #e8d5b7;
  border: none;
  border-radius: 8px;
  color: #1a1a2e;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.save-btn:hover {
  background: #f0e0c4;
}

/* Transition */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
  opacity: 0;
}
</style>
