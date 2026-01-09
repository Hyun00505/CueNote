<template>
  <div class="settings-view">
    <!-- Header -->
    <div class="settings-header">
      <button class="back-btn" @click="$emit('back')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        <span>{{ t('common.back') }}</span>
      </button>
      <div class="header-title">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
        <span>{{ t('settings.title') }}</span>
      </div>
    </div>

    <!-- Content -->
    <div class="settings-content">
      <div class="settings-inner">
        <!-- Language Section -->
        <section class="settings-section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M2 12h20"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
            {{ t('settings.language') }}
          </h3>
          <p class="section-desc">{{ t('settings.languageDesc') }}</p>
          
          <div class="language-options">
            <button
              v-for="lang in ['ko', 'en'] as const"
              :key="lang"
              class="language-btn"
              :class="{ active: currentLanguage === lang }"
              @click="setLanguage(lang)"
            >
              <span class="lang-flag">{{ lang === 'ko' ? '🇰🇷' : '🇺🇸' }}</span>
              <span class="lang-name">{{ languageNames[lang] }}</span>
              <svg v-if="currentLanguage === lang" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="lang-check">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </button>
          </div>
        </section>

        <!-- Theme Section -->
        <section class="settings-section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="5"/>
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
            </svg>
            {{ t('settings.theme') }}
          </h3>
          
          <div class="theme-grid">
            <button
              v-for="theme in themes"
              :key="theme.id"
              class="theme-item"
              :class="{ active: currentTheme === theme.id }"
              @click="setTheme(theme.id)"
            >
              <div class="theme-swatch" :style="{ background: theme.colors.bg }">
                <div class="swatch-sidebar" :style="{ background: theme.colors.sidebar }"></div>
                <div class="swatch-accent" :style="{ background: theme.colors.accent }"></div>
              </div>
              <span class="theme-label">{{ theme.name }}</span>
              <div class="theme-check" v-if="currentTheme === theme.id">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
            </button>
          </div>
        </section>

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

          <button type="button" class="api-key-link" @click="openApiKeyPage">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            {{ t('settings.getApiKey') }}
          </button>
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

        <!-- OCR Model Section -->
        <section class="settings-section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <path d="M12 18v-6"/>
              <path d="m9 15 3-3 3 3"/>
            </svg>
            OCR 모델 (문서 변환)
          </h3>

          <div class="ocr-status-card">
            <div class="ocr-status-header">
              <div class="ocr-status-icon" :class="{ ready: ocrStatus?.model_downloaded }">
                <svg v-if="ocrStatus?.model_downloaded" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 16v-4"/>
                  <path d="M12 8h.01"/>
                </svg>
              </div>
              <div class="ocr-status-info">
                <span class="ocr-status-title">EasyOCR 모델</span>
                <span class="ocr-status-desc">
                  {{ ocrStatus?.model_downloaded ? '다운로드 완료 - 사용 가능' : '다운로드 필요 (~100MB)' }}
                </span>
              </div>
            </div>

            <div class="ocr-languages">
              <span class="lang-label">지원 언어:</span>
              <span class="lang-tag">한국어</span>
              <span class="lang-tag">영어</span>
            </div>

            <button 
              v-if="!ocrStatus?.model_downloaded"
              class="btn-download-ocr"
              :disabled="ocrDownloading"
              @click="downloadOcrModel"
            >
              <span v-if="ocrDownloading" class="loading-spinner"></span>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              {{ ocrDownloading ? '다운로드 중... (잠시 기다려주세요)' : '모델 다운로드' }}
            </button>

            <div v-if="ocrStatus?.model_downloaded" class="ocr-ready-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              PDF/이미지 문서 변환 기능 사용 가능
            </div>

            <div v-if="ocrDownloadError" class="ocr-error">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {{ ocrDownloadError }}
            </div>
          </div>

          <p class="ocr-hint">
            PDF나 이미지에서 텍스트를 추출하는 OCR 모델입니다. 에디터 툴바의 "문서 변환" 버튼으로 사용할 수 있습니다.
          </p>
        </section>

        <!-- Handwriting OCR Section -->
        <section class="settings-section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>
              <path d="m15 5 4 4"/>
            </svg>
            손글씨 OCR 모델
          </h3>

          <div class="ocr-status-card handwriting-card">
            <div class="ocr-status-header">
              <div class="ocr-status-icon" :class="{ ready: handwritingStatus?.model_downloaded }">
                <svg v-if="handwritingStatus?.model_downloaded" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 16v-4"/>
                  <path d="M12 8h.01"/>
                </svg>
              </div>
              <div class="ocr-status-info">
                <span class="ocr-status-title">TrOCR (Microsoft)</span>
                <span class="ocr-status-desc">
                  {{ handwritingStatus?.model_downloaded ? '다운로드 완료 - 사용 가능' : '다운로드 필요 (~1GB)' }}
                </span>
              </div>
            </div>

            <div class="ocr-languages">
              <span class="lang-label">특징:</span>
              <span class="lang-tag handwriting-tag">손글씨 인식</span>
              <span class="lang-tag">영어 최적화</span>
            </div>

            <button 
              v-if="!handwritingStatus?.model_downloaded"
              class="btn-download-ocr btn-download-handwriting"
              :disabled="handwritingDownloading"
              @click="downloadHandwritingModel"
            >
              <span v-if="handwritingDownloading" class="loading-spinner"></span>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              {{ handwritingDownloading ? '다운로드 중... (약 1GB, 시간이 걸립니다)' : '모델 다운로드' }}
            </button>

            <div v-if="handwritingStatus?.model_downloaded" class="ocr-ready-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              손글씨 인식 기능 사용 가능
            </div>

            <div v-if="handwritingDownloadError" class="ocr-error">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {{ handwritingDownloadError }}
            </div>
          </div>

          <p class="ocr-hint">
            손글씨 텍스트를 인식하는 AI 모델입니다. 문서 변환 시 "손글씨 인식 모드"를 선택하면 사용됩니다. 깔끔한 필체일수록 인식률이 높습니다.
          </p>
        </section>
      </div>
    </div>

    <!-- Footer -->
    <div class="settings-footer">
      <button class="reset-btn" @click="handleReset">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
          <path d="M21 3v5h-5"/>
          <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
          <path d="M8 16H3v5"/>
        </svg>
        {{ t('common.reset') }}
      </button>
      <button class="save-btn" @click="$emit('back')">
        {{ t('common.done') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useSettings, useI18n } from '../composables';

defineEmits<{
  back: [];
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

const { t, currentLanguage, setLanguage, languageNames } = useI18n();

const isRefreshing = ref(false);

// 테마 설정
type ThemeId = 'dark' | 'light' | 'dim' | 'github-dark' | 'sepia';

const themes = computed(() => [
  { id: 'dark' as ThemeId, name: t('theme.dark'), colors: { bg: '#0f0f12', sidebar: '#16161a', accent: '#6b7280' } },
  { id: 'light' as ThemeId, name: t('theme.light'), colors: { bg: '#ffffff', sidebar: '#f5f5f5', accent: '#374151' } },
  { id: 'dim' as ThemeId, name: t('theme.dim'), colors: { bg: '#1c1c1c', sidebar: '#252525', accent: '#8b949e' } },
  { id: 'github-dark' as ThemeId, name: t('theme.github'), colors: { bg: '#0d1117', sidebar: '#161b22', accent: '#58a6ff' } },
  { id: 'sepia' as ThemeId, name: t('theme.sepia'), colors: { bg: '#f4ecd8', sidebar: '#e8e0cc', accent: '#5c4b37' } },
]);

const currentTheme = ref<ThemeId>('dark');

function setTheme(theme: ThemeId) {
  currentTheme.value = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('cuenote-theme', theme);
}

function initTheme() {
  const savedTheme = localStorage.getItem('cuenote-theme') as ThemeId | null;
  if (savedTheme) {
    currentTheme.value = savedTheme;
    document.documentElement.setAttribute('data-theme', savedTheme);
  }
}

// OCR 상태
interface OCRStatus {
  installed: boolean;
  model_downloaded: boolean;
  model_path: string;
  languages: string[];
  downloading: boolean;
}
const ocrStatus = ref<OCRStatus | null>(null);
const ocrDownloading = ref(false);
const ocrDownloadError = ref('');

// 손글씨 OCR 상태
interface HandwritingStatus {
  installed: boolean;
  model_downloaded: boolean;
  model_name: string;
  model_path: string;
  downloading: boolean;
}
const handwritingStatus = ref<HandwritingStatus | null>(null);
const handwritingDownloading = ref(false);
const handwritingDownloadError = ref('');

const CORE_BASE = 'http://127.0.0.1:8787';

// OCR 상태 확인
async function checkOcrStatus() {
  try {
    const res = await fetch(`${CORE_BASE}/ai/ocr/status`);
    if (res.ok) {
      ocrStatus.value = await res.json();
    }
  } catch (error) {
    console.error('Failed to check OCR status:', error);
  }
}

// OCR 모델 다운로드
async function downloadOcrModel() {
  ocrDownloading.value = true;
  ocrDownloadError.value = '';
  
  try {
    const res = await fetch(`${CORE_BASE}/ai/ocr/download`, {
      method: 'POST'
    });
    
    const data = await res.json();
    
    if (data.success) {
      await checkOcrStatus();
    } else {
      ocrDownloadError.value = data.message || '모델 다운로드에 실패했습니다.';
    }
  } catch (error) {
    console.error('OCR model download failed:', error);
    ocrDownloadError.value = '모델 다운로드에 실패했습니다. 네트워크를 확인해주세요.';
  } finally {
    ocrDownloading.value = false;
  }
}

// 손글씨 OCR 상태 확인
async function checkHandwritingStatus() {
  try {
    const res = await fetch(`${CORE_BASE}/ai/ocr/handwriting/status`);
    if (res.ok) {
      handwritingStatus.value = await res.json();
    }
  } catch (error) {
    console.error('Failed to check handwriting status:', error);
  }
}

// 손글씨 OCR 모델 다운로드
async function downloadHandwritingModel() {
  handwritingDownloading.value = true;
  handwritingDownloadError.value = '';
  
  try {
    const res = await fetch(`${CORE_BASE}/ai/ocr/handwriting/download`, {
      method: 'POST'
    });
    
    const data = await res.json();
    
    if (data.success) {
      await checkHandwritingStatus();
    } else {
      handwritingDownloadError.value = data.message || '손글씨 모델 다운로드에 실패했습니다.';
    }
  } catch (error) {
    console.error('Handwriting model download failed:', error);
    handwritingDownloadError.value = '손글씨 모델 다운로드에 실패했습니다. 네트워크를 확인해주세요.';
  } finally {
    handwritingDownloading.value = false;
  }
}

// 페이지 마운트 시 데이터 로드
onMounted(async () => {
  initTheme();
  await initSettings();
  await checkOcrStatus();
  await checkHandwritingStatus();
});

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

// 외부 브라우저로 API 키 페이지 열기
function openApiKeyPage() {
  const url = 'https://aistudio.google.com/app/apikey';
  if (window.cuenote?.openExternal) {
    window.cuenote.openExternal(url);
  } else {
    // 폴백: 일반 브라우저 환경
    window.open(url, '_blank');
  }
}
</script>

<style scoped>
.settings-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary);
}

