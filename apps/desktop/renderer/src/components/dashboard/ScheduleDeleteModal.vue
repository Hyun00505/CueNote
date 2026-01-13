<template>
  <div v-if="visible" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content delete-confirm">
      <div class="modal-header">
        <h3>{{ t('schedule.deleteConfirm') }}</h3>
      </div>
      <div class="modal-body">
        <p>{{ t('schedule.deleteQuestion') }}</p>
        <p class="delete-schedule-name">{{ scheduleName }}</p>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="emit('close')">{{ t('common.cancel') }}</button>
        <button class="delete-confirm-btn" @click="emit('confirm')">{{ t('common.delete') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from '../../composables';

defineProps<{
  visible: boolean;
  scheduleName: string;
}>();

const emit = defineEmits<{
  'close': [];
  'confirm': [];
}>();

const { t } = useI18n();
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
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

.modal-content {
  width: 340px;
  max-width: 90vw;
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: 14px;
  overflow: hidden;
  animation: modalIn 0.2s ease;
}

@keyframes modalIn {
  from { 
    opacity: 0;
    transform: scale(0.96) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  padding: 16px 22px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.modal-body {
  padding: 22px;
  text-align: center;
}

.modal-body p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.delete-schedule-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 8px !important;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 22px;
  border-top: 1px solid var(--border-subtle);
}

.cancel-btn,
.delete-confirm-btn {
  padding: 9px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--border-default);
}

.delete-confirm-btn {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.delete-confirm-btn:hover {
  background: rgba(239, 68, 68, 0.3);
}

/* Light theme */
:global([data-theme="light"]) .modal-content {
  background: #ffffff;
  border-color: rgba(0, 0, 0, 0.1);
}

:global([data-theme="light"]) .delete-confirm-btn {
  background: rgba(220, 38, 38, 0.1);
  border-color: rgba(220, 38, 38, 0.2);
  color: #dc2626;
}

:global([data-theme="light"]) .delete-confirm-btn:hover {
  background: rgba(220, 38, 38, 0.18);
}
</style>
