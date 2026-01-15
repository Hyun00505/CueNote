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

    <!-- Main Layout: Sidebar + Content -->
    <div class="settings-main">
      <!-- Settings Sidebar Navigation -->
      <nav class="settings-nav">
        <div class="nav-group">
          <div class="nav-group-title">일반</div>
          <button 
            class="nav-item" 
            :class="{ active: activeSection === 'general' }"
            @click="scrollToSection('general')"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
            <span>언어 및 테마</span>
          </button>
        </div>

        <div class="nav-group">
          <div class="nav-group-title">외관</div>
          <button 
            class="nav-item" 
            :class="{ active: activeSection === 'appearance' }"
            @click="scrollToSection('appearance')"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="4 7 4 4 20 4 20 7"/>
              <line x1="9" y1="20" x2="15" y2="20"/>
              <line x1="12" y1="4" x2="12" y2="20"/>
            </svg>
            <span>폰트 설정</span>
          </button>
          <button 
            class="nav-item" 
            :class="{ active: activeSection === 'shortcuts' }"
            @click="scrollToSection('shortcuts')"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="4" width="20" height="16" rx="2"/>
              <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M6 16h8"/>
            </svg>
            <span>단축키</span>
          </button>
        </div>

        <div class="nav-group">
          <div class="nav-group-title">AI</div>
          <button 
            class="nav-item" 
            :class="{ active: activeSection === 'ai' }"
            @click="scrollToSection('ai')"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
            <span>AI 모델</span>
          </button>
          <button 
            class="nav-item" 
            :class="{ active: activeSection === 'ocr' }"
            @click="scrollToSection('ocr')"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <path d="M12 18v-6"/>
              <path d="m9 15 3-3 3 3"/>
            </svg>
            <span>문서 변환 (OCR)</span>
          </button>
        </div>
      </nav>

<<<<<<< HEAD
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
=======
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

            <div v-if="!ocrStatus?.model_downloaded" class="download-section">
              <button 
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
                {{ ocrDownloading ? '다운로드 중...' : '모델 다운로드' }}
              </button>
              
              <!-- 진행률 바 -->
              <div v-if="ocrDownloading" class="download-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: ocrDownloadProgress + '%' }"></div>
                </div>
                <div class="progress-info">
                  <span class="progress-message">{{ ocrDownloadMessage }}</span>
                  <span class="progress-percent">{{ ocrDownloadProgress }}%</span>
                </div>
              </div>
            </div>

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

            <div v-if="!handwritingStatus?.model_downloaded" class="download-section">
              <button 
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
                {{ handwritingDownloading ? '다운로드 중...' : '모델 다운로드' }}
              </button>
              
              <!-- 진행률 바 -->
              <div v-if="handwritingDownloading" class="download-progress">
                <div class="progress-bar">
                  <div class="progress-fill handwriting" :style="{ width: handwritingDownloadProgress + '%' }"></div>
                </div>
                <div class="progress-info">
                  <span class="progress-message">{{ handwritingDownloadMessage }}</span>
                  <span class="progress-percent">{{ handwritingDownloadProgress }}%</span>
                </div>
              </div>
            </div>

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

    <!-- 커스텀 폰트 추가 모달 -->
    <Teleport to="body">
      <div v-if="showAddFontModal" class="font-modal-overlay" @click.self="closeAddFontModal">
        <div class="font-modal">
          <div class="font-modal-header">
            <h3>{{ t('fonts.addFont') }}</h3>
            <button class="font-modal-close" @click="closeAddFontModal">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="font-modal-body">
            <div class="font-form-group">
              <label>{{ t('fonts.fontFile') }}</label>
              <div class="font-file-input">
                <input 
                  type="text" 
                  :value="newFontFileName"
                  readonly
                  :placeholder="t('fonts.fontFilePlaceholder')"
                />
                <button class="font-browse-btn" @click="selectFontFile">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                  </svg>
                  {{ t('fonts.selectFile') }}
                </button>
              </div>
            </div>
            <div class="font-form-group">
              <label>{{ t('fonts.fontName') }}</label>
              <input 
                v-model="newFontName" 
                type="text" 
                :placeholder="t('fonts.fontNamePlaceholder')"
              />
            </div>
            <div class="font-form-group">
              <label>{{ t('fonts.fontCategory') }}</label>
              <div class="font-category-checkboxes">
                <label class="category-checkbox" :class="{ checked: newFontCategories.includes('sans') }">
                  <input type="checkbox" :checked="newFontCategories.includes('sans')" @change="toggleCategory('sans')" />
                  <span class="checkbox-label">Sans-serif (UI)</span>
                </label>
                <label class="category-checkbox" :class="{ checked: newFontCategories.includes('serif') }">
                  <input type="checkbox" :checked="newFontCategories.includes('serif')" @change="toggleCategory('serif')" />
                  <span class="checkbox-label">Serif (에디터)</span>
                </label>
                <label class="category-checkbox" :class="{ checked: newFontCategories.includes('mono') }">
                  <input type="checkbox" :checked="newFontCategories.includes('mono')" @change="toggleCategory('mono')" />
                  <span class="checkbox-label">Monospace (코드)</span>
                </label>
              </div>
            </div>
          </div>
          <div class="font-modal-footer">
            <button class="font-modal-btn cancel" @click="closeAddFontModal">{{ t('common.cancel') }}</button>
            <button 
              class="font-modal-btn primary" 
              @click="handleAddFont" 
              :disabled="!newFontName || !newFontFilePath || newFontCategories.length === 0 || isAddingFont"
            >
              <span v-if="isAddingFont" class="loading-spinner small"></span>
              {{ isAddingFont ? t('common.loading') : t('common.add') }}
            </button>
          </div>