/* Header */
.settings-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
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
  color: var(--text-secondary);
}

/* Content */
.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.settings-inner {
  max-width: 640px;
  margin: 0 auto;
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
  background: var(--bg-active);
  border-color: var(--border-strong);
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
  background: var(--bg-hover);
  color: var(--text-primary);
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
  background: var(--text-secondary);
  border-radius: 50%;
  color: var(--bg-primary);
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
  border-color: var(--border-strong);
  background: var(--bg-hover);
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
  background: var(--bg-hover);
  border: 1px solid var(--border-default);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  min-width: 70px;
}

.validate-btn:hover:not(:disabled) {
  background: var(--bg-active);
  border-color: var(--border-strong);
}

.validate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid var(--border-default);
  border-top-color: var(--text-primary);
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
  color: var(--text-primary);
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
  background: var(--bg-active);
  border-color: var(--border-strong);
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
  border-color: var(--text-secondary);
}

.radio-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: transparent;
  transition: all 0.15s ease;
}

.radio-dot.checked {
  background: var(--text-secondary);
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
  color: var(--text-primary);
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
  color: var(--text-primary);
}

/* Footer */
.settings-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: var(--bg-secondary);
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
  background: var(--text-secondary);
  border: none;
  border-radius: 8px;
  color: var(--bg-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.save-btn:hover {
  background: var(--text-primary);
}

/* OCR Status Card */
.ocr-status-card {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
}

.ocr-status-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.ocr-status-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(234, 179, 8, 0.1);
  border-radius: 10px;
  color: #fbbf24;
}

