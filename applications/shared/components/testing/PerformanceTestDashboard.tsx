/**
 * Performance Test Dashboard Component
 * 
 * Dashboard for running and monitoring performance tests,
 * viewing results, and tracking performance improvements.
 */

import React, { useState, useCallback } from 'react';
import { 
  performanceTestSuite, 
  PerformanceTestResult, 
  PerformanceTestConfig,
  AssertionResult 
} from '../testing/performanceTestSuite';

// Test result card component
const TestResultCard: React.FC<{ result: PerformanceTestResult }> = ({ result }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const statusColor = result.passed ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50';
  const statusIcon = result.passed ? '✅' : '❌';

  return (
    <div className={`border-l-4 p-4 rounded-r-lg ${statusColor}`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <span className="text-lg">{statusIcon}</span>
            <h3 className="font-semibold text-gray-900">{result.testName}</h3>
            <span className="px-2 py-1 text-xs bg-white bg-opacity-50 rounded">
              {result.duration}ms
            </span>
          </div>
          <div className="text-sm text-gray-600 mt-1">{result.scenario}</div>
          <div className="text-xs text-gray-500 mt-1">
            {new Date(result.timestamp).toLocaleString()}
          </div>
          
          <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-gray-600">Assertions</div>
              <div className={`font-medium ${result.summary.passedAssertions === result.summary.totalAssertions ? 'text-green-600' : 'text-red-600'}`}>
                {result.summary.passedAssertions}/{result.summary.totalAssertions}
              </div>
            </div>
            <div>
              <div className="text-gray-600">Avg Load Time</div>
              <div className="font-medium">{result.summary.averageLoadTime.toFixed(0)}ms</div>
            </div>
            <div>
              <div className="text-gray-600">Memory Usage</div>
              <div className="font-medium">{result.summary.averageMemoryUsage.toFixed(1)}MB</div>
            </div>
            <div>
              <div className="text-gray-600">Errors</div>
              <div className={`font-medium ${result.errors.length > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {result.errors.length}
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-2 hover:bg-white hover:bg-opacity-30 rounded"
          title="Toggle details"
        >
          <svg className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </div>

      {isExpanded && (
        <div className="mt-4 space-y-4">
          {/* Assertions */}
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Assertions</h4>
            <div className="space-y-1">
              {result.assertions.map((assertion, index) => (
                <div key={index} className={`text-sm p-2 rounded ${assertion.passed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {assertion.message}
                </div>
              ))}
            </div>
          </div>

          {/* Metrics */}
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Metrics</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
              {result.metrics.slice(0, 8).map((metric, index) => (
                <div key={index} className="bg-white bg-opacity-50 p-2 rounded">
                  <div className="font-medium">{metric.name}</div>
                  <div>{metric.value.toFixed(2)}{metric.unit}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Errors */}
          {result.errors.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Errors</h4>
              <div className="space-y-1">
                {result.errors.map((error, index) => (
                  <div key={index} className="text-sm bg-red-100 text-red-800 p-2 rounded">
                    {error}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Test summary component
const TestSummary: React.FC<{ summary: any }> = ({ summary }) => {
  const successRate = summary.totalTests > 0 ? (summary.passedTests / summary.totalTests) * 100 : 0;
  
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-xl font-semibold mb-4">Test Summary</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">{summary.totalTests}</div>
          <div className="text-sm text-gray-600">Total Tests</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{summary.passedTests}</div>
          <div className="text-sm text-green-700">Passed</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">{summary.failedTests}</div>
          <div className="text-sm text-red-700">Failed</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{successRate.toFixed(1)}%</div>
          <div className="text-sm text-blue-700">Success Rate</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">{(summary.totalDuration / 1000).toFixed(1)}s</div>
          <div className="text-sm text-purple-700">Total Duration</div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Average Load Time:</span>
            <span className="font-medium">{summary.averageLoadTime.toFixed(0)}ms</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Average Memory Usage:</span>
            <span className="font-medium">{summary.averageMemoryUsage.toFixed(1)}MB</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Test configuration component
const TestConfigCard: React.FC<{ 
  config: PerformanceTestConfig; 
  onRunTest: (config: PerformanceTestConfig) => void;
  isRunning: boolean;
}> = ({ config, onRunTest, isRunning }) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{config.name}</h3>
          <p className="text-sm text-gray-600 mt-1">{config.description}</p>
          
          <div className="mt-3 grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-gray-600">URL:</span>
              <div className="font-mono text-blue-600">{config.url}</div>
            </div>
            <div>
              <span className="text-gray-600">Iterations:</span>
              <div className="font-medium">{config.iterations}</div>
            </div>
            <div>
              <span className="text-gray-600">Timeout:</span>
              <div className="font-medium">{config.timeout}ms</div>
            </div>
            <div>
              <span className="text-gray-600">Scenarios:</span>
              <div className="font-medium">{config.scenarios.length}</div>
            </div>
          </div>
        </div>

        <button
          onClick={() => onRunTest(config)}
          disabled={isRunning}
          className={`px-4 py-2 rounded-lg transition-colors ${
            isRunning 
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isRunning ? 'Running...' : 'Run Test'}
        </button>
      </div>
    </div>
  );
};

// Main performance test dashboard component
export const PerformanceTestDashboard: React.FC = () => {
  const [testResults, setTestResults] = useState<PerformanceTestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'tests' | 'results'>('overview');

  // Mock test configurations (in real implementation, these would come from the test suite)
  const testConfigs: PerformanceTestConfig[] = [
    {
      name: 'Dashboard Performance Test',
      description: 'Test performance of main dashboard components',
      url: 'http://localhost:3000/dashboard',
      timeout: 30000,
      iterations: 5,
      warmupIterations: 2,
      thresholds: {
        loadTime: 3000,
        firstContentfulPaint: 1800,
        largestContentfulPaint: 2500,
        firstInputDelay: 100,
        cumulativeLayoutShift: 0.1,
        bundleSize: 1000,
        memoryUsage: 100,
        networkRequests: 50,
      },
      scenarios: []
    },
    {
      name: 'Quantumagi Performance Test',
      description: 'Test performance of Quantumagi dashboard with Solana integration',
      url: 'http://localhost:3000/quantumagi',
      timeout: 30000,
      iterations: 5,
      warmupIterations: 2,
      thresholds: {
        loadTime: 4000,
        firstContentfulPaint: 1800,
        largestContentfulPaint: 2500,
        firstInputDelay: 100,
        cumulativeLayoutShift: 0.1,
        bundleSize: 1000,
        memoryUsage: 120,
        networkRequests: 50,
      },
      scenarios: []
    }
  ];

  // Run all tests
  const handleRunAllTests = useCallback(async () => {
    setIsRunning(true);
    try {
      const results = await performanceTestSuite.runAllTests();
      setTestResults(results);
    } catch (error) {
      console.error('Failed to run performance tests:', error);
    } finally {
      setIsRunning(false);
    }
  }, []);

  // Run specific test
  const handleRunTest = useCallback(async (config: PerformanceTestConfig) => {
    setIsRunning(true);
    try {
      const result = await performanceTestSuite.runTest(config);
      setTestResults(prev => [result, ...prev]);
    } catch (error) {
      console.error('Failed to run performance test:', error);
    } finally {
      setIsRunning(false);
    }
  }, []);

  // Clear results
  const handleClearResults = useCallback(() => {
    setTestResults([]);
    performanceTestSuite.clearResults();
  }, []);

  // Get test summary
  const testSummary = performanceTestSuite.getTestSummary();

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Performance Test Suite</h1>
            <p className="text-gray-600 mt-1">
              Comprehensive performance testing for ACGS applications
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={handleRunAllTests}
              disabled={isRunning}
              className={`px-6 py-2 rounded-lg transition-colors ${
                isRunning 
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              {isRunning ? 'Running Tests...' : 'Run All Tests'}
            </button>
            <button
              onClick={handleClearResults}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Clear Results
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 mb-6">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'tests', label: 'Test Configurations' },
            { id: 'results', label: 'Test Results' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id as any)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {selectedTab === 'overview' && (
          <div className="space-y-6">
            {/* Test Summary */}
            <TestSummary summary={testSummary} />

            {/* Quick Actions */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={handleRunAllTests}
                  disabled={isRunning}
                  className="p-4 border-2 border-dashed border-blue-300 rounded-lg hover:border-blue-500 transition-colors text-center"
                >
                  <div className="text-blue-600 font-medium">Run Full Test Suite</div>
                  <div className="text-sm text-gray-600 mt-1">Execute all performance tests</div>
                </button>
                <button
                  onClick={() => setSelectedTab('tests')}
                  className="p-4 border-2 border-dashed border-green-300 rounded-lg hover:border-green-500 transition-colors text-center"
                >
                  <div className="text-green-600 font-medium">Configure Tests</div>
                  <div className="text-sm text-gray-600 mt-1">Manage test configurations</div>
                </button>
                <button
                  onClick={() => setSelectedTab('results')}
                  className="p-4 border-2 border-dashed border-purple-300 rounded-lg hover:border-purple-500 transition-colors text-center"
                >
                  <div className="text-purple-600 font-medium">View Results</div>
                  <div className="text-sm text-gray-600 mt-1">Analyze test results</div>
                </button>
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'tests' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Test Configurations</h2>
              <span className="text-sm text-gray-600">{testConfigs.length} tests configured</span>
            </div>
            
            {testConfigs.map((config, index) => (
              <TestConfigCard
                key={index}
                config={config}
                onRunTest={handleRunTest}
                isRunning={isRunning}
              />
            ))}
          </div>
        )}

        {selectedTab === 'results' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Test Results</h2>
              <span className="text-sm text-gray-600">{testResults.length} results</span>
            </div>
            
            {testResults.length === 0 ? (
              <div className="bg-white p-8 rounded-lg shadow-sm border text-center">
                <div className="text-gray-500">
                  <svg className="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p className="text-lg font-medium">No test results yet</p>
                  <p className="text-sm mt-1">Run some performance tests to see results here</p>
                </div>
              </div>
            ) : (
              testResults.map((result, index) => (
                <TestResultCard key={index} result={result} />
              ))
            )}
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Performance Test Suite v1.0 - Automated performance validation</p>
          <p>Targets: &lt;3s load time, &lt;100MB memory, &lt;1MB bundle size</p>
        </div>
      </div>
    </div>
  );
};

export default PerformanceTestDashboard;
