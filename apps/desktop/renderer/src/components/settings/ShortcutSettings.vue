<template>
  <div id="section-shortcuts" class="settings-category">
    <h2 class="category-title">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="2" y="4" width="20" height="16" rx="2" />
        <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M6 16h8" />
      </svg>
      {{ t('shortcuts.title') }}
    </h2>

    <section class="settings-section">
      <h3 class="section-title">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="2" y="4" width="20" height="16" rx="2" />
          <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M6 16h8" />
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
            <span v-for="(shortcut, index) in shortcuts.aiMenu" :key="index" class="shortcut-key">
              {{ formatShortcut(shortcut) }}
            </span>
          </div>
          <button class="shortcut-edit-btn" @click="openShortcutEditor('aiMenu')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
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
                <path d="M18 6L6 18M6 6l12 12" />
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
                <span v-for="(shortcut, index) in editingShortcuts" :key="index" class="shortcut-tag">
                  {{ formatShortcut(shortcut) }}
                  <button class="remove-shortcut" @click="removeEditingShortcut(index)">×</button>
                </span>
              </div>
            </div>

            <button class="add-shortcut-btn" @click="addCapturedShortcut" :disabled="!capturedShortcut">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
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
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { useI18n, useShortcuts, formatShortcut } from '../../composables';
import type { ShortcutConfig } from '../../composables/useShortcuts';

const { t } = useI18n();

const {
  shortcuts,
  updateAIMenuShortcuts,
  getDefaultShortcuts,
  eventToShortcut,
} = useShortcuts();

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
  background: var(--surface-1);
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
  background: var(--overlay-bg);
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
</style>
