<template>
  <div
    id="section-general"
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
        <circle
          cx="12"
          cy="12"
          r="3"
        />
        <path
          d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"
        />
      </svg>
      {{ t('settings.generalTitle') }}
    </h2>

    <!-- Language Section -->
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
          <circle
            cx="12"
            cy="12"
            r="10"
          />
          <path d="M2 12h20" />
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
        </svg>
        {{ t('settings.language') }}
      </h3>
      <p class="section-desc">
        {{ t('settings.languageDesc') }}
      </p>

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
          <svg
            v-if="currentLanguage === lang"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            class="lang-check"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </button>
      </div>
    </section>

    <!-- Theme Section -->
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
          <circle
            cx="12"
            cy="12"
            r="5"
          />
          <path
            d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
          />
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
          <div
            class="theme-swatch"
            :style="{ background: theme.colors.bg }"
          >
            <div
              class="swatch-sidebar"
              :style="{ background: theme.colors.sidebar }"
            />
            <div
              class="swatch-accent"
              :style="{ background: theme.colors.accent }"
            />
          </div>
          <span class="theme-label">{{ theme.name }}</span>
          <div
            v-if="currentTheme === theme.id"
            class="theme-check"
          >
            <svg
              width="10"
              height="10"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="3"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from '../../composables';

const { t, currentLanguage, setLanguage, languageNames } = useI18n();

// 테마 설정
type ThemeId = 'dark' | 'dim' | 'github-dark' | 'light';

const themes = computed(() => [
  { id: 'dark' as ThemeId, name: t('theme.dark'), colors: { bg: '#0f0f12', sidebar: '#16161a', accent: '#6b7280' } },
  { id: 'dim' as ThemeId, name: t('theme.dim'), colors: { bg: '#1c1c1c', sidebar: '#252525', accent: '#8b949e' } },
  { id: 'github-dark' as ThemeId, name: t('theme.github'), colors: { bg: '#0d1117', sidebar: '#161b22', accent: '#58a6ff' } },
  { id: 'light' as ThemeId, name: t('theme.light'), colors: { bg: '#ffffff', sidebar: '#f3f4f6', accent: '#4b5563' } },
]);

const currentTheme = ref<ThemeId>('dark');

function setTheme(theme: ThemeId) {
  currentTheme.value = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('cuenote-theme', theme);
}

function initTheme() {
  const savedTheme = localStorage.getItem('cuenote-theme');
  const validThemes: ThemeId[] = ['dark', 'dim', 'github-dark', 'light'];
  const theme = validThemes.includes(savedTheme as ThemeId) ? savedTheme as ThemeId : 'dark';

  currentTheme.value = theme;
  document.documentElement.setAttribute('data-theme', theme);
  if (savedTheme !== theme) {
    localStorage.setItem('cuenote-theme', theme);
  }
}

onMounted(() => {
  initTheme();
});

// 리셋 기능을 위해 expose
defineExpose({
  setTheme,
  currentTheme
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
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.language-btn:hover {
  background: var(--surface-2);
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
  grid-template-columns: repeat(4, 1fr);
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
