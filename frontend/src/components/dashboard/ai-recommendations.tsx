/**
 * AI Recommendations Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  SparklesIcon, 
  XMarkIcon, 
  CheckIcon, 
  ChevronRightIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/button';
import { useConstitutionalCompliance } from '@/contexts/constitutional-context';
import { usePersonalization } from '@/contexts/personalization-context';
import type { AIRecommendation } from '@/types';

interface AIRecommendationsProps {
  recommendations: AIRecommendation[];
  onExecute: (recommendationId: string) => void;
  onDismiss: (recommendationId: string) => void;
  isExecuting?: boolean;
  isDismissing?: boolean;
}

const impactColors = {
  high: 'border-red-500 bg-red-50',
  medium: 'border-yellow-500 bg-yellow-50',
  low: 'border-blue-500 bg-blue-50',
};

const impactIcons = {
  high: ExclamationTriangleIcon,
  medium: InformationCircleIcon,
  low: InformationCircleIcon,
};

export function AIRecommendations({
  recommendations,
  onExecute,
  onDismiss,
  isExecuting = false,
  isDismissing = false
}: AIRecommendationsProps) {
  const [expandedRecommendation, setExpandedRecommendation] = useState<string | null>(null);
  const { compliance } = useConstitutionalCompliance();
  const { preferences } = usePersonalization();

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center space-x-2 text-gray-500">
          <SparklesIcon className="h-5 w-5" />
          <span>No AI recommendations available</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900 flex items-center space-x-2">
          <SparklesIcon className="h-5 w-5 text-constitutional-600" />
          <span>AI Recommendations</span>
        </h3>
        <span className="text-sm text-gray-500">
          {recommendations.length} suggestion{recommendations.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-3">
        <AnimatePresence>
          {recommendations.map((recommendation) => {
            const ImpactIcon = impactIcons[recommendation.impact as keyof typeof impactIcons];
            const isExpanded = expandedRecommendation === recommendation.id;

            return (
              <motion.div
                key={recommendation.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`border rounded-lg p-4 transition-all duration-200 ${
                  impactColors[recommendation.impact as keyof typeof impactColors]
                }`}
              >
                <div className="flex items-start space-x-3">
                  <ImpactIcon className="h-5 w-5 mt-0.5 text-gray-600" />
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {recommendation.title}
                      </h4>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          recommendation.impact === 'high' ? 'bg-red-100 text-red-800' :
                          recommendation.impact === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {recommendation.impact}
                        </span>
                        {recommendation.constitutionalCompliance.compliant && (
                          <span className="px-2 py-1 text-xs bg-constitutional-100 text-constitutional-800 rounded-full">
                            Constitutional
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-600 mt-1">
                      {recommendation.description}
                    </p>

                    {recommendation.impact && (
                      <div className="mt-2 text-xs text-gray-500">
                        <span className="font-medium">Impact:</span> {recommendation.impact}
                      </div>
                    )}

                    {recommendation.confidence && (
                      <div className="mt-1 text-xs text-gray-500">
                        <span className="font-medium">Confidence:</span> {(recommendation.confidence * 100).toFixed(1)}%
                      </div>
                    )}

                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="mt-3 pt-3 border-t border-gray-200"
                        >
                          {recommendation.description && (
                            <div className="mb-3">
                              <h5 className="text-xs font-medium text-gray-700 mb-1">
                                Description:
                              </h5>
                              <p className="text-xs text-gray-600">
                                {recommendation.description}
                              </p>
                            </div>
                          )}

                          <div className="mb-3">
                            <h5 className="text-xs font-medium text-gray-700 mb-1">
                              Confidence: {Math.round(recommendation.confidence * 100)}%
                            </h5>
                            <h5 className="text-xs font-medium text-gray-700 mb-1">
                              Effort: {recommendation.effort}
                            </h5>
                          </div>

                          {recommendation.metadata && (
                            <div className="text-xs text-gray-500">
                              <span className="font-medium">Source:</span> {recommendation.metadata.source}
                              {recommendation.metadata.model && (
                                <span className="ml-2">
                                  <span className="font-medium">Model:</span> {recommendation.metadata.model}
                                </span>
                              )}
                            </div>
                          )}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>

                <div className="flex items-center justify-between mt-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setExpandedRecommendation(
                      isExpanded ? null : recommendation.id
                    )}
                    className="text-xs"
                  >
                    {isExpanded ? 'Show Less' : 'Show More'}
                    <ChevronRightIcon className={`h-3 w-3 ml-1 transition-transform ${
                      isExpanded ? 'rotate-90' : ''
                    }`} />
                  </Button>

                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onDismiss(recommendation.id)}
                      disabled={isDismissing}
                      className="text-xs"
                    >
                      <XMarkIcon className="h-3 w-3 mr-1" />
                      Dismiss
                    </Button>
                    
                    <Button
                      constitutional={recommendation.constitutionalCompliance.compliant}
                      size="sm"
                      onClick={() => onExecute(recommendation.id)}
                      disabled={isExecuting || !compliance.compliant}
                      className="text-xs"
                    >
                      <CheckIcon className="h-3 w-3 mr-1" />
                      Execute
                    </Button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {!compliance.compliant && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <ExclamationTriangleIcon className="h-4 w-4 text-red-600" />
            <span className="text-sm text-red-800">
              Constitutional compliance required to execute recommendations
            </span>
          </div>
        </div>
      )}
    </div>
  );
}