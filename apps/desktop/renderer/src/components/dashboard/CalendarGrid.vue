<template>
  <div class="calendar-container" ref="scrollRef">
    <!-- 배경 장식 -->
    <div class="calendar-bg-decoration">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
    </div>

    <!-- 뷰 모드 컨트롤 헤더 -->
    <div class="view-control-header">
      <!-- 네비게이션 -->
      <div class="nav-controls">
        <button class="nav-btn" @click="navigatePrev" :title="t('calendar.previous')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>
        <button class="nav-btn" @click="navigateNext" :title="t('calendar.next')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
        <button class="today-nav-btn" @click="navigateToday">
          {{ t('common.today') }}
        </button>
      </div>

      <!-- 현재 날짜 표시 -->
      <div class="current-period">
        <h2 class="period-title">{{ currentPeriodLabel }}</h2>
      </div>

      <!-- 뷰 모드 선택 -->
      <div class="view-mode-selector">
        <button v-for="mode in viewModes" :key="mode.value" class="view-mode-btn"
          :class="{ active: viewMode === mode.value }" @click="setViewMode(mode.value)">
          <component :is="mode.icon" />
          <span>{{ mode.label }}</span>
        </button>
      </div>
    </div>

    <!-- ===== 일간 뷰 ===== -->
    <div v-if="viewMode === 'day'" class="day-view">
      <!-- 날짜 정보 헤더 -->
      <div class="day-header-card">
        <div class="day-date-info">
          <div class="day-date-main">
            <span class="day-date-number">{{ currentDate.getDate() }}</span>
            <div class="day-date-details">
              <span class="day-date-weekday" :class="{
                'is-sunday': currentDate.getDay() === 0,
                'is-saturday': currentDate.getDay() === 6
              }">
                {{ weekdays[currentDate.getDay()] }}
              </span>
              <span class="day-date-month">
                {{ currentLanguage === 'ko'
                  ? `${currentDate.getFullYear()}년 ${monthNames[currentDate.getMonth() + 1]}`
                  : `${monthNames[currentDate.getMonth() + 1]} ${currentDate.getFullYear()}`
                }}
              </span>
            </div>
          </div>
          <div v-if="isSameDay(currentDate, new Date())" class="day-today-badge">
            <span class="pulse-dot"></span>
            {{ t('common.today') }}
          </div>
        </div>
        <div class="day-schedule-summary">
          <div class="summary-stat">
            <span class="stat-number">{{ todaySchedules.length }}</span>
            <span class="stat-label">{{ t('calendar.schedulesCount') }}</span>
          </div>
          <div class="summary-stat completed">
            <span class="stat-number">{{ todaySchedules.filter(s => s.completed).length }}</span>
            <span class="stat-label">{{ t('calendar.completed') }}</span>
          </div>
        </div>
      </div>

      <!-- 일정 리스트 (시간순) -->
      <div class="day-schedule-list" v-if="todaySchedules.length > 0">
        <div v-for="schedule in todaySchedules" :key="schedule.id"
          class="day-schedule-item"
          :class="{ 'is-completed': schedule.completed }"
          :style="{ '--schedule-color': schedule.color || '#c9a76c' }"
          @click="emit('select-date', currentDateStr)">
          <div class="schedule-time-block">
            <span class="schedule-time-text" v-if="schedule.startTime">
              {{ schedule.startTime }}
            </span>
            <span class="schedule-time-text all-day" v-else>
              {{ t('calendar.allDay') }}
            </span>
            <span class="schedule-end-time" v-if="schedule.endTime">
              ~ {{ schedule.endTime }}
            </span>
          </div>
          <div class="schedule-content-block">
            <div class="schedule-color-indicator"></div>
            <div class="schedule-details">
              <span class="schedule-title-text">{{ schedule.title }}</span>
              <span class="schedule-desc-text" v-if="schedule.description">
                {{ schedule.description }}
              </span>
            </div>
            <div class="schedule-status" v-if="schedule.completed">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div class="day-empty-state" v-else>
        <div class="empty-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="4" width="18" height="18" rx="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
            <circle cx="12" cy="15" r="1" />
          </svg>
        </div>
        <p class="empty-text">{{ t('calendar.noSchedulesToday') }}</p>
        <p class="empty-hint">{{ t('calendar.addScheduleHint') }}</p>
      </div>

      <!-- 시간별 타임라인 -->
      <div class="day-timeline">
        <div class="timeline-header">
          <span class="timeline-title">{{ currentLanguage === 'ko' ? '시간별 보기' : 'Timeline' }}</span>
        </div>
        <div class="timeline-body">
          <div v-for="hour in hours" :key="hour" class="timeline-hour-row">
            <div class="timeline-hour-label">{{ formatHour(hour) }}</div>
            <div class="timeline-hour-content">
              <div class="timeline-hour-line"></div>
              <!-- 해당 시간의 일정들 -->
              <div v-for="schedule in getSchedulesForHour(hour)" :key="schedule.id"
                class="timeline-schedule-block"
                :class="{ 'is-completed': schedule.completed }"
                :style="{ '--schedule-color': schedule.color || '#c9a76c' }">
                <span class="timeline-schedule-title">{{ schedule.title }}</span>
                <span class="timeline-schedule-time" v-if="schedule.startTime">
                  {{ schedule.startTime }}{{ schedule.endTime ? ` - ${schedule.endTime}` : '' }}
                </span>
              </div>
            </div>
            <!-- 현재 시간 인디케이터 -->
            <div v-if="isCurrentHour(hour) && isSameDay(currentDate, new Date())"
              class="timeline-current-indicator"
              :style="{ top: currentMinutePosition }">
              <div class="current-dot"></div>
              <div class="current-line"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 주간 뷰 ===== -->
    <div v-else-if="viewMode === 'week'" class="week-view">
      <div class="week-header">
        <div class="week-time-col"></div>
        <div v-for="(day, index) in currentWeekDays" :key="day.dateStr" class="week-day-header" :class="{
          'is-today': day.isToday,
          'is-selected': day.isSelected,
          'is-sunday': index === 0,
          'is-saturday': index === 6
        }" @click="emit('select-date', day.dateStr)">
          <span class="week-day-name">{{ weekdaysShort[index] }}</span>
          <span class="week-day-number">{{ day.day }}</span>
          <div v-if="day.scheduleCount > 0" class="week-event-badge">{{ day.scheduleCount }}</div>
        </div>
      </div>

      <div class="week-body">
        <div class="week-time-col">
          <div v-for="hour in hours" :key="hour" class="time-slot-label">
            {{ formatHour(hour) }}
          </div>
        </div>
        <div class="week-grid">
          <div v-for="(day, dayIndex) in currentWeekDays" :key="day.dateStr" class="week-day-column" :class="{
            'is-today': day.isToday,
            'is-selected': day.isSelected
          }" @click="emit('select-date', day.dateStr)">
            <div v-for="hour in hours" :key="hour" class="time-slot">
              <div class="slot-line"></div>
            </div>
            <!-- 스케줄 블록들 -->
            <div v-for="schedule in getSchedulesForDate(day.dateStr)" :key="schedule.id" class="week-schedule-block"
              :class="{ 'is-completed': schedule.completed }" :style="{
                ...getScheduleStyle(schedule),
                '--schedule-color': schedule.color || '#c9a76c'
              }" @click.stop="emit('select-date', day.dateStr)">
              <span class="schedule-title">{{ schedule.title }}</span>
              <span class="schedule-time" v-if="schedule.startTime">
                {{ schedule.startTime }}{{ schedule.endTime ? ` - ${schedule.endTime}` : '' }}
              </span>
            </div>
            <!-- 현재 시간 인디케이터 -->
            <div v-if="day.isToday" class="current-time-indicator" :style="{ top: currentTimePosition }">
              <div class="time-dot"></div>
              <div class="time-line"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 월간 뷰 ===== -->
    <div v-else-if="viewMode === 'month'" class="month-view">
      <!-- 이전 달 더보기 -->
      <button class="load-more-btn load-more-top" @click="emit('load-more', 'up')">
        <div class="load-more-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="18 15 12 9 6 15" />
          </svg>
        </div>
        <span>{{ t('calendar.loadPrevious') }}</span>
      </button>

      <!-- 월별 캘린더 카드 -->
      <div v-for="(monthData, monthIndex) in calendarMonths" :key="`${monthData.year}-${monthData.month}`"
        class="month-card" :ref="el => setMonthRef(el, monthData.year, monthData.month)"
        :style="{ '--delay': `${monthIndex * 0.05}s` }">
        <!-- 월 헤더 -->
        <div class="month-card-header">
          <div class="month-title-group">
            <span class="month-year">{{ monthData.year }}</span>
            <h3 class="month-name">{{ getMonthName(monthData.month) }}</h3>
          </div>
          <div class="month-badge" v-if="isCurrentMonth(monthData.year, monthData.month)">
            <span class="pulse-dot"></span>
            {{ t('common.today') }}
          </div>
        </div>

        <!-- 요일 헤더 -->
        <div class="weekday-row">
          <div v-for="(day, index) in weekdays" :key="day" class="weekday-cell" :class="{
            'weekend-sun': index === 0,
            'weekend-sat': index === 6
          }">
            {{ day }}
          </div>
        </div>

        <!-- 날짜 그리드 -->
        <div class="days-grid">
          <button v-for="day in monthData.days" :key="day.dateStr" class="day-cell" :class="{
            'other-month': !day.isCurrentMonth,
            'is-today': day.isToday,
            'is-selected': day.isSelected,
            'has-events': day.scheduleCount > 0,
            'is-sunday': day.date.getDay() === 0,
            'is-saturday': day.date.getDay() === 6,
            'all-completed': day.scheduleCount > 0 && day.completedCount === day.scheduleCount,
          }" @click="selectDateAndSwitchToWeek(day.dateStr)">
            <span class="day-number">{{ day.day }}</span>

            <!-- 일정 인디케이터 -->
            <div class="event-indicators" v-if="day.scheduleCount > 0">
              <div class="event-dots">
                <span v-for="n in Math.min(day.scheduleCount, 3)" :key="n" class="event-dot"
                  :class="{ 'completed': n <= day.completedCount }"></span>
                <span v-if="day.scheduleCount > 3" class="more-indicator">+{{ day.scheduleCount - 3 }}</span>
              </div>
            </div>

            <!-- 오늘 표시 링 -->
            <div v-if="day.isToday" class="today-ring"></div>

            <!-- 선택 배경 -->
            <div v-if="day.isSelected" class="selected-bg"></div>
          </button>
        </div>
      </div>

      <!-- 다음 달 더보기 -->
      <button class="load-more-btn load-more-bottom" @click="emit('load-more', 'down')">
        <span>{{ t('calendar.loadNext') }}</span>
        <div class="load-more-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </button>
    </div>

    <!-- ===== 연간 뷰 ===== -->
    <div v-else-if="viewMode === 'year'" class="year-view">
      <div class="year-grid">
        <div v-for="month in yearMonths" :key="month.month" class="year-month-card"
          :class="{ 'is-current-month': isCurrentMonth(currentYear, month.month) }"
          @click="switchToMonth(currentYear, month.month)">
          <div class="year-month-header">
            <span class="year-month-name">{{ getMonthName(month.month) }}</span>
            <span v-if="month.eventCount > 0" class="year-month-events">{{ month.eventCount }}</span>
          </div>
          <div class="mini-calendar">
            <div class="mini-weekdays">
              <span v-for="d in weekdaysMin" :key="d">{{ d }}</span>
            </div>
            <div class="mini-days">
              <button v-for="day in month.days" :key="day.dateStr" class="mini-day" :class="{
                'other-month': !day.isCurrentMonth,
                'is-today': day.isToday,
                'is-selected': day.isSelected,
                'has-events': day.scheduleCount > 0,
                'is-sunday': day.date.getDay() === 0,
                'is-saturday': day.date.getDay() === 6,
              }" @click.stop="selectDateAndSwitchToWeek(day.dateStr)">
                {{ day.day }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, h } from 'vue';
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

