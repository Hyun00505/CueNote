export type JobStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface Job {
  id: number;
  name: string;
  status: JobStatus;
}

export interface TodoItem {
  id: string;
  text: string;
  checked: boolean;
  notePath: string;
  lineNo: number;
}

export interface TodayPlanResponse {
  tldr: string;
  overdue: TodoItem[];
  dueSoon: TodoItem[];
  nextActions: string[];
  quickWins: string[];
}

export const schemas = require('./schemas.json');
