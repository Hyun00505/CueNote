import { ref, watch, computed } from 'vue';

const STORAGE_KEY = 'cuenote-fonts';
const CUSTOM_FONTS_KEY = 'cuenote-custom-fonts';

// 기본 폰트 옵션
export interface FontOption {
  id: string;
  name: string;
  value: string;
  type: 'system' | 'google' | 'custom';
  category: 'sans' | 'serif' | 'mono';
}

// 커스텀 폰트
export interface CustomFont {
  id: string;
  name: string;
  filePath: string;  // 로컬 파일 경로
  fileName: string;  // 저장된 파일명
  categories: ('sans' | 'serif' | 'mono')[];  // 여러 카테고리 지원
}

// 폰트 설정
export interface FontSettings {
  sansFont: string;
  serifFont: string;
  monoFont: string;
  uiScale: number;  // 퍼센트 (50, 75, 100, 125, 150, 175, 200)
}

// UI 스케일 옵션
export const UI_SCALE_OPTIONS = [50, 75, 100, 125, 150, 175, 200];

// 기본 설정
const defaultSettings: FontSettings = {
  sansFont: 'pretendard',
  serifFont: 'georgia',
  monoFont: 'jetbrains-mono',
  uiScale: 100,
};

// 시스템/Google 폰트 목록
const systemFonts: FontOption[] = [
  // Sans-serif 폰트
  { id: 'pretendard', name: 'Pretendard', value: "'Pretendard Variable', 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif", type: 'system', category: 'sans' },
  { id: 'inter', name: 'Inter', value: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif", type: 'google', category: 'sans' },
  { id: 'noto-sans-kr', name: 'Noto Sans KR', value: "'Noto Sans KR', sans-serif", type: 'google', category: 'sans' },
  { id: 'roboto', name: 'Roboto', value: "'Roboto', sans-serif", type: 'google', category: 'sans' },
  { id: 'open-sans', name: 'Open Sans', value: "'Open Sans', sans-serif", type: 'google', category: 'sans' },
  { id: 'lato', name: 'Lato', value: "'Lato', sans-serif", type: 'google', category: 'sans' },
  { id: 'source-sans', name: 'Source Sans 3', value: "'Source Sans 3', sans-serif", type: 'google', category: 'sans' },
  { id: 'ibm-plex-sans', name: 'IBM Plex Sans', value: "'IBM Plex Sans', sans-serif", type: 'google', category: 'sans' },
  
  // Serif 폰트
  { id: 'georgia', name: 'Georgia', value: "'Georgia', 'Noto Serif KR', serif", type: 'system', category: 'serif' },
  { id: 'noto-serif-kr', name: 'Noto Serif KR', value: "'Noto Serif KR', Georgia, serif", type: 'google', category: 'serif' },
  { id: 'playfair', name: 'Playfair Display', value: "'Playfair Display', Georgia, serif", type: 'google', category: 'serif' },
  { id: 'crimson-pro', name: 'Crimson Pro', value: "'Crimson Pro', Georgia, serif", type: 'google', category: 'serif' },
  { id: 'lora', name: 'Lora', value: "'Lora', Georgia, serif", type: 'google', category: 'serif' },
  { id: 'merriweather', name: 'Merriweather', value: "'Merriweather', Georgia, serif", type: 'google', category: 'serif' },
  { id: 'source-serif', name: 'Source Serif 4', value: "'Source Serif 4', Georgia, serif", type: 'google', category: 'serif' },
  { id: 'ibm-plex-serif', name: 'IBM Plex Serif', value: "'IBM Plex Serif', Georgia, serif", type: 'google', category: 'serif' },
  
  // Monospace 폰트
  { id: 'jetbrains-mono', name: 'JetBrains Mono', value: "'JetBrains Mono', 'SF Mono', Consolas, monospace", type: 'google', category: 'mono' },
  { id: 'fira-code', name: 'Fira Code', value: "'Fira Code', 'SF Mono', Consolas, monospace", type: 'google', category: 'mono' },
  { id: 'source-code-pro', name: 'Source Code Pro', value: "'Source Code Pro', Consolas, monospace", type: 'google', category: 'mono' },
  { id: 'ibm-plex-mono', name: 'IBM Plex Mono', value: "'IBM Plex Mono', Consolas, monospace", type: 'google', category: 'mono' },
  { id: 'd2coding', name: 'D2 Coding', value: "'D2Coding', 'D2 Coding', Consolas, monospace", type: 'google', category: 'mono' },
  { id: 'consolas', name: 'Consolas', value: "'Consolas', 'Courier New', monospace", type: 'system', category: 'mono' },
];

// 전역 상태
const fontSettings = ref<FontSettings>(loadSettings());
const customFonts = ref<CustomFont[]>(loadCustomFonts());

// 로드 함수들
function loadSettings(): FontSettings {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      return { ...defaultSettings, ...parsed };
    }
  } catch (e) {
    console.error('Failed to load font settings:', e);
  }
  return { ...defaultSettings };
}

