/**
 * API Compatibility Dashboard Component
 *
 * Real-time dashboard for monitoring API compatibility between legacy and new implementations,
 * tracking user adoption, and identifying integration issues during migration.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  apiCompatibilityMonitor,
  CompatibilityTestResult,
  UserAdoptionMetrics,
  MigrationProgress,
  CompatibilityIssue
} from '../../services/apiCompatibilityMonitor';

// Compatibility status indicator
const CompatibilityStatus: React.FC<{ compatible: boolean; issues: number }> = ({
  compatible,
  issues
}) => {
  if (compatible) {
    return (
      <div className="flex items-center space-x-2">
        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
        <span className="text-green-700 font-medium">Compatible</span>
      </div>
    );
  }

  const severity = issues > 5 ? 'critical' : issues > 2 ? 'high' : 'medium';
  const colors = {
    critical: 'bg-red-500 text-red-700',
    high: 'bg-orange-500 text-orange-700',
    medium: 'bg-yellow-500 text-yellow-700'
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-3 h-3 ${colors[severity].split(' ')[0]} rounded-full`}></div>
      <span className={`font-medium ${colors[severity].split(' ')[1]}`}>{issues} Issues</span>
    </div>
  );
};

// Migration progress bar
const MigrationProgressBar: React.FC<{ progress: MigrationProgress }> = ({ progress }) => {
  const completionRate = (progress.compatibleEndpoints / progress.totalEndpoints) * 100;

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold text-gray-900">{progress.service.toUpperCase()}</h3>
        <span className="text-sm text-gray-600">{completionRate.toFixed(1)}%</span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${completionRate}%` }}
        ></div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-gray-600">Compatible</div>
          <div className="font-medium">
            {progress.compatibleEndpoints}/{progress.totalEndpoints}
          </div>
        </div>
        <div>
          <div className="text-gray-600">Issues</div>
          <div
            className={`font-medium ${progress.activeIssues > 0 ? 'text-red-600' : 'text-green-600'}`}
          >
            {progress.activeIssues}
          </div>
        </div>
        <div>
          <div className="text-gray-600">Adoption</div>
          <div className="font-medium">{progress.adoptionRate.toFixed(1)}%</div>
        </div>
        <div>
          <div className="text-gray-600">ETA</div>
          <div className="font-medium">{progress.estimatedCompletion}</div>
        </div>
      </div>
    </div>
  );
};

// Compatibility issue card
const IssueCard: React.FC<{ issue: CompatibilityIssue; endpoint?: string }> = ({
  issue,
  endpoint
}) => {
  const severityColors = {
    critical: 'bg-red-100 border-red-500 text-red-900',
    high: 'bg-orange-100 border-orange-500 text-orange-900',
    medium: 'bg-yellow-100 border-yellow-500 text-yellow-900',
    low: 'bg-blue-100 border-blue-500 text-blue-900'
  };

  return (
    <div className={`border-l-4 p-3 rounded-r ${severityColors[issue.severity]}`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="font-medium">{issue.type.replace('_', ' ').toUpperCase()}</div>
          <div className="text-sm mt-1">{issue.description}</div>
          {endpoint && <div className="text-xs mt-1 opacity-75">{endpoint}</div>}
          {issue.field && (
            <div className="text-xs mt-1">
              Field: <code className="bg-white bg-opacity-50 px-1 rounded">{issue.field}</code>
            </div>
          )}
        </div>
        <span className="px-2 py-1 text-xs bg-white bg-opacity-50 rounded">
          {issue.severity.toUpperCase()}
        </span>
      </div>
      <div className="text-xs mt-2 opacity-75">Impact: {issue.impact}</div>
    </div>
  );
};

// Adoption metrics chart (simplified)
const AdoptionChart: React.FC<{ metrics: UserAdoptionMetrics[] }> = ({ metrics }) => {
  if (metrics.length === 0) {
    return <div className="text-center text-gray-500 py-8">No adoption data available</div>;
  }

  const latest = metrics[metrics.length - 1];

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border">
      <h3 className="font-semibold text-gray-900 mb-4">Adoption Metrics</h3>

      <div className="grid grid-cols-2 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{latest.adoptionRate.toFixed(1)}%</div>
          <div className="text-sm text-gray-600">Adoption Rate</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{latest.userCount}</div>
          <div className="text-sm text-gray-600">Active Users</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">{latest.sessionCount}</div>
          <div className="text-sm text-gray-600">Sessions</div>
        </div>
        <div className="text-center">
          <div
            className={`text-2xl font-bold ${latest.errorRate > 5 ? 'text-red-600' : 'text-green-600'}`}
          >
            {latest.errorRate.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Error Rate</div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Legacy Usage:</span>
          <span className="font-medium">{latest.legacyUsage}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">New Usage:</span>
          <span className="font-medium">{latest.newUsage}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Avg Response Time:</span>
          <span className="font-medium">{latest.averageResponseTime}ms</span>
        </div>
      </div>
    </div>
  );
};

// Main dashboard component
export const APICompatibilityDashboard: React.FC = () => {
  const [compatibilityReport, setCompatibilityReport] = useState<any>({});
  const [migrationProgress, setMigrationProgress] = useState<Record<string, MigrationProgress>>({});
  const [adoptionMetrics, setAdoptionMetrics] = useState<Record<string, UserAdoptionMetrics[]>>({});
  const [testResults, setTestResults] = useState<Record<string, CompatibilityTestResult[]>>({});
  const [isInitialized, setIsInitialized] = useState(false);
  const [selectedService, setSelectedService] = useState<string>('all');
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Initialize compatibility monitor
  useEffect(() => {
    const initializeMonitor = async () => {
      try {
        await apiCompatibilityMonitor.initialize();
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize API compatibility monitor:', error);
      }
    };

    initializeMonitor();

    return () => {
      apiCompatibilityMonitor.cleanup();
    };
  }, []);

  // Load data
  const loadData = useCallback(() => {
    if (!isInitialized) return;

    try {
      const report = apiCompatibilityMonitor.getCompatibilityReport();
      const progress = apiCompatibilityMonitor.getMigrationProgress();
      const adoption = apiCompatibilityMonitor.getAdoptionMetrics(
        selectedService === 'all' ? undefined : selectedService
      );
      const results = apiCompatibilityMonitor.getTestResults(
        selectedService === 'all' ? undefined : selectedService
      );

      setCompatibilityReport(report);
      setMigrationProgress(progress);
      setAdoptionMetrics(adoption);
      setTestResults(results);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load compatibility data:', error);
    }
  }, [isInitialized, selectedService]);

  // Auto-refresh data
  useEffect(() => {
    loadData();

    const interval = setInterval(loadData, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, [loadData]);

  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600">Initializing compatibility monitor...</span>
      </div>
    );
  }

  const services = Object.keys(migrationProgress);

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">API Compatibility Monitor</h1>
            <p className="text-gray-600 mt-1">
              Track migration progress and API compatibility across ACGS services
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={selectedService}
              onChange={e => setSelectedService(e.target.value)}
              className="px-3 py-2 border rounded-md"
            >
              <option value="all">All Services</option>
              {services.map(service => (
                <option key={service} value={service}>
                  {service.toUpperCase()}
                </option>
              ))}
            </select>
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

        {/* Summary Cards */}
        {compatibilityReport.summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="text-2xl font-bold text-gray-900">
                {compatibilityReport.summary.totalEndpoints}
              </div>
              <div className="text-sm text-gray-600">Total Endpoints</div>
            </div>
            <div className="bg-green-50 p-6 rounded-lg shadow-sm border">
              <div className="text-2xl font-bold text-green-600">
                {compatibilityReport.summary.compatibleEndpoints}
              </div>
              <div className="text-sm text-green-700">Compatible</div>
            </div>
            <div className="bg-red-50 p-6 rounded-lg shadow-sm border">
              <div className="text-2xl font-bold text-red-600">
                {compatibilityReport.summary.incompatibleEndpoints}
              </div>
              <div className="text-sm text-red-700">Issues Found</div>
            </div>
            <div className="bg-blue-50 p-6 rounded-lg shadow-sm border">
              <div className="text-2xl font-bold text-blue-600">
                {compatibilityReport.summary.overallCompatibility.toFixed(1)}%
              </div>
              <div className="text-sm text-blue-700">Overall Compatibility</div>
            </div>
          </div>
        )}

        {/* Migration Progress */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">Migration Progress</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.values(migrationProgress).map(progress => (
              <MigrationProgressBar key={progress.service} progress={progress} />
            ))}
          </div>
        </div>

        {/* Recent Issues */}
        {compatibilityReport.recentIssues && compatibilityReport.recentIssues.length > 0 && (
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-4">Recent Compatibility Issues</h2>
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <div className="space-y-3">
                {compatibilityReport.recentIssues
                  .slice(0, 10)
                  .map((issue: CompatibilityIssue, index: number) => (
                    <IssueCard key={index} issue={issue} />
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* Adoption Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Object.entries(adoptionMetrics).map(([key, metrics]) => (
            <AdoptionChart key={key} metrics={metrics} />
          ))}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>API Compatibility Monitor v1.0 - Monitoring interval: 5 minutes</p>
          <p>Performance targets: &lt;1s response time difference, &lt;5% schema variation</p>
        </div>
      </div>
    </div>
  );
};

export default APICompatibilityDashboard;
