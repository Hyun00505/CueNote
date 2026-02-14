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

export type ViewType = 'editor' | 'dashboard' | 'settings' | 'graph';

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

// 그래프 뷰 & AI 클러스터링 타입
export type GraphNode = {
  id: string;
  label: string;
  cluster: number;
  clusterLabel: string;
  size: number;
  color: string;
  preview: string;
  x?: number;
  y?: number;
  // d3-force 시뮬레이션용
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
};

export type GraphEdge = {
  source: string | GraphNode;
  target: string | GraphNode;
  weight: number;
  type: 'similarity' | 'link';
};

export type ClusterInfo = {
  id: number;
  label: string;
  color: string;
  noteCount: number;
  keywords: string[];
};

export type GraphData = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  clusters: ClusterInfo[];
  totalNotes: number;
};

export type RelatedNote = {
  path: string;
  title: string;
  similarity: number;
  clusterLabel: string;
  color: string;
  preview: string;
};

// 챗봇 관련 타입
export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant' | 'tool_call' | 'tool_result';
  content: string;
  toolCall?: ToolCallInfo;
  toolResult?: Record<string, unknown>;
  timestamp: number;
};

export type ToolCallInfo = {
  name: string;
  arguments: Record<string, unknown>;
};
