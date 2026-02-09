<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="env-modal-overlay delete-confirm"
      @click.self="emit('close')"
    >
      <div class="env-modal delete-modal">
        <div class="delete-modal-icon">
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <circle
              cx="12"
              cy="12"
              r="10"
            />
            <path d="M12 8v4M12 16h.01" />
          </svg>
        </div>
        <div class="delete-modal-content">
          <h3>{{ t('env.remove') }}</h3>
          <p class="delete-env-name">
            {{ envName }}
          </p>
          <p class="delete-description">
            {{ t('env.removeQuestion') }}<br>
            <span class="delete-note">{{ t('env.removeNote') }}</span>
          </p>
        </div>
        <div class="delete-modal-footer">
          <button
            class="env-modal-btn cancel"
            @click="emit('close')"
          >
            {{ t('common.cancel') }}
          </button>
          <button
            class="env-modal-btn danger"
            @click="emit('confirm')"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
            {{ t('env.removeBtn') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useI18n } from '../../composables';

defineProps<{
  visible: boolean;
  envName: string;
}>();

const emit = defineEmits<{
  'close': [];
  'confirm': [];
}>();

const { t } = useI18n();
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

.env-modal-overlay.delete-confirm {
  backdrop-filter: blur(4px);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.env-modal.delete-modal {
  background: var(--bg-primary);
  border-radius: 12px;
  width: 360px;
  text-align: center;
  padding: 0;
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

.delete-modal-icon {
  padding: 24px 24px 0;
  color: #f59e0b;
}

.delete-modal-icon svg {
  filter: drop-shadow(0 4px 12px rgba(245, 158, 11, 0.3));
}

.delete-modal-content {
  padding: 16px 24px 20px;
}

.delete-modal-content h3 {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.delete-env-name {
  margin: 0 0 12px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--accent);
}

.delete-description {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.delete-note {
  display: inline-block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.delete-modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
  justify-content: center;
}

.delete-modal-footer .env-modal-btn {
  flex: 1;
  max-width: 120px;
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

.env-modal-btn.danger {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  border: 1px solid #dc2626;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.env-modal-btn.danger:hover {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}
</style>
