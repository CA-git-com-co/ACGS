/**
 * API Integration Hub Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React, { memo } from 'react';

interface ApiIntegrationHubProps {
  apis?: any[];
  title?: string;
}

const ApiIntegrationHub: React.FC<ApiIntegrationHubProps> = memo(({ 
  apis = [], 
  title = 'API Integration Hub' 
}) => {
  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="space-y-3">
        {apis.length > 0 ? (
          apis.map((api, index) => (
            <div key={index} className="p-3 border rounded-lg bg-gray-50">
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
                  <button className="text-blue-600 hover:text-blue-800 text-sm">
                    Configure
                  </button>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="h-32 bg-gray-100 rounded flex items-center justify-center">
            <span className="text-gray-500">API Integration Hub</span>
          </div>
        )}
      </div>
    </div>
  );
});

ApiIntegrationHub.displayName = 'ApiIntegrationHub';

export default ApiIntegrationHub;