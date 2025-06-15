/**
 * Performance Testing Suite
 * 
 * Comprehensive performance testing framework for measuring bundle size,
 * loading times, memory usage, and other performance metrics during migration.
 */

import { performanceMetrics, PerformanceMetric, PerformanceBaseline } from '../services/performanceMetrics';

// Performance test configuration
export interface PerformanceTestConfig {
  name: string;
  description: string;
  url: string;
  timeout: number;
  iterations: number;
  warmupIterations: number;
  thresholds: PerformanceThresholds;
  scenarios: PerformanceScenario[];
}

// Performance thresholds
export interface PerformanceThresholds {
  loadTime: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  firstInputDelay: number;
  cumulativeLayoutShift: number;
  bundleSize: number;
  memoryUsage: number;
  networkRequests: number;
}

// Performance test scenario
export interface PerformanceScenario {
  name: string;
  description: string;
  actions: PerformanceAction[];
  assertions: PerformanceAssertion[];
}

// Performance action
export interface PerformanceAction {
  type: 'navigate' | 'click' | 'type' | 'wait' | 'scroll' | 'measure';
  target?: string;
  value?: string | number;
  timeout?: number;
}

// Performance assertion
export interface PerformanceAssertion {
  metric: string;
  operator: 'lt' | 'lte' | 'gt' | 'gte' | 'eq';
  value: number;
  unit: string;
}

// Performance test result
export interface PerformanceTestResult {
  testName: string;
  scenario: string;
  timestamp: number;
  duration: number;
  passed: boolean;
  metrics: PerformanceMetric[];
  assertions: AssertionResult[];
  errors: string[];
  summary: {
    totalAssertions: number;
    passedAssertions: number;
    failedAssertions: number;
    averageLoadTime: number;
    averageMemoryUsage: number;
  };
}

// Assertion result
export interface AssertionResult {
  assertion: PerformanceAssertion;
  actualValue: number;
  passed: boolean;
  message: string;
}

// Default test configurations
const DEFAULT_THRESHOLDS: PerformanceThresholds = {
  loadTime: 3000,
  firstContentfulPaint: 1800,
  largestContentfulPaint: 2500,
  firstInputDelay: 100,
  cumulativeLayoutShift: 0.1,
  bundleSize: 1000,
  memoryUsage: 100,
  networkRequests: 50,
};

// ACGS-specific test configurations
const ACGS_TEST_CONFIGS: PerformanceTestConfig[] = [
  {
    name: 'Dashboard Performance Test',
    description: 'Test performance of main dashboard components',
    url: 'http://localhost:3000/dashboard',
    timeout: 30000,
    iterations: 5,
    warmupIterations: 2,
    thresholds: DEFAULT_THRESHOLDS,
    scenarios: [
      {
        name: 'Dashboard Load',
        description: 'Measure dashboard loading performance',
        actions: [
          { type: 'navigate', target: '/dashboard' },
          { type: 'wait', value: 2000 },
          { type: 'measure' }
        ],
        assertions: [
          { metric: 'loadTime', operator: 'lt', value: 3000, unit: 'ms' },
          { metric: 'firstContentfulPaint', operator: 'lt', value: 1800, unit: 'ms' }
        ]
      }
    ]
  },
  {
    name: 'Quantumagi Performance Test',
    description: 'Test performance of Quantumagi dashboard',
    url: 'http://localhost:3000/quantumagi',
    timeout: 30000,
    iterations: 5,
    warmupIterations: 2,
    thresholds: { ...DEFAULT_THRESHOLDS, loadTime: 4000 }, // Higher threshold for Solana integration
    scenarios: [
      {
        name: 'Quantumagi Load',
        description: 'Measure Quantumagi dashboard loading with Solana integration',
        actions: [
          { type: 'navigate', target: '/quantumagi' },
          { type: 'wait', value: 3000 }, // Wait for Solana connection
          { type: 'measure' }
        ],
        assertions: [
          { metric: 'loadTime', operator: 'lt', value: 4000, unit: 'ms' },
          { metric: 'memoryUsage', operator: 'lt', value: 120, unit: 'MB' }
        ]
      }
    ]
  },
  {
    name: 'Bundle Size Test',
    description: 'Test JavaScript bundle size optimization',
    url: 'http://localhost:3000',
    timeout: 15000,
    iterations: 1,
    warmupIterations: 0,
    thresholds: DEFAULT_THRESHOLDS,
    scenarios: [
      {
        name: 'Bundle Analysis',
        description: 'Analyze bundle size and composition',
        actions: [
          { type: 'navigate', target: '/' },
          { type: 'measure' }
        ],
        assertions: [
          { metric: 'bundleSize', operator: 'lt', value: 1000, unit: 'KB' },
          { metric: 'networkRequests', operator: 'lt', value: 50, unit: 'count' }
        ]
      }
    ]
  }
];

/**
 * Performance Test Suite Class
 */
export class PerformanceTestSuite {
  private testConfigs: PerformanceTestConfig[] = [];
  private testResults: PerformanceTestResult[] = [];
  private isRunning = false;

