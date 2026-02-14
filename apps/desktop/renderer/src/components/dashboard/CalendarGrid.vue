<template>
  <div
    ref="scrollRef"
    class="calendar-container"
  >
    <!-- 배경 장식 -->
    <div class="calendar-bg-decoration">
      <div class="bg-circle bg-circle-1" />
      <div class="bg-circle bg-circle-2" />
      <div class="bg-circle bg-circle-3" />
    </div>

    <!-- 뷰 모드 컨트롤 헤더 -->
    <div class="view-control-header">
      <!-- 네비게이션 -->
      <div class="nav-controls">
        <button
          class="nav-btn"
          :title="t('calendar.previous')"
          @click="navigatePrev"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>
        <button
          class="nav-btn"
          :title="t('calendar.next')"
          @click="navigateNext"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
        <button
          class="today-nav-btn"
          @click="navigateToday"
        >
          {{ t('common.today') }}
        </button>
      </div>

      <!-- 현재 날짜 표시 -->
      <div class="current-period">
        <h2 class="period-title">
          {{ currentPeriodLabel }}
        </h2>
      </div>

      <!-- 뷰 모드 선택 -->
      <div class="view-mode-selector">
        <button
          v-for="mode in viewModes"
          :key="mode.value"
          class="view-mode-btn"
          :class="{ active: viewMode === mode.value }"
          @click="setViewMode(mode.value)"
        >
          <component :is="mode.icon" />
          <span>{{ mode.label }}</span>
        </button>
      </div>
    </div>

    <!-- ===== 일간 뷰 ===== -->
    <div
      v-if="viewMode === 'day'"
      class="day-view"
    >
      <!-- 메인 레이아웃: 좌측 사이드바 + 우측 타임라인 -->
      <div class="day-layout">
        <!-- 좌측: 날짜 정보 + 일정 요약 -->
        <div class="day-sidebar">
          <!-- 날짜 카드 -->
          <div
            class="day-date-card"
            :class="{ 'is-today': isSameDay(currentDate, new Date()) }"
          >
            <div class="date-card-bg" />
            <div class="date-card-content">
              <span
                class="date-weekday"
                :class="{
                  'is-sunday': currentDate.getDay() === 0,
                  'is-saturday': currentDate.getDay() === 6
                }"
              >{{ weekdays[currentDate.getDay()] }}</span>
              <span class="date-number">{{ currentDate.getDate() }}</span>
              <span class="date-month">{{ monthNames[currentDate.getMonth() + 1] }} {{ currentDate.getFullYear() }}</span>
              <div
                v-if="isSameDay(currentDate, new Date())"
                class="today-badge"
              >
                <span class="today-pulse" />
                {{ t('common.today') }}
              </div>
            </div>
          </div>

          <!-- 일정 통계 -->
          <div class="day-stats-card">
            <div class="stats-header">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
              <span>{{ currentLanguage === 'ko' ? '오늘의 일정' : "Today's Schedule" }}</span>
            </div>
            <div class="stats-grid">
              <div class="stat-box total">
                <span class="stat-value">{{ todaySchedules.length }}</span>
                <span class="stat-name">{{ t('calendar.total') || '전체' }}</span>
              </div>
              <div class="stat-box completed">
                <span class="stat-value">{{ todaySchedules.filter(s => s.completed).length }}</span>
                <span class="stat-name">{{ t('calendar.completed') || '완료' }}</span>
              </div>
              <div class="stat-box remaining">
                <span class="stat-value">{{ todaySchedules.filter(s => !s.completed).length }}</span>
                <span class="stat-name">{{ t('calendar.remaining') || '남음' }}</span>
              </div>
            </div>
            <!-- 진행률 바 -->
            <div
              v-if="todaySchedules.length > 0"
              class="stats-progress"
            >
              <div class="progress-track">
                <div
                  class="progress-fill"
                  :style="{ width: `${Math.round((todaySchedules.filter(s => s.completed).length / todaySchedules.length) * 100)}%` }"
                />
              </div>
              <span class="progress-text">{{ Math.round((todaySchedules.filter(s => s.completed).length / todaySchedules.length) * 100) }}%</span>
            </div>
          </div>

          <!-- 빠른 일정 목록 -->
          <div
            v-if="todaySchedules.length > 0"
            class="day-quick-list"
          >
            <div class="quick-list-header">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line
                  x1="8"
                  y1="6"
                  x2="21"
                  y2="6"
                /><line
                  x1="8"
                  y1="12"
                  x2="21"
                  y2="12"
                /><line
                  x1="8"
                  y1="18"
                  x2="21"
                  y2="18"
                />
                <line
                  x1="3"
                  y1="6"
                  x2="3.01"
                  y2="6"
                /><line
                  x1="3"
                  y1="12"
                  x2="3.01"
                  y2="12"
                /><line
                  x1="3"
                  y1="18"
                  x2="3.01"
                  y2="18"
                />
              </svg>
              <span>{{ currentLanguage === 'ko' ? '일정 목록' : 'Schedule List' }}</span>
            </div>
            <div class="quick-list-items">
              <div
                v-for="schedule in todaySchedules"
                :key="schedule.id" 
                class="quick-item" 
                :class="{ 'is-completed': schedule.completed }"
                :style="{ '--item-color': schedule.color || '#c9a76c' }"
                @click="handleScheduleClick(schedule, $event)"
              >
                <div class="quick-item-indicator" />
                <div class="quick-item-content">
                  <span class="quick-item-title">{{ schedule.title }}</span>
                  <span
                    v-if="schedule.startTime"
                    class="quick-item-time"
                  >
                    {{ schedule.startTime }}{{ schedule.endTime ? ` - ${schedule.endTime}` : '' }}
                  </span>
                  <span
                    v-else
                    class="quick-item-time all-day"
                  >{{ t('calendar.allDay') }}</span>
                </div>
                <div
                  v-if="schedule.completed"
                  class="quick-item-check"
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                  >
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- 빈 상태 -->
          <div
            v-else
            class="day-empty-card"
          >
            <div class="empty-illustration">
              <svg
                width="64"
                height="64"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1"
              >
                <rect
                  x="3"
                  y="4"
                  width="18"
                  height="18"
                  rx="2"
                  opacity="0.3"
                />
                <path
                  d="M8 2v4M16 2v4M3 10h18"
                  opacity="0.3"
                />
                <circle
                  cx="12"
                  cy="15"
                  r="3"
                  stroke-dasharray="2 2"
                />
              </svg>
            </div>
            <p class="empty-title">
              {{ t('calendar.noSchedulesToday') }}
            </p>
            <p class="empty-desc">
              {{ t('calendar.addScheduleHint') }}
            </p>
          </div>
        </div>

        <!-- 우측: 타임라인 뷰 -->
        <div class="day-timeline-area">
          <!-- 종일 일정 섹션 -->
          <div
            v-if="allDaySchedules.length > 0"
            class="day-allday-section"
          >
            <div class="allday-header">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect
                  x="3"
                  y="4"
                  width="18"
                  height="18"
                  rx="2"
                />
                <line
                  x1="3"
                  y1="10"
                  x2="21"
                  y2="10"
                />
              </svg>
              <span>{{ t('calendar.allDay') }}</span>
            </div>
            <div class="allday-items">
              <div
                v-for="schedule in allDaySchedules"
                :key="schedule.id"
                class="allday-schedule-item"
                :class="{ 'is-completed': schedule.completed }"
                :style="{ '--item-color': schedule.color || '#c9a76c' }"
                @click="handleScheduleClick(schedule, $event)"
              >
                <div class="allday-item-indicator" />
                <span class="allday-item-title">{{ schedule.title }}</span>
                <div
                  v-if="schedule.completed"
                  class="allday-item-check"
                >
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                  >
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <div
            ref="dayTimelineRef"
            class="timeline-container"
          >
            <!-- 현재 시간 표시 (상단 고정) -->
            <div
              v-if="isSameDay(currentDate, new Date())"
              class="current-time-badge"
            >
              <span class="time-icon">
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                  /><polyline points="12 6 12 12 16 14" />
                </svg>
              </span>
              <span class="time-text">{{ formatCurrentTime() }}</span>
            </div>

            <!-- 타임라인 그리드 -->
            <div class="timeline-grid">
              <div
                v-for="hour in hours"
                :key="hour"
                class="timeline-row" 
                :class="{ 'is-current-hour': isCurrentHour(hour) && isSameDay(currentDate, new Date()), 'is-past': isPastHour(hour) }"
              >
                <!-- 시간 라벨 -->
                <div class="timeline-hour">
                  <span class="hour-text">{{ formatHour(hour) }}</span>
                </div>
                
                <!-- 시간 슬롯 -->
                <div class="timeline-slot">
                  <div class="slot-line" />
                  
                  <!-- 현재 시간 인디케이터 -->
                  <div
                    v-if="isCurrentHour(hour) && isSameDay(currentDate, new Date())" 
                    class="now-indicator" 
                    :style="{ top: `${(new Date().getMinutes() / 60) * 100}%` }"
                  >
                    <div class="now-dot" />
                    <div class="now-line" />
                  </div>
                  
                  <!-- 해당 시간의 일정 -->
                  <div
                    v-for="schedule in getSchedulesForHour(hour)"
                    :key="schedule.id" 
                    class="timeline-event"
                    :class="{ 'is-completed': schedule.completed }"
                    :style="{ '--event-color': schedule.color || '#c9a76c' }"
                    @click="handleScheduleClick(schedule, $event)"
                  >
                    <div class="event-accent" />
                    <div class="event-content">
                      <span class="event-title">{{ schedule.title }}</span>
                      <span
                        v-if="schedule.startTime"
                        class="event-time"
                      >
                        {{ schedule.startTime }}{{ schedule.endTime ? ` ~ ${schedule.endTime}` : '' }}
                      </span>
                      <span
                        v-if="schedule.description"
                        class="event-desc"
                      >{{ schedule.description }}</span>
                    </div>
                    <div
                      v-if="schedule.completed"
                      class="event-status"
                    >
                      <svg
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2.5"
                      >
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 주간 뷰 ===== -->
    <div
      v-else-if="viewMode === 'week'"
      class="week-view"
    >
      <div class="week-header">
        <div class="week-time-col" />
        <div
          v-for="(day, index) in currentWeekDays"
          :key="day.dateStr"
          class="week-day-header"
          :class="{
            'is-today': day.isToday,
            'is-selected': day.isSelected,
            'is-sunday': index === 0,
            'is-saturday': index === 6
          }"
          @click="selectDateAndSwitchToDay(day.dateStr)"
        >
          <span class="week-day-name">{{ weekdaysShort[index] }}</span>
          <span class="week-day-number">{{ day.day }}</span>
          <div
            v-if="day.scheduleCount > 0"
            class="week-event-badge"
          >
            {{ day.scheduleCount }}
          </div>
        </div>
      </div>

      <!-- 종일 일정 섹션 -->
      <div
        v-if="hasAnyAllDaySchedules"
        class="week-allday-section"
      >
        <div class="week-allday-label">
          {{ t('calendar.allDay') }}
        </div>
        <div class="week-allday-grid">
          <div
            v-for="(day, dayIndex) in currentWeekDays"
            :key="'allday-' + day.dateStr"
            class="week-allday-cell"
            :class="{ 'is-today': day.isToday }"
            @click="selectDateAndSwitchToDay(day.dateStr)"
          >
            <div
              v-for="schedule in getAllDaySchedulesForDate(day.dateStr)"
              :key="schedule.id"
              class="allday-event"
              :class="{ 'is-completed': schedule.completed }"
              :style="{ '--schedule-color': schedule.color || '#c9a76c' }"
            >
              <span class="allday-event-title">{{ schedule.title }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="week-body">
        <div class="week-time-col">
          <div
            v-for="hour in hours"
            :key="hour"
            class="time-slot-label"
          >
            {{ formatHour(hour) }}
          </div>
        </div>
        <div class="week-grid">
          <div
            v-for="(day, dayIndex) in currentWeekDays"
            :key="day.dateStr"
            class="week-day-column"
            :class="{
              'is-today': day.isToday,
              'is-selected': day.isSelected
            }"
            @click="selectDateAndSwitchToDay(day.dateStr)"
          >
            <div
              v-for="hour in hours"
              :key="hour"
              class="time-slot"
            >
              <div class="slot-line" />
            </div>
            <!-- 스케줄 블록들 -->
            <div
              v-for="schedule in getSchedulesForDate(day.dateStr)"
              :key="schedule.id"
              class="week-schedule-block"
              :class="{ 'is-completed': schedule.completed }"
              :style="{
                ...getScheduleStyle(schedule),
                '--schedule-color': schedule.color || '#c9a76c'
              }"
              @click.stop="handleScheduleClick(schedule, $event)"
            >
              <span class="schedule-title">{{ schedule.title }}</span>
              <span
                v-if="schedule.startTime"
                class="schedule-time"
              >
                {{ schedule.startTime }}{{ schedule.endTime ? ` - ${schedule.endTime}` : '' }}
              </span>
            </div>
            <!-- 현재 시간 인디케이터 -->
            <div
              v-if="day.isToday"
              class="current-time-indicator"
              :style="{ top: currentTimePosition }"
            >
              <div class="time-dot" />
              <div class="time-line" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 월간 뷰 ===== -->
    <div
      v-else-if="viewMode === 'month'"
      class="month-view"
    >
      <!-- 이전 달 더보기 -->
      <button
        class="load-more-btn load-more-top"
        @click="emit('load-more', 'up')"
      >
        <div class="load-more-icon">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="18 15 12 9 6 15" />
          </svg>
        </div>
        <span>{{ t('calendar.loadPrevious') }}</span>
      </button>

      <!-- 월별 캘린더 카드 -->
      <div
        v-for="(monthData, monthIndex) in calendarMonths"
        :key="`${monthData.year}-${monthData.month}`"
        :ref="el => setMonthRef(el, monthData.year, monthData.month)"
        class="month-card"
        :style="{ '--delay': `${monthIndex * 0.05}s` }"
      >
        <!-- 월 헤더 -->
        <div class="month-card-header">
          <div class="month-title-group">
            <span class="month-year">{{ monthData.year }}</span>
            <h3 class="month-name">
              {{ getMonthName(monthData.month) }}
            </h3>
          </div>
          <div
            v-if="isCurrentMonth(monthData.year, monthData.month)"
            class="month-badge"
          >
            <span class="pulse-dot" />
            {{ t('common.today') }}
          </div>
        </div>

        <!-- 요일 헤더 -->
        <div class="weekday-row">
          <div
            v-for="(day, index) in weekdays"
            :key="day"
            class="weekday-cell"
            :class="{
              'weekend-sun': index === 0,
              'weekend-sat': index === 6
            }"
          >
            {{ day }}
          </div>
        </div>

        <!-- 날짜 그리드 -->
        <div class="days-grid">
          <div
            v-for="day in monthData.days"
            :key="day.dateStr"
            class="day-cell"
            :class="{
              'other-month': !day.isCurrentMonth,
              'is-today': day.isToday,
              'has-events': day.scheduleCount > 0,
              'is-sunday': day.date.getDay() === 0,
              'is-saturday': day.date.getDay() === 6,
              'all-completed': day.scheduleCount > 0 && day.completedCount === day.scheduleCount,
            }"
            @click="emit('select-date', day.dateStr)"
          >
            <div class="day-cell-header">
              <span class="day-number">{{ day.day }}</span>
              <button
                v-if="day.isCurrentMonth"
                class="day-add-btn"
                :title="t('calendar.addSchedule') || '일정 추가'"
                @click.stop="openQuickAdd(day.dateStr)"
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
                </svg>
              </button>
            </div>

            <!-- 인라인 빠른 추가 -->
            <div v-if="quickAddVisible && quickAddDate === day.dateStr" class="day-quick-add" @click.stop>
              <input
                ref="quickAddInputRef"
                v-model="quickAddTitle"
                class="day-quick-input"
                :placeholder="t('calendar.quickAdd') || '일정 입력...'"
                @keydown.enter="handleInlineQuickSave(day.dateStr)"
                @keydown.escape="closeQuickAdd"
                @blur="closeQuickAdd"
                autofocus
              />
            </div>

            <!-- 일정 미리보기 -->
            <div v-if="day.scheduleCount > 0" class="day-schedule-preview">
              <div
                v-for="schedule in getSchedulePreview(day.dateStr)"
                :key="schedule.id"
                class="preview-item"
                :class="{ 'is-completed': schedule.completed }"
                :style="{ '--preview-color': schedule.color || '#c9a76c' }"
                @click.stop="handleScheduleClick(schedule, $event)"
              >
                <span class="preview-dot" />
                <span class="preview-title">{{ schedule.title }}</span>
              </div>
              <div v-if="getMoreCount(day.dateStr) > 0" class="preview-more">
                +{{ getMoreCount(day.dateStr) }} {{ t('calendar.nMore') || '더보기' }}
              </div>
            </div>

            <!-- 일정 도트 인디케이터 (미리보기 아래) -->
            <div
              v-if="day.scheduleCount > 0 && getSchedulePreview(day.dateStr).length === 0"
              class="event-indicators"
            >
              <div class="event-dots">
                <span
                  v-for="n in Math.min(day.scheduleCount, 3)"
                  :key="n"
                  class="event-dot"
                  :class="{ 'completed': n <= day.completedCount }"
                />
                <span
                  v-if="day.scheduleCount > 3"
                  class="more-indicator"
                >+{{ day.scheduleCount - 3 }}</span>
              </div>
            </div>

            <!-- 오늘 표시 링 -->
            <div
              v-if="day.isToday"
              class="today-ring"
            />
          </div>
        </div>
      </div>

      <!-- 다음 달 더보기 -->
      <button
        class="load-more-btn load-more-bottom"
        @click="emit('load-more', 'down')"
      >
        <span>{{ t('calendar.loadNext') }}</span>
        <div class="load-more-icon">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </button>
    </div>

    <!-- ===== 연간 뷰 ===== -->
    <div
      v-else-if="viewMode === 'year'"
      class="year-view"
    >
      <div class="year-grid">
        <div
          v-for="month in yearMonths"
          :key="month.month"
          class="year-month-card"
          :class="{ 'is-current-month': isCurrentMonth(currentYear, month.month) }"
          @click="switchToMonth(currentYear, month.month)"
        >
          <div class="year-month-header">
            <span class="year-month-name">{{ getMonthName(month.month) }}</span>
            <span
              v-if="month.eventCount > 0"
              class="year-month-events"
            >{{ month.eventCount }}</span>
          </div>
          <div class="mini-calendar">
            <div class="mini-weekdays">
              <span
                v-for="d in weekdaysMin"
                :key="d"
              >{{ d }}</span>
            </div>
            <div class="mini-days">
              <button
                v-for="day in month.days"
                :key="day.dateStr"
                class="mini-day"
                :class="{
                  'other-month': !day.isCurrentMonth,
                  'is-today': day.isToday,
                  'has-events': day.scheduleCount > 0,
                  'is-sunday': day.date.getDay() === 0,
                  'is-saturday': day.date.getDay() === 6,
                }"
                @click.stop="selectDateAndSwitchToDay(day.dateStr)"
              >
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
import type { ScheduleItem } from '../../types';

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

