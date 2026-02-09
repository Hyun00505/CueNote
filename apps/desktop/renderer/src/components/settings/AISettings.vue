<template>
  <div
    id="section-ai"
    class="settings-category"
  >
    <h2 class="category-title">
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path d="M12 2L2 7l10 5 10-5-10-5z" />
        <path d="M2 17l10 5 10-5" />
        <path d="M2 12l10 5 10-5" />
      </svg>
      {{ t('settings.aiTitle') }}
    </h2>

    <section class="settings-section">
      <h3 class="section-title">
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
        {{ t('settings.aiProvider') }}
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
            <!-- Ollama 아이콘 -->
            <svg
              v-if="provider.id === 'ollama'"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <circle
                cx="12"
                cy="12"
                r="10"
              />
              <path d="M12 6v6l4 2" />
            </svg>
            <!-- Gemini 아이콘 -->
            <svg
              v-else-if="provider.id === 'gemini'"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
            <!-- OpenAI 아이콘 -->
            <svg
              v-else-if="provider.id === 'openai'"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <circle
                cx="12"
                cy="12"
                r="9"
              />
              <path d="M12 7v5l3 3" />
              <path d="M8 12h8" />
            </svg>
            <!-- Anthropic 아이콘 -->
            <svg
              v-else-if="provider.id === 'anthropic'"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <path d="M12 3L4 9v6l8 6 8-6V9l-8-6z" />
              <path d="M12 12v9" />
              <path d="M12 12L4 9" />
              <path d="M12 12l8-3" />
            </svg>
            <!-- 기본 아이콘 -->
            <svg
              v-else
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <rect
                x="3"
                y="3"
                width="18"
                height="18"
                rx="2"
              />
              <path d="M12 8v8" />
              <path d="M8 12h8" />
            </svg>
          </div>
          <div class="provider-info">
            <span class="provider-name">{{ provider.name }}</span>
            <span class="provider-desc">{{ provider.description }}</span>
          </div>
          <div
            v-if="settings.llm.provider === provider.id"
            class="provider-check"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
        </button>
      </div>
    </section>

    <!-- API Key Section (for providers that require API key) -->
    <section
      v-if="currentProvider?.requiresApiKey"
      class="settings-section"
    >
      <h3 class="section-title">
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <rect
            x="3"
            y="11"
            width="18"
            height="11"
            rx="2"
            ry="2"
          />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
        {{ currentProvider?.name }} API Key
      </h3>

      <div class="api-key-input-wrapper">
        <input
          v-model="settings.llm.apiKey"
          type="password"
          :placeholder="getApiKeyPlaceholder()"
          class="api-key-input"
          :class="{
            valid: keyValidationResult === true,
            invalid: keyValidationResult === false
          }"
          @input="onApiKeyChange"
        >
        <button
          class="validate-btn"
          :disabled="isValidatingKey || !settings.llm.apiKey"
          @click="handleValidateKey"
        >
          <span
            v-if="isValidatingKey"
            class="loading-spinner"
          />
          <span v-else>{{ t('settings.validate') }}</span>
        </button>
      </div>

      <div
        v-if="keyValidationResult !== null"
        class="validation-result"
      >
        <span
          v-if="keyValidationResult"
          class="valid-text"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          {{ t('settings.validKey') }}
        </span>
        <span
          v-else
          class="invalid-text"
        >
          <svg
            width="14"
            height="14"
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
              x1="15"
              y1="9"
              x2="9"
              y2="15"
            />
            <line
              x1="9"
              y1="9"
              x2="15"
              y2="15"
            />
          </svg>
          {{ t('settings.invalidKey') }}
        </span>
      </div>

      <button
        v-if="currentProvider?.apiKeyUrl"
        type="button"
        class="api-key-link"
        @click="openApiKeyPage"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
          <polyline points="15 3 21 3 21 9" />
          <line
            x1="10"
            y1="14"
            x2="21"
            y2="3"
          />
        </svg>
        {{ currentProvider?.name }} API Key 발급
      </button>
    </section>

    <!-- Model Selection Section -->
    <section class="settings-section">
      <div class="section-header-with-action">
        <h3 class="section-title">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polygon points="12 2 2 7 12 12 22 7 12 2" />
            <polyline points="2 17 12 22 22 17" />
            <polyline points="2 12 12 17 22 12" />
          </svg>
          {{ t('settings.modelSelect') }}
        </h3>
        <button
          v-if="settings.llm.provider === 'ollama'"
          class="refresh-btn"
          :disabled="isRefreshing"
          :title="t('settings.refreshModels')"
          @click="handleRefreshOllama"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            :class="{ spinning: isRefreshing }"
          >
            <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
            <path d="M21 3v5h-5" />
            <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
            <path d="M8 16H3v5" />
          </svg>
        </button>
      </div>

      <!-- Ollama 에러 메시지 -->
      <div
        v-if="settings.llm.provider === 'ollama' && ollamaError"
        class="ollama-error"
      >
        <svg
          width="14"
          height="14"
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
        <span>{{ ollamaError }}</span>
      </div>

      <!-- 로딩 상태 -->
      <div
        v-if="settingsLoading && currentModels.length === 0"
        class="models-loading"
      >
        <span class="loading-spinner" />
        <span>{{ t('settings.loadingModels') }}</span>
      </div>

      <div
        v-else
        class="model-list"
      >
        <button
          v-for="model in currentModels"
          :key="model.id"
          class="model-card"
          :class="{ active: settings.llm.model === model.id }"
          @click="settings.llm.model = model.id"
        >
          <div class="model-left">
            <div class="model-radio">
              <div
                class="radio-dot"
                :class="{ checked: settings.llm.model === model.id }"
              />
            </div>
            <div class="model-info">
              <div class="model-header">
                <span class="model-name">{{ model.name }}</span>
                <span
                  v-if="model.free"
                  class="free-badge"
                >{{
                  t('settings.badgeFree') }}</span>
                <span
                  v-if="model.free === false"
                  class="paid-badge"
                >{{
                  t('settings.badgePaid') }}</span>
              </div>
              <span class="model-desc">{{ model.description }}</span>
              <span class="model-id">{{ model.id }}</span>
            </div>
          </div>
        </button>
      </div>

      <p
        v-if="currentModels.length === 0 && !ollamaError"
        class="no-models"
      >
        {{ settings.llm.provider === 'ollama' ? t('settings.noModels') : t('settings.loadingModels') }}
      </p>

      <!-- Ollama 모델 설치 안내 -->
      <div
        v-if="settings.llm.provider === 'ollama' && currentModels.length === 0"
        class="ollama-install-hint"
      >
        <p>{{ t('settings.installHint') }}</p>
        <code>ollama pull qwen2.5:7b</code>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useSettings, useI18n, type LLMProvider } from '../../composables';

