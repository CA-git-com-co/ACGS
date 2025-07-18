/**
 * Workflow Preview Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React, { memo } from 'react';

interface WorkflowPreviewProps {
  steps?: string[];
  title?: string;
}

const WorkflowPreview: React.FC<WorkflowPreviewProps> = memo(({ 
  steps = [], 
  title = 'Workflow Preview' 
}) => {
  return (
    <div className="p-4 border rounded-lg bg-gray-50 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="space-y-3">
        {steps.length > 0 ? (
          steps.map((step, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                {index + 1}
              </div>
              <div className="flex-1">
                <div className="bg-white p-3 rounded-lg border border-gray-200">
                  <span className="text-sm">{step}</span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="h-32 bg-gray-100 rounded flex items-center justify-center">
            <span className="text-gray-500">Workflow Preview</span>
          </div>
        )}
      </div>
    </div>
  );
});

WorkflowPreview.displayName = 'WorkflowPreview';

export default WorkflowPreview;