.ocr-status-icon.ready {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.ocr-status-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ocr-status-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.ocr-status-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.ocr-languages {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  padding-left: 52px;
}

.lang-label {
  font-size: 12px;
  color: var(--text-muted);
}

.lang-tag {
  padding: 3px 8px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  color: #a78bfa;
}

.btn-download-ocr {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-download-ocr:hover:not(:disabled) {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.btn-download-ocr:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.ocr-ready-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #22c55e;
}

.ocr-error {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  font-size: 12px;
  color: #f87171;
}

.ocr-hint {
  margin-top: 12px;
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

/* 손글씨 OCR 섹션 스타일 */
.handwriting-card {
  border-color: rgba(139, 92, 246, 0.2);
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05), rgba(124, 58, 237, 0.08));
}

.handwriting-card .ocr-status-icon.ready {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
}

.handwriting-tag {
  background: rgba(139, 92, 246, 0.15) !important;
  color: #a78bfa !important;
}

.btn-download-handwriting {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
}

.btn-download-handwriting:hover:not(:disabled) {
  background: linear-gradient(135deg, #a78bfa, #8b5cf6) !important;
}

/* Section Description */
.section-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 14px;
}

/* Language Options */
.language-options {
  display: flex;
  gap: 10px;
}

.language-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.language-btn:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: var(--border-default);
}

.language-btn.active {
  background: var(--bg-active);
  border-color: var(--border-strong);
}

.lang-flag {
  font-size: 20px;
}

.lang-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.lang-check {
  color: var(--text-secondary);
}

/* Theme Grid */
.theme-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.theme-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 10px 8px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;
}

.theme-item:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
}

.theme-item.active {
  border-color: var(--text-secondary);
  background: var(--bg-active);
}

.theme-swatch {
  width: 40px;
  height: 28px;
  border-radius: 6px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.swatch-sidebar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 12px;
}

.swatch-accent {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.theme-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-secondary);
}

.theme-item.active .theme-label {
  color: var(--text-primary);
}

.theme-item .theme-check {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  background: var(--text-secondary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--bg-primary);
}
</style>
