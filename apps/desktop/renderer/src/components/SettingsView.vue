<template>
  <div class="settings-view">
    <!-- Header -->
    <div class="settings-header">
      <button class="back-btn" @click="$emit('back')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        <span>{{ t('common.back') }}</span>
      </button>
      <div class="header-title">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3" />
          <path
            d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
        <span>{{ t('settings.title') }}</span>
      </div>
    </div>

    <!-- Main Layout: Sidebar + Content -->
    <div class="settings-main">
      <!-- Settings Sidebar Navigation -->
      <nav class="settings-nav">
        <div class="nav-group">
          <div class="nav-group-title">{{ t('settings.general') }}</div>
          <button class="nav-item" :class="{ active: activeSection === 'general' }" @click="scrollToSection('general')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3" />
              <path
                d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
            <span>{{ t('settings.menuLanguageTheme') }}</span>
          </button>
        </div>

        <div class="nav-group">
          <div class="nav-group-title">{{ t('settings.appearance') }}</div>
          <button class="nav-item" :class="{ active: activeSection === 'appearance' }"
            @click="scrollToSection('appearance')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="4 7 4 4 20 4 20 7" />
              <line x1="9" y1="20" x2="15" y2="20" />
              <line x1="12" y1="4" x2="12" y2="20" />
            </svg>
            <span>{{ t('settings.menuFonts') }}</span>
          </button>
          <button class="nav-item" :class="{ active: activeSection === 'shortcuts' }"
            @click="scrollToSection('shortcuts')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="4" width="20" height="16" rx="2" />
              <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M6 16h8" />
            </svg>
            <span>{{ t('shortcuts.title') }}</span>
          </button>
        </div>

        <div class="nav-group">
          <div class="nav-group-title">{{ t('settings.ai') }}</div>
          <button class="nav-item" :class="{ active: activeSection === 'ai' }" @click="scrollToSection('ai')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
            <span>{{ t('settings.menuAiModel') }}</span>
          </button>
          <button class="nav-item" :class="{ active: activeSection === 'ocr' }" @click="scrollToSection('ocr')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <path d="M12 18v-6" />
              <path d="m9 15 3-3 3 3" />
            </svg>
            <span>{{ t('settings.menuOcr') }}</span>
          </button>
        </div>
      </nav>

      <!-- Content -->
      <div class="settings-content" ref="settingsContentRef">
        <div class="settings-inner">
          <!-- 일반 설정 -->
          <GeneralSettings ref="generalSettingsRef" />

          <!-- 폰트 설정 -->
          <AppearanceSettings />

          <!-- 단축키 -->
          <ShortcutSettings />

          <!-- AI 모델 설정 -->
          <AISettings />

          <!-- OCR 설정 -->
          <OCRSettings />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useSettings, useI18n, useFonts } from '../composables';
import {
  GeneralSettings,
  AppearanceSettings,
  ShortcutSettings,
  AISettings,
  OCRSettings
} from './settings';

defineEmits<{
  back: [];
}>();

const { t } = useI18n();
const { initSettings, resetSettings } = useSettings();
const { initFonts, resetFontSettings } = useFonts();

// Refs for child components
const generalSettingsRef = ref<InstanceType<typeof GeneralSettings> | null>(null);

// 사이드바 내비게이션 관련 상태
const activeSection = ref('general');
const settingsContentRef = ref<HTMLElement | null>(null);

// 섹션으로 스크롤 이동
function scrollToSection(sectionId: string) {
  activeSection.value = sectionId;
  const element = document.getElementById(`section-${sectionId}`);
  if (element && settingsContentRef.value) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

// 스크롤 위치에 따라 activeSection 업데이트
function updateActiveSection() {
  if (!settingsContentRef.value) return;

  const sections = ['general', 'appearance', 'shortcuts', 'ai', 'ocr'];
  const containerHeight = settingsContentRef.value.clientHeight;

  for (let i = sections.length - 1; i >= 0; i--) {
    const section = document.getElementById(`section-${sections[i]}`);
    if (section) {
      const rect = section.getBoundingClientRect();
      const containerRect = settingsContentRef.value.getBoundingClientRect();
      const relativeTop = rect.top - containerRect.top;

      if (relativeTop <= containerHeight * 0.3) {
        activeSection.value = sections[i];
        break;
      }
    }
  }
}

// 전체 초기화
function handleResetAll() {
  resetSettings();
  resetFontSettings();
  if (generalSettingsRef.value) {
    generalSettingsRef.value.setTheme('dark');
  }
}

// 페이지 마운트 시 데이터 로드
onMounted(async () => {
  initFonts();
  await initSettings();

  // 스크롤 이벤트 리스너 등록
  if (settingsContentRef.value) {
    settingsContentRef.value.addEventListener('scroll', updateActiveSection);
  }
});

// 컴포넌트 언마운트 시 이벤트 리스너 제거
onUnmounted(() => {
  if (settingsContentRef.value) {
    settingsContentRef.value.removeEventListener('scroll', updateActiveSection);
  }
});

// Expose for parent component if needed
defineExpose({
  handleResetAll
});
</script>

<style scoped>
.settings-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary);
  color: var(--text-primary);
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
  padding: 8px 12px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.back-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-title svg {
  color: var(--text-muted);
}

/* Main Layout */
.settings-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Sidebar Navigation */
.settings-nav {
  width: 220px;
  flex-shrink: 0;
  padding: 20px 16px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  overflow-y: auto;
}

.nav-group {
  margin-bottom: 20px;
}

.nav-group:last-child {
  margin-bottom: 0;
}

.nav-group-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  padding: 0 12px;
  margin-bottom: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--bg-active);
  color: var(--text-primary);
}

.nav-item svg {
  flex-shrink: 0;
  opacity: 0.7;
}

.nav-item.active svg {
  opacity: 1;
}

/* Content Area */
.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 32px 40px;
}

.settings-inner {
  max-width: 720px;
  margin: 0 auto;
}
</style>