const props = defineProps<{
  calendarMonths: MonthData[];
  allSchedules?: ScheduleItem[];
}>();

const emit = defineEmits<{
  'select-date': [dateStr: string];
  'load-more': [direction: 'up' | 'down'];
  'fetch-range-schedules': [startDate: string, endDate: string];
  'quick-add': [data: { title: string; date: string; startTime: string; endTime: string }];
  'schedule-click': [schedule: ScheduleItem, event: MouseEvent];
}>();

const { t, currentLanguage } = useI18n();

// 상태
const scrollRef = ref<HTMLElement | null>(null);
const monthRefs = ref<Record<string, HTMLElement | null>>({});
const viewMode = ref<ViewMode>('month');
const currentDate = ref(new Date());

// Quick-add 상태
const quickAddVisible = ref(false);
const quickAddDate = ref('');
const quickAddTime = ref('');
const quickAddTitle = ref('');
const quickAddInputRef = ref<HTMLInputElement | null>(null);

function openQuickAdd(dateStr: string, startTime: string = '') {
  quickAddDate.value = dateStr;
  quickAddTime.value = startTime;
  quickAddTitle.value = '';
  quickAddVisible.value = true;
}

function closeQuickAdd() {
  quickAddVisible.value = false;
  quickAddDate.value = '';
  quickAddTime.value = '';
}

