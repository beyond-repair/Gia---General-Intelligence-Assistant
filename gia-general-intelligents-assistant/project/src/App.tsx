import React, { useState } from 'react';
import { Brain } from 'lucide-react';
import { TaskInput } from './components/TaskInput';
import { WorkflowVisualizer } from './components/WorkflowVisualizer';
import { TaskList } from './components/TaskList';
import { Task, WorkflowNode } from './types';

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

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [workflow, setWorkflow] = useState<WorkflowNode[]>(initialWorkflowNodes);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleTaskSubmit = (description: string) => {
    setIsProcessing(true);
    const newTask: Task = {
      id: crypto.randomUUID(),
      description,
      status: 'processing',
      steps: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    setTasks((prev) => [newTask, ...prev]);

    // Simulate workflow progression
    const nodeCount = workflow.length;
    workflow.forEach((node, index) => {
      setTimeout(() => {
        setWorkflow((prev) =>
          prev.map((n, i) => ({
            ...n,
            status: i === index ? 'active' : i < index ? 'completed' : 'idle',
          }))
        );

        if (index === nodeCount - 1) {
          setTimeout(() => {
            setWorkflow((prev) =>
              prev.map((n) => ({ ...n, status: 'completed' }))
            );
            setTasks((prev) =>
              prev.map((t) =>
                t.id === newTask.id ? { ...t, status: 'completed' } : t
              )
            );
            setIsProcessing(false);
          }, 1000);
        }
      }, index * 2000);
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <Brain className="w-8 h-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">
              Gia - General Intelligence Assistant
            </h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="space-y-8">
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