type ViewMode = 'day' | 'week' | 'month' | 'year';

interface ScheduleItem {
  id: string;
  title: string;
  description: string;
  date: string;
  startTime: string;
  endTime: string;
  color: string;
  completed: boolean;
}

const props = defineProps<{
  calendarMonths: MonthData[];
  allSchedules?: ScheduleItem[];
}>();

const emit = defineEmits<{
  'select-date': [dateStr: string];
  'load-more': [direction: 'up' | 'down'];
  'fetch-range-schedules': [startDate: string, endDate: string];
}>();

const { t, currentLanguage } = useI18n();

// 상태
const scrollRef = ref<HTMLElement | null>(null);
const monthRefs = ref<Record<string, HTMLElement | null>>({});
const viewMode = ref<ViewMode>('month');
const currentDate = ref(new Date());
const currentYear = computed(() => currentDate.value.getFullYear());

// 뷰 모드 아이콘 컴포넌트
const DayIcon = () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('rect', { x: 3, y: 4, width: 18, height: 18, rx: 2 }),
  h('line', { x1: 3, y1: 10, x2: 21, y2: 10 }),
  h('circle', { cx: 12, cy: 15, r: 2 }),
]);

const WeekIcon = () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('rect', { x: 3, y: 4, width: 18, height: 18, rx: 2 }),
  h('line', { x1: 3, y1: 10, x2: 21, y2: 10 }),
]);

