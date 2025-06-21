/**
 * Quantumagi Validation Dashboard Component
 *
 * Real-time dashboard for monitoring Quantumagi Solana integration,
 * constitutional compliance, and governance workflow validation.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  quantumagiValidator,
  IntegrationValidationReport,
  ValidationResult
} from '../testing/quantumagiIntegrationValidator';

// Validation status indicator
const ValidationStatusIndicator: React.FC<{ status: 'passed' | 'failed' | 'warning' }> = ({
  status
}) => {
  const statusConfig = {
    passed: { icon: '✅', color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200' },
    failed: { icon: '❌', color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' },
    warning: {
      icon: '⚠️',
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
      border: 'border-yellow-200'
    }
  };

  const config = statusConfig[status];

  return (
    <div
      className={`flex items-center space-x-2 px-2 py-1 rounded ${config.bg} ${config.border} border`}
    >
      <span>{config.icon}</span>
      <span className={`text-sm font-medium ${config.color}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    </div>
  );
};

// Validation result card
const ValidationResultCard: React.FC<{ result: ValidationResult }> = ({ result }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const statusColors = {
    passed: 'border-green-500 bg-green-50',
    failed: 'border-red-500 bg-red-50',
    warning: 'border-yellow-500 bg-yellow-50'
  };

  return (
    <div className={`border-l-4 p-4 rounded-r-lg ${statusColors[result.status]}`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center space-x-3">
            <ValidationStatusIndicator status={result.status} />
            <h3 className="font-semibold text-gray-900">
              {result.component.replace(/_/g, ' ').toUpperCase()}
            </h3>
          </div>
          <p className="text-sm text-gray-700 mt-2">{result.message}</p>
          <div className="text-xs text-gray-500 mt-1">
            {new Date(result.timestamp).toLocaleString()}
          </div>
        </div>

        {result.details && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 hover:bg-white hover:bg-opacity-50 rounded"
            title="Toggle details"
          >
            <svg
              className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>

      {isExpanded && result.details && (
        <div className="mt-4 p-3 bg-white bg-opacity-50 rounded">
          <h4 className="font-medium text-gray-900 mb-2">Details</h4>
          <pre className="text-xs text-gray-700 whitespace-pre-wrap overflow-x-auto">
            {JSON.stringify(result.details, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

// Overall status card
const OverallStatusCard: React.FC<{ report: IntegrationValidationReport | null }> = ({
  report
}) => {
  if (!report) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h2 className="text-xl font-semibold mb-4">Quantumagi Integration Status</h2>
        <div className="text-center text-gray-500 py-8">
          <div className="animate-pulse">
            <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-4"></div>
            <p>Initializing validation...</p>
          </div>
        </div>
      </div>
    );
  }

  const statusConfig = {
    healthy: { icon: '🟢', color: 'text-green-600', bg: 'bg-green-50' },
    degraded: { icon: '🟡', color: 'text-yellow-600', bg: 'bg-yellow-50' },
    critical: { icon: '🔴', color: 'text-red-600', bg: 'bg-red-50' }
  };

  const config = statusConfig[report.overallStatus];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-xl font-semibold mb-4">Quantumagi Integration Status</h2>

      <div className={`p-4 rounded-lg ${config.bg} mb-4`}>
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{config.icon}</span>
          <div>
            <div className={`text-lg font-semibold ${config.color}`}>
              {report.overallStatus.charAt(0).toUpperCase() + report.overallStatus.slice(1)}
            </div>
            <div className="text-sm text-gray-600">
              Success Rate: {report.successRate.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">{report.summary.totalChecks}</div>
          <div className="text-sm text-gray-600">Total Checks</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{report.summary.passedChecks}</div>
          <div className="text-sm text-green-700">Passed</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">{report.summary.failedChecks}</div>
          <div className="text-sm text-red-700">Failed</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-yellow-600">{report.summary.warningChecks}</div>
          <div className="text-sm text-yellow-700">Warnings</div>
        </div>
      </div>
    </div>
  );
};

// Deployment info card
const DeploymentInfoCard: React.FC<{ report: IntegrationValidationReport | null }> = ({
  report
}) => {
  if (!report) return null;

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-xl font-semibold mb-4">Deployment Information</h2>

      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-gray-600">Cluster:</span>
          <span className="font-medium">{report.deploymentInfo.cluster}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Constitution Hash:</span>
          <span className="font-mono text-sm">{report.deploymentInfo.constitutionHash}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Deployment Date:</span>
          <span className="font-medium">
            {new Date(report.deploymentInfo.deploymentDate).toLocaleDateString()}
          </span>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t">
        <h3 className="font-medium text-gray-900 mb-2">Program IDs</h3>
        <div className="space-y-2">
          {Object.entries(report.deploymentInfo.programIds).map(([name, id]) => (
            <div key={name} className="flex justify-between items-center">
              <span className="text-sm text-gray-600">{name}:</span>
              <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">{id}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Performance metrics card
const PerformanceMetricsCard: React.FC<{ report: IntegrationValidationReport | null }> = ({
  report
}) => {
  if (!report) return null;

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-xl font-semibold mb-4">Performance Metrics</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {report.performanceMetrics.averageResponseTime.toFixed(0)}ms
          </div>
          <div className="text-sm text-blue-700">Avg Response Time</div>
        </div>
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {report.performanceMetrics.connectionLatency.toFixed(0)}ms
          </div>
          <div className="text-sm text-green-700">Connection Latency</div>
        </div>
        <div className="text-center p-4 bg-purple-50 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">
            {report.performanceMetrics.transactionThroughput.toFixed(1)}
          </div>
          <div className="text-sm text-purple-700">TX Throughput</div>
        </div>
      </div>
    </div>
  );
};

// Main dashboard component
export const QuantumagiValidationDashboard: React.FC = () => {
  const [validationReport, setValidationReport] = useState<IntegrationValidationReport | null>(
    null
  );
  const [isRunning, setIsRunning] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  // Run validation
  const runValidation = useCallback(async () => {
    setIsRunning(true);
    try {
      const report = await quantumagiValidator.runFullValidation();
      setValidationReport(report);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Validation failed:', error);
    } finally {
      setIsRunning(false);
    }
  }, []);

  // Auto-refresh effect
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(runValidation, 60000); // 1 minute
      return () => clearInterval(interval);
    }
  }, [autoRefresh, runValidation]);

  // Initial validation
  useEffect(() => {
    runValidation();
  }, [runValidation]);

  // Filter validation results by category
  const getResultsByCategory = (category: string) => {
    if (!validationReport) return [];
    return validationReport.validationResults.filter(result => result.component.includes(category));
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Quantumagi Validation Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Real-time validation of Quantumagi Solana integration and governance workflows
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={e => setAutoRefresh(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm text-gray-600">Auto-refresh</span>
            </label>
            {lastUpdate && (
              <div className="text-sm text-gray-500">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </div>
            )}
            <button
              onClick={runValidation}
              disabled={isRunning}
              className={`px-6 py-2 rounded-lg transition-colors ${
                isRunning
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isRunning ? 'Running Validation...' : 'Run Validation'}
            </button>
          </div>
        </div>

        {/* Overall Status */}
        <div className="mb-6">
          <OverallStatusCard report={validationReport} />
        </div>

        {/* Deployment Info and Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <DeploymentInfoCard report={validationReport} />
          <PerformanceMetricsCard report={validationReport} />
        </div>

        {/* Validation Results */}
        {validationReport && (
          <div className="space-y-6">
            {/* Solana Infrastructure */}
            <div>
              <h2 className="text-xl font-semibold mb-4">Solana Infrastructure</h2>
              <div className="space-y-3">
                {getResultsByCategory('solana')
                  .concat(getResultsByCategory('program'))
                  .map((result, index) => (
                    <ValidationResultCard key={index} result={result} />
                  ))}
              </div>
            </div>

            {/* ACGS Services */}
            <div>
              <h2 className="text-xl font-semibold mb-4">ACGS Service Integration</h2>
              <div className="space-y-3">
                {getResultsByCategory('acgs').map((result, index) => (
                  <ValidationResultCard key={index} result={result} />
                ))}
              </div>
            </div>

            {/* Governance & Compliance */}
            <div>
              <h2 className="text-xl font-semibold mb-4">Governance & Compliance</h2>
              <div className="space-y-3">
                {getResultsByCategory('constitution')
                  .concat(getResultsByCategory('pgc'))
                  .concat(getResultsByCategory('workflow'))
                  .map((result, index) => (
                    <ValidationResultCard key={index} result={result} />
                  ))}
              </div>
            </div>

            {/* System Health */}
            <div>
              <h2 className="text-xl font-semibold mb-4">System Health</h2>
              <div className="space-y-3">
                {getResultsByCategory('performance')
                  .concat(getResultsByCategory('data'))
                  .concat(getResultsByCategory('network'))
                  .map((result, index) => (
                    <ValidationResultCard key={index} result={result} />
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Quantumagi Validation Dashboard v1.0 - Constitutional Governance on Solana</p>
          <p>
            Targets: &gt;95% success rate, &lt;500ms response times, 100% constitutional compliance
          </p>
        </div>
      </div>
    </div>
  );
};

export default QuantumagiValidationDashboard;
