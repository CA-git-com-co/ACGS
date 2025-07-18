/**
 * Dashboard Preview Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React, { memo } from 'react';

interface DashboardPreviewProps {
  widgets?: any[];
  title?: string;
}

const DashboardPreview: React.FC<DashboardPreviewProps> = memo(({ 
  widgets = [], 
  title = 'Dashboard Preview' 
}) => {
  return (
    <div className="p-4 border rounded-lg bg-gray-50 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {widgets.length > 0 ? (
          widgets.map((widget, index) => (
            <div key={index} className="p-4 bg-white rounded-lg shadow-sm border">
              <h4 className="font-medium text-gray-800">
                {widget.title || `Widget ${index + 1}`}
              </h4>
              <div className="mt-2 h-24 bg-gray-100 rounded flex items-center justify-center">
                <span className="text-gray-500 text-sm">
                  {widget.type || 'Chart'} Preview
                </span>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-2 h-32 bg-gray-100 rounded flex items-center justify-center">
            <span className="text-gray-500">Dashboard Preview</span>
          </div>
        )}
      </div>
    </div>
  );
});

DashboardPreview.displayName = 'DashboardPreview';

export default DashboardPreview;