function handleQuickAddSave(data: { title: string; date: string; startTime: string; endTime: string }) {
  emit('quick-add', data);
  closeQuickAdd();
}

function handleInlineQuickSave(dateStr: string) {
  if (!quickAddTitle.value.trim()) {
    closeQuickAdd();
    return;
  }
  emit('quick-add', {
    title: quickAddTitle.value.trim(),
    date: dateStr,
    startTime: quickAddTime.value || '',
    endTime: '',
  });
  quickAddTitle.value = '';
  closeQuickAdd();
}

function handleScheduleClick(schedule: ScheduleItem, event: MouseEvent) {
  event.stopPropagation();
  emit('schedule-click', schedule, event);
}

// 날짜별 스케줄 미리보기 가져오기 (최대 2개)
function getSchedulePreview(dateStr: string): ScheduleItem[] {
  const schedules = getSchedulesForDate(dateStr);
  return schedules.slice(0, 2);
}

function getMoreCount(dateStr: string): number {
  const schedules = getSchedulesForDate(dateStr);
  return Math.max(0, schedules.length - 2);
}
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

// 특정 날짜의 스케줄 가져오기 (시간순 정렬, 시간이 있는 것만)
function getSchedulesForDate(dateStr: string): ScheduleItem[] {
  const schedules = weekSchedulesMap.value[dateStr] || [];
  return schedules
    .filter(s => s.startTime) // 시간이 있는 일정만
    .sort((a, b) => a.startTime.localeCompare(b.startTime));
}