  constructor(configs: PerformanceTestConfig[] = ACGS_TEST_CONFIGS) {
    this.testConfigs = configs;
  }

  /**
   * Run all performance tests
   */
  async runAllTests(): Promise<PerformanceTestResult[]> {
    if (this.isRunning) {
      throw new Error('Performance tests are already running');
    }

    this.isRunning = true;
    this.testResults = [];

    try {
      console.log('Starting performance test suite...');
      
      for (const config of this.testConfigs) {
        console.log(`Running test: ${config.name}`);
        const result = await this.runTest(config);
        this.testResults.push(result);
      }

      console.log('Performance test suite completed');
      return this.testResults;
    } finally {
      this.isRunning = false;
    }
  }

  /**
   * Run a specific performance test
   */
  async runTest(config: PerformanceTestConfig): Promise<PerformanceTestResult> {
    const startTime = Date.now();
    const metrics: PerformanceMetric[] = [];
    const assertions: AssertionResult[] = [];
    const errors: string[] = [];

    try {
      // Run warmup iterations
      for (let i = 0; i < config.warmupIterations; i++) {
        console.log(`Warmup iteration ${i + 1}/${config.warmupIterations}`);
        await this.runScenarios(config.scenarios, true);
      }

      // Run actual test iterations
      for (let i = 0; i < config.iterations; i++) {
        console.log(`Test iteration ${i + 1}/${config.iterations}`);
        const iterationMetrics = await this.runScenarios(config.scenarios, false);
        metrics.push(...iterationMetrics);
      }

      // Run assertions
      for (const scenario of config.scenarios) {
        for (const assertion of scenario.assertions) {
          const result = this.evaluateAssertion(assertion, metrics);
          assertions.push(result);
        }
      }

    } catch (error) {
      errors.push(error instanceof Error ? error.message : 'Unknown error');
    }

    const duration = Date.now() - startTime;
    const passedAssertions = assertions.filter(a => a.passed).length;
    const passed = errors.length === 0 && passedAssertions === assertions.length;

    return {
      testName: config.name,
      scenario: config.scenarios.map(s => s.name).join(', '),
      timestamp: startTime,
      duration,
      passed,
      metrics,
      assertions,
      errors,
      summary: {
        totalAssertions: assertions.length,
        passedAssertions,
        failedAssertions: assertions.length - passedAssertions,
        averageLoadTime: this.calculateAverageMetric(metrics, 'loadTime'),
        averageMemoryUsage: this.calculateAverageMetric(metrics, 'memoryUsage'),
      }
    };
  }

  /**
   * Run test scenarios
   */
  private async runScenarios(scenarios: PerformanceScenario[], isWarmup: boolean): Promise<PerformanceMetric[]> {
    const metrics: PerformanceMetric[] = [];

    for (const scenario of scenarios) {
      try {
        const scenarioMetrics = await this.runScenario(scenario, isWarmup);
        if (!isWarmup) {
          metrics.push(...scenarioMetrics);
        }
      } catch (error) {
        console.error(`Scenario failed: ${scenario.name}`, error);
      }
    }

    return metrics;
  }

  /**
   * Run a single scenario
   */
  private async runScenario(scenario: PerformanceScenario, isWarmup: boolean): Promise<PerformanceMetric[]> {
    const metrics: PerformanceMetric[] = [];
    const startTime = Date.now();

    // Execute actions
    for (const action of scenario.actions) {
      await this.executeAction(action);
    }

    // Collect metrics if not warmup
    if (!isWarmup) {
      const collectedMetrics = await this.collectMetrics(scenario.name);
      metrics.push(...collectedMetrics);
    }

    return metrics;
  }

  /**
   * Execute a performance action
   */
  private async executeAction(action: PerformanceAction): Promise<void> {
    switch (action.type) {
      case 'navigate':
        await this.navigate(action.target || '/');
        break;
      case 'wait':
        await this.wait(action.value as number || 1000);
        break;
      case 'measure':
        await this.measurePerformance();
        break;
      case 'click':
        await this.click(action.target || '');
        break;
      case 'type':
        await this.type(action.target || '', action.value as string || '');
        break;
      case 'scroll':
        await this.scroll(action.value as number || 0);
        break;
      default:
        console.warn(`Unknown action type: ${action.type}`);
    }
  }

  /**
   * Navigate to URL (simulated)
   */
  private async navigate(url: string): Promise<void> {
    // In a real implementation, this would use a browser automation tool
    console.log(`Navigating to: ${url}`);
    await this.wait(100); // Simulate navigation delay
  }