const MonthIcon = () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('rect', { x: 3, y: 4, width: 18, height: 18, rx: 2 }),
  h('line', { x1: 16, y1: 2, x2: 16, y2: 6 }),
  h('line', { x1: 8, y1: 2, x2: 8, y2: 6 }),
  h('line', { x1: 3, y1: 10, x2: 21, y2: 10 }),
]);

const YearIcon = () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('rect', { x: 3, y: 3, width: 7, height: 7 }),
  h('rect', { x: 14, y: 3, width: 7, height: 7 }),
  h('rect', { x: 3, y: 14, width: 7, height: 7 }),
  h('rect', { x: 14, y: 14, width: 7, height: 7 }),
]);

const viewModes = computed(() => [
  { value: 'day' as ViewMode, label: t('calendar.dayView'), icon: DayIcon },
  { value: 'week' as ViewMode, label: t('calendar.weekView'), icon: WeekIcon },
  { value: 'month' as ViewMode, label: t('calendar.monthView'), icon: MonthIcon },
  { value: 'year' as ViewMode, label: t('calendar.yearView'), icon: YearIcon },
]);

const hours = Array.from({ length: 24 }, (_, i) => i);

const weekdays = computed(() => [
  t('days.sun'), t('days.mon'), t('days.tue'), t('days.wed'),
  t('days.thu'), t('days.fri'), t('days.sat')
]);

const weekdaysShort = computed(() => [
  t('days.sunShort') || '일', t('days.monShort') || '월', t('days.tueShort') || '화',
  t('days.wedShort') || '수', t('days.thuShort') || '목', t('days.friShort') || '금',
  t('days.satShort') || '토'
]);

const weekdaysMin = computed(() => ['일', '월', '화', '수', '목', '금', '토']);

const monthNames = computed(() => [
  '',
  t('months.jan'), t('months.feb'), t('months.mar'), t('months.apr'),
  t('months.may'), t('months.jun'), t('months.jul'), t('months.aug'),
  t('months.sep'), t('months.oct'), t('months.nov'), t('months.dec'),
]);

// 현재 기간 라벨
const currentPeriodLabel = computed(() => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth() + 1;
  const day = currentDate.value.getDate();
  const dayOfWeek = currentDate.value.getDay();
  const isKo = currentLanguage.value === 'ko';

  if (viewMode.value === 'day') {
    const dayNames = isKo
      ? ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일']
      : ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

    if (isKo) {
      return `${year}년 ${month}월 ${day}일 ${dayNames[dayOfWeek]}`;
    } else {
      return `${dayNames[dayOfWeek]}, ${monthNames.value[month]} ${day}, ${year}`;
    }
  } else if (viewMode.value === 'week') {
    const weekStart = getWeekStart(currentDate.value);
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekEnd.getDate() + 6);

    if (isKo) {
      if (weekStart.getMonth() === weekEnd.getMonth()) {
        return `${year}년 ${month}월 ${weekStart.getDate()}일 - ${weekEnd.getDate()}일`;
      } else {
        return `${weekStart.getMonth() + 1}월 ${weekStart.getDate()}일 - ${weekEnd.getMonth() + 1}월 ${weekEnd.getDate()}일`;
      }
    } else {
      // English format
      const startMonth = monthNames.value[weekStart.getMonth() + 1];
      const endMonth = monthNames.value[weekEnd.getMonth() + 1];
      if (weekStart.getMonth() === weekEnd.getMonth()) {
        return `${startMonth} ${weekStart.getDate()} - ${weekEnd.getDate()}, ${year}`;
      } else {
        return `${startMonth} ${weekStart.getDate()} - ${endMonth} ${weekEnd.getDate()}, ${year}`;
      }
    }
  } else if (viewMode.value === 'month') {
    if (isKo) {
      return `${year}년 ${monthNames.value[month]}`;
    } else {
      return `${monthNames.value[month]} ${year}`;
    }
  } else {
    return `${year}`;
  }
});

