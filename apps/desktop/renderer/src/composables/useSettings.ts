import { ref, watch } from 'vue';
import { API_BASE_URL } from '../config/api';

const STORAGE_KEY = 'cuenote-settings';

// LLM 제공자 타입
export interface LLMProvider {
  id: string;
  name: string;
  description: string;
  requiresApiKey: boolean;
  apiKeyUrl?: string;
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
    apiKey: string;  // 현재 선택된 provider의 API 키 (호환성 유지)
    model: string;
    apiKeys: {
      gemini?: string;
      openai?: string;
      anthropic?: string;
    };
  };
  ocr?: {
    engine: string;  // 'gemini' | 'rapidocr'
    geminiModel?: string;  // Gemini Vision 모델
  };
}

// Gemini Vision 모델 목록 (2025 최신)
export const GEMINI_VISION_MODELS = [
  {
    id: 'gemini-3-flash-preview',
    name: 'Gemini 3 Flash Preview',
    description: '최신 빠른 모델, 뛰어난 시각 인식',
    free: true,
    recommended: true,
  },
  {
    id: 'gemini-3-pro-preview',
    name: 'Gemini 3 Pro Preview',
    description: '최고 성능 멀티모달 모델',
    free: false,
  },
  {
    id: 'gemini-2.5-flash',
    name: 'Gemini 2.5 Flash',
    description: '안정적인 고속 모델, Vision 지원 (추천)',
    free: true,
  },
  {
    id: 'gemini-2.5-flash-lite',
    name: 'Gemini 2.5 Flash-Lite',
    description: '가장 빠르고 저렴한 모델',
    free: true,
  },
  {
    id: 'gemini-2.5-pro',
    name: 'Gemini 2.5 Pro',
    description: '복잡한 이미지 분석에 최적화',
    free: false,
  },
  {
    id: 'gemini-2.0-flash',
    name: 'Gemini 2.0 Flash',
    description: '고속 모델 (2026년 3월 종료 예정)',
    free: true,
  },
];