  /**
   * Wait for specified time
   */
  private async wait(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Measure performance (simulated)
   */
  private async measurePerformance(): Promise<void> {
    // In a real implementation, this would collect actual browser metrics
    console.log('Measuring performance...');
    await this.wait(50); // Simulate measurement time
  }

  /**
   * Click element (simulated)
   */
  private async click(selector: string): Promise<void> {
    console.log(`Clicking: ${selector}`);
    await this.wait(50);
  }

  /**
   * Type text (simulated)
   */
  private async type(selector: string, text: string): Promise<void> {
    console.log(`Typing "${text}" into: ${selector}`);
    await this.wait(text.length * 10); // Simulate typing speed
  }

  /**
   * Scroll page (simulated)
   */
  private async scroll(pixels: number): Promise<void> {
    console.log(`Scrolling: ${pixels}px`);
    await this.wait(100);
  }

  /**
   * Collect performance metrics (simulated)
   */
  private async collectMetrics(scenarioName: string): Promise<PerformanceMetric[]> {
    const timestamp = Date.now();
    
    // In a real implementation, these would be actual browser metrics
    const mockMetrics: PerformanceMetric[] = [
      {
        name: 'loadTime',
        value: Math.random() * 2000 + 1000, // 1-3 seconds
        unit: 'ms',
        timestamp,
        category: 'loading',
        component: scenarioName
      },
      {
        name: 'firstContentfulPaint',
        value: Math.random() * 1000 + 800, // 0.8-1.8 seconds
        unit: 'ms',
        timestamp,
        category: 'loading',
        component: scenarioName
      },
      {
        name: 'memoryUsage',
        value: Math.random() * 50 + 50, // 50-100 MB
        unit: 'MB',
        timestamp,
        category: 'memory',
        component: scenarioName
      },
      {
        name: 'bundleSize',
        value: Math.random() * 500 + 500, // 500-1000 KB
        unit: 'KB',
        timestamp,
        category: 'bundle',
        component: scenarioName
      }
    ];

    return mockMetrics;
  }

  /**
   * Evaluate performance assertion
   */
  private evaluateAssertion(assertion: PerformanceAssertion, metrics: PerformanceMetric[]): AssertionResult {
    const relevantMetrics = metrics.filter(m => m.name === assertion.metric);
    
    if (relevantMetrics.length === 0) {
      return {
        assertion,
        actualValue: 0,
        passed: false,
        message: `No metrics found for ${assertion.metric}`
      };
    }

    const actualValue = this.calculateAverageMetric(relevantMetrics, assertion.metric);
    let passed = false;

    switch (assertion.operator) {
      case 'lt':
        passed = actualValue < assertion.value;
        break;
      case 'lte':
        passed = actualValue <= assertion.value;
        break;
      case 'gt':
        passed = actualValue > assertion.value;
        break;
      case 'gte':
        passed = actualValue >= assertion.value;
        break;
      case 'eq':
        passed = Math.abs(actualValue - assertion.value) < 0.01;
        break;
    }

    const message = passed
      ? `✓ ${assertion.metric} ${assertion.operator} ${assertion.value}${assertion.unit} (actual: ${actualValue.toFixed(2)}${assertion.unit})`
      : `✗ ${assertion.metric} ${assertion.operator} ${assertion.value}${assertion.unit} (actual: ${actualValue.toFixed(2)}${assertion.unit})`;

    return {
      assertion,
      actualValue,
      passed,
      message
    };
  }

  /**
   * Calculate average metric value
   */
  private calculateAverageMetric(metrics: PerformanceMetric[], metricName: string): number {
    const relevantMetrics = metrics.filter(m => m.name === metricName);
    if (relevantMetrics.length === 0) return 0;
    
    const sum = relevantMetrics.reduce((total, metric) => total + metric.value, 0);
    return sum / relevantMetrics.length;
  }

  /**
   * Get test results
   */
  getTestResults(): PerformanceTestResult[] {
    return [...this.testResults];
  }

  /**
   * Get test summary
   */
  getTestSummary(): {
    totalTests: number;
    passedTests: number;
    failedTests: number;
    totalDuration: number;
    averageLoadTime: number;
    averageMemoryUsage: number;
  } {
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r => r.passed).length;
    const failedTests = totalTests - passedTests;
    const totalDuration = this.testResults.reduce((sum, r) => sum + r.duration, 0);
    
    const allMetrics = this.testResults.flatMap(r => r.metrics);
    const averageLoadTime = this.calculateAverageMetric(allMetrics, 'loadTime');
    const averageMemoryUsage = this.calculateAverageMetric(allMetrics, 'memoryUsage');

    return {
      totalTests,
      passedTests,
      failedTests,
      totalDuration,
      averageLoadTime,
      averageMemoryUsage
    };
  }

  /**
   * Export test results
   */
  exportResults(): {
    summary: any;
    results: PerformanceTestResult[];
    timestamp: number;
  } {
    return {
      summary: this.getTestSummary(),
      results: this.getTestResults(),
      timestamp: Date.now()
    };
  }

  /**
   * Add custom test configuration
   */
  addTestConfig(config: PerformanceTestConfig): void {
    this.testConfigs.push(config);
  }

  /**
   * Clear test results
   */
  clearResults(): void {
    this.testResults = [];
  }
}

// Singleton instance
export const performanceTestSuite = new PerformanceTestSuite();

// Export default instance
export default performanceTestSuite;