// 현재 주의 날짜들
const currentWeekDays = computed(() => {
  const weekStart = getWeekStart(currentDate.value);
  const days: CalendarDay[] = [];
  const today = new Date();

  for (let i = 0; i < 7; i++) {
    const date = new Date(weekStart);
    date.setDate(date.getDate() + i);
    const dateStr = formatDateStr(date);

    // 해당 날짜의 일정 수 찾기
    let scheduleCount = 0;
    let completedCount = 0;
    for (const monthData of props.calendarMonths) {
      const dayData = monthData.days.find(d => d.dateStr === dateStr);
      if (dayData) {
        scheduleCount = dayData.scheduleCount;
        completedCount = dayData.completedCount;
        break;
      }
    }

    days.push({
      day: date.getDate(),
      date,
      dateStr,
      isCurrentMonth: date.getMonth() === currentDate.value.getMonth(),
      isToday: isSameDay(date, today),
      isSelected: false, // 나중에 selectedDate prop 추가 가능
      scheduleCount,
      completedCount,
    });
  }

  return days;
});

// 연간 뷰 월별 데이터
const yearMonths = computed(() => {
  const year = currentDate.value.getFullYear();
  const today = new Date();
  const months = [];

  for (let month = 1; month <= 12; month++) {
    const days = generateMonthDays(year, month, today);
    const eventCount = days.reduce((sum, d) => sum + (d.isCurrentMonth ? d.scheduleCount : 0), 0);

    months.push({
      month,
      days,
      eventCount,
    });
  }

  return months;
});

// 현재 시간 위치 (퍼센트)
const currentTimePosition = computed(() => {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes();
  const totalMinutes = hours * 60 + minutes;
  const percentage = (totalMinutes / (24 * 60)) * 100;
  return `${percentage}%`;
});

// 주간 뷰용 스케줄 맵 (날짜별로 그룹화)
const weekSchedulesMap = computed(() => {
  const map: Record<string, ScheduleItem[]> = {};
  if (!props.allSchedules) return map;

  for (const schedule of props.allSchedules) {
    if (!map[schedule.date]) {
      map[schedule.date] = [];
    }
    map[schedule.date].push(schedule);
  }

  return map;
});

// 특정 날짜의 스케줄 가져오기 (시간순 정렬)
function getSchedulesForDate(dateStr: string): ScheduleItem[] {
  const schedules = weekSchedulesMap.value[dateStr] || [];
  return schedules.sort((a, b) => {
    if (!a.startTime) return 1;
    if (!b.startTime) return -1;
    return a.startTime.localeCompare(b.startTime);
  });
}

// 스케줄 위치 및 높이 계산
function getScheduleStyle(schedule: ScheduleItem) {
  if (!schedule.startTime) {
    return { top: '0%', height: '48px' };
  }

  const [startHour, startMin] = schedule.startTime.split(':').map(Number);
  const startMinutes = startHour * 60 + startMin;
  const topPercent = (startMinutes / (24 * 60)) * 100;

  let heightPercent = (60 / (24 * 60)) * 100; // 기본 1시간
  if (schedule.endTime) {
    const [endHour, endMin] = schedule.endTime.split(':').map(Number);
    const endMinutes = endHour * 60 + endMin;
    const durationMinutes = endMinutes - startMinutes;
    heightPercent = (durationMinutes / (24 * 60)) * 100;
  }

  return {
    top: `${topPercent}%`,
    height: `${Math.max(heightPercent, 2)}%`, // 최소 높이
  };
}

// 유틸리티 함수들
function getWeekStart(date: Date): Date {
  const d = new Date(date);
  const day = d.getDay();
  d.setDate(d.getDate() - day);
  return d;
}

function formatDateStr(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function isSameDay(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();
}

function formatHour(hour: number): string {
  const isKo = currentLanguage.value === 'ko';
  if (isKo) {
    if (hour === 0) return '오전 12시';
    if (hour < 12) return `오전 ${hour}시`;
    if (hour === 12) return '오후 12시';
    return `오후 ${hour - 12}시`;
  } else {
    if (hour === 0) return '12 AM';
    if (hour < 12) return `${hour} AM`;
    if (hour === 12) return '12 PM';
    return `${hour - 12} PM`;
  }
}

function generateMonthDays(year: number, month: number, today: Date): CalendarDay[] {
  const firstDay = new Date(year, month - 1, 1);
  const lastDay = new Date(year, month, 0);
  const days: CalendarDay[] = [];

  // 이전 달 날짜들
  const startDayOfWeek = firstDay.getDay();
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(year, month - 1, -i);
    const dateStr = formatDateStr(date);

    // 일정 수 찾기
    let scheduleCount = 0;
    let completedCount = 0;
    for (const monthData of props.calendarMonths) {
      const dayData = monthData.days.find(d => d.dateStr === dateStr);
      if (dayData) {
        scheduleCount = dayData.scheduleCount;
        completedCount = dayData.completedCount;
        break;
      }
    }

    days.push({
      day: date.getDate(),
      date,
      dateStr,
      isCurrentMonth: false,
      isToday: isSameDay(date, today),
      isSelected: false,
      scheduleCount,
      completedCount,
    });
  }

  // 현재 달 날짜들
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const date = new Date(year, month - 1, day);
    const dateStr = formatDateStr(date);

    let scheduleCount = 0;
    let completedCount = 0;
    for (const monthData of props.calendarMonths) {
      const dayData = monthData.days.find(d => d.dateStr === dateStr);
      if (dayData) {
        scheduleCount = dayData.scheduleCount;
        completedCount = dayData.completedCount;
        break;
      }
    }

    days.push({
      day,
      date,
      dateStr,
      isCurrentMonth: true,
      isToday: isSameDay(date, today),
      isSelected: false,
      scheduleCount,
      completedCount,
    });
  }

  // 다음 달 날짜들 (6주 채우기)
  const remaining = 42 - days.length;
  for (let i = 1; i <= remaining; i++) {
    const date = new Date(year, month, i);
    const dateStr = formatDateStr(date);

    let scheduleCount = 0;
    let completedCount = 0;
    for (const monthData of props.calendarMonths) {
      const dayData = monthData.days.find(d => d.dateStr === dateStr);
      if (dayData) {
        scheduleCount = dayData.scheduleCount;
        completedCount = dayData.completedCount;
        break;
      }
    }

    days.push({
      day: date.getDate(),
      date,
      dateStr,
      isCurrentMonth: false,
      isToday: isSameDay(date, today),
      isSelected: false,
      scheduleCount,
      completedCount,
    });
  }

  return days;
}

