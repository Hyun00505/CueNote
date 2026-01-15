<template>
  <Teleport to="body">
    <div v-if="visible" class="disconnect-modal-overlay" @click.self="emit('close')">
      <div class="disconnect-modal">
        <div class="disconnect-modal-icon">
          <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
          </svg>
        </div>
        <div class="disconnect-modal-content">
          <h3>{{ t('github.disconnect') }}</h3>
          <p class="disconnect-repo-name">{{ repoName }}</p>
          <p class="disconnect-description">{{ t('github.disconnectQuestion') }}</p>
          <div class="disconnect-warning">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <span>{{ t('github.disconnectWarning') }}</span>
          </div>
        </div>
        <div class="disconnect-modal-footer">
          <button class="disconnect-btn cancel" @click="emit('close')">{{ t('common.cancel') }}</button>
          <button class="disconnect-btn confirm" @click="emit('confirm')">{{ t('github.disconnectBtn') }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useI18n } from '../../composables';

defineProps<{
  visible: boolean;
  repoName: string;
}>();

const emit = defineEmits<{
  'close': [];
  'confirm': [];
}>();

const { t } = useI18n();
</script>

<style scoped>
.disconnect-modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.disconnect-modal {
  background: var(--bg-primary);
  border-radius: 16px;
  width: 380px;
  text-align: center;
  padding: 0;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.35);
  border: 1px solid var(--border-subtle);
  animation: modalSlideUp 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(24px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.disconnect-modal-icon {
  padding: 28px 24px 8px;
  color: #8b5cf6;
}

.disconnect-modal-icon svg {
  filter: drop-shadow(0 6px 16px rgba(139, 92, 246, 0.35));
}

.disconnect-modal-content {
  padding: 12px 28px 24px;
}

.disconnect-modal-content h3 {
  margin: 0 0 16px;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.disconnect-repo-name {
  margin: 0 0 16px;
  padding: 10px 16px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #8b5cf6;
}

.disconnect-description {
  margin: 0 0 16px;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.disconnect-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  font-size: 13px;
  color: #ef4444;
}

.disconnect-warning svg {
  flex-shrink: 0;
}

.disconnect-modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 28px;
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
  border-radius: 0 0 16px 16px;
}

.disconnect-btn {
  flex: 1;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.disconnect-btn.cancel {
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.disconnect-btn.cancel:hover {
  background: var(--bg-hover);
  border-color: var(--border-primary);
}

.disconnect-btn.confirm {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  border: 1px solid #dc2626;
  color: white;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
}

.disconnect-btn.confirm:hover {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
  transform: translateY(-1px);
}

.disconnect-btn.confirm:active {
  transform: translateY(0);
}
</style>
