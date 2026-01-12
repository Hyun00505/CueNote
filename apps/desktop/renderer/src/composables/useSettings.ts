import { ref, watch } from 'vue';

const CORE_BASE = 'http://127.0.0.1:8787';
const STORAGE_KEY = 'cuenote-settings';

// LLM 제공자 타입
export interface LLMProvider {
  id: string;
  name: string;
  description: string;
  requiresApiKey: boolean;
}

// LLM 모델 타입
export interface LLMModel {
  id: string;
  name: string;
  description: string;
  free: boolean;
  context_window: number;
}

// 설정 타입
export interface AppSettings {
  llm: {
    provider: string;
    apiKey: string;
    model: string;
  };
  ocr?: {
    engine: string;  // 'gemini' | 'rapidocr'
    geminiModel?: string;  // Gemini Vision 모델
  };
}

// Gemini Vision 모델 목록
export const GEMINI_VISION_MODELS = [
  {
    id: 'gemini-2.0-flash',
    name: 'Gemini 2.0 Flash',
    description: '차세대 고속 모델, Vision 지원 (15 RPM)',
    free: true,
    recommended: true,
  },
  {
    id: 'gemini-2.0-flash-lite',
    name: 'Gemini 2.0 Flash Lite',
    description: '초경량 모델, 빠른 처리 (30 RPM)',
    free: true,
  },
  {
    id: 'gemini-1.5-flash',
    name: 'Gemini 1.5 Flash',
    description: '안정적인 고속 모델, Vision 지원 (15 RPM)',
    free: true,
  },
  {
    id: 'gemini-1.5-flash-8b',
    name: 'Gemini 1.5 Flash 8B',
    description: '경량 모델, 가장 빠른 처리 (15 RPM)',
    free: true,
  },
  {
    id: 'gemini-1.5-pro',
    name: 'Gemini 1.5 Pro',
    description: '고성능 모델, 복잡한 이미지 분석 (2 RPM)',
    free: true,  // 무료 제한 있음
  },
  {
    id: 'gemini-2.5-flash',
    name: 'Gemini 2.5 Flash',
    description: '최신 고속 모델, 균형 잡힌 성능 (15 RPM)',
    free: true,
  },
  {
    id: 'gemini-2.5-pro',
    name: 'Gemini 2.5 Pro',
    description: '최고 성능 모델, 복잡한 작업에 적합',
    free: false,
  },
];

// 기본 설정 (모델은 동적으로 설정)
const defaultSettings: AppSettings = {
  llm: {
    provider: 'ollama',
    apiKey: '',
    model: ''  // 첫 번째 사용 가능한 모델로 자동 설정
  },
  ocr: {
    engine: 'rapidocr',  // 기본값: 로컬 OCR
    geminiModel: 'gemini-2.0-flash'  // Gemini 사용 시 기본 모델
  }
};

// 전역 상태
const settings = ref<AppSettings>(loadSettings());
const providers = ref<LLMProvider[]>([]);
const ollamaModels = ref<LLMModel[]>([]);
const geminiModels = ref<LLMModel[]>([]);
const ollamaError = ref<string | null>(null);
const isValidatingKey = ref(false);
const keyValidationResult = ref<boolean | null>(null);
const settingsLoading = ref(false);

// 로컬 스토리지에서 설정 로드
function loadSettings(): AppSettings {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      return { ...defaultSettings, ...parsed };
    }
  } catch (e) {
    console.error('Failed to load settings:', e);
  }
  return { ...defaultSettings };
}

// 설정 저장
function saveSettings() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings.value));
  } catch (e) {
    console.error('Failed to save settings:', e);
  }
}

// 설정 변경 감지하여 자동 저장
watch(settings, saveSettings, { deep: true });