function getMonthName(month: number): string {
  return monthNames.value[month] || `${month}월`;
}

function isCurrentMonth(year: number, month: number): boolean {
  const today = new Date();
  return today.getFullYear() === year && today.getMonth() + 1 === month;
}

function setMonthRef(el: any, year: number, month: number) {
  if (el) {
    monthRefs.value[`${year}-${month}`] = el;
  }
}

// 네비게이션 함수들
function setViewMode(mode: ViewMode) {
  viewMode.value = mode;
}

function navigatePrev() {
  const d = new Date(currentDate.value);
  if (viewMode.value === 'day') {
    d.setDate(d.getDate() - 1);
  } else if (viewMode.value === 'week') {
    d.setDate(d.getDate() - 7);
  } else if (viewMode.value === 'month') {
    d.setMonth(d.getMonth() - 1);
  } else {
    d.setFullYear(d.getFullYear() - 1);
  }
  currentDate.value = d;

  // 월간 뷰에서 해당 월로 스크롤
  if (viewMode.value === 'month') {
    scrollToMonth(d.getFullYear(), d.getMonth() + 1);
  }
}

function navigateNext() {
  const d = new Date(currentDate.value);
  if (viewMode.value === 'day') {
    d.setDate(d.getDate() + 1);
  } else if (viewMode.value === 'week') {
    d.setDate(d.getDate() + 7);
  } else if (viewMode.value === 'month') {
    d.setMonth(d.getMonth() + 1);
  } else {
    d.setFullYear(d.getFullYear() + 1);
  }
  currentDate.value = d;

  // 월간 뷰에서 해당 월로 스크롤
  if (viewMode.value === 'month') {
    scrollToMonth(d.getFullYear(), d.getMonth() + 1);
  }
}

function navigateToday() {
  if (viewMode.value === 'month') {
    scrollToToday(true); // 부드럽게 이동
  } else {
    currentDate.value = new Date();
  }
}

function scrollToMonth(year: number, month: number) {
  nextTick(() => {
    requestAnimationFrame(() => {
      const key = `${year}-${month}`;
      const el = monthRefs.value[key];
      if (el && scrollRef.value) {
        const containerRect = scrollRef.value.getBoundingClientRect();
        const elementRect = el.getBoundingClientRect();
        const scrollOffset = elementRect.top - containerRect.top + scrollRef.value.scrollTop - 70;

        scrollRef.value.scrollTo({
          top: scrollOffset,
          behavior: 'smooth'
        });
      } else if (!el) {
        // 해당 월이 로드되지 않은 경우, 더 많은 달을 로드하도록 요청
        const today = new Date();
        const targetDate = new Date(year, month - 1, 1);
        if (targetDate < today) {
          emit('load-more', 'up');
        } else {
          emit('load-more', 'down');
        }
      }
    });
  });
}

function switchToMonth(year: number, month: number) {
  viewMode.value = 'month';
  currentDate.value = new Date(year, month - 1, 1);
  scrollToMonth(year, month);
}

function selectDateAndSwitchToMonth(dateStr: string) {
  emit('select-date', dateStr);
  viewMode.value = 'month';
  const [year, month] = dateStr.split('-').map(Number);
  currentDate.value = new Date(year, month - 1, 1);
}

function selectDateAndSwitchToWeek(dateStr: string) {
  emit('select-date', dateStr);
  viewMode.value = 'week';
  const [year, month, day] = dateStr.split('-').map(Number);
  currentDate.value = new Date(year, month - 1, day);
}

function scrollToToday(smooth: boolean = false) {
  // currentDate도 오늘로 설정
  currentDate.value = new Date();

  nextTick(() => {
    nextTick(() => {
      requestAnimationFrame(() => {
        const today = new Date();
        const key = `${today.getFullYear()}-${today.getMonth() + 1}`;
        const el = monthRefs.value[key];
        if (el && scrollRef.value) {
          // scrollIntoView 대신 직접 스크롤 위치 계산
          const containerRect = scrollRef.value.getBoundingClientRect();
          const elementRect = el.getBoundingClientRect();
          const scrollOffset = elementRect.top - containerRect.top + scrollRef.value.scrollTop - 70;

          scrollRef.value.scrollTo({
            top: scrollOffset,
            behavior: smooth ? 'smooth' : 'auto'
          });
        }
      });
    });
  });
}

// 현재 날짜 문자열 (Day 뷰용)
const currentDateStr = computed(() => formatDateStr(currentDate.value));

// 오늘의 일정 (Day 뷰용)
const todaySchedules = computed(() => {
  return getSchedulesForDate(currentDateStr.value);
});

// 특정 시간대의 일정 가져오기 (Day 뷰용)
function getSchedulesForHour(hour: number): ScheduleItem[] {
  return todaySchedules.value.filter(schedule => {
    if (!schedule.startTime) return hour === 0; // 종일 일정은 0시에 표시
    const [startHour] = schedule.startTime.split(':').map(Number);
    return startHour === hour;
  });
}

// 현재 시간인지 확인
function isCurrentHour(hour: number): boolean {
  return new Date().getHours() === hour;
}

// 현재 분 위치 (퍼센트)
const currentMinutePosition = computed(() => {
  const minutes = new Date().getMinutes();
  return `${(minutes / 60) * 100}%`;
});