// 특정 날짜의 종일 일정 가져오기 (시간이 없는 것)
function getAllDaySchedulesForDate(dateStr: string): ScheduleItem[] {
  const schedules = weekSchedulesMap.value[dateStr] || [];
  return schedules.filter(s => !s.startTime);
}

// 현재 주에 종일 일정이 있는지 확인
const hasAnyAllDaySchedules = computed(() => {
  return currentWeekDays.value.some(day => {
    const schedules = weekSchedulesMap.value[day.dateStr] || [];
    return schedules.some(s => !s.startTime);
  });
});

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
  // 뷰 모드 변경 후 DOM이 완전히 렌더링될 때까지 기다림
  nextTick(() => {
    nextTick(() => {
      scrollToMonth(year, month);
    });
  });
}

function selectDateAndSwitchToMonth(dateStr: string) {
  emit('select-date', dateStr);
  viewMode.value = 'month';
  const [year, month] = dateStr.split('-').map(Number);
  currentDate.value = new Date(year, month - 1, 1);
}

function selectDateAndSwitchToDay(dateStr: string) {
  emit('select-date', dateStr);
  viewMode.value = 'day';
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

// 특정 시간대의 일정 가져오기 (Day 뷰용) - 시간이 있는 일정만
function getSchedulesForHour(hour: number): ScheduleItem[] {
  return todaySchedules.value.filter(schedule => {
    if (!schedule.startTime) return false; // 종일 일정은 타임라인에서 제외
    const [startHour] = schedule.startTime.split(':').map(Number);
    return startHour === hour;
  });
}

// 종일 일정 가져오기 (Day 뷰용) - weekSchedulesMap에서 직접 가져옴
const allDaySchedules = computed(() => {
  return getAllDaySchedulesForDate(currentDateStr.value);
});

// 현재 시간인지 확인
function isCurrentHour(hour: number): boolean {
  return new Date().getHours() === hour;
}

// 과거 시간인지 확인
function isPastHour(hour: number): boolean {
  const now = new Date();
  if (!isSameDay(currentDate.value, now)) return false;
  return hour < now.getHours();
}

// 현재 시간 포맷
function formatCurrentTime(): string {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes();
  const isKo = currentLanguage.value === 'ko';
  
  if (isKo) {
    const period = hours < 12 ? '오전' : '오후';
    const displayHour = hours === 0 ? 12 : hours > 12 ? hours - 12 : hours;
    return `${period} ${displayHour}:${String(minutes).padStart(2, '0')}`;
  } else {
    const period = hours < 12 ? 'AM' : 'PM';
    const displayHour = hours === 0 ? 12 : hours > 12 ? hours - 12 : hours;
    return `${displayHour}:${String(minutes).padStart(2, '0')} ${period}`;
  }
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
      color-mix(in srgb, var(--schedule-color) 18%, var(--surface-2) 82%) 0%,
      color-mix(in srgb, var(--schedule-color) 10%, var(--surface-1) 90%) 100%);
  border: 1px solid color-mix(in srgb, var(--schedule-color) 20%, var(--surface-4) 80%);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  z-index: 3;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px color-mix(in srgb, var(--schedule-color) 10%, transparent 90%);
}

