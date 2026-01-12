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

        <!-- Shortcuts Section -->
        <section class="settings-section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="4" width="20" height="16" rx="2"/>
              <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M6 16h8"/>
            </svg>
            {{ t('shortcuts.title') }}
          </h3>
          <p class="section-desc">{{ t('shortcuts.desc') }}</p>
          
          <div class="shortcut-list">
            <div class="shortcut-item">
              <div class="shortcut-info">
                <span class="shortcut-name">{{ t('shortcuts.aiMenu') }}</span>
                <span class="shortcut-desc">{{ t('shortcuts.aiMenuDesc') }}</span>
              </div>
              <div class="shortcut-keys">
                <span 
                  v-for="(shortcut, index) in shortcuts.aiMenu" 
                  :key="index" 
                  class="shortcut-key"
                >
                  {{ formatShortcut(shortcut) }}
                </span>
              </div>
              <button class="shortcut-edit-btn" @click="openShortcutEditor('aiMenu')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
            </div>
          </div>
        </section>

        <!-- Shortcut Editor Modal -->
        <Teleport to="body">
          <div v-if="showShortcutEditor" class="shortcut-modal-overlay" @click.self="closeShortcutEditor">
            <div class="shortcut-modal">
              <div class="shortcut-modal-header">
                <h3>{{ t('shortcuts.edit') }}</h3>
                <button class="shortcut-modal-close" @click="closeShortcutEditor">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                  </svg>
                </button>
              </div>
              <div class="shortcut-modal-body">
                <p class="shortcut-modal-hint">{{ t('shortcuts.pressKeys') }}</p>
                
                <div class="shortcut-capture-area" tabindex="0" @keydown="captureShortcut" ref="shortcutCaptureRef">
                  <span v-if="capturedShortcut" class="captured-shortcut">
                    {{ formatShortcut(capturedShortcut) }}
                  </span>
                  <span v-else class="capture-placeholder">{{ t('shortcuts.waitingForInput') }}</span>
                </div>
                
                <div class="current-shortcuts">
                  <span class="current-label">{{ t('shortcuts.current') }}:</span>
                  <div class="current-keys">
                    <span 
                      v-for="(shortcut, index) in editingShortcuts" 
                      :key="index" 
                      class="shortcut-tag"
                    >
                      {{ formatShortcut(shortcut) }}
                      <button class="remove-shortcut" @click="removeEditingShortcut(index)">×</button>
                    </span>
                  </div>
                </div>
                
                <button class="add-shortcut-btn" @click="addCapturedShortcut" :disabled="!capturedShortcut">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="12" y1="5" x2="12" y2="19"/>
                    <line x1="5" y1="12" x2="19" y2="12"/>
                  </svg>
                  {{ t('shortcuts.addShortcut') }}
                </button>
              </div>
              <div class="shortcut-modal-footer">
                <button class="shortcut-modal-btn reset" @click="resetToDefault">
                  {{ t('shortcuts.resetDefault') }}
                </button>
                <button class="shortcut-modal-btn cancel" @click="closeShortcutEditor">
                  {{ t('common.cancel') }}
                </button>
                <button class="shortcut-modal-btn primary" @click="saveShortcuts" :disabled="editingShortcuts.length === 0">
                  {{ t('common.save') }}
                </button>
              </div>
            </div>
          </div>
        </Teleport>

        <!-- Font Section -->
        <section class="settings-section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="4 7 4 4 20 4 20 7"/>
              <line x1="9" y1="20" x2="15" y2="20"/>
              <line x1="12" y1="4" x2="12" y2="20"/>
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
              <select 
                class="font-select"
                :value="fontSettings.sansFont"
                @change="updateFontSettings({ sansFont: ($event.target as HTMLSelectElement).value })"
              >
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
              <select 
                class="font-select"
                :value="fontSettings.serifFont"
                @change="updateFontSettings({ serifFont: ($event.target as HTMLSelectElement).value })"
              >
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
              <select 
                class="font-select"
                :value="fontSettings.monoFont"
                @change="updateFontSettings({ monoFont: ($event.target as HTMLSelectElement).value })"
              >
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
              <button 
                v-for="scale in uiScaleOptions" 
                :key="scale"
                class="ui-scale-btn"
                :class="{ active: fontSettings.uiScale === scale }"
                @click="updateFontSettings({ uiScale: scale })"
              >
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
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
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
                    <span v-for="cat in font.categories" :key="cat" class="custom-font-category">{{ cat }}</span>
                  </div>
                </div>
                <button class="remove-font-btn" @click="handleRemoveFont(font.id)">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
            </div>
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

        <!-- OCR Engine Section -->
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
        </div>
      </div>
    </Teleport>

    <!-- Footer -->
    <div class="settings-footer">
      <div class="reset-buttons">
        <button class="reset-btn appearance" @click="handleResetAppearance" :title="t('common.resetAppearance')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"/>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
          {{ t('common.resetAppearance') }}
        </button>
        <button class="reset-btn all" @click="handleResetAll" :title="t('common.resetAll')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
            <path d="M21 3v5h-5"/>
            <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
            <path d="M8 16H3v5"/>
          </svg>
          {{ t('common.resetAll') }}
        </button>
      </div>
      <button class="save-btn" @click="$emit('back')">
        {{ t('common.done') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, nextTick } from 'vue';
import { useSettings, useI18n, useFonts, useShortcuts, formatShortcut } from '../composables';
import { GEMINI_VISION_MODELS } from '../composables/useSettings';
import type { ShortcutConfig } from '../composables/useShortcuts';

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

const {
  fontSettings,
  customFonts,
  sansFonts,
  serifFonts,
  monoFonts,
  initFonts,
  updateFontSettings,
  addCustomFont,
  removeCustomFont,
  resetFontSettings,
  uiScaleOptions,
} = useFonts();

const {
  shortcuts,
  updateAIMenuShortcuts,
  getDefaultShortcuts,
  eventToShortcut,
} = useShortcuts();

const isRefreshing = ref(false);

// 단축키 편집 관련 상태
const showShortcutEditor = ref(false);
const editingShortcutType = ref<'aiMenu' | null>(null);
const editingShortcuts = ref<ShortcutConfig[]>([]);
const capturedShortcut = ref<ShortcutConfig | null>(null);
const shortcutCaptureRef = ref<HTMLElement | null>(null);

function openShortcutEditor(type: 'aiMenu') {
  editingShortcutType.value = type;
  editingShortcuts.value = [...shortcuts.value[type]];
  capturedShortcut.value = null;
  showShortcutEditor.value = true;
  
  nextTick(() => {
    shortcutCaptureRef.value?.focus();
  });
}

function closeShortcutEditor() {
  showShortcutEditor.value = false;
  editingShortcutType.value = null;
  editingShortcuts.value = [];
  capturedShortcut.value = null;
}

function captureShortcut(e: KeyboardEvent) {
  e.preventDefault();
  e.stopPropagation();
  
  const shortcut = eventToShortcut(e);
  if (shortcut) {
    capturedShortcut.value = shortcut;
  }
}

function addCapturedShortcut() {
  if (!capturedShortcut.value) return;
  
  // 중복 체크
  const isDuplicate = editingShortcuts.value.some(s => 
    s.key === capturedShortcut.value!.key &&
    s.modifiers.ctrl === capturedShortcut.value!.modifiers.ctrl &&
    s.modifiers.alt === capturedShortcut.value!.modifiers.alt &&
    s.modifiers.shift === capturedShortcut.value!.modifiers.shift &&
    s.modifiers.meta === capturedShortcut.value!.modifiers.meta
  );
  
  if (!isDuplicate) {
    editingShortcuts.value.push(capturedShortcut.value);
  }
  
  capturedShortcut.value = null;
  shortcutCaptureRef.value?.focus();
}

function removeEditingShortcut(index: number) {
  editingShortcuts.value.splice(index, 1);
}

function resetToDefault() {
  if (editingShortcutType.value) {
    const defaults = getDefaultShortcuts();
    editingShortcuts.value = [...defaults[editingShortcutType.value]];
  }
}

function saveShortcuts() {
  if (editingShortcutType.value === 'aiMenu') {
    updateAIMenuShortcuts(editingShortcuts.value);
  }
  closeShortcutEditor();
}

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
    alert('Electron 환경에서만 사용 가능합니다.');
    return;
  }
  
  const filePath = await window.cuenote.selectFont();
  if (filePath) {
    newFontFilePath.value = filePath;
    // 파일명에서 기본 폰트 이름 추출
    const fileName = filePath.split(/[/\\]/).pop() || '';
    newFontFileName.value = fileName;
    if (!newFontName.value) {
      // 확장자 제거한 이름을 기본값으로
      newFontName.value = fileName.replace(/\.(ttf|otf|woff2?|eot)$/i, '');
    }
  }
}

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

