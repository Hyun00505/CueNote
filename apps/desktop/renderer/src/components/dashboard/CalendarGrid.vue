<template>
  <div class="calendar-scroll" ref="scrollRef">
    <!-- 이전 달 더보기 버튼 -->
    <button class="load-more-btn" @click="emit('load-more', 'up')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="18 15 12 9 6 15"/>
      </svg>
      이전 달 더보기
    </button>

    <!-- 월별 캘린더 -->
    <div
      v-for="monthData in calendarMonths"
      :key="`${monthData.year}-${monthData.month}`"
      class="month-section"
      :ref="el => setMonthRef(el, monthData.year, monthData.month)"
    >
      <div class="month-header">
        <h2>{{ monthData.label }}</h2>
      </div>

      <!-- 요일 헤더 -->
      <div class="weekday-header">
        <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
      </div>

      <!-- 달력 그리드 -->
      <div class="calendar-grid">
        <div
          v-for="day in monthData.days"
          :key="day.dateStr"
          class="calendar-day"
          :class="{
            'other-month': !day.isCurrentMonth,
            'today': day.isToday,
            'selected': day.isSelected,
            'has-schedules': day.scheduleCount > 0,
            'sunday': day.date.getDay() === 0,
            'saturday': day.date.getDay() === 6,
          }"
          @click="emit('select-date', day.dateStr)"
        >
          <span class="day-number">{{ day.day }}</span>
          <div v-if="day.scheduleCount > 0" class="schedule-indicator">
            <span class="schedule-count">{{ day.scheduleCount }}</span>
            <span v-if="day.completedCount > 0" class="completed-badge">
              ✓{{ day.completedCount }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 다음 달 더보기 버튼 -->
    <button class="load-more-btn" @click="emit('load-more', 'down')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 12 15 18 9"/>
      </svg>
      다음 달 더보기
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import { useI18n } from '../../composables';

interface CalendarDay {
  day: number;
  date: Date;
  dateStr: string;
  isCurrentMonth: boolean;
  isToday: boolean;
  isSelected: boolean;
  scheduleCount: number;
  completedCount: number;
}

interface MonthData {
  year: number;
  month: number;
  label: string;
  days: CalendarDay[];
}

const props = defineProps<{
  calendarMonths: MonthData[];
}>();

const emit = defineEmits<{
  'select-date': [dateStr: string];
  'load-more': [direction: 'up' | 'down'];
}>();

const { t } = useI18n();

const scrollRef = ref<HTMLElement | null>(null);
const monthRefs = ref<Record<string, HTMLElement | null>>({});

const weekdays = computed(() => [
  t('days.sun'), t('days.mon'), t('days.tue'), t('days.wed'), 
  t('days.thu'), t('days.fri'), t('days.sat')
]);

function setMonthRef(el: any, year: number, month: number) {
  if (el) {
    monthRefs.value[`${year}-${month}`] = el;
  }
}

function scrollToToday() {
  nextTick(() => {
    const today = new Date();
    const key = `${today.getFullYear()}-${today.getMonth() + 1}`;
    const el = monthRefs.value[key];
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
}

defineExpose({ scrollToToday });
</script>

<style scoped>
.calendar-scroll {
  padding: 20px 32px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.load-more-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed var(--border-subtle);
  border-radius: 10px;
  color: var(--text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.load-more-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-default);
  color: var(--text-secondary);
}

.load-more-btn:last-child {
  margin-bottom: 0;
  margin-top: 20px;
}

.month-section {
  margin-bottom: 32px;
}

.month-section:last-of-type {
  margin-bottom: 0;
}

.month-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.month-header h2 {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 6px;
}

.weekday {
  padding: 8px 0;
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
}

.weekday:first-child {
  color: #ef4444;
}

.weekday:last-child {
  color: #3b82f6;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  aspect-ratio: 1.2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 6px 4px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.calendar-day:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-subtle);
}

.calendar-day.other-month {
  opacity: 0.3;
}

.calendar-day.today {
  background: rgba(201, 167, 108, 0.12);
  border-color: rgba(201, 167, 108, 0.35);
}

.calendar-day.today .day-number {
  color: #c9a76c;
  font-weight: 700;
}

.calendar-day.selected {
  background: rgba(201, 167, 108, 0.22);
  border-color: #c9a76c;
}

.calendar-day.has-schedules {
  background: rgba(255, 255, 255, 0.04);
}

.calendar-day.sunday .day-number {
  color: #ef4444;
}

.calendar-day.saturday .day-number {
  color: #3b82f6;
}

.day-number {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.calendar-day.other-month .day-number {
  color: var(--text-muted);
}

.schedule-indicator {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 9px;
}

.schedule-count {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: rgba(201, 167, 108, 0.3);
  border-radius: 8px;
  color: #e8d5b7;
  font-weight: 600;
}

.completed-badge {
  color: #22c55e;
  font-weight: 600;
}

/* Light Theme */
:global([data-theme="light"]) .calendar-day {
  background: rgba(0, 0, 0, 0.02);
}

:global([data-theme="light"]) .calendar-day:hover {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
}

:global([data-theme="light"]) .calendar-day.today {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.3);
}

:global([data-theme="light"]) .calendar-day.today .day-number {
  color: #2563eb;
}

:global([data-theme="light"]) .calendar-day.selected {
  background: rgba(59, 130, 246, 0.12);
  border-color: #3b82f6;
}

:global([data-theme="light"]) .schedule-count {
  background: rgba(59, 130, 246, 0.15);
  color: #1d4ed8;
}

:global([data-theme="light"]) .load-more-btn {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.1);
  color: #6b7280;
}

:global([data-theme="light"]) .load-more-btn:hover {
  background: rgba(0, 0, 0, 0.04);
  border-color: rgba(0, 0, 0, 0.15);
  color: #374151;
}
</style>
