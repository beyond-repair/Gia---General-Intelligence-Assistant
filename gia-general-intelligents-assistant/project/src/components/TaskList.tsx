import React from 'react';
import { Task } from '../types';
import { CheckCircle, XCircle, Clock, PlayCircle } from 'lucide-react';

interface TaskListProps {
  tasks: Task[];
}

export function TaskList({ tasks }: TaskListProps) {
  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-green-500" />;
      case 'failed':
        return <XCircle className="text-red-500" />;
      case 'processing':
        return <PlayCircle className="text-blue-500" />;
      default:
        return <Clock className="text-gray-500" />;
    }
  };

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <div
          key={task.id}
          className="bg-white rounded-lg shadow-md p-4 border border-gray-200"
        >
          <div className="flex items-center gap-3">
            {getStatusIcon(task.status)}
            <div className="flex-1">
              <h3 className="font-medium">{task.description}</h3>
              <div className="mt-2 space-y-2">
                {task.steps.map((step) => (
                  <div
                    key={step.id}
                    className="text-sm flex items-center gap-2 text-gray-600"
                  >
                    {getStatusIcon(step.status)}
                    <span>{step.name}</span>
                    {step.output && (
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                        {step.output}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
            <span className="text-sm text-gray-500">
              {new Date(task.createdAt).toLocaleTimeString()}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}