.week-schedule-block:hover {
  background: linear-gradient(135deg,
      color-mix(in srgb, var(--schedule-color) 25%, var(--surface-3) 75%) 0%,
      color-mix(in srgb, var(--schedule-color) 15%, var(--surface-2) 85%) 100%);
  border-color: color-mix(in srgb, var(--schedule-color) 35%, var(--surface-4) 65%);
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

/* ===== 주간 뷰 종일 일정 섹션 ===== */
.week-allday-section {
  display: flex;
  border-bottom: 1px solid var(--surface-3);
  background: var(--surface-1);
}

.week-allday-label {
  width: 60px;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  border-right: 1px solid var(--surface-2);
}

.week-allday-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.week-allday-cell {
  min-height: 40px;
  padding: 4px;
  border-right: 1px solid var(--surface-2);
  display: flex;
  flex-direction: column;
  gap: 3px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.week-allday-cell:last-child {
  border-right: none;
}

.week-allday-cell:hover {
  background: var(--surface-2);
}

.week-allday-cell.is-today {
  background: rgba(201, 167, 108, 0.05);
}

.allday-event {
  padding: 4px 8px;
  background: linear-gradient(135deg,
    color-mix(in srgb, var(--schedule-color) 20%, var(--surface-2) 80%) 0%,
    color-mix(in srgb, var(--schedule-color) 12%, var(--surface-1) 88%) 100%);
  border: 1px solid color-mix(in srgb, var(--schedule-color) 25%, var(--surface-4) 75%);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.allday-event:hover {
  background: linear-gradient(135deg,
    color-mix(in srgb, var(--schedule-color) 28%, var(--surface-3) 72%) 0%,
    color-mix(in srgb, var(--schedule-color) 18%, var(--surface-2) 82%) 100%);
  transform: scale(1.02);
}

.allday-event.is-completed {
  opacity: 0.5;
}

.allday-event-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
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
  grid-template-rows: repeat(6, minmax(80px, 1fr));
  gap: 4px;
  flex: 1;
}

.day-cell {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  padding: 4px 6px;
  background: var(--surface-1);
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  overflow: hidden;
  min-height: 80px;
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
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  z-index: 1;
}

/* Day cell header with add button */
.day-cell-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2px;
}

.day-add-btn {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  opacity: 0;
  transition: all 0.15s ease;
  padding: 0;
}

.day-cell:hover .day-add-btn {
  opacity: 1;
}

.day-add-btn:hover {
  background: rgba(201, 167, 108, 0.2);
  color: #c9a76c;
}

/* Schedule preview in month cells */
.day-schedule-preview {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 100%;
  z-index: 1;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 1px 4px;
  border-radius: 3px;
  cursor: pointer;
  transition: background 0.12s ease;
  min-width: 0;
}

.preview-item:hover {
  background: rgba(201, 167, 108, 0.12);
}

.preview-item.is-completed {
  opacity: 0.5;
}

.preview-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--preview-color, #c9a76c);
  flex-shrink: 0;
}