>>>>>>> ab9efc6809c9dc83a3671c0756822e5619584c8e
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

<<<<<<< HEAD
// 전체 초기화
function handleResetAll() {
  resetSettings();
  resetFontSettings();
  if (generalSettingsRef.value) {
    generalSettingsRef.value.setTheme('dark');
=======
// 폰트 추가
async function handleAddFont() {
  if (!newFontName.value || !newFontFilePath.value) return;
  if (!window.cuenote?.saveFont) {
    alert('Electron 환경에서만 사용 가능합니다.');
    return;
  }
  
  isAddingFont.value = true;
  
  try {
    // 파일을 앱 데이터 폴더로 복사
    const result = await window.cuenote.saveFont(newFontFilePath.value, newFontName.value);
    
    if (result.success) {
      // 폰트 정보 저장
      addCustomFont({
        name: newFontName.value,
        filePath: result.path,
        fileName: result.fileName,
        categories: newFontCategories.value,
      });
      closeAddFontModal();
    } else {
      alert(`폰트 저장 실패: ${result.error}`);
    }
  } catch (error) {
    console.error('Failed to add font:', error);
    alert('폰트 추가 중 오류가 발생했습니다.');
  } finally {
    isAddingFont.value = false;
  }
}

// 폰트 제거
async function handleRemoveFont(id: string) {
  const removed = await removeCustomFont(id);
  if (removed && window.cuenote?.deleteFont) {
    // 파일도 삭제
    await window.cuenote.deleteFont(removed.filePath);
  }
}

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
const ocrDownloadProgress = ref(0);
const ocrDownloadMessage = ref('');

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
const handwritingDownloadProgress = ref(0);
const handwritingDownloadMessage = ref('');

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

// OCR 모델 다운로드 (SSE 스트리밍)
async function downloadOcrModel() {
  ocrDownloading.value = true;
  ocrDownloadError.value = '';
  ocrDownloadProgress.value = 0;
  ocrDownloadMessage.value = '다운로드 준비 중...';
  
  try {
    const eventSource = new EventSource(`${CORE_BASE}/ai/ocr/download/stream`);
    
    eventSource.addEventListener('progress', (event) => {
      const data = JSON.parse(event.data);
      ocrDownloadProgress.value = data.progress || 0;
      ocrDownloadMessage.value = data.message || '다운로드 중...';
    });
    
    eventSource.addEventListener('complete', async (event) => {
      const data = JSON.parse(event.data);
      ocrDownloadProgress.value = 100;
      ocrDownloadMessage.value = data.message || '완료!';
      eventSource.close();
      await checkOcrStatus();
      ocrDownloading.value = false;
    });
    
    eventSource.addEventListener('error', (event) => {
      // SSE 에러 이벤트 처리
      if (event instanceof MessageEvent) {
        const data = JSON.parse(event.data);
        ocrDownloadError.value = data.message || '다운로드에 실패했습니다.';
      } else {
        ocrDownloadError.value = '연결이 끊어졌습니다. 다시 시도해주세요.';
      }
      eventSource.close();
      ocrDownloading.value = false;
    });
    
    eventSource.onerror = () => {
      // 연결 에러 처리
      if (ocrDownloading.value) {
        ocrDownloadError.value = '연결이 끊어졌습니다. 다시 시도해주세요.';
        eventSource.close();
        ocrDownloading.value = false;
      }
    };
  } catch (error) {
    console.error('OCR model download failed:', error);
    ocrDownloadError.value = '모델 다운로드에 실패했습니다. 네트워크를 확인해주세요.';
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

// 손글씨 OCR 모델 다운로드 (SSE 스트리밍)
async function downloadHandwritingModel() {
  handwritingDownloading.value = true;
  handwritingDownloadError.value = '';
  handwritingDownloadProgress.value = 0;
  handwritingDownloadMessage.value = '다운로드 준비 중...';
  
  try {
    const eventSource = new EventSource(`${CORE_BASE}/ai/ocr/handwriting/download/stream`);
    
    eventSource.addEventListener('progress', (event) => {
      const data = JSON.parse(event.data);
      handwritingDownloadProgress.value = data.progress || 0;
      handwritingDownloadMessage.value = data.message || '다운로드 중...';
    });
    
    eventSource.addEventListener('complete', async (event) => {
      const data = JSON.parse(event.data);
      handwritingDownloadProgress.value = 100;
      handwritingDownloadMessage.value = data.message || '완료!';
      eventSource.close();
      await checkHandwritingStatus();
      handwritingDownloading.value = false;
    });
    
    eventSource.addEventListener('error', (event) => {
      // SSE 에러 이벤트 처리
      if (event instanceof MessageEvent) {
        const data = JSON.parse(event.data);
        handwritingDownloadError.value = data.message || '다운로드에 실패했습니다.';
      } else {
        handwritingDownloadError.value = '연결이 끊어졌습니다. 다시 시도해주세요.';
      }
      eventSource.close();
      handwritingDownloading.value = false;
    });
    
    eventSource.onerror = () => {
      // 연결 에러 처리
      if (handwritingDownloading.value) {
        handwritingDownloadError.value = '연결이 끊어졌습니다. 다시 시도해주세요.';
        eventSource.close();
        handwritingDownloading.value = false;
      }
    };
  } catch (error) {
    console.error('Handwriting model download failed:', error);
    handwritingDownloadError.value = '손글씨 모델 다운로드에 실패했습니다. 네트워크를 확인해주세요.';
    handwritingDownloading.value = false;
>>>>>>> ab9efc6809c9dc83a3671c0756822e5619584c8e
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
<<<<<<< HEAD
  color: var(--text-secondary);
=======
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

/* Download Section */
.download-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Download Progress */
.download-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.handwriting {
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-message {
  font-size: 12px;
  color: var(--text-secondary);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.progress-percent {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-left: 12px;
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
>>>>>>> ab9efc6809c9dc83a3671c0756822e5619584c8e
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
