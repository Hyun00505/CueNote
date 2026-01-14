<template>
  <div class="schedule-panel">
    <!-- 패널 배경 장식 -->
    <div class="panel-decoration">
      <div class="deco-gradient"></div>
    </div>

    <!-- 헤더 -->
    <div class="panel-header">
      <div class="date-display">
        <div class="date-badge" :class="{ 'is-today': isToday }">
          <span class="date-day">{{ selectedDay }}</span>
          <div class="date-info">
            <span class="date-month">{{ selectedMonthStr }}</span>
            <span class="date-weekday">{{ selectedWeekday }}</span>
          </div>
        </div>
        <div v-if="isToday" class="today-indicator">
          <span class="today-dot"></span>
          {{ t('common.today') || '오늘' }}
        </div>
      </div>
      
      <div class="header-actions">
        <button 
          class="header-btn ai-btn" 
          @click="emit('ai-extract')" 
          :title="t('calendar.aiExtract')"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H6a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 8 6a4 4 0 0 1 4-4z"/>
          </svg>
        </button>
        <button 
          class="header-btn today-btn-icon" 
          @click="emit('go-today')" 
          :title="t('common.today')"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </button>
        <button class="header-btn add-btn" @click="emit('add-schedule')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 일정 카운트 바 -->
    <div class="schedule-stats" v-if="schedules.length > 0">
      <div class="stat-item">
        <span class="stat-count">{{ schedules.length }}</span>
        <span class="stat-label">{{ t('calendar.total') || '전체' }}</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item completed">
        <span class="stat-count">{{ completedCount }}</span>
        <span class="stat-label">{{ t('calendar.completed') || '완료' }}</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item pending">
        <span class="stat-count">{{ schedules.length - completedCount }}</span>
        <span class="stat-label">{{ t('calendar.remaining') || '남음' }}</span>
      </div>
      <!-- 진행률 바 -->
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>
    </div>

    <!-- 일정 목록 -->
    <div class="schedule-list" v-if="!loading">
      <TransitionGroup name="schedule-list">
        <div
          v-for="(schedule, index) in schedules"
          :key="schedule.id"
          class="schedule-card"
          :class="{ 'is-completed': schedule.completed }"
          :style="{ '--index': index, '--card-color': schedule.color || '#c9a76c' }"
        >
          <button
            class="check-button"
            @click="emit('toggle-complete', schedule.id)"
            :class="{ checked: schedule.completed }"
          >
            <svg v-if="schedule.completed" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </button>

          <div class="card-content" @click="emit('edit-schedule', schedule)">
            <span class="card-title">{{ schedule.title }}</span>
            <div class="card-meta" v-if="schedule.startTime || schedule.description">
              <span class="card-time" v-if="schedule.startTime">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                {{ schedule.startTime }}{{ schedule.endTime ? ` - ${schedule.endTime}` : '' }}
              </span>
            </div>
          </div>

          <button 
            class="delete-button" 
            @click="emit('delete-schedule', schedule)"
            :title="t('common.delete') || '삭제'"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
            </svg>
          </button>
        </div>
      </TransitionGroup>

      <!-- 빈 상태 -->
      <div v-if="schedules.length === 0" class="empty-state">
        <div class="empty-illustration">
          <svg width="80" height="80" viewBox="0 0 100 100" fill="none">
            <circle cx="50" cy="50" r="45" stroke="currentColor" stroke-width="2" stroke-dasharray="8 4" opacity="0.2"/>
            <circle cx="50" cy="50" r="30" stroke="currentColor" stroke-width="2" stroke-dasharray="6 3" opacity="0.15"/>
            <path d="M35 50h30M50 35v30" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity="0.3"/>
          </svg>
        </div>
        <p class="empty-title">{{ t('calendar.noSchedules') || '일정이 없습니다' }}</p>
        <p class="empty-subtitle">{{ t('calendar.addScheduleHint') || '새로운 일정을 추가해보세요' }}</p>
        <button class="empty-add-btn" @click="emit('add-schedule')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          {{ t('calendar.addFirst') || '일정 추가하기' }}
        </button>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-else class="loading-state">
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
      </div>
      <span>{{ t('calendar.loading') || '불러오는 중...' }}</span>
    </div>

    <!-- 에러 -->
    <Transition name="error-fade">
      <div v-if="error" class="error-banner">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>{{ error }}</span>
      </div>
    </Transition>
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
  'ai-extract': [];
  'go-today': [];
}>();