.preview-item.is-completed .preview-dot {
  background: #34d399;
}

.preview-title {
  font-size: 10px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview-item.is-completed .preview-title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.preview-more {
  font-size: 9px;
  font-weight: 600;
  color: var(--text-muted);
  padding: 0 4px;
}

/* Inline quick-add in day cell */
.day-quick-add {
  width: 100%;
  margin-top: 2px;
}

.day-quick-input {
  width: 100%;
  padding: 3px 6px;
  font-size: 10px;
  font-family: inherit;
  background: var(--surface-3);
  border: 1px solid rgba(201, 167, 108, 0.3);
  border-radius: 4px;
  color: var(--text-primary);
  outline: none;
  transition: border-color 0.15s ease;
}

.day-quick-input:focus {
  border-color: rgba(201, 167, 108, 0.5);
  box-shadow: 0 0 0 2px rgba(201, 167, 108, 0.1);
}

.day-quick-input::placeholder {
  color: var(--text-muted);
  font-size: 10px;
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

/* ===== 일간 뷰 (새 디자인) ===== */
.day-view {
  position: relative;
  z-index: 1;
  flex: 1;
  min-height: 0;
}

.day-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 20px;
  height: 100%;
  min-height: 0;
}

/* 좌측 사이드바 */
.day-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  padding-right: 4px;
}

/* 날짜 카드 */
.day-date-card {
  position: relative;
  padding: 28px 24px;
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px solid var(--surface-3);
  border-radius: 20px;
  overflow: hidden;
  text-align: center;
}

