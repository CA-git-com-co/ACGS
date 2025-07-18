/**
 * Workflow Component for No-Code Builder
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React, { memo } from 'react';

interface WorkflowComponentProps {
  steps?: string[];
  title?: string;
}

const WorkflowComponent: React.FC<WorkflowComponentProps> = memo(({ 
  steps = [], 
  title = 'Workflow' 
}) => {
  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <div className="space-y-2">
        {steps.length > 0 ? (
          steps.map((step, index) => (
            <div key={index} className="flex items-center space-x-2">
              <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm">
                {index + 1}
              </div>
              <span>{step}</span>
            </div>
          ))
        ) : (
          <div className="h-32 bg-gray-100 rounded flex items-center justify-center">
            <span className="text-gray-500">Workflow Component</span>
          </div>
        )}
      </div>
    </div>
  );
});

WorkflowComponent.displayName = 'WorkflowComponent';

export default WorkflowComponent;