<template>
  <Teleport to="body">
    <div v-if="visible" class="env-modal-overlay" @click.self="emit('close')">
      <div class="env-modal">
        <div class="env-modal-header">
          <h3>새 GitHub 리포지토리</h3>
          <button class="env-modal-close" @click="emit('close')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="env-modal-body">
          <div class="env-form-group">
            <label>리포지토리 이름</label>
            <input 
              v-model="repoName" 
              type="text" 
              placeholder="my-notes"
              @keydown.enter="handleCreate"
            />
          </div>
          <div class="env-form-group">
            <label>설명 (선택)</label>
            <input 
              v-model="repoDescription" 
              type="text" 
              placeholder="나의 마크다운 노트"
            />
          </div>
          <div class="env-form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="repoPrivate" />
              <span>Private 리포지토리로 생성</span>
            </label>
          </div>
          <div class="env-form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="repoInitReadme" />
              <span>README.md 파일 추가</span>
            </label>
          </div>
          <p v-if="error" class="env-error">{{ error }}</p>
        </div>
        <div class="env-modal-footer">
          <button class="env-modal-btn cancel" @click="emit('close')">{{ t('common.cancel') }}</button>
          <button 
            class="env-modal-btn primary" 
            @click="handleCreate" 
            :disabled="!repoName.trim() || creating"
          >
            <span v-if="creating" class="loading-spinner-sm"></span>
            <span v-else>생성하기</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from '../../composables';

const props = defineProps<{
  visible: boolean;
  creating: boolean;
  error: string | null;
}>();

const emit = defineEmits<{
  'close': [];
  'create': [payload: { name: string; description: string; isPrivate: boolean; initReadme: boolean }];
}>();

const { t } = useI18n();

const repoName = ref('');
const repoDescription = ref('');
const repoPrivate = ref(false);
const repoInitReadme = ref(true);

watch(() => props.visible, (newVal) => {
  if (newVal) {
    repoName.value = '';
    repoDescription.value = '';
    repoPrivate.value = false;
    repoInitReadme.value = true;
  }
});

function handleCreate() {
  if (!repoName.value.trim()) return;
  emit('create', {
    name: repoName.value.trim(),
    description: repoDescription.value,
    isPrivate: repoPrivate.value,
    initReadme: repoInitReadme.value
  });
}
</script>

<style scoped>
.env-modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.env-modal {
  background: var(--bg-primary);
  border-radius: 12px;
  width: 420px;
  max-width: 90vw;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  animation: modalSlideUp 0.2s ease;
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

.env-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.env-modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.env-modal-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.env-modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.env-modal-body {
  padding: 24px;
}

.env-form-group {
  margin-bottom: 16px;
}

.env-form-group:last-child {
  margin-bottom: 0;
}

.env-form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.env-form-group input[type="text"] {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.15s ease;
}

.env-form-group input[type="text"]:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--accent-primary);
  cursor: pointer;
}

.env-error {
  margin-top: 12px;
  padding: 10px 12px;
  background: var(--error-glow);
  border: 1px solid var(--error);
  border-radius: 6px;
  color: var(--error);
  font-size: 13px;
}

.env-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
}

.env-modal-btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.env-modal-btn.cancel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.env-modal-btn.cancel:hover {
  background: var(--bg-hover);
}

.env-modal-btn.primary {
  background: var(--accent-primary);
  border: 1px solid var(--accent-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 90px;
}

.env-modal-btn.primary:hover:not(:disabled) {
  filter: brightness(1.1);
}

.env-modal-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border-default);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