interface OCRStatus {
  installed: boolean;
  model_downloaded: boolean;
  model_path: string;
  languages: string[];
  engine: string;
  engine_name: string;
  engine_description: string;
  requires_api_key: boolean;
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
const ocrStatus = ref<OCRStatus | null>(null);
const ocrDownloading = ref(false);
const ocrDownloadError = ref('');

const CORE_BASE = 'http://127.0.0.1:8787';

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
    // 기본값 유지
  }
}

// OCR 상태 확인
async function checkOcrStatus() {
  try {
    const engine = settings.value.ocr?.engine || 'rapidocr';
    const res = await fetch(`${CORE_BASE}/ai/ocr/status?engine=${engine}`);
    if (res.ok) {
      ocrStatus.value = await res.json();
    }
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
  saveSettings();
  checkOcrStatus();
}

// Gemini Vision 모델 목록
const geminiVisionModels = GEMINI_VISION_MODELS;

// Gemini Vision 모델 선택
function selectGeminiVisionModel(modelId: string) {
  if (!settings.value.ocr) {
    settings.value.ocr = { engine: 'gemini', geminiModel: modelId };
  } else {
    settings.value.ocr.geminiModel = modelId;
  }
  saveSettings();
}

// 페이지 마운트 시 데이터 로드
onMounted(async () => {
  initTheme();
  initFonts();
  await initSettings();
  await fetchOcrEngines();
  await checkOcrStatus();
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

function handleResetAll() {
  resetSettings();
  resetFontSettings();
  setTheme('dark');
}

function handleResetAppearance() {
  resetFontSettings();
  setTheme('dark');
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

.reset-buttons {
  display: flex;
  gap: 8px;
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

.reset-btn.appearance {
  color: var(--text-muted);
}

.reset-btn.appearance:hover {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
  color: #a78bfa;
}

.reset-btn.all {
  color: var(--text-muted);
}

.reset-btn.all:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #f87171;
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

/* OCR 엔진 선택 스타일 */
.ocr-engine-selector {
  margin-bottom: 16px;
}

.ocr-engine-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.ocr-engine-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  background: var(--bg-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.ocr-engine-option:hover:not(.disabled) {
  border-color: var(--accent);
  background: rgba(201, 167, 108, 0.05);
}

.ocr-engine-option.selected {
  border-color: var(--accent);
  background: rgba(201, 167, 108, 0.1);
}

.ocr-engine-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ocr-engine-option input[type="radio"] {
  margin-top: 2px;
  accent-color: var(--accent);
}

.engine-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.engine-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.engine-name {
  font-weight: 600;
  font-size: 13px;
  color: var(--text-primary);
}

.engine-accuracy {
  font-size: 11px;
  color: var(--accent);
  font-weight: 500;
}

.engine-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.4;
}

.engine-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.engine-tags .tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.engine-tags .tag.api-key {
  background: rgba(234, 179, 8, 0.15);
  color: #ca8a04;
}

.engine-tags .tag.free {
  background: rgba(34, 197, 94, 0.15);
  color: #16a34a;
}

.engine-tags .tag.lang {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

/* Gemini Vision 설정 */
.gemini-vision-settings {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

.vision-model-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
  max-height: 280px;
  overflow-y: auto;
}

.vision-model-option {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--border-light);
  border-radius: 6px;
  background: var(--bg-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.vision-model-option:hover {
  border-color: var(--accent);
  background: rgba(201, 167, 108, 0.05);
}

.vision-model-option.selected {
  border-color: var(--accent);
  background: rgba(201, 167, 108, 0.1);
}

.vision-model-option input[type="radio"] {
  margin-top: 2px;
  accent-color: var(--accent);
}

.vision-model-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.vision-model-header {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.vision-model-name {
  font-weight: 600;
  font-size: 12px;
  color: var(--text-primary);
}

.vision-model-desc {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.4;
}

.badge {
  font-size: 9px;
  padding: 2px 5px;
  border-radius: 3px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.recommended {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.badge.free {
  background: rgba(34, 197, 94, 0.15);
  color: #16a34a;
}

.badge.paid {
  background: rgba(239, 68, 68, 0.15);
  color: #dc2626;
}

.gemini-ocr-notice {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 6px;
  background: rgba(201, 167, 108, 0.1);
  border: 1px solid rgba(201, 167, 108, 0.2);
  margin-top: 12px;
}

.gemini-ocr-notice svg {
  flex-shrink: 0;
  color: var(--accent);
  margin-top: 2px;
}

.gemini-ocr-notice span {
  font-size: 12px;
  color: var(--text-secondary);
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

/* Shortcuts Section */
.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
}

.shortcut-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.shortcut-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.shortcut-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.shortcut-keys {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.shortcut-key {
  padding: 4px 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  font-family: var(--font-mono);
  color: var(--text-secondary);
}

.shortcut-edit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.shortcut-edit-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
  color: var(--text-primary);
}

/* Shortcut Editor Modal */
.shortcut-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease;
}

.shortcut-modal {
  background: var(--bg-primary);
  border-radius: 12px;
  width: 420px;
  max-width: 90vw;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  animation: modalSlideUp 0.2s ease;
}

.shortcut-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.shortcut-modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.shortcut-modal-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.shortcut-modal-close:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.shortcut-modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.shortcut-modal-hint {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: center;
}

.shortcut-capture-area {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  background: rgba(139, 92, 246, 0.08);
  border: 2px dashed rgba(139, 92, 246, 0.3);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  outline: none;
}

.shortcut-capture-area:focus {
  border-color: rgba(139, 92, 246, 0.6);
  background: rgba(139, 92, 246, 0.12);
}

.captured-shortcut {
  font-size: 18px;
  font-weight: 600;
  font-family: var(--font-mono);
  color: #a78bfa;
}

.capture-placeholder {
  font-size: 13px;
  color: var(--text-muted);
}

.current-shortcuts {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.current-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

.current-keys {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.shortcut-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 6px;
  font-size: 13px;
  font-family: var(--font-mono);
  color: var(--text-primary);
}

.remove-shortcut {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 14px;
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.15s ease;
}

.remove-shortcut:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.add-shortcut-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 8px;
  color: #a78bfa;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-shortcut-btn:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.5);
}

.add-shortcut-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.shortcut-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
}

.shortcut-modal-btn {
  padding: 10px 18px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.shortcut-modal-btn.reset {
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--text-muted);
  margin-right: auto;
}

.shortcut-modal-btn.reset:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
}

.shortcut-modal-btn.cancel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.shortcut-modal-btn.cancel:hover {
  background: var(--bg-hover);
}

.shortcut-modal-btn.primary {
  background: var(--gradient-primary);
  border: 1px solid transparent;
  color: white;
}

.shortcut-modal-btn.primary:hover:not(:disabled) {
  filter: brightness(1.1);
}

.shortcut-modal-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Font Settings */
/* UI Scale Settings */
.ui-scale-settings {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  margin-bottom: 20px;
}

.ui-scale-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.ui-scale-header label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.ui-scale-current {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 4px 10px;
  border-radius: 4px;
}

.ui-scale-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.ui-scale-btn {
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.ui-scale-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.ui-scale-btn.active {
  background: var(--gradient-primary);
  border-color: transparent;
  color: white;
}

.font-settings-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 20px;
}

.font-setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.02);
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
  font-size: 12px;
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
  border-color: var(--text-secondary);
}


/* Custom Fonts Section */
.custom-fonts-section {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
}

.custom-fonts-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 14px;
}

.custom-fonts-title {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.custom-fonts-desc {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.add-font-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-font-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.no-custom-fonts {
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
  font-size: 13px;
}

.custom-fonts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.custom-font-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
}

.custom-font-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.custom-font-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.custom-font-categories {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.custom-font-category {
  font-size: 10px;
  color: var(--text-muted);
  padding: 2px 6px;
  background: var(--bg-hover);
  border-radius: 4px;
}

.remove-font-btn {
  padding: 6px;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.remove-font-btn:hover {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

/* Font Modal */
.font-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
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

.font-form-group input,
.font-category-select {
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 14px;
  transition: all 0.15s ease;
}

.font-form-group input:focus,
.font-category-select:focus {
  outline: none;
  border-color: var(--text-secondary);
}

.font-form-group input::placeholder {
  color: var(--text-muted);
}

.font-file-input {
  display: flex;
  gap: 8px;
}

.font-file-input input {
  flex: 1;
  cursor: default;
}

.font-browse-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.font-browse-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.font-modal-btn .loading-spinner.small {
  width: 14px;
  height: 14px;
  border-width: 2px;
  margin-right: 6px;
}

.font-category-select {
  cursor: pointer;
}

.font-category-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.category-checkbox:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
}

.category-checkbox.checked {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
}

.category-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #8b5cf6;
  cursor: pointer;
}

.checkbox-label {
  font-size: 13px;
  color: var(--text-primary);
}

.font-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
}

.font-modal-btn {
  padding: 10px 20px;
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
</style>
