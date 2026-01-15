<template>
  <div id="section-ocr" class="settings-category">
    <h2 class="category-title">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <path d="M12 18v-6"/>
        <path d="m9 15 3-3 3 3"/>
      </svg>
      문서 변환 (OCR)
    </h2>

    <section class="settings-section">
      <h3 class="section-title">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <path d="M12 18v-6"/>
          <path d="m9 15 3-3 3 3"/>
        </svg>
        OCR 엔진 (문서 변환)
      </h3>

      <!-- OCR 엔진 선택 -->
      <div class="ocr-engine-selector">
        <label class="setting-label">OCR 엔진 선택</label>
        <div class="ocr-engine-options">
          <label 
            v-for="engine in ocrEngines" 
            :key="engine.id"
            class="ocr-engine-option"
            :class="{ 
              selected: settings.ocr?.engine === engine.id,
              disabled: !engine.available && engine.id !== 'gemini'
            }"
          >
            <input 
              type="radio" 
              name="ocr-engine" 
              :value="engine.id"
              :checked="settings.ocr?.engine === engine.id"
              :disabled="!engine.available && engine.id !== 'gemini'"
              @change="selectOcrEngine(engine.id)"
            />
            <div class="engine-info">
              <div class="engine-header">
                <span class="engine-name">{{ engine.name }}</span>
                <span v-if="engine.accuracy" class="engine-accuracy">정확도: {{ engine.accuracy }}</span>
              </div>
              <span class="engine-desc">{{ engine.description }}</span>
              <div class="engine-tags">
                <span v-if="engine.requires_api_key" class="tag api-key">API 키 필요</span>
                <span v-else class="tag free">무료</span>
                <span v-for="lang in engine.languages?.slice(0, 3)" :key="lang" class="tag lang">{{ lang }}</span>
              </div>
            </div>
          </label>
        </div>
      </div>

      <!-- Gemini Vision 모델 선택 (Gemini 선택 시) -->
      <div v-if="settings.ocr?.engine === 'gemini'" class="gemini-vision-settings">
        <label class="setting-label">Vision 모델 선택</label>
        <div class="vision-model-list">
          <label 
            v-for="model in geminiVisionModels" 
            :key="model.id"
            class="vision-model-option"
            :class="{ selected: settings.ocr?.geminiModel === model.id }"
          >
            <input 
              type="radio" 
              name="gemini-vision-model" 
              :value="model.id"
              :checked="settings.ocr?.geminiModel === model.id"
              @change="selectGeminiVisionModel(model.id)"
            />
            <div class="vision-model-info">
              <div class="vision-model-header">
                <span class="vision-model-name">{{ model.name }}</span>
                <span v-if="model.recommended" class="badge recommended">추천</span>
                <span v-if="model.free" class="badge free">무료</span>
                <span v-else class="badge paid">유료</span>
              </div>
              <span class="vision-model-desc">{{ model.description }}</span>
            </div>
          </label>
        </div>
        
        <div class="gemini-ocr-notice">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4"/>
            <path d="M12 8h.01"/>
          </svg>
          <span>Gemini Vision OCR은 위에서 설정한 Gemini API 키를 사용합니다. 무료 모델은 분당/일당 요청 제한이 있습니다.</span>
        </div>
      </div>

      <p class="ocr-hint">
        에디터 툴바의 "문서 변환" 버튼으로 PDF나 이미지에서 텍스트를 추출할 수 있습니다.
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useSettings } from '../../composables';
import { GEMINI_VISION_MODELS } from '../../composables/useSettings';

const { settings } = useSettings();

// OCR 상태
interface OCREngine {
  id: string;
  name: string;
  description: string;
  available: boolean;
  requires_api_key: boolean;
  accuracy: string;
  speed: string;
  languages: string[];
}