// Day/Week 뷰일 때 스케줄 가져오기
watch([viewMode, currentDate], ([mode]) => {
  if (mode === 'day') {
    const dateStr = formatDateStr(currentDate.value);
    emit('fetch-range-schedules', dateStr, dateStr);
  } else if (mode === 'week') {
    const weekDays = currentWeekDays.value;
    if (weekDays.length > 0) {
      const startDate = weekDays[0].dateStr;
      const endDate = weekDays[weekDays.length - 1].dateStr;
      emit('fetch-range-schedules', startDate, endDate);
    }
  }
}, { immediate: true });

defineExpose({ scrollToToday });
</script>

<style scoped>
.calendar-container {
  position: relative;
  padding: 0 24px 20px;
  overflow-y: auto;
  scroll-behavior: smooth;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 배경 장식 */
.calendar-bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.03;
}

.bg-circle-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #c9a76c, #e8d5b7);
  top: -100px;
  right: -100px;
}

.bg-circle-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #10b981, #34d399);
  bottom: 20%;
  left: -100px;
}

.bg-circle-3 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  bottom: -50px;
  right: 30%;
}

/* ===== 뷰 컨트롤 헤더 ===== */
.view-control-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 20px;
  margin: 0 -24px 16px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-subtle);
}

.nav-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--surface-2);
  border: 1px solid var(--surface-4);
  border-radius: 10px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background: var(--surface-4);
  border-color: var(--glass-highlight);
  color: var(--text-primary);
}

.today-nav-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.15) 0%, rgba(201, 167, 108, 0.08) 100%);
  border: 1px solid rgba(201, 167, 108, 0.25);
  border-radius: 10px;
  color: #c9a76c;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

.today-nav-btn:hover {
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.25) 0%, rgba(201, 167, 108, 0.12) 100%);
  border-color: rgba(201, 167, 108, 0.4);
}

.current-period {
  flex: 1;
  text-align: center;
}

.period-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.02em;
}

.view-mode-selector {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: var(--surface-1);
  border: 1px solid var(--surface-3);
  border-radius: 12px;
}

.view-mode-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-mode-btn:hover {
  background: var(--surface-2);
  color: var(--text-secondary);
}

.view-mode-btn.active {
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.2) 0%, rgba(201, 167, 108, 0.1) 100%);
  color: #c9a76c;
}

/* ===== 주간 뷰 ===== */
.week-view {
  position: relative;
  z-index: 1;
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px solid var(--surface-3);
  border-radius: 20px;
  overflow: hidden;
}

.week-header {
  display: grid;
  grid-template-columns: 60px repeat(7, 1fr);
  border-bottom: 1px solid var(--surface-3);
}

.week-time-col {
  padding: 12px 8px;
  background: var(--surface-1);
  border-right: 1px solid var(--surface-2);
}

.week-day-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.week-day-header:hover {
  background: var(--surface-2);
}

.week-day-header.is-today {
  background: rgba(201, 167, 108, 0.08);
}

.week-day-header.is-sunday .week-day-name,
.week-day-header.is-sunday .week-day-number {
  color: #f87171;
}

.week-day-header.is-saturday .week-day-name,
.week-day-header.is-saturday .week-day-number {
  color: #60a5fa;
}

.week-day-name {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
}

.week-day-number {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.week-day-header.is-today .week-day-number {
  color: #c9a76c;
}

.week-event-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: linear-gradient(135deg, #c9a76c, #e8d5b7);
  border-radius: 9px;
  font-size: 10px;
  font-weight: 700;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
}

.week-body {
  display: grid;
  grid-template-columns: 60px 1fr;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

.week-body .week-time-col {
  padding: 0;
}

.time-slot-label {
  height: 48px;
  padding: 4px 8px;
  font-size: 10px;
  font-weight: 500;
  color: var(--text-muted);
  text-align: right;
  border-bottom: 1px solid var(--surface-1);
}

.week-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.week-day-column {
  position: relative;
  border-right: 1px solid var(--surface-2);
}

.week-day-column:last-child {
  border-right: none;
}

.week-day-column.is-today {
  background: rgba(201, 167, 108, 0.03);
}

.time-slot {
  height: 48px;
  position: relative;
}

.slot-line {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--surface-2);
}

/* 주간 뷰 스케줄 블록 */
.week-schedule-block {
  position: absolute;
  left: 2px;
  right: 2px;
  padding: 6px 10px;
  background: linear-gradient(135deg,
      color-mix(in srgb, var(--schedule-color) 18%, rgba(30, 30, 35, 0.95) 82%) 0%,
      color-mix(in srgb, var(--schedule-color) 10%, rgba(25, 25, 30, 0.9) 90%) 100%);
  border: 1px solid color-mix(in srgb, var(--schedule-color) 20%, transparent 80%);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  z-index: 3;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px color-mix(in srgb, var(--schedule-color) 10%, transparent 90%);
}

.week-schedule-block:hover {
  background: linear-gradient(135deg,
      color-mix(in srgb, var(--schedule-color) 25%, rgba(35, 35, 40, 0.98) 75%) 0%,
      color-mix(in srgb, var(--schedule-color) 15%, rgba(30, 30, 35, 0.95) 85%) 100%);
  border-color: color-mix(in srgb, var(--schedule-color) 35%, transparent 65%);
  transform: scale(1.02);
  z-index: 4;
  box-shadow: 0 4px 16px color-mix(in srgb, var(--schedule-color) 20%, transparent 80%);
}

.week-schedule-block.is-completed {
  opacity: 0.5;
}

.week-schedule-block .schedule-title {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.week-schedule-block .schedule-time {
  display: block;
  font-size: 9px;
  color: var(--text-muted);
  margin-top: 2px;
  opacity: 0.8;
}

.current-time-indicator {
  position: absolute;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  z-index: 5;
  pointer-events: none;
}

.time-dot {
  width: 10px;
  height: 10px;
  background: #ef4444;
  border-radius: 50%;
  margin-left: -5px;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

.time-line {
  flex: 1;
  height: 2px;
  background: #ef4444;
}

/* ===== 월간 뷰 ===== */
.month-view {
  position: relative;
  z-index: 1;
}

/* 더보기 버튼 */
.load-more-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px 20px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, var(--surface-1) 0%, var(--bg-primary) 100%);
  border: 1px solid var(--surface-3);
  border-radius: 14px;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.load-more-btn:hover {
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.08) 0%, rgba(201, 167, 108, 0.04) 100%);
  border-color: rgba(201, 167, 108, 0.2);
  color: #c9a76c;
}

