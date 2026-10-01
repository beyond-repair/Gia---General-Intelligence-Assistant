const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

export interface ApiTaskStep {
  id: string;
  task_id: string;
  name: string;
  status: string;
  type: string;
  output?: string | null;
}

export interface ApiTask {
  id: string;
  description: string;
  status: string;
  result?: string | null;
  created_at: string;
  updated_at: string;
  steps: ApiTaskStep[];
}

export async function createTask(description: string): Promise<ApiTask> {
  const resp = await fetch(`${API_BASE}/tasks/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ description }),
  });
  if (!resp.ok) {
    throw new Error(`createTask failed: ${resp.status}`);
  }
  return resp.json();
}

export async function listTasks(): Promise<ApiTask[]> {
  const resp = await fetch(`${API_BASE}/tasks/`);
  if (!resp.ok) {
    throw new Error(`listTasks failed: ${resp.status}`);
  }
  return resp.json();
}

export async function getTask(id: string): Promise<ApiTask> {
  const resp = await fetch(`${API_BASE}/tasks/${id}`);
  if (!resp.ok) {
    throw new Error(`getTask failed: ${resp.status}`);
  }
  return resp.json();
}