.day-date-card.is-today {
  border-color: rgba(201, 167, 108, 0.4);
  background: linear-gradient(165deg, 
    color-mix(in srgb, #c9a76c 8%, var(--surface-2) 92%) 0%, 
    color-mix(in srgb, #c9a76c 4%, var(--surface-1) 96%) 100%);
}

.date-card-bg {
  position: absolute;
  top: -50%;
  right: -30%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(201, 167, 108, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.date-card-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.date-weekday {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.date-weekday.is-sunday { color: #f87171; }
.date-weekday.is-saturday { color: #60a5fa; }

.date-number {
  font-size: 72px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: -0.04em;
}

.day-date-card.is-today .date-number {
  background: linear-gradient(135deg, #c9a76c 0%, #e8d5b7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.date-month {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  margin-top: 4px;
}

.today-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding: 6px 14px;
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.2) 0%, rgba(201, 167, 108, 0.1) 100%);
  border: 1px solid rgba(201, 167, 108, 0.3);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  color: #c9a76c;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.today-pulse {
  width: 6px;
  height: 6px;
  background: #c9a76c;
  border-radius: 50%;
  animation: pulse-animation 2s ease-in-out infinite;
}

@keyframes pulse-animation {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.3); }
}

/* 통계 카드 */
.day-stats-card {
  padding: 20px;
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px solid var(--surface-3);
  border-radius: 16px;
}

.stats-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stats-header svg { opacity: 0.6; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px 8px;
  background: var(--surface-1);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.stat-box:hover {
  background: var(--surface-3);
  transform: translateY(-2px);
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
}

.stat-box.completed .stat-value { color: #34d399; }
.stat-box.remaining .stat-value { color: #fbbf24; }

.stat-name {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.stats-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-track {
  flex: 1;
  height: 6px;
  background: var(--surface-3);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #34d399);
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-text {
  font-size: 12px;
  font-weight: 700;
  color: #34d399;
  min-width: 40px;
  text-align: right;
}

/* 빠른 일정 목록 */
.day-quick-list {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px solid var(--surface-3);
  border-radius: 16px;
  overflow: hidden;
}

.quick-list-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--surface-3);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.quick-list-header svg { opacity: 0.6; }

.quick-list-items {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.quick-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  margin-bottom: 6px;
  background: var(--surface-1);
  border: 1px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-item:last-child { margin-bottom: 0; }

.quick-item:hover {
  background: var(--surface-3);
  border-color: color-mix(in srgb, var(--item-color) 30%, transparent 70%);
  transform: translateX(4px);
}

.quick-item.is-completed { opacity: 0.5; }

.quick-item-indicator {
  width: 4px;
  height: 32px;
  background: var(--item-color);
  border-radius: 2px;
  flex-shrink: 0;
}

.quick-item-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.quick-item-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quick-item.is-completed .quick-item-title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.quick-item-time {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
}

.quick-item-time.all-day {
  color: #c9a76c;
  font-weight: 600;
}

.quick-item-check {
  color: #34d399;
  flex-shrink: 0;
}

/* 빈 상태 카드 */
.day-empty-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 20px;
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px dashed var(--surface-4);
  border-radius: 16px;
  text-align: center;
}

.empty-illustration {
  color: var(--text-muted);
  opacity: 0.4;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 6px;
}

.empty-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}

/* 우측 타임라인 영역 */
.day-timeline-area {
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: linear-gradient(165deg, var(--surface-2) 0%, var(--surface-1) 100%);
  border: 1px solid var(--surface-3);
  border-radius: 20px;
  overflow: hidden;
}

/* 일간 뷰 종일 일정 섹션 */
.day-allday-section {
  border-bottom: 1px solid var(--surface-3);
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(201, 167, 108, 0.06) 0%, rgba(201, 167, 108, 0.02) 100%);
}

.allday-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 11px;
  font-weight: 700;
  color: #c9a76c;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.allday-header svg {
  opacity: 0.7;
}

.allday-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.allday-schedule-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: linear-gradient(135deg,
    color-mix(in srgb, var(--item-color) 15%, var(--surface-2) 85%) 0%,
    color-mix(in srgb, var(--item-color) 8%, var(--surface-1) 92%) 100%);
  border: 1px solid color-mix(in srgb, var(--item-color) 25%, var(--surface-4) 75%);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.allday-schedule-item:hover {
  background: linear-gradient(135deg,
    color-mix(in srgb, var(--item-color) 22%, var(--surface-3) 78%) 0%,
    color-mix(in srgb, var(--item-color) 12%, var(--surface-2) 88%) 100%);
  border-color: color-mix(in srgb, var(--item-color) 40%, var(--surface-4) 60%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px color-mix(in srgb, var(--item-color) 15%, transparent 85%);
}

.allday-schedule-item.is-completed {
  opacity: 0.5;
}

.allday-item-indicator {
  width: 4px;
  height: 20px;
  background: var(--item-color);
  border-radius: 2px;
  flex-shrink: 0;
}

.allday-item-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.allday-schedule-item.is-completed .allday-item-title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.allday-item-check {
  color: #34d399;
  flex-shrink: 0;
}

.timeline-container {
  flex: 1;
  overflow-y: auto;
  position: relative;
}

/* 현재 시간 배지 */
.current-time-badge {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.08) 100%);
  border-bottom: 1px solid rgba(239, 68, 68, 0.2);
  backdrop-filter: blur(8px);
}

.time-icon {
  color: #ef4444;
  display: flex;
  align-items: center;
}

.time-text {
  font-size: 14px;
  font-weight: 700;
  color: #ef4444;
  font-variant-numeric: tabular-nums;
}

/* 타임라인 그리드 */
.timeline-grid {
  padding: 0 0 20px;
}

.timeline-row {
  display: flex;
  min-height: 72px;
  position: relative;
  transition: background 0.2s ease;
}

.timeline-row:hover {
  background: var(--surface-1);
}

.timeline-row.is-current-hour {
  background: rgba(239, 68, 68, 0.04);
}

.timeline-row.is-past {
  opacity: 0.6;
}

.timeline-hour {
  width: 72px;
  padding: 12px 16px 12px 12px;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  flex-shrink: 0;
}

.hour-text {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  line-height: 1;
}

.timeline-row.is-current-hour .hour-text {
  color: #ef4444;
  font-weight: 700;
}

.timeline-slot {
  flex: 1;
  position: relative;
  padding: 8px 16px 8px 0;
  min-height: 72px;
}

.slot-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 16px;
  height: 1px;
  background: var(--surface-3);
}

/* 현재 시간 인디케이터 */
.now-indicator {
  position: absolute;
  left: 0;
  right: 16px;
  display: flex;
  align-items: center;
  z-index: 5;
  pointer-events: none;
}

.now-dot {
  width: 10px;
  height: 10px;
  background: #ef4444;
  border-radius: 50%;
  margin-left: -5px;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2), 0 0 12px rgba(239, 68, 68, 0.4);
  animation: now-pulse 2s ease-in-out infinite;
}

@keyframes now-pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2), 0 0 12px rgba(239, 68, 68, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0.1), 0 0 20px rgba(239, 68, 68, 0.3); }
}