function loadCustomFonts(): CustomFont[] {
  try {
    const stored = localStorage.getItem(CUSTOM_FONTS_KEY);
    if (stored) {
      const fonts = JSON.parse(stored);
      // 기존 category (단일값) -> categories (배열) 마이그레이션
      return fonts.map((font: any) => {
        if (font.category && !font.categories) {
          return {
            ...font,
            categories: [font.category],
          };
        }
        return font;
      });
    }
  } catch (e) {
    console.error('Failed to load custom fonts:', e);
  }
  return [];
}

// 저장 함수들
function saveSettings() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(fontSettings.value));
  } catch (e) {
    console.error('Failed to save font settings:', e);
  }
}

function saveCustomFonts() {
  try {
    localStorage.setItem(CUSTOM_FONTS_KEY, JSON.stringify(customFonts.value));
  } catch (e) {
    console.error('Failed to save custom fonts:', e);
  }
}

// CSS 변수 및 스타일 적용
function applyFontSettings() {
  const root = document.documentElement;
  
  // 폰트 찾기
  const sansFont = getAllFonts('sans').find(f => f.id === fontSettings.value.sansFont);
  const serifFont = getAllFonts('serif').find(f => f.id === fontSettings.value.serifFont);
  const monoFont = getAllFonts('mono').find(f => f.id === fontSettings.value.monoFont);
  
  // CSS 변수 적용
  if (sansFont) {
    root.style.setProperty('--font-sans', sansFont.value);
  }
  if (serifFont) {
    root.style.setProperty('--font-serif', serifFont.value);
  }
  if (monoFont) {
    root.style.setProperty('--font-mono', monoFont.value);
  }
  
  // UI 스케일 적용 - Electron webFrame API 사용 (가장 안정적)
  const scale = fontSettings.value.uiScale / 100;
  if (window.cuenote?.setZoomFactor) {
    window.cuenote.setZoomFactor(scale);
  }
}

// Google Fonts URL 생성
function getGoogleFontsUrl(fontIds: string[]): string {
  const googleFonts = fontIds
    .map(id => systemFonts.find(f => f.id === id))
    .filter(f => f && f.type === 'google')
    .map(f => {
      const name = f!.name.replace(/\s+/g, '+');
      return `family=${name}:wght@400;500;600;700`;
    });
  
  if (googleFonts.length === 0) return '';
  return `https://fonts.googleapis.com/css2?${googleFonts.join('&')}&display=swap`;
}

// 파일 경로에서 format 추출
function getFontFormat(filePath: string): string {
  const lowerPath = filePath.toLowerCase();
  if (lowerPath.endsWith('.woff2')) return 'woff2';
  if (lowerPath.endsWith('.woff')) return 'woff';
  if (lowerPath.endsWith('.ttf')) return 'truetype';
  if (lowerPath.endsWith('.otf')) return 'opentype';
  if (lowerPath.endsWith('.eot')) return 'embedded-opentype';
  return 'truetype';
}