const { t } = useI18n();

const weekdays = computed(() => [
  t('days.sun'), t('days.mon'), t('days.tue'), t('days.wed'), 
  t('days.thu'), t('days.fri'), t('days.sat')
]);

const months = computed(() => [
  '', t('months.jan') || '1월', t('months.feb') || '2월', t('months.mar') || '3월',
  t('months.apr') || '4월', t('months.may') || '5월', t('months.jun') || '6월',
  t('months.jul') || '7월', t('months.aug') || '8월', t('months.sep') || '9월',
  t('months.oct') || '10월', t('months.nov') || '11월', t('months.dec') || '12월'
]);

const parsedDate = computed(() => {
  if (!props.selectedDate) return null;
  const [year, month, day] = props.selectedDate.split('-').map(Number);
  return new Date(year, month - 1, day);
});

const selectedDay = computed(() => parsedDate.value?.getDate() || '');
const selectedMonthStr = computed(() => {
  if (!parsedDate.value) return '';
  return months.value[parsedDate.value.getMonth() + 1];
});
const selectedWeekday = computed(() => {
  if (!parsedDate.value) return '';
  return weekdays.value[parsedDate.value.getDay()];
});

const isToday = computed(() => {
  if (!parsedDate.value) return false;
  const today = new Date();
  return (
    parsedDate.value.getDate() === today.getDate() &&
    parsedDate.value.getMonth() === today.getMonth() &&
    parsedDate.value.getFullYear() === today.getFullYear()
  );
});

const completedCount = computed(() => 
  props.schedules.filter(s => s.completed).length
);

const progressPercent = computed(() => {
  if (props.schedules.length === 0) return 0;
  return Math.round((completedCount.value / props.schedules.length) * 100);
});
</script>

<style scoped>
.schedule-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.02) 0%, transparent 100%);
  border-left: 1px solid rgba(255, 255, 255, 0.06);
}

/* 배경 장식 */
.panel-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  pointer-events: none;
  overflow: hidden;
}

.deco-gradient {
  position: absolute;
  top: -100px;
  right: -50px;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(201, 167, 108, 0.08) 0%, transparent 70%);
  border-radius: 50%;
}

/* 헤더 */
.panel-header {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px 20px 16px;
  z-index: 1;
}

.date-display {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.date-badge {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-day {
  font-size: 42px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: -0.03em;
}

.date-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.date-month {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.date-weekday {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

.date-badge.is-today .date-day {
  background: linear-gradient(135deg, #c9a76c 0%, #e8d5b7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.today-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #c9a76c;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.today-dot {
  width: 6px;
  height: 6px;
  background: #c9a76c;
  border-radius: 50%;
  animation: todayPulse 2s ease-in-out infinite;
}

@keyframes todayPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.3); }
}

/* 헤더 버튼들 */
.header-actions {
  display: flex;
  gap: 8px;
}

.header-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  color: var(--text-primary);
  transform: translateY(-2px);
}

.header-btn.ai-btn {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.header-btn.ai-btn:hover {
  background: rgba(16, 185, 129, 0.18);
  border-color: rgba(16, 185, 129, 0.35);
}

.header-btn.today-btn-icon {
  background: rgba(201, 167, 108, 0.1);
  border-color: rgba(201, 167, 108, 0.2);
  color: #c9a76c;
}

.header-btn.today-btn-icon:hover {
  background: rgba(201, 167, 108, 0.18);
  border-color: rgba(201, 167, 108, 0.35);
}

.header-btn.add-btn {
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.2) 0%, rgba(201, 167, 108, 0.1) 100%);
  border-color: rgba(201, 167, 108, 0.3);
  color: #e8d5b7;
}

.header-btn.add-btn:hover {
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.3) 0%, rgba(201, 167, 108, 0.15) 100%);
  border-color: rgba(201, 167, 108, 0.5);
}