const { t } = useI18n();

const {
  settings,
  providers,
  ollamaModels,
  geminiModels,
  openaiModels,
  anthropicModels,
  ollamaError,
  isValidatingKey,
  keyValidationResult,
  settingsLoading,
  validateApiKey,
  onProviderChange
} = useSettings();

const isRefreshing = ref(false);

// 현재 선택된 provider 정보
const currentProvider = computed((): LLMProvider | undefined => {
  return providers.value.find(p => p.id === settings.value.llm.provider);
});

// 현재 provider에 맞는 모델 목록
const currentModels = computed(() => {
  switch (settings.value.llm.provider) {
    case 'gemini':
      return geminiModels.value;
    case 'openai':
      return openaiModels.value;
    case 'anthropic':
      return anthropicModels.value;
    default:
      return ollamaModels.value;
  }
});

// API 키 플레이스홀더
function getApiKeyPlaceholder(): string {
  const provider = settings.value.llm.provider;
  switch (provider) {
    case 'gemini':
      return 'AIza...';
    case 'openai':
      return 'sk-...';
    case 'anthropic':
      return 'sk-ant-...';
    default:
      return t('settings.apiKeyPlaceholder');
  }
}

// API 키 변경 시 apiKeys에도 저장
function onApiKeyChange() {
  const provider = settings.value.llm.provider;
  if (provider !== 'ollama') {
    settings.value.llm.apiKeys[provider as keyof typeof settings.value.llm.apiKeys] = settings.value.llm.apiKey;
  }
}