// 기본 설정 (모델은 동적으로 설정)
const defaultSettings: AppSettings = {
  llm: {
    provider: 'ollama',
    apiKey: '',
    model: '',  // 첫 번째 사용 가능한 모델로 자동 설정
    apiKeys: {
      gemini: '',
      openai: '',
      anthropic: ''
    }
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
const openaiModels = ref<LLMModel[]>([]);
const anthropicModels = ref<LLMModel[]>([]);
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
      // apiKeys가 없는 경우 기본값 병합
      const llm = {
        ...defaultSettings.llm,
        ...parsed.llm,
        apiKeys: {
          ...defaultSettings.llm.apiKeys,
          ...(parsed.llm?.apiKeys || {})
        }
      };
      return { ...defaultSettings, ...parsed, llm };
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
      const res = await fetch(`${API_BASE_URL}/llm/providers`);
      const data = await res.json();
      providers.value = data.providers || [];
    } catch (e) {
      console.error('Failed to fetch providers:', e);
      // 기본 제공자 설정
      providers.value = [
        { id: 'ollama', name: 'Ollama (로컬)', description: '로컬에서 실행되는 오픈소스 LLM', requiresApiKey: false },
        { id: 'gemini', name: 'Google Gemini', description: 'Google의 최신 AI 모델', requiresApiKey: true, apiKeyUrl: 'https://aistudio.google.com/app/apikey' },
        { id: 'openai', name: 'OpenAI', description: 'GPT-4, GPT-3.5 등 OpenAI 모델', requiresApiKey: true, apiKeyUrl: 'https://platform.openai.com/api-keys' },
        { id: 'anthropic', name: 'Anthropic Claude', description: 'Claude 3.5, Claude 3 등 Anthropic 모델', requiresApiKey: true, apiKeyUrl: 'https://console.anthropic.com/settings/keys' }
      ];
    }
  }

  // Ollama 모델 목록 가져오기
  async function fetchOllamaModels() {
    ollamaError.value = null;
    try {
      const res = await fetch(`${API_BASE_URL}/llm/ollama/models`);
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
      const res = await fetch(`${API_BASE_URL}/llm/gemini/models`);
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

  // OpenAI 모델 목록 가져오기
  async function fetchOpenAIModels() {
    try {
      const res = await fetch(`${API_BASE_URL}/llm/openai/models`);
      const data = await res.json();
      openaiModels.value = data.models || [];

      if (settings.value.llm.provider === 'openai') {
        const currentModel = settings.value.llm.model;
        const modelExists = openaiModels.value.some(m => m.id === currentModel);

        if (!currentModel || !modelExists) {
          if (openaiModels.value.length > 0) {
            settings.value.llm.model = openaiModels.value[0].id;
          }
        }
      }
    } catch (e) {
      console.error('Failed to fetch OpenAI models:', e);
    }
  }

  // Anthropic 모델 목록 가져오기
  async function fetchAnthropicModels() {
    try {
      const res = await fetch(`${API_BASE_URL}/llm/anthropic/models`);
      const data = await res.json();
      anthropicModels.value = data.models || [];

      if (settings.value.llm.provider === 'anthropic') {
        const currentModel = settings.value.llm.model;
        const modelExists = anthropicModels.value.some(m => m.id === currentModel);

        if (!currentModel || !modelExists) {
          if (anthropicModels.value.length > 0) {
            settings.value.llm.model = anthropicModels.value[0].id;
          }
        }
      }
    } catch (e) {
      console.error('Failed to fetch Anthropic models:', e);
    }
  }

  // API 키 검증 (provider에 따라 적절한 엔드포인트 호출)
  async function validateApiKey(apiKey: string, provider?: string): Promise<boolean> {
    if (!apiKey) {
      keyValidationResult.value = null;
      return false;
    }

    const targetProvider = provider || settings.value.llm.provider;

    // Ollama는 API 키 불필요
    if (targetProvider === 'ollama') {
      keyValidationResult.value = true;
      return true;
    }

    isValidatingKey.value = true;
    keyValidationResult.value = null;

    try {
      const res = await fetch(`${API_BASE_URL}/llm/${targetProvider}/validate-key`, {
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
        fetchGeminiModels(),
        fetchOpenAIModels(),
        fetchAnthropicModels()
      ]);
    } finally {
      settingsLoading.value = false;
    }
  }

  // 현재 선택된 제공자에 따른 모델 목록
  function getCurrentModels(): LLMModel[] {
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
  }

  // 설정 업데이트
  function updateSettings(newSettings: Partial<AppSettings>) {
    settings.value = { ...settings.value, ...newSettings };
  }

  // LLM 설정 업데이트
  function updateLLMSettings(llmSettings: Partial<AppSettings['llm']>) {
    settings.value.llm = { ...settings.value.llm, ...llmSettings };
  }

  // 제공자 변경 시 기본 모델 및 API 키 설정
  function onProviderChange(providerId: string) {
    // 기존 API 키 저장
    const oldProvider = settings.value.llm.provider;
    if (oldProvider !== 'ollama' && settings.value.llm.apiKey) {
      settings.value.llm.apiKeys[oldProvider as keyof typeof settings.value.llm.apiKeys] = settings.value.llm.apiKey;
    }

    settings.value.llm.provider = providerId;

    // 새 provider의 저장된 API 키 불러오기
    if (providerId !== 'ollama') {
      settings.value.llm.apiKey = settings.value.llm.apiKeys[providerId as keyof typeof settings.value.llm.apiKeys] || '';
    } else {
      settings.value.llm.apiKey = '';
    }

    // API 키 검증 결과 초기화
    keyValidationResult.value = null;

    // 제공자에 맞는 기본 모델 설정
    let models: LLMModel[] = [];
    switch (providerId) {
      case 'gemini':
        models = geminiModels.value;
        break;
      case 'openai':
        models = openaiModels.value;
        break;
      case 'anthropic':
        models = anthropicModels.value;
        break;
      default:
        models = ollamaModels.value;
    }

    if (models.length > 0) {
      // 무료 모델이 있으면 우선 선택, 없으면 첫 번째 모델
      const defaultModel = models.find(m => m.free) || models[0];
      settings.value.llm.model = defaultModel.id;
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
    openaiModels,
    anthropicModels,
    ollamaError,
    isValidatingKey,
    keyValidationResult,
    settingsLoading,
    fetchProviders,
    fetchOllamaModels,
    fetchGeminiModels,
    fetchOpenAIModels,
    fetchAnthropicModels,
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
