/**
 * Advanced Form Builder Preview Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import React, { memo } from 'react';

interface AdvancedFormBuilderPreviewProps {
  fields?: any[];
  title?: string;
}

const AdvancedFormBuilderPreview: React.FC<AdvancedFormBuilderPreviewProps> = memo(({ 
  fields = [], 
  title = 'Form Preview' 
}) => {
  return (
    <div className="p-4 border rounded-lg bg-gray-50 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="space-y-4">
        {fields.length > 0 ? (
          fields.map((field, index) => (
            <div key={index} className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                {field.label || `Field ${index + 1}`}
              </label>
              <div className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white">
                <span className="text-gray-400">
                  {field.placeholder || `${field.type || 'text'} input`}
                </span>
              </div>
            </div>
          ))
        ) : (
          <div className="h-32 bg-gray-100 rounded flex items-center justify-center">
            <span className="text-gray-500">Form Preview</span>
          </div>
        )}
        <div className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md text-center">
          Submit Button (Preview)
        </div>
      </div>
    </div>
  );
});

AdvancedFormBuilderPreview.displayName = 'AdvancedFormBuilderPreview';

export default AdvancedFormBuilderPreview;