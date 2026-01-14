import { ref, computed, watch } from 'vue';
import type { ScheduleItem, ScheduleCountByDate, CalendarDay } from '../types';

const API_BASE = 'http://127.0.0.1:8787';

// 전역 상태
const schedules = ref<ScheduleItem[]>([]);
const scheduleCounts = ref<ScheduleCountByDate[]>([]);
const selectedDate = ref<string>('');
const loading = ref(false);
const error = ref<string | null>(null);

// 여러 달 표시를 위한 상태
const visibleMonthsCount = ref(6); // 표시할 달 수
const startMonthOffset = ref(-1); // 현재 달 기준 시작 오프셋 (-1 = 지난달부터)

// 날짜 포맷팅 유틸리티
function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatMonth(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
}

function isSameDay(d1: Date, d2: Date): boolean {
  return d1.getFullYear() === d2.getFullYear() &&
         d1.getMonth() === d2.getMonth() &&
         d1.getDate() === d2.getDate();
}

// 월 정보 타입
export type MonthData = {
  year: number;
  month: number;
  label: string;
  days: CalendarDay[];
};

export function useSchedule() {
  const today = new Date();
  
  // 여러 달의 캘린더 데이터 생성
  const calendarMonths = computed<MonthData[]>(() => {
    const months: MonthData[] = [];
    const baseDate = new Date();
    
    for (let i = 0; i < visibleMonthsCount.value; i++) {
      const monthOffset = startMonthOffset.value + i;
      const targetDate = new Date(baseDate.getFullYear(), baseDate.getMonth() + monthOffset, 1);
      const year = targetDate.getFullYear();
      const month = targetDate.getMonth();
      
      // 이번 달의 첫 날과 마지막 날
      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);
      
      // 달력 시작일 (이전 달 포함, 일요일 시작)
      const startDate = new Date(firstDay);
      startDate.setDate(startDate.getDate() - firstDay.getDay());
      
      // 필요한 주 수 계산 (최대 6주)
      const totalDays = firstDay.getDay() + lastDay.getDate();
      const weeksNeeded = Math.ceil(totalDays / 7);
      const daysToShow = weeksNeeded * 7;
      
      const days: CalendarDay[] = [];
      const current = new Date(startDate);
      
      for (let j = 0; j < daysToShow; j++) {
        const dateStr = formatDate(current);
        const countInfo = scheduleCounts.value.find(c => c.date === dateStr);
        
        days.push({
          date: new Date(current),
          dateStr,
          day: current.getDate(),
          isCurrentMonth: current.getMonth() === month,
          isToday: isSameDay(current, today),
          isSelected: dateStr === selectedDate.value,
          scheduleCount: countInfo?.count || 0,
          completedCount: countInfo?.completedCount || 0,
        });
        
        current.setDate(current.getDate() + 1);
      }
      
      months.push({
        year,
        month: month + 1,
        label: `${year}년 ${month + 1}월`,
        days,
      });
    }
    
    return months;
  });

  // 선택된 날짜의 일정
  const selectedSchedules = computed(() => {
    return schedules.value.filter(s => s.date === selectedDate.value);
  });

  // 오늘로 이동
  function goToToday() {
    startMonthOffset.value = -1;
    selectedDate.value = formatDate(new Date());
    fetchSchedulesByDate(selectedDate.value);
  }

  // 날짜 선택
  function selectDate(dateStr: string) {
    selectedDate.value = dateStr;
    fetchSchedulesByDate(dateStr);
  }

  // 더 많은 달 로드 (위로/아래로)
  function loadMoreMonths(direction: 'up' | 'down') {
    if (direction === 'up') {
      startMonthOffset.value -= 3;
    } else {
      visibleMonthsCount.value += 3;
    }
    fetchAllVisibleCounts();
  }

  // 모든 보이는 달의 일정 개수 조회
  async function fetchAllVisibleCounts() {
    const allCounts: ScheduleCountByDate[] = [];
    const baseDate = new Date();
    
    for (let i = 0; i < visibleMonthsCount.value; i++) {
      const monthOffset = startMonthOffset.value + i;
      const targetDate = new Date(baseDate.getFullYear(), baseDate.getMonth() + monthOffset, 1);
      const monthStr = formatMonth(targetDate);
      
      try {
        const res = await fetch(`${API_BASE}/schedules/counts?month=${monthStr}`);
        if (res.ok) {
          const data = await res.json();
          allCounts.push(...(data.counts || []));
        }
      } catch (e) {
        console.error('일정 개수 조회 실패:', e);
      }
    }
    
    scheduleCounts.value = allCounts;
  }

  async function fetchSchedulesByDate(date: string) {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/schedules?date=${date}`);
      if (res.ok) {
        const data = await res.json();
        schedules.value = data.schedules || [];
      }
    } catch (e) {
      error.value = '일정을 불러오는데 실패했습니다';
      console.error('일정 조회 실패:', e);
    } finally {
      loading.value = false;
    }
  }

  async function createSchedule(schedule: Omit<ScheduleItem, 'id' | 'completed' | 'createdAt' | 'updatedAt'>) {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/schedules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(schedule),
      });
      if (res.ok) {
        const data = await res.json();
        schedules.value.push(data.schedule);
        // rangeSchedules에도 추가 (해당 날짜 범위에 포함되면)
        rangeSchedules.value.push(data.schedule);
        await fetchAllVisibleCounts();
        return data.schedule;
      }
    } catch (e) {
      error.value = '일정 생성에 실패했습니다';
      console.error('일정 생성 실패:', e);
    } finally {
      loading.value = false;
    }
    return null;
  }

  async function updateSchedule(id: string, updates: Partial<ScheduleItem>) {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/schedules/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      if (res.ok) {
        const data = await res.json();
        const index = schedules.value.findIndex(s => s.id === id);
        if (index !== -1) {
          schedules.value[index] = data.schedule;
        }
        // rangeSchedules도 업데이트
        const rangeIndex = rangeSchedules.value.findIndex(s => s.id === id);
        if (rangeIndex !== -1) {
          rangeSchedules.value[rangeIndex] = data.schedule;
        }
        await fetchAllVisibleCounts();
        return data.schedule;
      }
    } catch (e) {
      error.value = '일정 수정에 실패했습니다';
      console.error('일정 수정 실패:', e);
    } finally {
      loading.value = false;
    }
    return null;
  }

  async function deleteSchedule(id: string) {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/schedules/${id}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        schedules.value = schedules.value.filter(s => s.id !== id);
        // rangeSchedules에서도 제거
        rangeSchedules.value = rangeSchedules.value.filter(s => s.id !== id);
        await fetchAllVisibleCounts();
        return true;
      }
    } catch (e) {
      error.value = '일정 삭제에 실패했습니다';
      console.error('일정 삭제 실패:', e);
    } finally {
      loading.value = false;
    }
    return false;
  }

  async function toggleComplete(id: string) {
    const schedule = schedules.value.find(s => s.id === id);
    if (schedule) {
      return updateSchedule(id, { completed: !schedule.completed });
    }
    return null;
  }

  // AI 일정 추출
  async function extractSchedulesFromNote(
    content: string,
    provider: string = 'ollama',
    apiKey: string = '',
    model: string = ''
  ) {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/ai/extract-schedules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          language: 'ko',
          provider,
          api_key: apiKey,
          model,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        return {
          schedules: data.schedules || [],
          confidence: data.confidence || 0,
        };
      }
    } catch (e) {
      error.value = '일정 추출에 실패했습니다';
      console.error('일정 추출 실패:', e);
    } finally {
      loading.value = false;
    }
    return { schedules: [], confidence: 0 };
  }

  // 일괄 생성
  async function createSchedulesBatch(newSchedules: Omit<ScheduleItem, 'id' | 'completed' | 'createdAt' | 'updatedAt'>[]) {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch(`${API_BASE}/schedules/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSchedules),
      });
      if (res.ok) {
        const data = await res.json();
        const addedForSelectedDate = data.schedules.filter((s: ScheduleItem) => s.date === selectedDate.value);
        schedules.value.push(...addedForSelectedDate);
        await fetchAllVisibleCounts();
        return data.schedules;
      }
    } catch (e) {
      error.value = '일정 일괄 생성에 실패했습니다';
      console.error('일정 일괄 생성 실패:', e);
    } finally {
      loading.value = false;
    }
    return [];
  }

  // 날짜 범위로 스케줄 가져오기 (주간 뷰용)
  const rangeSchedules = ref<ScheduleItem[]>([]);
  
  async function fetchSchedulesByDateRange(startDate: string, endDate: string): Promise<ScheduleItem[]> {
    try {
      const res = await fetch(`${API_BASE}/schedules?start_date=${startDate}&end_date=${endDate}`);
      if (res.ok) {
        const data = await res.json();
        rangeSchedules.value = data.schedules || [];
        return rangeSchedules.value;
      }
    } catch (e) {
      console.error('날짜 범위 스케줄 조회 실패:', e);
    }
    return [];
  }

  // 초기화
  function init() {
    const todayStr = formatDate(today);
    selectedDate.value = todayStr;
    fetchAllVisibleCounts();
    fetchSchedulesByDate(todayStr);
  }

  return {
    // 상태
    schedules,
    scheduleCounts,
    selectedDate,
    loading,
    error,
    calendarMonths,
    selectedSchedules,
    visibleMonthsCount,
    startMonthOffset,
    rangeSchedules,
    
    // 액션
    goToToday,
    selectDate,
    loadMoreMonths,
    fetchAllVisibleCounts,
    fetchSchedulesByDate,
    fetchSchedulesByDateRange,
    createSchedule,
    updateSchedule,
    deleteSchedule,
    toggleComplete,
    extractSchedulesFromNote,
    createSchedulesBatch,
    init,
    
    // 유틸리티
    formatDate,
    formatMonth,
  };
}