.load-more-bottom {
  margin-bottom: 0;
  margin-top: 24px;
}

.load-more-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--surface-2);
  border-radius: 8px;
}

/* 월 카드 */
.month-card {
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px solid var(--surface-3);
  border-radius: 20px;
  padding: 20px 24px 24px;
  margin-bottom: 24px;
  animation: cardFadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) backwards;
  animation-delay: var(--delay, 0s);
  scroll-margin-top: 70px;
  display: flex;
  flex-direction: column;
}

.month-card:last-of-type {
  margin-bottom: 0;
}

@keyframes cardFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.month-card-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--surface-3);
}

.month-title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.month-year {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

.month-name {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.month-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.15) 0%, rgba(201, 167, 108, 0.08) 100%);
  border: 1px solid rgba(201, 167, 108, 0.25);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: #c9a76c;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background: #c9a76c;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {

  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }

  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 6px;
}

.weekday-cell {
  padding: 8px 4px;
  text-align: center;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.weekday-cell.weekend-sun {
  color: #f87171;
}

.weekday-cell.weekend-sat {
  color: #60a5fa;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(6, minmax(48px, 1fr));
  gap: 4px;
  flex: 1;
}

.day-cell {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 6px;
  background: var(--surface-1);
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  overflow: hidden;
  min-height: 48px;
}

.day-cell:hover {
  background: var(--surface-4);
  border-color: var(--glass-highlight);
  transform: translateY(-1px);
}

.day-cell.other-month {
  opacity: 0.3;
  background: transparent;
}

.day-cell.is-today {
  background: rgba(201, 167, 108, 0.12);
  border-color: rgba(201, 167, 108, 0.3);
}

.day-cell.is-today .day-number {
  color: #c9a76c;
  font-weight: 800;
}

.day-cell.is-selected {
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.2) 0%, rgba(201, 167, 108, 0.12) 100%);
  border-color: rgba(201, 167, 108, 0.4);
  box-shadow: 0 2px 12px rgba(201, 167, 108, 0.15);
}

.day-cell.is-selected .day-number {
  color: #e8d5b7;
  font-weight: 700;
}

.day-cell.has-events {
  background: var(--surface-2);
}

.day-cell.all-completed {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.2);
}

.day-cell.all-completed .day-number {
  color: #34d399;
}

.day-cell.is-sunday .day-number {
  color: #f87171;
}

.day-cell.is-saturday .day-number {
  color: #60a5fa;
}

.day-number {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  z-index: 1;
}

.event-indicators {
  margin-top: 4px;
  z-index: 1;
}

.event-dots {
  display: flex;
  align-items: center;
  gap: 3px;
}

.event-dot {
  width: 5px;
  height: 5px;
  background: linear-gradient(135deg, #c9a76c, #e8d5b7);
  border-radius: 50%;
}

.event-dot.completed {
  background: linear-gradient(135deg, #22c55e, #34d399);
}

.more-indicator {
  font-size: 9px;
  font-weight: 700;
  color: var(--text-muted);
  margin-left: 2px;
}

.today-ring {
  position: absolute;
  inset: 4px;
  border: 2px solid rgba(201, 167, 108, 0.4);
  border-radius: 10px;
  pointer-events: none;
  animation: todayPulse 3s ease-in-out infinite;
}

@keyframes todayPulse {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}

.selected-bg {
  position: absolute;
  inset: 2px;
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.15) 0%, transparent 100%);
  border: 1px solid rgba(201, 167, 108, 0.4);
  border-radius: 10px;
  pointer-events: none;
}

/* ===== 연간 뷰 ===== */
.year-view {
  position: relative;
  z-index: 1;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.year-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 16px;
  flex: 1;
  min-height: 0;
}

.year-month-card {
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px solid var(--surface-3);
  border-radius: 16px;
  padding: 12px 16px;
  transition: all 0.25s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.year-month-card:hover {
  border-color: var(--glass-highlight);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.year-month-card.is-current-month {
  border-color: rgba(201, 167, 108, 0.3);
  background: linear-gradient(165deg, rgba(201, 167, 108, 0.08) 0%, rgba(201, 167, 108, 0.02) 100%);
}

.year-month-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--surface-3);
}

.year-month-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.year-month-events {
  padding: 2px 8px;
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.2), rgba(201, 167, 108, 0.1));
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  color: #c9a76c;
}

.mini-calendar {
  font-size: 10px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.mini-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 4px;
}

.mini-weekdays span {
  text-align: center;
  color: var(--text-muted);
  font-weight: 600;
  padding: 2px;
}

.mini-weekdays span:first-child {
  color: #f87171;
}

.mini-weekdays span:last-child {
  color: #60a5fa;
}

.mini-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(6, 1fr);
  gap: 2px;
  flex: 1;
}

.mini-day {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 4px;
  color: var(--text-secondary);
  font-size: 10px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
  min-height: 0;
}

.mini-day:hover {
  background: var(--surface-4);
}

.mini-day.other-month {
  opacity: 0.3;
}

.mini-day.is-today {
  background: rgba(201, 167, 108, 0.2);
  color: #c9a76c;
  font-weight: 700;
}