async function handleRefreshOllama() {
  isRefreshing.value = true;
  const { refreshOllamaModels } = useSettings();
  await refreshOllamaModels();
  isRefreshing.value = false;
}

async function handleValidateKey() {
  await validateApiKey(settings.value.llm.apiKey, settings.value.llm.provider);
}

function openApiKeyPage() {
  const url = currentProvider.value?.apiKeyUrl || '';
  if (!url) return;

  if (window.cuenote?.openExternal) {
    window.cuenote.openExternal(url);
  } else {
    window.open(url, '_blank');
  }
}
</script>

<style scoped>
.settings-category {
  margin-bottom: 48px;
  padding-bottom: 32px;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-primary);
}

.category-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--accent);
}

.category-title svg {
  color: var(--accent);
}

.settings-section {
  margin-bottom: 32px;
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

.section-header-with-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.section-header-with-action .section-title {
  margin-bottom: 0;
}

/* Provider Cards */
.provider-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.provider-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
  position: relative;
}

.provider-card:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
}

.provider-card.active {
  background: var(--bg-active);
  border-color: var(--border-strong);
}

.provider-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border-radius: 8px;
  color: var(--text-muted);
}

.provider-card.active .provider-icon {
  color: var(--text-primary);
}

.provider-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.provider-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.provider-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.provider-check {
  position: absolute;
  top: 8px;
  right: 8px;
  color: var(--text-secondary);
}

/* API Key */
.api-key-input-wrapper {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.api-key-input {
  flex: 1;
  padding: 12px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  transition: all 0.15s ease;
}

.api-key-input:focus {
  outline: none;
  border-color: var(--text-muted);
}

.api-key-input.valid {
  border-color: #22c55e;
}

.api-key-input.invalid {
  border-color: #ef4444;
}

.validate-btn {
  padding: 0 18px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.validate-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--border-default);
}

.validate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.validation-result {
  margin-bottom: 12px;
}

.valid-text {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #22c55e;
  font-size: 13px;
}

.invalid-text {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #ef4444;
  font-size: 13px;
}

.api-key-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  transition: color 0.15s ease;
}

.api-key-link:hover {
  color: var(--text-primary);
}

/* Refresh Button */
.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn svg.spinning {
  animation: spin 1s linear infinite;
}

/* Ollama Error */
.ollama-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: #f87171;
  font-size: 13px;
  margin-bottom: 14px;
}

/* Models Loading */
.models-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 30px;
  color: var(--text-muted);
  font-size: 13px;
}

/* Model List */
.model-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.model-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.model-card:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
}

.model-card.active {
  background: var(--bg-active);
  border-color: var(--border-strong);
}

.model-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-radio {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-default);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.radio-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: transparent;
  transition: all 0.15s ease;
}

.radio-dot.checked {
  background: var(--text-primary);
}

.model-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.model-header {
  display: flex;
  align-items: center;
  gap: 6px;
}

.model-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.free-badge,
.paid-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
}

.free-badge {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.paid-badge {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.model-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.model-id {
  font-size: 11px;
  color: var(--text-muted);
  font-family: var(--font-mono);
  opacity: 0.7;
}

.no-models {
  text-align: center;
  padding: 30px;
  color: var(--text-muted);
  font-size: 13px;
}

.ollama-install-hint {
  margin-top: 16px;
  padding: 16px;
  background: rgba(139, 92, 246, 0.08);
  border: 1px dashed rgba(139, 92, 246, 0.3);
  border-radius: 8px;
}

.ollama-install-hint p {
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 8px;
}

.ollama-install-hint code {
  display: block;
  padding: 10px 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  color: #a78bfa;
  font-family: var(--font-mono);
  font-size: 13px;
}

.loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border-subtle);
  border-top-color: var(--text-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
