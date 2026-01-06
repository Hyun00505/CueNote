export type JobStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface Job {
  id: number;
  name: string;
  status: JobStatus;
}

export const schemas = require('./schemas.json');
