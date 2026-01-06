import schemas from './schemas.json'

export type JobStatus = 'queued' | 'running' | 'completed' | 'failed'

export interface Job {
  id: number
  name: string
  status: JobStatus
}

export * from './types'
export { schemas }
