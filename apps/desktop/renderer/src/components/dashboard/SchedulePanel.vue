<template>
  <div class="schedule-panel">
    <div class="panel-header">
      <h3>{{ selectedDateLabel }}</h3>
      <button class="add-schedule-btn" @click="emit('add-schedule')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span>일정 추가</span>
      </button>
    </div>

    <!-- 일정 목록 -->
    <div class="schedule-list" v-if="!loading">
      <div
        v-for="schedule in schedules"
        :key="schedule.id"
        class="schedule-item"
        :class="{ completed: schedule.completed }"
      >
        <div class="schedule-color-dot" :style="{ background: schedule.color }"></div>
        
        <div class="schedule-main" @click="emit('edit-schedule', schedule)">
          <span class="schedule-title">{{ schedule.title }}</span>
          <span class="schedule-time" v-if="schedule.startTime">
            {{ schedule.startTime }}{{ schedule.endTime ? ` ~ ${schedule.endTime}` : '' }}
          </span>
        </div>

        <div class="schedule-actions">
          <button
            class="check-btn"
            @click="emit('toggle-complete', schedule.id)"
            :title="schedule.completed ? '완료 취소' : '완료'"
          >
            <svg v-if="schedule.completed" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="9"/>
            </svg>
          </button>
          <button class="more-btn" @click="emit('delete-schedule', schedule)" title="삭제">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 일정 없음 -->
      <div v-if="schedules.length === 0" class="empty-state">
        <p>{{ t('calendar.noSchedules') }}</p>
        <button class="add-first-btn" @click="emit('add-schedule')">{{ t('calendar.addFirst') }}</button>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-else class="loading-schedules">
      <div class="spinner"></div>
      <span>일정을 불러오는 중...</span>
    </div>

    <!-- 에러 -->
    <div v-if="error" class="error-message">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from '../../composables';
import type { ScheduleItem } from '../../types';

const props = defineProps<{
  schedules: ScheduleItem[];
  selectedDate: string | null;
  loading: boolean;
  error: string | null;
}>();

const emit = defineEmits<{
  'add-schedule': [];
  'edit-schedule': [schedule: ScheduleItem];
  'delete-schedule': [schedule: ScheduleItem];
  'toggle-complete': [id: number];
}>();

const { t } = useI18n();

const weekdays = computed(() => [
  t('days.sun'), t('days.mon'), t('days.tue'), t('days.wed'), 
  t('days.thu'), t('days.fri'), t('days.sat')
]);

const selectedDateLabel = computed(() => {
  if (!props.selectedDate) return '';
  const [year, month, day] = props.selectedDate.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  const dayOfWeek = weekdays.value[date.getDay()];
  return `${month}월 ${day}일 (${dayOfWeek})`;
});
</script>

<style scoped>
.schedule-panel {
  border-left: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.01);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.panel-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.add-schedule-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 12px;
  background: rgba(201, 167, 108, 0.12);
  border: 1px solid rgba(201, 167, 108, 0.25);
  border-radius: 7px;
  color: #e8d5b7;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-schedule-btn:hover {
  background: rgba(201, 167, 108, 0.2);
  border-color: rgba(201, 167, 108, 0.35);
}

.schedule-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

.schedule-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.12s ease;
}

.schedule-item:last-child {
  border-bottom: none;
}

.schedule-item:hover {
  background: rgba(255, 255, 255, 0.02);
  margin: 0 -16px;
  padding: 14px 16px;
  border-radius: 8px;
}

.schedule-item.completed .schedule-title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.schedule-color-dot {
  width: 4px;
  height: 32px;
  border-radius: 2px;
  flex-shrink: 0;
}

.schedule-main {
  flex: 1;
  min-width: 0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.schedule-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.schedule-time {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 400;
}

.schedule-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.schedule-item:hover .schedule-actions {
  opacity: 1;
}

.check-btn,
.more-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.12s ease;
}

.check-btn:hover {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.more-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.schedule-item.completed .check-btn {
  color: #22c55e;
  opacity: 1;
}

.schedule-item.completed .schedule-actions {
  opacity: 1;
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
  text-align: center;
}

.empty-state p {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 16px;
  font-weight: 400;
}

.add-first-btn {
  padding: 10px 20px;
  background: transparent;
  border: 1px dashed var(--border-default);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.add-first-btn:hover {
  background: rgba(201, 167, 108, 0.08);
  border-color: rgba(201, 167, 108, 0.4);
  color: #c9a76c;
}

/* Loading */
.loading-schedules {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 20px;
  color: var(--text-muted);
  font-size: 13px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(201, 167, 108, 0.2);
  border-top-color: #c9a76c;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error */
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  margin: 14px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: #ef4444;
  font-size: 12px;
}

/* Light theme */
:global([data-theme="light"]) .schedule-panel {
  background: rgba(0, 0, 0, 0.01);
}

:global([data-theme="light"]) .add-schedule-btn {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.2);
  color: #2563eb;
}

:global([data-theme="light"]) .add-schedule-btn:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.3);
}

:global([data-theme="light"]) .schedule-item {
  border-bottom-color: rgba(0, 0, 0, 0.06);
}

:global([data-theme="light"]) .schedule-item:hover {
  background: rgba(0, 0, 0, 0.02);
}

:global([data-theme="light"]) .schedule-title {
  color: #1f2937;
}

:global([data-theme="light"]) .add-first-btn:hover {
  background: rgba(59, 130, 246, 0.05);
  border-color: rgba(59, 130, 246, 0.3);
  color: #2563eb;
}
</style>
