/**
 * Chart Component for No-Code Builder
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React, { memo } from 'react';

interface ChartComponentProps {
  data?: any[];
  type?: 'line' | 'bar' | 'pie';
  title?: string;
}

const ChartComponent: React.FC<ChartComponentProps> = memo(({ 
  data = [], 
  type = 'line', 
  title = 'Chart' 
}) => {
  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
        <span className="text-gray-500">Chart Component - {type}</span>
      </div>
    </div>
  );
});

ChartComponent.displayName = 'ChartComponent';

export default ChartComponent;