/* 통계 바 */
.schedule-stats {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 20px;
  margin: 0 16px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  z-index: 1;
}

.stat-item {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.stat-count {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.stat-item.completed .stat-count {
  color: #34d399;
}

.stat-item.pending .stat-count {
  color: #fbbf24;
}

.stat-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.08);
}

.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 0 0 12px 12px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #34d399);
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 일정 목록 */
.schedule-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 16px 16px;
  z-index: 1;
}

/* 일정 카드 */
.schedule-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  margin-bottom: 10px;
  background: linear-gradient(
    135deg, 
    color-mix(in srgb, var(--card-color) 8%, rgba(30, 30, 35, 0.9) 92%) 0%, 
    color-mix(in srgb, var(--card-color) 4%, rgba(25, 25, 30, 0.85) 96%) 100%
  );
  border: 1px solid color-mix(in srgb, var(--card-color) 15%, transparent 85%);
  border-radius: 14px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  animation: cardSlideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) backwards;
  animation-delay: calc(var(--index) * 0.05s);
}

@keyframes cardSlideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.schedule-card:hover {
  background: linear-gradient(
    135deg, 
    color-mix(in srgb, var(--card-color) 14%, rgba(35, 35, 40, 0.95) 86%) 0%, 
    color-mix(in srgb, var(--card-color) 8%, rgba(30, 30, 35, 0.9) 92%) 100%
  );
  border-color: color-mix(in srgb, var(--card-color) 25%, transparent 75%);
  transform: translateX(4px);
  box-shadow: 0 4px 20px color-mix(in srgb, var(--card-color) 15%, transparent 85%);
}

.schedule-card:last-child {
  margin-bottom: 0;
}

.schedule-card.is-completed {
  opacity: 0.6;
}

.schedule-card.is-completed:hover {
  opacity: 0.8;
}


/* 체크 버튼 */
.check-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: color-mix(in srgb, var(--card-color) 10%, transparent 90%);
  border: 2px solid color-mix(in srgb, var(--card-color) 30%, transparent 70%);
  border-radius: 8px;
  color: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.check-button:hover {
  border-color: var(--card-color);
  background: color-mix(in srgb, var(--card-color) 20%, transparent 80%);
}

.check-button.checked {
  background: var(--card-color);
  border-color: var(--card-color);
  color: white;
}

/* 카드 콘텐츠 */
.card-content {
  flex: 1;
  min-width: 0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
  transition: color 0.2s ease;
}

.schedule-card.is-completed .card-title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-time {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
}

.card-time svg {
  opacity: 0.6;
}

/* 삭제 버튼 */
.delete-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
}

.schedule-card:hover .delete-button {
  opacity: 1;
}

.delete-button:hover {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

/* 빈 상태 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.empty-illustration {
  color: var(--text-muted);
  margin-bottom: 20px;
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 6px;
}

.empty-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 24px;
}

.empty-add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.15) 0%, rgba(201, 167, 108, 0.08) 100%);
  border: 1px solid rgba(201, 167, 108, 0.25);
  border-radius: 12px;
  color: #c9a76c;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.25s ease;
}

.empty-add-btn:hover {
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.25) 0%, rgba(201, 167, 108, 0.12) 100%);
  border-color: rgba(201, 167, 108, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(201, 167, 108, 0.15);
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 48px 24px;
  color: var(--text-muted);
  font-size: 13px;
}

.loading-spinner {
  position: relative;
  width: 40px;
  height: 40px;
}

.spinner-ring {
  position: absolute;
  inset: 0;
  border: 2px solid transparent;
  border-radius: 50%;
}

.spinner-ring:nth-child(1) {
  border-top-color: #c9a76c;
  animation: spin 1s linear infinite;
}

.spinner-ring:nth-child(2) {
  inset: 4px;
  border-right-color: rgba(201, 167, 108, 0.5);
  animation: spin 1.5s linear infinite reverse;
}

.spinner-ring:nth-child(3) {
  inset: 8px;
  border-bottom-color: rgba(201, 167, 108, 0.3);
  animation: spin 2s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 에러 배너 */
.error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  margin: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 12px;
  color: #ef4444;
  font-size: 13px;
}

