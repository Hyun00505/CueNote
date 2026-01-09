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

