export interface Task {
  id: string;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  steps: TaskStep[];
  result?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface TaskStep {
  id: string;
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  output?: string;
  type: 'understand_task' | 'gather_information' | 'generate_code' | 'execute_code' | 'self_correct';
}

export interface WorkflowNode {
  name: string;
  description: string;
  status: 'idle' | 'active' | 'completed' | 'error';
  dependencies: string[];
}