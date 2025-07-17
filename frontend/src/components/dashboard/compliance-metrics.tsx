/**
 * Compliance Metrics Component
 * Constitutional Hash: cdd01ef066bc6cf2
 */

'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline';
import { useConstitutionalCompliance } from '@/contexts/constitutional-context';
import type { ConstitutionalCompliance } from '@/types';

interface ComplianceMetricsProps {
  metrics: ConstitutionalCompliance;
  isLoading?: boolean;
}

export function ComplianceMetrics({ metrics, isLoading = false }: ComplianceMetricsProps) {
  const { compliance } = useConstitutionalCompliance();

  const scoreColor = useMemo(() => {
    const score = metrics ? Math.round(metrics.score * 100) : 0;
    if (score >= 95) return 'text-green-600';
    if (score >= 85) return 'text-yellow-600';
    if (score >= 75) return 'text-orange-600';
    return 'text-red-600';
  }, [metrics?.score]);

  const scoreBgColor = useMemo(() => {
    const score = metrics ? Math.round(metrics.score * 100) : 0;
    if (score >= 95) return 'bg-green-100';
    if (score >= 85) return 'bg-yellow-100';
    if (score >= 75) return 'bg-orange-100';
    return 'bg-red-100';
  }, [metrics?.score]);

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

  if (!metrics) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center space-x-2 text-gray-500">
          <ShieldCheckIcon className="h-5 w-5" />
          <span>No compliance metrics available</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900 flex items-center space-x-2">
          <ShieldCheckIcon className="h-5 w-5 text-constitutional-600" />
          <span>Constitutional Compliance</span>
        </h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">Hash:</span>
          <code className="text-xs bg-gray-100 px-2 py-1 rounded">
            {metrics.hash}
          </code>
        </div>
      </div>

      {/* Overall Score */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Score</span>
          <div className="flex items-center space-x-2">
            <span className={`text-2xl font-bold ${scoreColor}`}>
              {Math.round(metrics.score * 100)}%
            </span>
          </div>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2">
          <motion.div
            className={`h-2 rounded-full ${scoreBgColor.replace('bg-', 'bg-').replace('-100', '-500')}`}
            initial={{ width: 0 }}
            animate={{ width: `${Math.round(metrics.score * 100)}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Compliance Categories */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-gray-700 flex items-center space-x-2">
          <ChartBarIcon className="h-4 w-4" />
          <span>Compliance Categories</span>
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { name: 'Constitutional Compliance', score: Math.round(metrics.score * 100), status: metrics.compliant ? 'compliant' : 'non-compliant' },
            { name: 'Hash Validation', score: metrics.hash === 'cdd01ef066bc6cf2' ? 100 : 0, status: metrics.hash === 'cdd01ef066bc6cf2' ? 'compliant' : 'non-compliant' }
          ].map((category, index) => (
            <motion.div
              key={category.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="border border-gray-200 rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  {category.name}
                </span>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-medium ${
                    category.score >= 95 ? 'text-green-600' :
                    category.score >= 85 ? 'text-yellow-600' :
                    category.score >= 75 ? 'text-orange-600' :
                    'text-red-600'
                  }`}>
                    {category.score}%
                  </span>
                  {category.status === 'compliant' ? (
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  ) : category.status === 'warning' ? (
                    <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500" />
                  ) : (
                    <XCircleIcon className="h-4 w-4 text-red-500" />
                  )}
                </div>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <motion.div
                  className={`h-1.5 rounded-full ${
                    category.score >= 95 ? 'bg-green-500' :
                    category.score >= 85 ? 'bg-yellow-500' :
                    category.score >= 75 ? 'bg-orange-500' :
                    'bg-red-500'
                  }`}
                  initial={{ width: 0 }}
                  animate={{ width: `${category.score}%` }}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                />
              </div>

              {category.name === 'Constitutional Compliance' && metrics.violations.length > 0 && (
                <div className="mt-2">
                  <span className="text-xs text-gray-500">
                    {metrics.violations.length} violation{metrics.violations.length !== 1 ? 's' : ''}
                  </span>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Recent Violations */}
      {metrics.violations && metrics.violations.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center space-x-2">
            <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
            <span>Recent Violations</span>
          </h4>
          <div className="space-y-2">
            {metrics.violations.slice(0, 3).map((violation, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-red-50 rounded-lg">
                <ExclamationTriangleIcon className="h-4 w-4 text-red-500 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-red-800 truncate">
                    {violation}
                  </p>
                  <p className="text-xs text-red-600">
                    {new Date(metrics.lastValidated).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Last Updated */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Last updated: {new Date(metrics.lastValidated).toLocaleString()}
        </p>
      </div>
    </div>
  );
}