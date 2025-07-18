/**
 * Data Table Preview Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React, { memo } from 'react';

interface DataTablePreviewProps {
  data?: any[];
  columns?: string[];
  title?: string;
}

const DataTablePreview: React.FC<DataTablePreviewProps> = memo(({ 
  data = [], 
  columns = [], 
  title = 'Data Table Preview' 
}) => {
  return (
    <div className="p-4 border rounded-lg bg-gray-50 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="overflow-x-auto">
        {data.length > 0 && columns.length > 0 ? (
          <table className="w-full border-collapse border border-gray-200">
            <thead>
              <tr className="bg-gray-100">
                {columns.map((column, index) => (
                  <th key={index} className="border border-gray-200 px-4 py-2 text-left text-sm font-medium">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.slice(0, 3).map((row, index) => (
                <tr key={index} className="bg-white">
                  {columns.map((column, colIndex) => (
                    <td key={colIndex} className="border border-gray-200 px-4 py-2 text-sm">
                      {row[column] || '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="h-32 bg-gray-100 rounded flex items-center justify-center">
            <span className="text-gray-500">Data Table Preview</span>
          </div>
        )}
      </div>
    </div>
  );
});

DataTablePreview.displayName = 'DataTablePreview';

export default DataTablePreview;