// 기본 OCR 엔진 목록 (API 실패 시 fallback)
const DEFAULT_OCR_ENGINES: OCREngine[] = [
  {
    id: 'rapidocr',
    name: 'RapidOCR',
    description: '로컬 OCR, 무료, 인터넷 불필요',
    available: true,
    requires_api_key: false,
    accuracy: '보통',
    speed: '빠름',
    languages: ['한국어', '영어', '일본어', '중국어'],
  },
  {
    id: 'gemini',
    name: 'Gemini Vision',
    description: 'Google AI 기반, 최고 정확도 (API 키 필요)',
    available: true,
    requires_api_key: true,
    accuracy: '최상',
    speed: '보통',
    languages: ['한국어', '영어', '일본어', '중국어', '다국어'],
  },
];

const ocrEngines = ref<OCREngine[]>(DEFAULT_OCR_ENGINES);
const CORE_BASE = 'http://127.0.0.1:8787';

// Gemini Vision 모델 목록
const geminiVisionModels = GEMINI_VISION_MODELS;

// OCR 엔진 목록 가져오기
async function fetchOcrEngines() {
  try {
    const res = await fetch(`${CORE_BASE}/ai/ocr/engines`);
    if (res.ok) {
      const engines = await res.json();
      if (engines && engines.length > 0) {
        ocrEngines.value = engines;
      }
    }
  } catch (error) {
    console.error('Failed to fetch OCR engines, using defaults:', error);
  }
}

// OCR 상태 확인
async function checkOcrStatus() {
  try {
    const engine = settings.value.ocr?.engine || 'rapidocr';
    await fetch(`${CORE_BASE}/ai/ocr/status?engine=${engine}`);
  } catch (error) {
    console.error('Failed to check OCR status:', error);
  }
}

// OCR 엔진 선택
function selectOcrEngine(engineId: string) {
  if (!settings.value.ocr) {
    settings.value.ocr = { engine: 'rapidocr', geminiModel: 'gemini-2.0-flash' };
  }
  settings.value.ocr.engine = engineId;
  checkOcrStatus();
}

// Gemini Vision 모델 선택
function selectGeminiVisionModel(modelId: string) {
  if (!settings.value.ocr) {
    settings.value.ocr = { engine: 'gemini', geminiModel: modelId };
  } else {
    settings.value.ocr.geminiModel = modelId;
  }
}

onMounted(async () => {
  await fetchOcrEngines();
  await checkOcrStatus();
});
</script>

<style scoped>
.settings-category {
  margin-bottom: 48px;
  padding-bottom: 32px;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-primary);
}

.settings-category:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
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

/* OCR Engine Selector */
.ocr-engine-selector {
  margin-bottom: 20px;
}

.setting-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.ocr-engine-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ocr-engine-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.ocr-engine-option:hover:not(.disabled) {
  background: var(--bg-hover);
  border-color: var(--border-default);
}

.ocr-engine-option.selected {
  background: var(--bg-active);
  border-color: var(--border-strong);
}

.ocr-engine-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ocr-engine-option input[type="radio"] {
  margin-top: 4px;
  accent-color: var(--accent);
}

.engine-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.engine-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.engine-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.engine-accuracy {
  font-size: 11px;
  color: var(--text-muted);
}

.engine-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.engine-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
}

.tag.api-key {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.tag.free {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.tag.lang {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

/* Gemini Vision Settings */
.gemini-vision-settings {
  margin-top: 20px;
  padding: 16px;
  background: rgba(139, 92, 246, 0.05);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 10px;
}

.vision-model-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.vision-model-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.vision-model-option:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
}

.vision-model-option.selected {
  background: var(--bg-active);
  border-color: rgba(139, 92, 246, 0.4);
}

.vision-model-option input[type="radio"] {
  margin-top: 3px;
  accent-color: #a78bfa;
}

.vision-model-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.vision-model-header {
  display: flex;
  align-items: center;
  gap: 6px;
}

.vision-model-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.recommended {
  background: rgba(139, 92, 246, 0.2);
  color: #a78bfa;
}

.badge.free {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.badge.paid {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.vision-model-desc {
  font-size: 11px;
  color: var(--text-muted);
}

.gemini-ocr-notice {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 8px;
}

.gemini-ocr-notice svg {
  flex-shrink: 0;
  color: #a78bfa;
  margin-top: 2px;
}

.gemini-ocr-notice span {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.ocr-hint {
  margin-top: 16px;
  padding: 12px 14px;
  background: var(--bg-secondary);
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-muted);
}
</style>