export function useSettings() {
  // LLM 제공자 목록 가져오기
  async function fetchProviders() {
    try {
      const res = await fetch(`${CORE_BASE}/llm/providers`);
      const data = await res.json();
      providers.value = data.providers || [];
    } catch (e) {
      console.error('Failed to fetch providers:', e);
      // 기본 제공자 설정
      providers.value = [
        { id: 'ollama', name: 'Ollama (로컬)', description: '로컬에서 실행되는 오픈소스 LLM', requiresApiKey: false },
        { id: 'gemini', name: 'Google Gemini', description: 'Google의 최신 AI 모델', requiresApiKey: true }
      ];
    }
  }

  // Ollama 모델 목록 가져오기
  async function fetchOllamaModels() {
    ollamaError.value = null;
    try {
      const res = await fetch(`${CORE_BASE}/llm/ollama/models`);
      const data = await res.json();
      ollamaModels.value = data.models || [];
      
      // 에러 메시지가 있으면 저장
      if (data.error) {
        ollamaError.value = data.error;
      }
      
      // 현재 설정된 모델이 목록에 없거나 비어있으면 첫 번째 모델로 설정
      if (settings.value.llm.provider === 'ollama') {
        const currentModel = settings.value.llm.model;
        const modelExists = ollamaModels.value.some(m => m.id === currentModel);
        
        if (!currentModel || !modelExists) {
          if (ollamaModels.value.length > 0) {
            settings.value.llm.model = ollamaModels.value[0].id;
          }
        }
      }
    } catch (e) {
      console.error('Failed to fetch Ollama models:', e);
      ollamaError.value = 'Ollama 서버에 연결할 수 없습니다';
      ollamaModels.value = [];
    }
  }

  // Gemini 모델 목록 가져오기
  async function fetchGeminiModels() {
    try {
      const res = await fetch(`${CORE_BASE}/llm/gemini/models`);
      const data = await res.json();
      geminiModels.value = data.models || [];
      
      // 현재 Gemini가 선택되어 있고, 모델이 없거나 유효하지 않으면 첫 번째 모델로 설정
      if (settings.value.llm.provider === 'gemini') {
        const currentModel = settings.value.llm.model;
        const modelExists = geminiModels.value.some(m => m.id === currentModel);
        
        if (!currentModel || !modelExists) {
          if (geminiModels.value.length > 0) {
            settings.value.llm.model = geminiModels.value[0].id;
          }
        }
      }
    } catch (e) {
      console.error('Failed to fetch Gemini models:', e);
    }
  }

  // API 키 검증
  async function validateApiKey(apiKey: string): Promise<boolean> {
    if (!apiKey) {
      keyValidationResult.value = null;
      return false;
    }

    isValidatingKey.value = true;
    keyValidationResult.value = null;

    try {
      const res = await fetch(`${CORE_BASE}/llm/gemini/validate-key`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey })
      });
      const data = await res.json();
      keyValidationResult.value = data.valid;
      return data.valid;
    } catch (e) {
      console.error('Failed to validate API key:', e);
      keyValidationResult.value = false;
      return false;
    } finally {
      isValidatingKey.value = false;
    }
  }

  // 설정 초기화
  async function initSettings() {
    settingsLoading.value = true;
    try {
      await Promise.all([
        fetchProviders(),
        fetchOllamaModels(),
        fetchGeminiModels()
      ]);
    } finally {
      settingsLoading.value = false;
    }
  }

  // 현재 선택된 제공자에 따른 모델 목록
  function getCurrentModels(): LLMModel[] {
    if (settings.value.llm.provider === 'gemini') {
      return geminiModels.value;
    }
    return ollamaModels.value;
  }

  // 설정 업데이트
  function updateSettings(newSettings: Partial<AppSettings>) {
    settings.value = { ...settings.value, ...newSettings };
  }

  // LLM 설정 업데이트
  function updateLLMSettings(llmSettings: Partial<AppSettings['llm']>) {
    settings.value.llm = { ...settings.value.llm, ...llmSettings };
  }

  // 제공자 변경 시 기본 모델 설정
  function onProviderChange(providerId: string) {
    settings.value.llm.provider = providerId;
    
    // 제공자에 맞는 기본 모델 설정
    if (providerId === 'gemini') {
      const defaultModel = geminiModels.value.find(m => m.free) || geminiModels.value[0];
      if (defaultModel) {
        settings.value.llm.model = defaultModel.id;
      }
    } else {
      const defaultModel = ollamaModels.value[0];
      if (defaultModel) {
        settings.value.llm.model = defaultModel.id;
      }
    }
  }

  // 설정 리셋
  function resetSettings() {
    settings.value = { ...defaultSettings };
  }

  // Ollama 모델 목록 새로고침
  async function refreshOllamaModels() {
    await fetchOllamaModels();
  }

  return {
    settings,
    providers,
    ollamaModels,
    geminiModels,
    ollamaError,
    isValidatingKey,
    keyValidationResult,
    settingsLoading,
    fetchProviders,
    fetchOllamaModels,
    fetchGeminiModels,
    validateApiKey,
    initSettings,
    getCurrentModels,
    updateSettings,
    updateLLMSettings,
    onProviderChange,
    resetSettings,
    refreshOllamaModels
  };
}
