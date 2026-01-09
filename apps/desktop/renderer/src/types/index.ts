export type TodoItem = {
  id: string;
  text: string;
  checked: boolean;
  notePath: string;
  lineNo: number;
};

export type TodayPlan = {
  tldr: string;
  overdue: TodoItem[];
  dueSoon: TodoItem[];
  nextActions: string[];
  quickWins: string[];
};

export type ViewType = 'editor' | 'dashboard' | 'settings';

// 일정 관련 타입
export type ScheduleItem = {
  id: string;
  title: string;
  description: string;
  date: string; // YYYY-MM-DD
  startTime: string; // HH:MM
  endTime: string; // HH:MM
  color: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
};

export type ScheduleCountByDate = {
  date: string;
  count: number;
  completedCount: number;
};

export type CalendarDay = {
  date: Date;
  dateStr: string; // YYYY-MM-DD
  day: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  isSelected: boolean;
  scheduleCount: number;
  completedCount: number;
};

