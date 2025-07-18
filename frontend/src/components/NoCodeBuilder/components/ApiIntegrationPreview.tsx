/**
 * API Integration Preview Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React, { memo } from 'react';

interface ApiIntegrationPreviewProps {
  apis?: any[];
  title?: string;
}

const ApiIntegrationPreview: React.FC<ApiIntegrationPreviewProps> = memo(({ 
  apis = [], 
  title = 'API Integration Preview' 
}) => {
  return (
    <div className="p-4 border rounded-lg bg-gray-50 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="space-y-3">
        {apis.length > 0 ? (
          apis.map((api, index) => (
            <div key={index} className="p-3 border rounded-lg bg-white">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-800">
                    {api.name || `API ${index + 1}`}
                  </h4>
                  <p className="text-sm text-gray-600">
                    {api.endpoint || 'No endpoint configured'}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    api.status === 'active' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {api.status || 'inactive'}
                  </span>
                  <span className="text-gray-400 text-sm">Preview</span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="h-32 bg-gray-100 rounded flex items-center justify-center">
            <span className="text-gray-500">API Integration Preview</span>
          </div>
        )}
      </div>
    </div>
  );
});

ApiIntegrationPreview.displayName = 'ApiIntegrationPreview';

export default ApiIntegrationPreview;