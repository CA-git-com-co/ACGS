/**
 * Performance Dashboard Component
 * 
 * Real-time dashboard for monitoring application performance metrics,
 * baseline comparisons, and migration impact analysis.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  performanceMetrics, 
  PerformanceBaseline, 
  PerformanceMetric, 
  PerformanceSummary,
  PerformanceComparison 
} from '../../services/performanceMetrics';

// Performance metric card component
const MetricCard: React.FC<{
  title: string;
  value: number;
  unit: string;
  threshold?: number;
  trend?: 'up' | 'down' | 'stable';
  description?: string;
}> = ({ title, value, unit, threshold, trend, description }) => {
  const isGood = threshold ? value <= threshold : true;
  const statusColor = isGood ? 'text-green-600' : 'text-red-600';
  const bgColor = isGood ? 'bg-green-50' : 'bg-red-50';
  const borderColor = isGood ? 'border-green-200' : 'border-red-200';

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <span className="text-red-500">↗</span>;
      case 'down':
        return <span className="text-green-500">↘</span>;
      case 'stable':
        return <span className="text-gray-500">→</span>;
      default:
        return null;
    }
  };

  return (
    <div className={`p-4 rounded-lg border ${bgColor} ${borderColor}`}>
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-sm font-medium text-gray-700">{title}</h3>
          <div className={`text-2xl font-bold ${statusColor}`}>
            {value.toFixed(value < 10 ? 2 : 0)}{unit}
          </div>
          {threshold && (
            <div className="text-xs text-gray-500 mt-1">
              Threshold: {threshold}{unit}
            </div>
          )}
        </div>
        <div className="flex items-center space-x-1">
          {getTrendIcon()}
          {!isGood && (
            <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          )}
        </div>
      </div>
      {description && (
        <div className="text-xs text-gray-600 mt-2">{description}</div>
      )}
    </div>
  );
};

// Web Vitals component
const WebVitals: React.FC<{ summary: PerformanceSummary }> = ({ summary }) => {
  const vitals = [
    {
      name: 'First Contentful Paint',
      value: summary.firstContentfulPaint,
      unit: 'ms',
      threshold: 1800,
      description: 'Time until first content appears'
    },
    {
      name: 'Largest Contentful Paint',
      value: summary.largestContentfulPaint,
      unit: 'ms',
      threshold: 2500,
      description: 'Time until largest content appears'
    },
    {
      name: 'First Input Delay',
      value: summary.firstInputDelay,
      unit: 'ms',
      threshold: 100,
      description: 'Time until page becomes interactive'
    },
    {
      name: 'Cumulative Layout Shift',
      value: summary.cumulativeLayoutShift,
      unit: '',
      threshold: 0.1,
      description: 'Visual stability score'
    }
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-xl font-semibold mb-4">Core Web Vitals</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {vitals.map(vital => (
          <MetricCard
            key={vital.name}
            title={vital.name}
            value={vital.value}
            unit={vital.unit}
            threshold={vital.threshold}
            description={vital.description}
          />
        ))}
      </div>
    </div>
  );
};

// Performance comparison component
const PerformanceComparison: React.FC<{ comparison: PerformanceComparison | null }> = ({ 
  comparison 
}) => {
  if (!comparison) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h2 className="text-xl font-semibold mb-4">Performance Comparison</h2>
        <div className="text-center text-gray-500 py-8">
          No baseline available for comparison
        </div>
      </div>
    );
  }

  const getImprovementColor = (status: string) => {
    switch (status) {
      case 'improved': return 'text-green-600';
      case 'degraded': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getImprovementIcon = (status: string) => {
    switch (status) {
      case 'improved': return '↗';
      case 'degraded': return '↘';
      default: return '→';
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Performance Comparison</h2>
        <div className="text-sm text-gray-600">
          vs. {comparison.baseline.name}
        </div>
      </div>
      
      <div className="mb-4 p-4 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className={`text-3xl font-bold ${comparison.overallScore > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {comparison.overallScore > 0 ? '+' : ''}{comparison.overallScore.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Overall Performance Change</div>
        </div>
      </div>

      <div className="space-y-3">
        {Object.entries(comparison.improvements).map(([metric, data]) => (
          <div key={metric} className="flex justify-between items-center py-2 border-b border-gray-100">
            <div className="flex-1">
              <div className="font-medium text-gray-900">
                {metric.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
              </div>
              <div className="text-sm text-gray-600">
                {data.baseline.toFixed(2)} → {data.current.toFixed(2)}
              </div>
            </div>
            <div className={`text-right ${getImprovementColor(data.status)}`}>
              <div className="font-medium">
                {getImprovementIcon(data.status)} {Math.abs(data.percentage).toFixed(1)}%
              </div>
              <div className="text-xs">
                {data.status}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Baseline management component
const BaselineManagement: React.FC<{
  baselines: PerformanceBaseline[];
  onCreateBaseline: (name: string) => void;
  onSelectBaseline: (id: string) => void;
  selectedBaselineId?: string;
}> = ({ baselines, onCreateBaseline, onSelectBaseline, selectedBaselineId }) => {
  const [newBaselineName, setNewBaselineName] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  const handleCreateBaseline = () => {
    if (newBaselineName.trim()) {
      onCreateBaseline(newBaselineName.trim());
      setNewBaselineName('');
      setShowCreateForm(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Performance Baselines</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Create Baseline
        </button>
      </div>

      {showCreateForm && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex space-x-2">
            <input
              type="text"
              value={newBaselineName}
              onChange={(e) => setNewBaselineName(e.target.value)}
              placeholder="Baseline name (e.g., 'Pre-migration', 'Post-optimization')"
              className="flex-1 px-3 py-2 border rounded-md"
            />
            <button
              onClick={handleCreateBaseline}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Create
            </button>
            <button
              onClick={() => setShowCreateForm(false)}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="space-y-2">
        {baselines.length === 0 ? (
          <div className="text-center text-gray-500 py-4">
            No baselines created yet
          </div>
        ) : (
          baselines.map(baseline => (
            <div
              key={baseline.id}
              className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                selectedBaselineId === baseline.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => onSelectBaseline(baseline.id)}
            >
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-medium">{baseline.name}</div>
                  <div className="text-sm text-gray-600">
                    {new Date(baseline.timestamp).toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-500">
                    {baseline.environment} • v{baseline.version}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">
                    {baseline.summary.userSatisfactionScore.toFixed(0)}/100
                  </div>
                  <div className="text-xs text-gray-500">Score</div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// Main performance dashboard component
export const PerformanceDashboard: React.FC = () => {
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [baselines, setBaselines] = useState<PerformanceBaseline[]>([]);
  const [selectedBaselineId, setSelectedBaselineId] = useState<string>('');
  const [comparison, setComparison] = useState<PerformanceComparison | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Initialize performance monitoring
  useEffect(() => {
    const initializePerformance = async () => {
      try {
        await performanceMetrics.initialize();
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize performance monitoring:', error);
      }
    };

    initializePerformance();

    return () => {
      performanceMetrics.cleanup();
    };
  }, []);

  // Load data
  const loadData = useCallback(() => {
    if (!isInitialized) return;

    try {
      // Get current performance summary
      const endTime = Date.now();
      const startTime = endTime - 3600000; // Last hour
      const currentSummary = performanceMetrics.getPerformanceSummary(startTime, endTime);
      setSummary(currentSummary);

      // Get baselines
      const currentBaselines = performanceMetrics.getBaselines();
      setBaselines(currentBaselines);

      // Update comparison if baseline is selected
      if (selectedBaselineId) {
        const comp = performanceMetrics.compareWithBaseline(selectedBaselineId);
        setComparison(comp);
      }

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load performance data:', error);
    }
  }, [isInitialized, selectedBaselineId]);

  // Auto-refresh data
  useEffect(() => {
    loadData();

    const interval = setInterval(loadData, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, [loadData]);

  // Create baseline
  const handleCreateBaseline = useCallback(async (name: string) => {
    try {
      const baseline = await performanceMetrics.collectBaseline(name);
      setBaselines(prev => [baseline, ...prev]);
      
      // Auto-select the new baseline
      setSelectedBaselineId(baseline.id);
    } catch (error) {
      console.error('Failed to create baseline:', error);
    }
  }, []);

  // Select baseline for comparison
  const handleSelectBaseline = useCallback((id: string) => {
    setSelectedBaselineId(id);
    const comp = performanceMetrics.compareWithBaseline(id);
    setComparison(comp);
  }, []);

  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600">Initializing performance monitoring...</span>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Performance Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Monitor application performance and track migration improvements
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {lastUpdate && (
              <div className="text-sm text-gray-500">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </div>
            )}
            <button
              onClick={loadData}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Web Vitals */}
        {summary && <WebVitals summary={summary} />}

        {/* Performance Comparison and Baseline Management */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <PerformanceComparison comparison={comparison} />
          <BaselineManagement
            baselines={baselines}
            onCreateBaseline={handleCreateBaseline}
            onSelectBaseline={handleSelectBaseline}
            selectedBaselineId={selectedBaselineId}
          />
        </div>

        {/* Additional Metrics */}
        {summary && (
          <div className="mt-6 bg-white p-6 rounded-lg shadow-sm border">
            <h2 className="text-xl font-semibold mb-4">Additional Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                title="Bundle Size"
                value={summary.bundleSize}
                unit="KB"
                threshold={1000}
                description="Total JavaScript bundle size"
              />
              <MetricCard
                title="Memory Usage"
                value={summary.memoryUsage}
                unit="MB"
                threshold={100}
                description="Current memory consumption"
              />
              <MetricCard
                title="Network Requests"
                value={summary.networkRequests}
                unit=""
                description="Total network requests made"
              />
              <MetricCard
                title="Error Rate"
                value={summary.errorRate}
                unit="%"
                threshold={5}
                description="Percentage of failed operations"
              />
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Performance Dashboard v1.0 - Collection interval: 1 minute</p>
          <p>Targets: &lt;3s load time, &lt;1.8s FCP, &lt;2.5s LCP, &lt;100ms FID, &lt;0.1 CLS</p>
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard;