// 커스텀 폰트 로드
function loadCustomFontStyles() {
  // 기존 커스텀 폰트 스타일 제거
  const existingStyle = document.getElementById('cuenote-custom-fonts');
  if (existingStyle) {
    existingStyle.remove();
  }
  
  if (customFonts.value.length === 0) return;
  
  // 새 스타일 요소 생성
  const style = document.createElement('style');
  style.id = 'cuenote-custom-fonts';
  
  const cssRules = customFonts.value.map(font => {
    const format = getFontFormat(font.filePath);
    // 로컬 파일 경로를 file:// URL로 변환 (Windows 경로 처리)
    const fileUrl = font.filePath.startsWith('file://') 
      ? font.filePath 
      : `file:///${font.filePath.replace(/\\/g, '/')}`;
    
    return `@font-face {
  font-family: '${font.name}';
  src: url('${fileUrl}') format('${format}');
  font-weight: normal;
  font-style: normal;
  font-display: swap;
}`;
  }).join('\n\n');
  
  style.textContent = cssRules;
  document.head.appendChild(style);
}

// Google Fonts 동적 로드
function loadGoogleFonts() {
  const fontIds = [
    fontSettings.value.sansFont,
    fontSettings.value.serifFont,
    fontSettings.value.monoFont,
  ];
  
  const url = getGoogleFontsUrl(fontIds);
  if (!url) return;
  
  // 기존 동적 폰트 링크 제거
  const existingLink = document.getElementById('cuenote-google-fonts');
  if (existingLink) {
    existingLink.remove();
  }
  
  // 새 링크 추가
  const link = document.createElement('link');
  link.id = 'cuenote-google-fonts';
  link.rel = 'stylesheet';
  link.href = url;
  document.head.appendChild(link);
}

// 모든 폰트 가져오기 (카테고리별)
function getAllFonts(category: 'sans' | 'serif' | 'mono'): FontOption[] {
  const system = systemFonts.filter(f => f.category === category);
  const custom = customFonts.value
    .filter(f => f.categories.includes(category))
    .map(f => ({
      id: f.id,
      name: f.name,
      value: `'${f.name}', ${category === 'mono' ? 'monospace' : category === 'serif' ? 'serif' : 'sans-serif'}`,
      type: 'custom' as const,
      category,
    }));
  
  return [...system, ...custom];
}

// 설정 변경 감지 및 적용
watch(fontSettings, () => {
  saveSettings();
  loadGoogleFonts();
  applyFontSettings();
}, { deep: true });

watch(customFonts, () => {
  saveCustomFonts();
  loadCustomFontStyles();
}, { deep: true });

export function useFonts() {
  // 초기화
  function initFonts() {
    loadCustomFontStyles();
    loadGoogleFonts();
    applyFontSettings();
  }
  
  // 폰트 설정 업데이트
  function updateFontSettings(settings: Partial<FontSettings>) {
    fontSettings.value = { ...fontSettings.value, ...settings };
  }
  
  // 커스텀 폰트 추가 (파일 저장 후 호출)
  function addCustomFont(font: Omit<CustomFont, 'id'>): string {
    const id = `custom-${Date.now()}`;
    
    // 중복 체크 (같은 파일명)
    if (customFonts.value.some(f => f.fileName === font.fileName)) {
      return '';
    }
    
    customFonts.value.push({
      id,
      ...font,
    });
    
    return id;
  }
  
  // 커스텀 폰트 제거 (파일 삭제는 호출자가 처리)
  async function removeCustomFont(id: string): Promise<CustomFont | null> {
    const index = customFonts.value.findIndex(f => f.id === id);
    if (index !== -1) {
      const removed = customFonts.value.splice(index, 1)[0];
      return removed;
    }
    return null;
  }
  
  // 설정 리셋
  function resetFontSettings() {
    fontSettings.value = { ...defaultSettings };
    customFonts.value = [];
    loadCustomFontStyles();
    loadGoogleFonts();
    applyFontSettings();
  }
  
  // Computed
  const sansFonts = computed(() => getAllFonts('sans'));
  const serifFonts = computed(() => getAllFonts('serif'));
  const monoFonts = computed(() => getAllFonts('mono'));
  
  return {
    fontSettings,
    customFonts,
    sansFonts,
    serifFonts,
    monoFonts,
    uiScaleOptions: UI_SCALE_OPTIONS,
    initFonts,
    updateFontSettings,
    addCustomFont,
    removeCustomFont,
    resetFontSettings,
    getAllFonts,
  };
}
