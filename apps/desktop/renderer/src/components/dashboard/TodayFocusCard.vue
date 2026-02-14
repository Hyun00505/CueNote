<template>
  <div
    v-if="schedules.length > 0 || showEmpty"
    class="today-focus"
    @click="$emit('go-today')"
  >
    <div class="focus-left">
      <div class="focus-date-block">
        <span class="focus-day">{{ todayDay }}</span>
        <div class="focus-date-info">
          <span class="focus-weekday">{{ todayWeekday }}</span>
          <span class="focus-month">{{ todayMonth }}</span>
        </div>
      </div>
      <div class="focus-divider" />
      <div class="focus-summary">
        <div v-if="nextSchedule" class="next-up">
          <span class="next-label">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
            </svg>
            {{ t('calendar.nextUp') || '다음 일정' }}
          </span>
          <span class="next-title">{{ nextSchedule.title }}</span>
          <span v-if="nextSchedule.startTime" class="next-time">{{ nextSchedule.startTime }}{{ nextSchedule.endTime ? ` - ${nextSchedule.endTime}` : '' }}</span>
        </div>
        <div v-else class="all-done">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12" />
          </svg>
          <span>{{ t('calendar.allDoneToday') || '오늘 일정을 모두 완료했어요!' }}</span>
        </div>
      </div>
    </div>
    <div class="focus-right">
      <div class="focus-stats">
        <span class="stat-number">{{ remaining }}</span>
        <span class="stat-label">{{ t('calendar.remaining') || '남음' }}</span>
      </div>
      <div class="focus-progress">
        <svg :width="40" :height="40" viewBox="0 0 40 40">
          <circle cx="20" cy="20" r="16" fill="none" stroke="var(--surface-4)" stroke-width="3" />
          <circle
            cx="20" cy="20" r="16"
            fill="none"
            stroke="url(#progressGrad)"
            stroke-width="3"
            stroke-linecap="round"
            :stroke-dasharray="`${progressCircle} 100.53`"
            :style="{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%', transition: 'stroke-dasharray 0.5s ease' }"
          />
          <defs>
            <linearGradient id="progressGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#22c55e" />
              <stop offset="100%" stop-color="#34d399" />
            </linearGradient>
          </defs>
        </svg>
        <span class="progress-text">{{ progressPercent }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from '../../composables';
import type { ScheduleItem } from '../../types';

const props = defineProps<{
  schedules: ScheduleItem[];
  showEmpty?: boolean;
}>();

defineEmits<{
  'go-today': [];
}>();

const { t } = useI18n();

const today = new Date();
const todayDay = today.getDate();

const weekdayNames = computed(() => {
  const days = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
  return days;
});
const monthNames = ['', '1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];

const todayWeekday = weekdayNames.value[today.getDay()];
const todayMonth = monthNames[today.getMonth() + 1] + ' ' + today.getFullYear();

const completed = computed(() => props.schedules.filter(s => s.completed).length);
const remaining = computed(() => props.schedules.filter(s => !s.completed).length);
const progressPercent = computed(() => {
  if (props.schedules.length === 0) return 0;
  return Math.round((completed.value / props.schedules.length) * 100);
});
const progressCircle = computed(() => {
  return (progressPercent.value / 100) * 100.53; // circumference = 2 * PI * 16
});

const nextSchedule = computed(() => {
  const now = new Date();
  const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  
  // Find next uncompleted schedule
  const upcoming = props.schedules
    .filter(s => !s.completed)
    .sort((a, b) => {
      if (!a.startTime && !b.startTime) return 0;
      if (!a.startTime) return 1;
      if (!b.startTime) return -1;
      return a.startTime.localeCompare(b.startTime);
    });

  // Return first one that hasn't passed, or first uncompleted
  const future = upcoming.find(s => !s.startTime || s.startTime >= currentTime);
  return future || upcoming[0] || null;
});
</script>

<style scoped>
.today-focus {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: linear-gradient(135deg, 
    color-mix(in srgb, #c9a76c 6%, var(--surface-1) 94%) 0%, 
    color-mix(in srgb, #10b981 4%, var(--surface-1) 96%) 100%
  );
  border-bottom: 1px solid var(--surface-3);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  z-index: 1;
  flex-shrink: 0;
}

.today-focus:hover {
  background: linear-gradient(135deg, 
    color-mix(in srgb, #c9a76c 10%, var(--surface-2) 90%) 0%, 
    color-mix(in srgb, #10b981 6%, var(--surface-2) 94%) 100%
  );
}

.focus-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.focus-date-block {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.focus-day {
  font-size: 36px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, #c9a76c 0%, #e8d5b7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.focus-date-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.focus-weekday {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.focus-month {
  font-size: 11px;
  color: var(--text-muted);
}

.focus-divider {
  width: 1px;
  height: 32px;
  background: var(--surface-4);
  flex-shrink: 0;
}

.focus-summary {
  flex: 1;
  min-width: 0;
}

.next-up {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.next-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.next-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.next-time {
  font-size: 12px;
  color: var(--text-muted);
}

.all-done {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #34d399;
  font-size: 13px;
  font-weight: 600;
}

.focus-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.focus-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
}

.stat-number {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 10px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.focus-progress {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-text {
  position: absolute;
  font-size: 10px;
  font-weight: 700;
  color: var(--text-secondary);
}
</style>
