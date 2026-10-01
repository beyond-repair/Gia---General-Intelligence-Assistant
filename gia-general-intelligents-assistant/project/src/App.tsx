import React, { useCallback, useEffect, useState } from 'react';
import { Brain } from 'lucide-react';
import { TaskInput } from './components/TaskInput';
import { WorkflowVisualizer } from './components/WorkflowVisualizer';
import { TaskList } from './components/TaskList';
import { Task, WorkflowNode } from './types';
import { ApiTask, createTask, getTask, listTasks } from './api/client';

const initialWorkflowNodes: WorkflowNode[] = [
  {
    name: 'Understand Task',
    description: 'Analyze and decompose the task',
    status: 'idle',
    dependencies: [],
  },
  {
    name: 'Gather Info',
    description: 'Collect relevant information',
    status: 'idle',
    dependencies: ['understand_task'],
  },
  {
    name: 'Generate Code',
    description: 'Create solution code',
    status: 'idle',
    dependencies: ['gather_information'],
  },
  {
    name: 'Execute',
    description: 'Run and validate solution',
    status: 'idle',
    dependencies: ['generate_code'],
  },
  {
    name: 'Optimize',
    description: 'Self-correct and improve',
    status: 'idle',
    dependencies: ['execute_code'],
  },
];

function mapApiTask(t: ApiTask): Task {
  return {
    id: t.id,
    description: t.description,
    status: t.status,
    result: t.result ?? undefined,
    createdAt: new Date(t.created_at),
    updatedAt: new Date(t.updated_at),
    steps: (t.steps || []).map((s) => ({
      id: s.id,
      name: s.name,
      status: s.status,
      type: s.type,
      output: s.output ?? undefined,
    })),
  };
}

function workflowFromTask(task: Task | null): WorkflowNode[] {
  if (!task || !task.steps.length) {
    return initialWorkflowNodes.map((n) => ({ ...n, status: 'idle' as const }));
  }
  // Map first 5 display-oriented steps onto the visualizer
  const visual = initialWorkflowNodes.map((node) => {
    const match = task.steps.find((s) => s.name === node.name);
    if (!match) return { ...node, status: 'idle' as const };
    let status: WorkflowNode['status'] = 'idle';
    if (match.status === 'completed') status = 'completed';
    else if (match.status === 'processing') status = 'active';
    else if (match.status === 'failed') status = 'error';
    return { ...node, status };
  });
  return visual;
}

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [workflow, setWorkflow] = useState<WorkflowNode[]>(initialWorkflowNodes);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  const refreshTasks = useCallback(async () => {
    try {
      const data = await listTasks();
      setTasks(data.map(mapApiTask));
      setApiOnline(true);
      setError(null);
    } catch (e) {
      setApiOnline(false);
      setError(
        'Backend unreachable. Start it with: cd gia-general-intelligents-assistant/project/backend && python run.py'
      );
    }
  }, []);

  useEffect(() => {
    refreshTasks();
  }, [refreshTasks]);

  const pollTask = async (id: string) => {
    for (let i = 0; i < 60; i++) {
      const fresh = await getTask(id);
      const mapped = mapApiTask(fresh);
      setTasks((prev) => {
        const others = prev.filter((t) => t.id !== id);
        return [mapped, ...others];
      });
      setWorkflow(workflowFromTask(mapped));
      if (mapped.status === 'completed' || mapped.status === 'failed') {
        return mapped;
      }
      await new Promise((r) => setTimeout(r, 250));
    }
    throw new Error('Timed out waiting for task');
  };

  const handleTaskSubmit = async (description: string) => {
    setIsProcessing(true);
    setError(null);
    try {
      const created = await createTask(description);
      const mapped = mapApiTask(created);
      setTasks((prev) => [mapped, ...prev.filter((t) => t.id !== mapped.id)]);
      setWorkflow(workflowFromTask(mapped));
      await pollTask(mapped.id);
      setApiOnline(true);
    } catch (e) {
      setApiOnline(false);
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <Brain className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Gia - General Intelligence Assistant
              </h1>
              <p className="text-sm text-gray-500">
                Claim-0 stub prototype · AGI claims UNSUPPORTED
                {apiOnline === true && ' · API connected'}
                {apiOnline === false && ' · API offline'}
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="space-y-8">
          {error && (
            <div className="bg-amber-50 border border-amber-200 text-amber-900 rounded-lg p-4 text-sm">
              {error}
            </div>
          )}

          <div className="flex justify-center">
            <TaskInput onSubmit={handleTaskSubmit} disabled={isProcessing} />
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4">Current Workflow</h2>
            <WorkflowVisualizer nodes={workflow} />
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4">Task History</h2>
            <TaskList tasks={tasks} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
