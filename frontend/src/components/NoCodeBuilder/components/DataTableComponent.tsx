/**
 * Data Table Component for No-Code Builder
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React, { memo } from 'react';

interface DataTableComponentProps {
  data?: any[];
  columns?: string[];
  title?: string;
}

const DataTableComponent: React.FC<DataTableComponentProps> = memo(({ 
  data = [], 
  columns = [], 
  title = 'Data Table' 
}) => {
  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <div className="overflow-x-auto">
        {data.length > 0 && columns.length > 0 ? (
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                {columns.map((column, index) => (
                  <th key={index} className="border border-gray-300 px-4 py-2 text-left">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr key={index}>
                  {columns.map((column, colIndex) => (
                    <td key={colIndex} className="border border-gray-300 px-4 py-2">
                      {row[column] || '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="h-32 bg-gray-100 rounded flex items-center justify-center">
            <span className="text-gray-500">Data Table Component</span>
          </div>
        )}
      </div>
    </div>
  );
});

DataTableComponent.displayName = 'DataTableComponent';

export default DataTableComponent;