.error-fade-enter-active,
.error-fade-leave-active {
  transition: all 0.3s ease;
}

.error-fade-enter-from,
.error-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 리스트 트랜지션 */
.schedule-list-enter-active {
  transition: all 0.3s ease;
}

.schedule-list-leave-active {
  transition: all 0.2s ease;
}

.schedule-list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.schedule-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.schedule-list-move {
  transition: transform 0.3s ease;
}

/* ======== Light Theme ======== */
:global([data-theme="light"]) .schedule-panel {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.6) 100%);
  border-left-color: rgba(0, 0, 0, 0.06);
}

:global([data-theme="light"]) .deco-gradient {
  background: radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, transparent 70%);
}

:global([data-theme="light"]) .date-badge.is-today .date-day {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  background-clip: text;
}

:global([data-theme="light"]) .today-indicator {
  color: #2563eb;
}

:global([data-theme="light"]) .today-dot {
  background: #2563eb;
}

:global([data-theme="light"]) .header-btn {
  background: rgba(0, 0, 0, 0.03);
  border-color: rgba(0, 0, 0, 0.08);
  color: #4b5563;
}

:global([data-theme="light"]) .header-btn:hover {
  background: rgba(0, 0, 0, 0.06);
  border-color: rgba(0, 0, 0, 0.12);
  color: #1f2937;
}

:global([data-theme="light"]) .header-btn.ai-btn {
  background: rgba(16, 185, 129, 0.08);
  border-color: rgba(16, 185, 129, 0.2);
  color: #059669;
}

:global([data-theme="light"]) .header-btn.today-btn-icon {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.2);
  color: #2563eb;
}

:global([data-theme="light"]) .header-btn.add-btn {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(59, 130, 246, 0.06) 100%);
  border-color: rgba(59, 130, 246, 0.25);
  color: #2563eb;
}

:global([data-theme="light"]) .schedule-stats {
  background: rgba(255, 255, 255, 0.8);
  border-color: rgba(0, 0, 0, 0.06);
}

:global([data-theme="light"]) .stat-divider {
  background: rgba(0, 0, 0, 0.08);
}

:global([data-theme="light"]) .progress-bar {
  background: rgba(0, 0, 0, 0.06);
}

:global([data-theme="light"]) .schedule-card {
  background: linear-gradient(
    135deg, 
    color-mix(in srgb, var(--card-color) 6%, rgba(255, 255, 255, 0.95) 94%) 0%, 
    color-mix(in srgb, var(--card-color) 3%, rgba(250, 250, 252, 0.9) 97%) 100%
  );
  border-color: color-mix(in srgb, var(--card-color) 12%, rgba(0, 0, 0, 0.06) 88%);
}

:global([data-theme="light"]) .schedule-card:hover {
  background: linear-gradient(
    135deg, 
    color-mix(in srgb, var(--card-color) 10%, rgba(255, 255, 255, 1) 90%) 0%, 
    color-mix(in srgb, var(--card-color) 6%, rgba(255, 255, 255, 0.95) 94%) 100%
  );
  border-color: color-mix(in srgb, var(--card-color) 20%, transparent 80%);
  box-shadow: 0 4px 16px color-mix(in srgb, var(--card-color) 12%, transparent 88%);
}

:global([data-theme="light"]) .check-button {
  background: color-mix(in srgb, var(--card-color) 8%, transparent 92%);
  border-color: color-mix(in srgb, var(--card-color) 25%, transparent 75%);
}

:global([data-theme="light"]) .card-title {
  color: #1f2937;
}

:global([data-theme="light"]) .empty-add-btn {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
  border-color: rgba(59, 130, 246, 0.25);
  color: #2563eb;
}

:global([data-theme="light"]) .empty-add-btn:hover {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.08) 100%);
  border-color: rgba(59, 130, 246, 0.35);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.12);
}

:global([data-theme="light"]) .spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
}

:global([data-theme="light"]) .spinner-ring:nth-child(2) {
  border-right-color: rgba(59, 130, 246, 0.5);
}

:global([data-theme="light"]) .spinner-ring:nth-child(3) {
  border-bottom-color: rgba(59, 130, 246, 0.3);
}
</style>