.mini-day.is-selected {
  background: #c9a76c;
  color: #1a1a1a;
  font-weight: 700;
}

.mini-day.has-events {
  position: relative;
}

.mini-day.has-events::after {
  content: '';
  position: absolute;
  bottom: 2px;
  width: 3px;
  height: 3px;
  background: #c9a76c;
  border-radius: 50%;
}

.mini-day.is-sunday {
  color: #f87171;
}

.mini-day.is-saturday {
  color: #60a5fa;
}

/* ===== 일간 뷰 ===== */
.day-view {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.day-header-card {
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px solid var(--surface-3);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.day-date-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.day-date-main {
  display: flex;
  align-items: center;
  gap: 16px;
}

.day-date-number {
  font-size: 56px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: -0.03em;
}

.day-date-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.day-date-weekday {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.day-date-weekday.is-sunday {
  color: #f87171;
}

.day-date-weekday.is-saturday {
  color: #60a5fa;
}

.day-date-month {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-muted);
}

.day-today-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.2) 0%, rgba(201, 167, 108, 0.1) 100%);
  border: 1px solid rgba(201, 167, 108, 0.3);
  border-radius: 24px;
  font-size: 13px;
  font-weight: 600;
  color: #c9a76c;
}

.day-schedule-summary {
  display: flex;
  gap: 24px;
}

.summary-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 20px;
  background: var(--surface-1);
  border-radius: 12px;
}

.summary-stat .stat-number {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.summary-stat .stat-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
}

.summary-stat.completed .stat-number {
  color: #34d399;
}

/* 일정 리스트 */
.day-schedule-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.day-schedule-item {
  display: flex;
  gap: 16px;
  padding: 16px 20px;
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px solid var(--surface-3);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.day-schedule-item:hover {
  border-color: var(--glass-highlight);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.day-schedule-item.is-completed {
  opacity: 0.6;
}

.schedule-time-block {
  min-width: 80px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.schedule-time-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.schedule-time-text.all-day {
  font-size: 14px;
  color: #c9a76c;
}

.schedule-end-time {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

.schedule-content-block {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.schedule-color-indicator {
  width: 4px;
  height: 100%;
  min-height: 40px;
  background: var(--schedule-color);
  border-radius: 2px;
}

.schedule-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.schedule-title-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.day-schedule-item.is-completed .schedule-title-text {
  text-decoration: line-through;
  color: var(--text-muted);
}

.schedule-desc-text {
  font-size: 13px;
  color: var(--text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.schedule-status {
  color: #34d399;
}

/* 빈 상태 */
.day-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px dashed var(--surface-4);
  border-radius: 20px;
}

.day-empty-state .empty-icon {
  color: var(--text-muted);
  opacity: 0.5;
  margin-bottom: 16px;
}

.day-empty-state .empty-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.day-empty-state .empty-hint {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

/* 타임라인 */
.day-timeline {
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px solid var(--surface-3);
  border-radius: 20px;
  overflow: hidden;
}

.timeline-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--surface-3);
}

.timeline-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.timeline-body {
  max-height: 500px;
  overflow-y: auto;
}

.timeline-hour-row {
  position: relative;
  display: flex;
  min-height: 60px;
  border-bottom: 1px solid var(--surface-2);
}

.timeline-hour-row:last-child {
  border-bottom: none;
}

.timeline-hour-label {
  width: 80px;
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  text-align: right;
  flex-shrink: 0;
  background: var(--surface-1);
  border-right: 1px solid var(--surface-2);
}

.timeline-hour-content {
  flex: 1;
  padding: 8px 12px;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.timeline-hour-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--surface-2);
}

.timeline-schedule-block {
  padding: 8px 12px;
  background: linear-gradient(135deg,
      color-mix(in srgb, var(--schedule-color) 18%, rgba(30, 30, 35, 0.95) 82%) 0%,
      color-mix(in srgb, var(--schedule-color) 10%, rgba(25, 25, 30, 0.9) 90%) 100%);
  border: 1px solid color-mix(in srgb, var(--schedule-color) 20%, transparent 80%);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.timeline-schedule-block:hover {
  background: linear-gradient(135deg,
      color-mix(in srgb, var(--schedule-color) 25%, rgba(35, 35, 40, 0.98) 75%) 0%,
      color-mix(in srgb, var(--schedule-color) 15%, rgba(30, 30, 35, 0.95) 85%) 100%);
  border-color: color-mix(in srgb, var(--schedule-color) 35%, transparent 65%);
}

.timeline-schedule-block.is-completed {
  opacity: 0.5;
}

.timeline-schedule-title {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.timeline-schedule-time {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.timeline-current-indicator {
  position: absolute;
  left: 80px;
  right: 0;
  display: flex;
  align-items: center;
  z-index: 5;
  pointer-events: none;
}

.timeline-current-indicator .current-dot {
  width: 10px;
  height: 10px;
  background: #ef4444;
  border-radius: 50%;
  margin-left: -5px;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

.timeline-current-indicator .current-line {
  flex: 1;
  height: 2px;
  background: #ef4444;
}

/* 반응형 */
@media (max-width: 900px) {
  .year-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .view-control-header {
    flex-wrap: wrap;
    gap: 12px;
  }

  .current-period {
    order: -1;
    flex-basis: 100%;
    text-align: left;
  }

  .day-header-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .day-schedule-summary {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 600px) {
  .year-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .view-mode-btn span {
    display: none;
  }

  .day-date-number {
    font-size: 40px;
  }

  .day-date-weekday {
    font-size: 16px;
  }

  .day-schedule-item {
    flex-direction: column;
    gap: 12px;
  }

  .schedule-time-block {
    flex-direction: row;
    gap: 8px;
    align-items: center;
  }

  .timeline-hour-label {
    width: 60px;
    font-size: 10px;
  }
}
</style>
