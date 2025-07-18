/**
 * Governance Insights Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LightBulbIcon, 
  ChartBarIcon,
  UsersIcon,
  DocumentTextIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { usePersonalization } from '@/contexts/personalization-context';
import type { GovernanceInsight } from '@/types';

interface GovernanceMetric {
  name: string;
  value: number;
  trend?: number;
  unit?: string;
  type?: string;
  description?: string;
}

interface GovernanceInsightsProps {
  insights: GovernanceInsight;
  isLoading?: boolean;
}

const metricIcons = {
  agent_performance: ChartBarIcon,
  user_engagement: UsersIcon,
  policy_compliance: DocumentTextIcon,
  response_time: ClockIcon,
  default: LightBulbIcon
};

export function GovernanceInsights({ insights, isLoading = false }: GovernanceInsightsProps) {
  const [expandedInsight, setExpandedInsight] = useState<string | null>(null);
  const { preferences } = usePersonalization();

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!insights) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center space-x-2 text-gray-500">
          <LightBulbIcon className="h-5 w-5" />
          <span>No governance insights available</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900 flex items-center space-x-2">
          <LightBulbIcon className="h-5 w-5 text-constitutional-600" />
          <span>Governance Insights</span>
        </h3>
        <span className="text-sm text-gray-500">
          {insights.createdAt && <span suppressHydrationWarning>{new Date(insights.createdAt).toLocaleDateString()}</span>}
        </span>
      </div>

      {/* Key Metrics */}
      {insights.data?.keyMetrics && insights.data.keyMetrics.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Key Metrics</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {insights.data.keyMetrics.map((metric: GovernanceMetric, index: number) => {
              const IconComponent = metricIcons[metric.type as keyof typeof metricIcons] || metricIcons.default;
              
              return (
                <motion.div
                  key={metric.name}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <IconComponent className="h-4 w-4 text-constitutional-600" />
                      <span className="text-sm font-medium text-gray-700">
                        {metric.name}
                      </span>
                    </div>
                    {metric.trend && (
                      <div className="flex items-center space-x-1">
                        {metric.trend > 0 ? (
                          <ArrowTrendingUpIcon className="h-3 w-3 text-green-500" />
                        ) : (
                          <ArrowTrendingDownIcon className="h-3 w-3 text-red-500" />
                        )}
                        <span className={`text-xs ${metric.trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {Math.abs(metric.trend)}%
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="text-2xl font-bold text-gray-900 mb-1">
                    {metric.value}
                    {metric.unit && <span className="text-lg text-gray-500 ml-1">{metric.unit}</span>}
                  </div>
                  
                  {metric.description && (
                    <p className="text-xs text-gray-500">
                      {metric.description}
                    </p>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* Insights */}
      {insights.data?.insights && insights.data.insights.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">AI-Generated Insights</h4>
          <div className="space-y-3">
            {insights.data.insights.map((insight: any, index: number) => {
              const isExpanded = expandedInsight === insight.id;
              
              return (
                <motion.div
                  key={insight.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg ${
                      insight.type === 'warning' ? 'bg-yellow-100' :
                      insight.type === 'success' ? 'bg-green-100' :
                      insight.type === 'info' ? 'bg-blue-100' :
                      'bg-gray-100'
                    }`}>
                      <LightBulbIcon className={`h-4 w-4 ${
                        insight.type === 'warning' ? 'text-yellow-600' :
                        insight.type === 'success' ? 'text-green-600' :
                        insight.type === 'info' ? 'text-blue-600' :
                        'text-gray-600'
                      }`} />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h5 className="text-sm font-medium text-gray-900">
                          {insight.title}
                        </h5>
                        <div className="flex items-center space-x-2">
                          {insight.confidence && (
                            <span className="text-xs text-gray-500">
                              {(insight.confidence * 100).toFixed(0)}% confidence
                            </span>
                          )}
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            insight.priority === 'high' ? 'bg-red-100 text-red-800' :
                            insight.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {insight.priority}
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-sm text-gray-600 mt-1">
                        {insight.summary}
                      </p>

                      <AnimatePresence>
                        {isExpanded && insight.details && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="mt-3 pt-3 border-t border-gray-200"
                          >
                            <div className="text-sm text-gray-700">
                              {insight.details.analysis && (
                                <div className="mb-3">
                                  <h6 className="font-medium mb-1">Analysis:</h6>
                                  <p>{insight.details.analysis}</p>
                                </div>
                              )}
                              
                              {insight.details.recommendations && insight.details.recommendations.length > 0 && (
                                <div className="mb-3">
                                  <h6 className="font-medium mb-1">Recommendations:</h6>
                                  <ul className="list-disc list-inside space-y-1 text-sm">
                                    {insight.details.recommendations.map((rec: string, idx: number) => (
                                      <li key={idx}>{rec}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              
                              {insight.details.impactAreas && insight.details.impactAreas.length > 0 && (
                                <div>
                                  <h6 className="font-medium mb-1">Impact Areas:</h6>
                                  <div className="flex flex-wrap gap-1">
                                    {insight.details.impactAreas.map((area: string, idx: number) => (
                                      <span key={idx} className="px-2 py-1 text-xs bg-gray-100 rounded">
                                        {area}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                      
                      <button
                        onClick={() => setExpandedInsight(isExpanded ? null : insight.id)}
                        className="flex items-center space-x-1 text-xs text-constitutional-600 hover:text-constitutional-700 mt-2"
                      >
                        <span>{isExpanded ? 'Show Less' : 'Show More'}</span>
                        <ChevronRightIcon className={`h-3 w-3 transition-transform ${
                          isExpanded ? 'rotate-90' : ''
                        }`} />
                      </button>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* Trend Analysis */}
      {insights.data?.trendAnalysis && (
        <div className="pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Trend Analysis</h4>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-700">
              {insights.data.trendAnalysis.summary}
            </p>
            
            {insights.data.trendAnalysis.predictions && insights.data.trendAnalysis.predictions.length > 0 && (
              <div className="mt-3">
                <h6 className="text-xs font-medium text-gray-600 mb-2">Predictions:</h6>
                <ul className="text-sm text-gray-600 space-y-1">
                  {insights.data.trendAnalysis.predictions.map((prediction: string, idx: number) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <span className="text-constitutional-600 mt-1">•</span>
                      <span>{prediction}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}