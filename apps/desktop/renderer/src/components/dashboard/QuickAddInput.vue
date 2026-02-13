<template>
  <div
    v-if="visible"
    class="quick-add-wrapper"
    :style="wrapperStyle"
  >
    <div class="quick-add-input-container">
      <div class="quick-add-dot" />
      <input
        ref="inputRef"
        v-model="title"
        type="text"
        class="quick-add-input"
        :placeholder="placeholder || (t('calendar.quickAdd') || '일정 제목 입력...')"
        @keydown.enter="handleSave"
        @keydown.escape="handleCancel"
        @blur="handleBlur"
      >
      <kbd class="quick-add-hint">↵</kbd>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { useI18n } from '../../composables';

const props = defineProps<{
  visible: boolean;
  date: string;
  startTime?: string;
  placeholder?: string;
  wrapperStyle?: Record<string, string>;
}>();

const emit = defineEmits<{
  'save': [data: { title: string; date: string; startTime: string; endTime: string }];
  'cancel': [];
}>();

const { t } = useI18n();

const title = ref('');
const inputRef = ref<HTMLInputElement | null>(null);

watch(() => props.visible, (val) => {
  if (val) {
    title.value = '';
    nextTick(() => {
      inputRef.value?.focus();
    });
  }
});

function handleSave() {
  if (!title.value.trim()) {
    handleCancel();
    return;
  }
  
  let endTime = '';
  if (props.startTime) {
    // Auto-calculate end time (1 hour later)
    const [h, m] = props.startTime.split(':').map(Number);
    const endH = (h + 1) % 24;
    endTime = `${String(endH).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
  }

  emit('save', {
    title: title.value.trim(),
    date: props.date,
    startTime: props.startTime || '',
    endTime,
  });
  title.value = '';
}

function handleCancel() {
  title.value = '';
  emit('cancel');
}

function handleBlur() {
  // Small delay to allow click events to fire first
  setTimeout(() => {
    if (!title.value.trim()) {
      handleCancel();
    }
  }, 200);
}
</script>

<style scoped>
.quick-add-wrapper {
  animation: quickAddIn 0.15s ease;
}

@keyframes quickAddIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.quick-add-input-container {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--surface-2);
  border: 1px solid rgba(201, 167, 108, 0.3);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.quick-add-dot {
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #c9a76c, #e8d5b7);
  border-radius: 50%;
  flex-shrink: 0;
}

.quick-add-input {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  outline: none;
  min-width: 0;
}

.quick-add-input::placeholder {
  color: var(--text-muted);
}

.quick-add-hint {
  font-size: 10px;
  padding: 2px 6px;
  background: var(--surface-3);
  border: 1px solid var(--surface-4);
  border-radius: 4px;
  color: var(--text-muted);
  font-family: inherit;
  flex-shrink: 0;
}
</style>
