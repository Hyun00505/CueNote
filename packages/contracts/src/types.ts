export interface TodoItem {
  id: string
  text: string
  checked: boolean
  notePath: string
  lineNo: number
}

export interface TodayPlanRequest {
  nowISO: string
  todos: TodoItem[]
}

export interface TodayPlanResponse {
  tldr: string
  overdue: TodoItem[]
  dueSoon: TodoItem[]
  nextActions: string[]
  quickWins: string[]
}
