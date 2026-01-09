import { ref, watch } from 'vue';

const STORAGE_KEY = 'cuenote-shortcuts';

// 단축키 타입
export interface ShortcutConfig {
  key: string;        // 키 (예: 'a', '/', 'Enter')
  modifiers: {
    ctrl?: boolean;
    alt?: boolean;
    shift?: boolean;
    meta?: boolean;   // Cmd on Mac
  };
}

// 단축키 설정 타입
export interface ShortcutSettings {
  aiMenu: ShortcutConfig[];  // AI 메뉴 열기 (여러 단축키 지원)
}

// 기본 단축키 설정
const defaultShortcuts: ShortcutSettings = {
  aiMenu: [
    { key: 'a', modifiers: { alt: true } },           // Alt + A
    { key: '/', modifiers: {} },                       // / 키
  ]
};

// 전역 상태
const shortcuts = ref<ShortcutSettings>(loadShortcuts());

// 로컬 스토리지에서 단축키 로드
function loadShortcuts(): ShortcutSettings {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      return { ...defaultShortcuts, ...parsed };
    }
  } catch (e) {
    console.error('Failed to load shortcuts:', e);
  }
  return { ...defaultShortcuts };
}

// 단축키 저장
function saveShortcuts() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(shortcuts.value));
  } catch (e) {
    console.error('Failed to save shortcuts:', e);
  }
}

// 설정 변경 감지하여 자동 저장
watch(shortcuts, saveShortcuts, { deep: true });

// 단축키를 사람이 읽기 좋은 형식으로 변환
export function formatShortcut(config: ShortcutConfig): string {
  const parts: string[] = [];
  
  if (config.modifiers.ctrl) parts.push('Ctrl');
  if (config.modifiers.alt) parts.push('Alt');
  if (config.modifiers.shift) parts.push('Shift');
  if (config.modifiers.meta) parts.push('Cmd');
  
  // 특수 키 이름 변환
  let keyName = config.key;
  if (keyName === ' ') keyName = 'Space';
  else if (keyName === '/') keyName = '/';
  else if (keyName.length === 1) keyName = keyName.toUpperCase();
  
  parts.push(keyName);
  
  return parts.join(' + ');
}

// 키보드 이벤트가 단축키와 일치하는지 확인
export function matchesShortcut(event: KeyboardEvent, config: ShortcutConfig): boolean {
  // modifier 키 자체가 눌린 경우 무시
  if (['Control', 'Alt', 'Shift', 'Meta'].includes(event.key)) {
    return false;
  }
  
  const keyMatches = event.key.toLowerCase() === config.key.toLowerCase();
  const ctrlMatches = !!config.modifiers.ctrl === (event.ctrlKey || event.metaKey);
  const altMatches = !!config.modifiers.alt === event.altKey;
  const shiftMatches = !!config.modifiers.shift === event.shiftKey;
  
  // modifier가 없는 단축키 (예: /)는 modifier가 눌리지 않았을 때만 매치
  if (!config.modifiers.ctrl && !config.modifiers.alt && !config.modifiers.shift && !config.modifiers.meta) {
    return keyMatches && !event.ctrlKey && !event.altKey && !event.shiftKey && !event.metaKey;
  }
  
  return keyMatches && ctrlMatches && altMatches && shiftMatches;
}

// 키보드 이벤트에서 ShortcutConfig 생성
export function eventToShortcut(event: KeyboardEvent): ShortcutConfig | null {
  // modifier 키만 눌린 경우 무시
  if (['Control', 'Alt', 'Shift', 'Meta'].includes(event.key)) {
    return null;
  }
  
  return {
    key: event.key,
    modifiers: {
      ctrl: event.ctrlKey,
      alt: event.altKey,
      shift: event.shiftKey,
      meta: event.metaKey,
    }
  };
}

export function useShortcuts() {
  // AI 메뉴 단축키 확인
  function isAIMenuShortcut(event: KeyboardEvent): boolean {
    return shortcuts.value.aiMenu.some(config => matchesShortcut(event, config));
  }
  
  // AI 메뉴 단축키 업데이트
  function updateAIMenuShortcuts(newShortcuts: ShortcutConfig[]) {
    shortcuts.value.aiMenu = newShortcuts;
  }
  
  // 단축키 설정 리셋
  function resetShortcuts() {
    shortcuts.value = { ...defaultShortcuts };
  }
  
  // 기본 단축키로 리셋
  function getDefaultShortcuts(): ShortcutSettings {
    return { ...defaultShortcuts };
  }
  
  return {
    shortcuts,
    isAIMenuShortcut,
    updateAIMenuShortcuts,
    resetShortcuts,
    getDefaultShortcuts,
    formatShortcut,
    matchesShortcut,
    eventToShortcut,
  };
}
