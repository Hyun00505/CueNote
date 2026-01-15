<template>
  <div id="section-appearance" class="settings-category">
    <h2 class="category-title">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="4 7 4 4 20 4 20 7" />
        <line x1="9" y1="20" x2="15" y2="20" />
        <line x1="12" y1="4" x2="12" y2="20" />
      </svg>
      {{ t('settings.appearanceTitle') }}
    </h2>

    <section class="settings-section">
      <h3 class="section-title">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="4 7 4 4 20 4 20 7" />
          <line x1="9" y1="20" x2="15" y2="20" />
          <line x1="12" y1="4" x2="12" y2="20" />
        </svg>
        {{ t('fonts.title') }}
      </h3>
      <p class="section-desc">{{ t('fonts.desc') }}</p>

      <!-- 폰트 선택 그리드 -->
      <div class="font-settings-grid">
        <!-- UI 폰트 -->
        <div class="font-setting-item">
          <div class="font-setting-label">
            <span class="font-label-text">{{ t('fonts.uiFont') }}</span>
            <span class="font-label-desc">{{ t('fonts.uiFontDesc') }}</span>
          </div>
          <select class="font-select" :value="fontSettings.sansFont"
            @change="updateFontSettings({ sansFont: ($event.target as HTMLSelectElement).value })">
            <option v-for="font in sansFonts" :key="font.id" :value="font.id">
              {{ font.name }}
            </option>
          </select>
        </div>

        <!-- 에디터 폰트 -->
        <div class="font-setting-item">
          <div class="font-setting-label">
            <span class="font-label-text">{{ t('fonts.editorFont') }}</span>
            <span class="font-label-desc">{{ t('fonts.editorFontDesc') }}</span>
          </div>
          <select class="font-select" :value="fontSettings.serifFont"
            @change="updateFontSettings({ serifFont: ($event.target as HTMLSelectElement).value })">
            <option v-for="font in serifFonts" :key="font.id" :value="font.id">
              {{ font.name }}
            </option>
          </select>
        </div>

        <!-- 코드 폰트 -->
        <div class="font-setting-item">
          <div class="font-setting-label">
            <span class="font-label-text">{{ t('fonts.codeFont') }}</span>
            <span class="font-label-desc">{{ t('fonts.codeFontDesc') }}</span>
          </div>
          <select class="font-select" :value="fontSettings.monoFont"
            @change="updateFontSettings({ monoFont: ($event.target as HTMLSelectElement).value })">
            <option v-for="font in monoFonts" :key="font.id" :value="font.id">
              {{ font.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- UI 크기 -->
      <div class="ui-scale-settings">
        <div class="ui-scale-header">
          <label>{{ t('fonts.uiScale') }}</label>
          <span class="ui-scale-current">{{ fontSettings.uiScale }}%</span>
        </div>
        <div class="ui-scale-buttons">
          <button v-for="scale in uiScaleOptions" :key="scale" class="ui-scale-btn"
            :class="{ active: fontSettings.uiScale === scale }" @click="updateFontSettings({ uiScale: scale })">
            {{ scale }}%
          </button>
        </div>
      </div>

      <!-- 커스텀 폰트 -->
      <div class="custom-fonts-section">
        <div class="custom-fonts-header">
          <div>
            <span class="custom-fonts-title">{{ t('fonts.customFonts') }}</span>
            <span class="custom-fonts-desc">{{ t('fonts.customFontsDesc') }}</span>
          </div>
          <button class="add-font-btn" @click="openAddFontModal">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            {{ t('fonts.addFont') }}
          </button>
        </div>

        <div v-if="customFonts.length === 0" class="no-custom-fonts">
          {{ t('fonts.noCustomFonts') }}
        </div>
        <div v-else class="custom-fonts-list">
          <div v-for="font in customFonts" :key="font.id" class="custom-font-item">
            <div class="custom-font-info">
              <span class="custom-font-name">{{ font.name }}</span>
              <div class="custom-font-categories">
                <span v-for="cat in font.categories" :key="cat" class="custom-font-category">{{ fontCategoryLabels[cat]
                  }}</span>
              </div>
            </div>
            <button class="remove-font-btn" @click="handleRemoveFont(font.id)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- 커스텀 폰트 추가 모달 -->
    <Teleport to="body">
      <div v-if="showAddFontModal" class="font-modal-overlay" @click.self="closeAddFontModal">
        <div class="font-modal">
          <div class="font-modal-header">
            <h3>{{ t('fonts.addFont') }}</h3>
            <button class="font-modal-close" @click="closeAddFontModal">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="font-modal-body">
            <div class="font-form-group">
              <label>{{ t('fonts.fontFile') }}</label>
              <div class="font-file-input">
                <input type="text" :value="newFontFileName" readonly :placeholder="t('fonts.fontFilePlaceholder')" />
                <button class="font-browse-btn" @click="selectFontFile">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  {{ t('fonts.selectFile') }}
                </button>
              </div>
            </div>
            <div class="font-form-group">
              <label>{{ t('fonts.fontName') }}</label>
              <input v-model="newFontName" type="text" :placeholder="t('fonts.fontNamePlaceholder')" />
            </div>
            <div class="font-form-group">
              <label>{{ t('fonts.fontCategory') }}</label>
              <div class="font-category-checkboxes">
                <label v-for="cat in (['sans', 'serif', 'mono'] as const)" :key="cat" class="font-category-checkbox"
                  :class="{ checked: newFontCategories.includes(cat) }">
                  <input type="checkbox" :checked="newFontCategories.includes(cat)" @change="toggleCategory(cat)" />
                  <span>{{ fontCategoryLabels[cat] }}</span>
                </label>
              </div>
            </div>
          </div>
          <div class="font-modal-footer">
            <button class="font-modal-btn cancel" @click="closeAddFontModal">
              {{ t('common.cancel') }}
            </button>
            <button class="font-modal-btn primary" @click="handleAddFont"
              :disabled="!newFontName || !newFontFilePath || isAddingFont">
              <span v-if="isAddingFont" class="loading-spinner-sm"></span>
              <span v-else>{{ t('common.add') }}</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n, useFonts } from '../../composables';

const { t } = useI18n();

const {
  fontSettings,
  customFonts,
  sansFonts,
  serifFonts,
  monoFonts,
  updateFontSettings,
  addCustomFont,
  removeCustomFont,
  uiScaleOptions,
} = useFonts();

// 카테고리 라벨
const fontCategoryLabels = computed(() => ({
  sans: t('fonts.categorySans'),
  serif: t('fonts.categorySerif'),
  mono: t('fonts.categoryMono'),
}));

// 커스텀 폰트 추가 모달
const showAddFontModal = ref(false);
const newFontName = ref('');
const newFontFilePath = ref('');
const newFontFileName = ref('');
const newFontCategories = ref<('sans' | 'serif' | 'mono')[]>(['sans']);
const isAddingFont = ref(false);

function openAddFontModal() {
  newFontName.value = '';
  newFontFilePath.value = '';
  newFontFileName.value = '';
  newFontCategories.value = ['sans'];
  showAddFontModal.value = true;
}

function toggleCategory(cat: 'sans' | 'serif' | 'mono') {
  const idx = newFontCategories.value.indexOf(cat);
  if (idx === -1) {
    newFontCategories.value.push(cat);
  } else {
    newFontCategories.value.splice(idx, 1);
  }
}

function closeAddFontModal() {
  showAddFontModal.value = false;
}

// 폰트 파일 선택
async function selectFontFile() {
  if (!window.cuenote?.selectFont) {
    alert(t('fonts.alertElectronOnly'));
    return;
  }

  const filePath = await window.cuenote.selectFont();
  if (filePath) {
    newFontFilePath.value = filePath;
    const fileName = filePath.split(/[/\\]/).pop() || '';
    newFontFileName.value = fileName;
    if (!newFontName.value) {
      newFontName.value = fileName.replace(/\.(ttf|otf|woff2?|eot)$/i, '');
    }
  }
}

// 폰트 추가
async function handleAddFont() {
  if (!newFontName.value || !newFontFilePath.value) return;
  if (!window.cuenote?.saveFont) {
    alert(t('fonts.alertElectronOnly'));
    return;
  }

  isAddingFont.value = true;

  try {
    const result = await window.cuenote.saveFont(newFontFilePath.value, newFontName.value);

    if (result.success && result.path && result.fileName) {
      addCustomFont({
        name: newFontName.value,
        filePath: result.path,
        fileName: result.fileName,
        categories: newFontCategories.value,
      });
      closeAddFontModal();
    } else {
      alert(`${t('fonts.alertSaveFailed')}${result.error}`);
    }
  } catch (error) {
    console.error('Failed to add font:', error);
    alert(t('fonts.alertError'));
  } finally {
    isAddingFont.value = false;
  }
}

// 폰트 제거
async function handleRemoveFont(id: string) {
  const removed = await removeCustomFont(id);
  if (removed && window.cuenote?.deleteFont) {
    await window.cuenote.deleteFont(removed.filePath);
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

/* Font Settings */
.font-settings-grid {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.font-setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 14px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
}

.font-setting-label {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.font-label-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.font-label-desc {
  font-size: 11px;
  color: var(--text-muted);
}

.font-select {
  min-width: 180px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.font-select:hover {
  border-color: var(--border-default);
}

.font-select:focus {
  outline: none;
  border-color: var(--text-muted);
}

/* UI Scale Settings */
.ui-scale-settings {
  padding: 16px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  margin-bottom: 20px;
}

.ui-scale-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.ui-scale-header label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.ui-scale-current {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.ui-scale-buttons {
  display: flex;
  gap: 6px;
}

.ui-scale-btn {
  flex: 1;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.ui-scale-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
}

.ui-scale-btn.active {
  background: var(--bg-active);
  border-color: var(--text-muted);
  color: var(--text-primary);
}

/* Custom Fonts */
.custom-fonts-section {
  padding: 16px;
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
}

.custom-fonts-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.custom-fonts-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  display: block;
}

.custom-fonts-desc {
  font-size: 11px;
  color: var(--text-muted);
  display: block;
  margin-top: 2px;
}

.add-font-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 6px;
  color: #a78bfa;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-font-btn:hover {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.5);
}

.no-custom-fonts {
  padding: 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.custom-fonts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.custom-font-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
}

.custom-font-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.custom-font-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.custom-font-categories {
  display: flex;
  gap: 4px;
}

.custom-font-category {
  padding: 2px 6px;
  background: var(--bg-primary);
  border-radius: 4px;
  font-size: 10px;
  color: var(--text-muted);
}

.remove-font-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.remove-font-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #f87171;
}

/* Font Modal */
.font-modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease;
}

.font-modal {
  background: var(--bg-primary);
  border-radius: 12px;
  width: 420px;
  max-width: 90vw;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  animation: modalSlideUp 0.2s ease;
}

.font-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.font-modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.font-modal-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.font-modal-close:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.font-modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.font-form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.font-form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.font-form-group input[type="text"] {
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  transition: all 0.15s ease;
}

.font-form-group input[type="text"]:focus {
  outline: none;
  border-color: var(--text-muted);
}

.font-file-input {
  display: flex;
  gap: 8px;
}

.font-file-input input {
  flex: 1;
}

.font-browse-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.font-browse-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
}

.font-category-checkboxes {
  display: flex;
  gap: 8px;
}

.font-category-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.font-category-checkbox:hover {
  background: var(--bg-hover);
}

.font-category-checkbox.checked {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
}

.font-category-checkbox input {
  display: none;
}

.font-category-checkbox span {
  font-size: 13px;
  color: var(--text-secondary);
}

.font-category-checkbox.checked span {
  color: #a78bfa;
}

.font-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
}

.font-modal-btn {
  padding: 10px 18px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.font-modal-btn.cancel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.font-modal-btn.cancel:hover {
  background: var(--bg-hover);
}

.font-modal-btn.primary {
  background: var(--gradient-primary);
  border: 1px solid transparent;
  color: white;
}

.font-modal-btn.primary:hover:not(:disabled) {
  filter: brightness(1.1);
}

.font-modal-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border-strong);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