.now-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, #ef4444, transparent);
}

/* 타임라인 이벤트 */
.timeline-event {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  margin-bottom: 8px;
  background: linear-gradient(135deg,
    color-mix(in srgb, var(--event-color) 12%, var(--surface-2) 88%) 0%,
    color-mix(in srgb, var(--event-color) 6%, var(--surface-1) 94%) 100%);
  border: 1px solid color-mix(in srgb, var(--event-color) 20%, var(--surface-4) 80%);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.timeline-event:last-child { margin-bottom: 0; }

.timeline-event:hover {
  background: linear-gradient(135deg,
    color-mix(in srgb, var(--event-color) 18%, var(--surface-3) 82%) 0%,
    color-mix(in srgb, var(--event-color) 10%, var(--surface-2) 90%) 100%);
  border-color: color-mix(in srgb, var(--event-color) 35%, var(--surface-4) 65%);
  transform: translateX(6px);
  box-shadow: 0 4px 20px color-mix(in srgb, var(--event-color) 15%, transparent 85%);
}

.timeline-event.is-completed {
  opacity: 0.5;
}

.event-accent {
  width: 4px;
  min-height: 36px;
  background: var(--event-color);
  border-radius: 2px;
  flex-shrink: 0;
}

.event-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.event-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
}

.timeline-event.is-completed .event-title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.event-time {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

.event-desc {
  font-size: 12px;
  color: var(--text-muted);
  opacity: 0.8;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-top: 2px;
}

.event-status {
  color: #34d399;
  flex-shrink: 0;
  margin-top: 2px;
}

/* 반응형 */
@media (max-width: 1100px) {
  .day-layout {
    grid-template-columns: 280px 1fr;
    gap: 16px;
  }
  
  .date-number {
    font-size: 60px;
  }
  
  .stat-value {
    font-size: 24px;
  }
}

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

  .day-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
  
  .day-sidebar {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 12px;
    overflow-y: visible;
    padding-right: 0;
  }
  
  .day-date-card {
    flex: 1;
    min-width: 200px;
    padding: 20px;
  }
  
  .date-number {
    font-size: 48px;
  }
  
  .day-stats-card {
    flex: 1;
    min-width: 200px;
  }
  
  .day-quick-list {
    flex-basis: 100%;
    max-height: 200px;
  }
  
  .day-empty-card {
    flex-basis: 100%;
    padding: 24px;
  }
}

@media (max-width: 600px) {
  .year-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .view-mode-btn span {
    display: none;
  }

  .day-sidebar {
    flex-direction: column;
  }
  
  .day-date-card,
  .day-stats-card {
    min-width: unset;
  }
  
  .date-number {
    font-size: 40px;
  }
  
  .stats-grid {
    gap: 8px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .timeline-hour {
    width: 56px;
    padding: 8px 12px 8px 8px;
  }
  
  .hour-text {
    font-size: 10px;
  }
  
  .timeline-event {
    padding: 10px 12px;
  }
  
  .event-title {
    font-size: 13px;
  }
}
</style>
