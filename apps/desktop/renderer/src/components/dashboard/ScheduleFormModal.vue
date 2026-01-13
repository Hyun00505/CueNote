<template>
  <div v-if="visible" class="modal-overlay" @click.self="emit('close')">
    <div class="schedule-modal">
      <div class="schedule-modal-header">
        <span class="modal-title">{{ isEdit ? t('schedule.edit') : t('schedule.new') }}</span>
        <button class="modal-close" @click="emit('close')">×</button>
      </div>

      <div class="schedule-modal-body">
        <div class="input-field title-field">
          <input
            type="text"
            v-model="form.title"
            :placeholder="t('schedule.titlePlaceholder')"
            autofocus
          />
        </div>

        <div class="input-row">
          <div class="input-field date-field">
            <label>📅 {{ t('schedule.date') }}</label>
            <input type="date" v-model="form.date" />
          </div>
        </div>

        <div class="input-row time-row">
          <div class="input-field">
            <label>🕐 {{ t('schedule.startTime') }}</label>
            <input type="time" v-model="form.startTime" placeholder="--:--" />
          </div>
          <span class="time-divider">~</span>
          <div class="input-field">
            <label>🕐 {{ t('schedule.endTime') }}</label>
            <input type="time" v-model="form.endTime" placeholder="--:--" />
          </div>
        </div>

        <div class="input-field memo-field">
          <label>📝 {{ t('schedule.memo') }}</label>
          <textarea
            v-model="form.description"
            :placeholder="t('schedule.memoPlaceholder')"
            rows="2"
          ></textarea>
        </div>

        <div class="color-field">
          <label>{{ t('schedule.labelColor') }}</label>
          <div class="color-options">
            <button
              v-for="color in colorOptions"
              :key="color"
              class="color-dot"
              :class="{ active: form.color === color }"
              :style="{ background: color }"
              @click="form.color = color"
            ></button>
          </div>
        </div>
      </div>

      <div class="schedule-modal-footer">
        <button class="btn-cancel" @click="emit('close')">{{ t('common.cancel') }}</button>
        <button
          class="btn-save"
          :disabled="!form.title.trim()"
          @click="handleSave"
        >
          {{ isEdit ? t('common.edit') : t('common.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from '../../composables';
import type { ScheduleItem } from '../../types';

const props = defineProps<{
  visible: boolean;
  editingSchedule: ScheduleItem | null;
  selectedDate: string | null;
}>();

const emit = defineEmits<{
  'close': [];
  'save': [data: { title: string; description: string; date: string; startTime: string; endTime: string; color: string }];
}>();

const { t } = useI18n();

const colorOptions = [
  '#c9a76c', '#22c55e', '#3b82f6', '#8b5cf6',
  '#ec4899', '#f59e0b', '#ef4444', '#6b7280',
];

const isEdit = ref(false);

const form = ref({
  title: '',
  description: '',
  date: '',
  startTime: '',
  endTime: '',
  color: '#c9a76c',
});

watch(() => props.visible, (newVal) => {
  if (newVal) {
    if (props.editingSchedule) {
      isEdit.value = true;
      form.value = {
        title: props.editingSchedule.title,
        description: props.editingSchedule.description,
        date: props.editingSchedule.date,
        startTime: props.editingSchedule.startTime,
        endTime: props.editingSchedule.endTime,
        color: props.editingSchedule.color,
      };
    } else {
      isEdit.value = false;
      let defaultDate = props.selectedDate;
      if (!defaultDate) {
        const today = new Date();
        defaultDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
      }
      form.value = {
        title: '',
        description: '',
        date: defaultDate,
        startTime: '',
        endTime: '',
        color: '#c9a76c',
      };
    }
  }
});

function handleSave() {
  if (!form.value.title.trim()) return;
  emit('save', { ...form.value });
}
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

.schedule-modal {
  width: 380px;
  max-width: 90vw;
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: 16px;
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

.schedule-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.modal-close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  font-size: 20px;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.12s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-primary);
}

.schedule-modal-body {
  padding: 20px;
}

.input-field {
  margin-bottom: 16px;
}

.input-field label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.title-field input {
  width: 100%;
  padding: 14px 0;
  background: none;
  border: none;
  border-bottom: 2px solid var(--border-subtle);
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 500;
  font-family: inherit;
  letter-spacing: -0.02em;
  transition: border-color 0.15s ease;
}

.title-field input:focus {
  outline: none;
  border-bottom-color: #c9a76c;
}

.title-field input::placeholder {
  color: var(--text-muted);
  font-weight: 400;
}

.input-row {
  display: flex;
  gap: 12px;
}

.date-field {
  flex: 1;
}

.date-field input,
.time-row .input-field input {
  width: 100%;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  transition: all 0.12s ease;
}

.date-field input:focus,
.time-row .input-field input:focus {
  outline: none;
  border-color: rgba(201, 167, 108, 0.5);
  background: rgba(255, 255, 255, 0.05);
}

.time-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  margin-bottom: 16px;
}

.time-row .input-field {
  flex: 1;
  margin-bottom: 0;
}

.time-divider {
  color: var(--text-muted);
  padding-bottom: 12px;
  font-size: 14px;
}

.memo-field textarea {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  resize: none;
  transition: all 0.12s ease;
  line-height: 1.5;
}

.memo-field textarea:focus {
  outline: none;
  border-color: rgba(201, 167, 108, 0.5);
  background: rgba(255, 255, 255, 0.05);
}

.memo-field textarea::placeholder {
  color: var(--text-muted);
}

.color-field {
  margin-top: 4px;
}

.color-field label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.color-options {
  display: flex;
  gap: 8px;
}

.color-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.12s ease;
}

.color-dot:hover {
  transform: scale(1.15);
}

.color-dot.active {
  border-color: white;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.15);
}

.schedule-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.01);
}

.btn-cancel,
.btn-save {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.12s ease;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: var(--border-default);
}

.btn-save {
  background: #c9a76c;
  border: none;
  color: #1a1a1a;
}

.btn-save:hover:not(:disabled) {
  background: #d4b67d;
}

.btn-save:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Light theme */
:global([data-theme="light"]) .schedule-modal {
  background: #ffffff;
  border-color: rgba(0, 0, 0, 0.1);
}

:global([data-theme="light"]) .title-field input {
  color: #1f2937;
  border-bottom-color: rgba(0, 0, 0, 0.1);
}

:global([data-theme="light"]) .title-field input:focus {
  border-bottom-color: #3b82f6;
}

:global([data-theme="light"]) .date-field input,
:global([data-theme="light"]) .time-row .input-field input,
:global([data-theme="light"]) .memo-field textarea {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.1);
  color: #1f2937;
}

:global([data-theme="light"]) .date-field input:focus,
:global([data-theme="light"]) .time-row .input-field input:focus,
:global([data-theme="light"]) .memo-field textarea:focus {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.02);
}

:global([data-theme="light"]) .btn-save {
  background: #3b82f6;
  color: #ffffff;
}

:global([data-theme="light"]) .btn-save:hover:not(:disabled) {
  background: #2563eb;
}
</style>
