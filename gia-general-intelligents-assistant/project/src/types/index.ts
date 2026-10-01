export interface Task {
  id: string;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | string;
  steps: TaskStep[];
  result?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface TaskStep {
  id: string;
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | string;
  output?: string;
  type: string;
}

export interface WorkflowNode {
  name: string;
  description: string;
  status: 'idle' | 'active' | 'completed' | 'error';
  dependencies: string[];
}
