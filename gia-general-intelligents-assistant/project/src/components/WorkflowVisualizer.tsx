import React from 'react';
import { WorkflowNode } from '../types';
import { Circle, ArrowRight } from 'lucide-react';

interface WorkflowVisualizerProps {
  nodes: WorkflowNode[];
}

export function WorkflowVisualizer({ nodes }: WorkflowVisualizerProps) {
  return (
    <div className="flex items-center gap-4 overflow-x-auto py-6 px-4">
      {nodes.map((node, index) => (
        <React.Fragment key={node.name}>
          <div className="flex flex-col items-center min-w-[150px]">
            <div
              className={`p-4 rounded-lg ${
                node.status === 'active'
                  ? 'bg-blue-100 border-blue-500'
                  : node.status === 'completed'
                  ? 'bg-green-100 border-green-500'
                  : node.status === 'error'
                  ? 'bg-red-100 border-red-500'
                  : 'bg-gray-100 border-gray-500'
              } border-2`}
            >
              <div className="flex items-center gap-2">
                <Circle
                  size={16}
                  className={
                    node.status === 'active'
                      ? 'text-blue-500'
                      : node.status === 'completed'
                      ? 'text-green-500'
                      : node.status === 'error'
                      ? 'text-red-500'
                      : 'text-gray-500'
                  }
                />
                <span className="font-medium">{node.name}</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">{node.description}</p>
            </div>
          </div>
          {index < nodes.length - 1 && (
            <ArrowRight size={24} className="text-gray-400 flex-shrink-0" />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}