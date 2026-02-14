<template>
  <Teleport to="body">
    <div
      v-if="visible && schedule"
      class="popover-overlay"
      @click.self="$emit('close')"
    >
      <div
        class="schedule-popover"
        :style="positionStyle"
      >
        <div class="popover-arrow" />
        
        <div class="popover-header">
          <div
            class="popover-color-bar"
            :style="{ background: schedule.color || '#c9a76c' }"
          />
          <div class="popover-title-area">
            <h4 class="popover-title" :class="{ completed: schedule.completed }">
              {{ schedule.title }}
            </h4>
            <div v-if="schedule.startTime" class="popover-time">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
              </svg>
              {{ schedule.startTime }}{{ schedule.endTime ? ` - ${schedule.endTime}` : '' }}
            </div>
            <div v-if="schedule.date" class="popover-date">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" />
                <line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
              </svg>
              {{ schedule.date }}
            </div>
          </div>
        </div>
        
        <div v-if="schedule.description" class="popover-description">
          {{ schedule.description }}
        </div>

        <div class="popover-actions">
          <button
            class="action-btn complete-btn"
            :class="{ 'is-completed': schedule.completed }"
            @click="$emit('toggle-complete', schedule.id)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            {{ schedule.completed ? (t('calendar.completed') || '완료됨') : (t('calendar.markComplete') || '완료') }}
          </button>
          <button
            class="action-btn edit-btn"
            @click="$emit('edit', schedule)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
            {{ t('common.edit') || '수정' }}
          </button>
          <button
            class="action-btn delete-btn"
            @click="$emit('delete', schedule)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
            </svg>
            {{ t('common.delete') || '삭제' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from '../../composables';
import type { ScheduleItem } from '../../types';

const props = defineProps<{
  visible: boolean;
  schedule: ScheduleItem | null;
  anchorRect?: { top: number; left: number; width: number; height: number } | null;
}>();

defineEmits<{
  'close': [];
  'edit': [schedule: ScheduleItem];
  'delete': [schedule: ScheduleItem];
  'toggle-complete': [id: string];
}>();

const { t } = useI18n();

const positionStyle = computed(() => {
  if (!props.anchorRect) return {};
  const rect = props.anchorRect;
  return {
    top: `${rect.top + rect.height + 8}px`,
    left: `${Math.max(8, rect.left)}px`,
  };
});
</script>

<style scoped>
.popover-overlay {
  position: fixed;
  inset: 0;
  z-index: 999;
}

.schedule-popover {
  position: fixed;
  width: 280px;
  background: var(--bg-primary);
  border: 1px solid var(--surface-4);
  border-radius: 14px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25), 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  animation: popoverIn 0.15s ease;
  z-index: 1000;
}

@keyframes popoverIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-4px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.popover-header {
  display: flex;
  gap: 12px;
  padding: 16px 16px 12px;
}

.popover-color-bar {
  width: 4px;
  border-radius: 2px;
  flex-shrink: 0;
  align-self: stretch;
}

.popover-title-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.popover-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
}

.popover-title.completed {
  text-decoration: line-through;
  color: var(--text-muted);
}

.popover-time,
.popover-date {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
}

.popover-time svg,
.popover-date svg {
  opacity: 0.6;
}

.popover-description {
  padding: 0 16px 12px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  border-bottom: 1px solid var(--surface-3);
}

.popover-actions {
  display: flex;
  padding: 8px;
  gap: 4px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 8px 4px;
  background: none;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  font-family: inherit;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn:hover {
  background: var(--surface-3);
  color: var(--text-primary);
}

.complete-btn:hover,
.complete-btn.is-completed {
  color: #34d399;
  background: rgba(52, 211, 153, 0.1);
}

.edit-btn:hover {
  color: #60a5fa;
  background: rgba(96, 165, 250, 0.1);
}

.delete-btn:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}
</style>
