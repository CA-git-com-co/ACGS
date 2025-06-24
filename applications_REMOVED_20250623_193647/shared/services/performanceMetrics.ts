/**
 * Performance Metrics Collection and Analysis System
 *
 * Establishes baseline performance metrics for legacy-frontend and tracks
 * improvements during migration to shared architecture.
 */

// Performance metric interfaces
export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: number;
  category: 'loading' | 'runtime' | 'network' | 'memory' | 'bundle' | 'user_experience';
  component?: string;
  route?: string;
  metadata?: Record<string, any>;
}

export interface PerformanceBaseline {
  id: string;
  name: string;
  description: string;
  timestamp: number;
  environment: 'development' | 'staging' | 'production';
  version: string;
  metrics: PerformanceMetric[];
  summary: PerformanceSummary;
}

export interface PerformanceSummary {
  loadTime: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  firstInputDelay: number;
  cumulativeLayoutShift: number;
  bundleSize: number;
  memoryUsage: number;
  networkRequests: number;
  errorRate: number;
  userSatisfactionScore: number;
}

export interface PerformanceComparison {
  baseline: PerformanceBaseline;
  current: PerformanceBaseline;
  improvements: Record<
    string,
    {
      baseline: number;
      current: number;
      improvement: number;
      percentage: number;
      status: 'improved' | 'degraded' | 'unchanged';
    }
  >;
  overallScore: number;
}

// Performance monitoring configuration
export interface PerformanceConfig {
  enabled: boolean;
  collectInterval: number; // milliseconds
  retentionDays: number;
  thresholds: {
    loadTime: number;
    firstContentfulPaint: number;
    largestContentfulPaint: number;
    firstInputDelay: number;
    cumulativeLayoutShift: number;
    memoryUsage: number; // MB
    bundleSize: number; // KB
  };
  routes: string[];
  components: string[];
}

// Default configuration
const DEFAULT_CONFIG: PerformanceConfig = {
  enabled: true,
  collectInterval: 60000, // 1 minute
  retentionDays: 30,
  thresholds: {
    loadTime: 3000, // 3 seconds
    firstContentfulPaint: 1800, // 1.8 seconds
    largestContentfulPaint: 2500, // 2.5 seconds
    firstInputDelay: 100, // 100ms
    cumulativeLayoutShift: 0.1,
    memoryUsage: 100, // 100MB
    bundleSize: 1000 // 1MB
  },
  routes: [
    '/',
    '/dashboard',
    '/quantumagi',
    '/ac-management',
    '/policy-synthesis',
    '/public-consultation'
  ],
  components: [
    'App',
    'Dashboard',
    'QuantumagiDashboard',
    'ConstitutionalCouncilDashboard',
    'PolicySynthesis',
    'PublicConsultation'
  ]
};

/**
 * Performance Metrics Collector Class
 */
export class PerformanceMetricsCollector {
  private config: PerformanceConfig;
  private metrics: Map<string, PerformanceMetric[]> = new Map();
  private baselines: Map<string, PerformanceBaseline> = new Map();
  private observer: PerformanceObserver | null = null;
  private collectionInterval: NodeJS.Timeout | null = null;
  private isInitialized = false;

  constructor(config: Partial<PerformanceConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Initialize performance monitoring
   */
  async initialize(): Promise<void> {
    if (this.isInitialized || typeof window === 'undefined') return;

    try {
      // Set up Performance Observer
      this.setupPerformanceObserver();

      // Set up Web Vitals monitoring
      this.setupWebVitalsMonitoring();

      // Start periodic collection
      this.startPeriodicCollection();

      // Collect initial baseline
      await this.collectBaseline('initial');

      this.isInitialized = true;
      console.log('Performance metrics collector initialized');
    } catch (error) {
      console.error('Failed to initialize performance metrics collector:', error);
      throw error;
    }
  }

  /**
   * Set up Performance Observer
   */
  private setupPerformanceObserver(): void {
    if (!('PerformanceObserver' in window)) {
      console.warn('PerformanceObserver not supported');
      return;
    }

    this.observer = new PerformanceObserver(list => {
      const entries = list.getEntries();
      entries.forEach(entry => {
        this.processPerformanceEntry(entry);
      });
    });

    // Observe different types of performance entries
    try {
      this.observer.observe({ entryTypes: ['navigation', 'resource', 'measure', 'paint'] });
    } catch (error) {
      console.warn('Some performance entry types not supported:', error);
    }
  }

  /**
   * Set up Web Vitals monitoring
   */
  private setupWebVitalsMonitoring(): void {
    // First Contentful Paint
    this.observeWebVital('first-contentful-paint', value => {
      this.recordMetric({
        name: 'first_contentful_paint',
        value,
        unit: 'ms',
        timestamp: Date.now(),
        category: 'loading'
      });
    });

    // Largest Contentful Paint
    this.observeWebVital('largest-contentful-paint', value => {
      this.recordMetric({
        name: 'largest_contentful_paint',
        value,
        unit: 'ms',
        timestamp: Date.now(),
        category: 'loading'
      });
    });

    // First Input Delay
    this.observeWebVital('first-input-delay', value => {
      this.recordMetric({
        name: 'first_input_delay',
        value,
        unit: 'ms',
        timestamp: Date.now(),
        category: 'user_experience'
      });
    });

    // Cumulative Layout Shift
    this.observeWebVital('cumulative-layout-shift', value => {
      this.recordMetric({
        name: 'cumulative_layout_shift',
        value,
        unit: 'score',
        timestamp: Date.now(),
        category: 'user_experience'
      });
    });
  }

  /**
   * Observe specific Web Vital
   */
  private observeWebVital(name: string, callback: (value: number) => void): void {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver(list => {
          const entries = list.getEntries();
          entries.forEach(entry => {
            if (entry.name === name) {
              callback(entry.startTime);
            }
          });
        });
        observer.observe({
          entryTypes: ['paint', 'largest-contentful-paint', 'first-input', 'layout-shift']
        });
      } catch (error) {
        console.warn(`Failed to observe ${name}:`, error);
      }
    }
  }

  /**
   * Process performance entry
   */
  private processPerformanceEntry(entry: PerformanceEntry): void {
    const metric: PerformanceMetric = {
      name: entry.name,
      value: entry.duration || entry.startTime,
      unit: 'ms',
      timestamp: Date.now(),
      category: this.categorizeEntry(entry),
      metadata: {
        entryType: entry.entryType,
        startTime: entry.startTime,
        duration: entry.duration
      }
    };

    // Add additional metadata based on entry type
    if (entry.entryType === 'navigation') {
      const navEntry = entry as PerformanceNavigationTiming;
      metric.metadata = {
        ...metric.metadata,
        domContentLoaded: navEntry.domContentLoadedEventEnd - navEntry.domContentLoadedEventStart,
        loadComplete: navEntry.loadEventEnd - navEntry.loadEventStart,
        transferSize: navEntry.transferSize,
        encodedBodySize: navEntry.encodedBodySize
      };
    } else if (entry.entryType === 'resource') {
      const resourceEntry = entry as PerformanceResourceTiming;
      metric.metadata = {
        ...metric.metadata,
        transferSize: resourceEntry.transferSize,
        encodedBodySize: resourceEntry.encodedBodySize,
        decodedBodySize: resourceEntry.decodedBodySize
      };
    }

    this.recordMetric(metric);
  }

  /**
   * Categorize performance entry
   */
  private categorizeEntry(entry: PerformanceEntry): PerformanceMetric['category'] {
    if (entry.entryType === 'navigation') return 'loading';
    if (entry.entryType === 'resource') return 'network';
    if (entry.entryType === 'paint') return 'loading';
    if (entry.entryType === 'measure') return 'runtime';
    return 'runtime';
  }

  /**
   * Start periodic collection
   */
  private startPeriodicCollection(): void {
    if (this.collectionInterval) {
      clearInterval(this.collectionInterval);
    }

    this.collectionInterval = setInterval(() => {
      this.collectRuntimeMetrics();
    }, this.config.collectInterval);
  }

  /**
   * Collect runtime metrics
   */
  private collectRuntimeMetrics(): void {
    // Memory usage
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      this.recordMetric({
        name: 'memory_used',
        value: memory.usedJSHeapSize / 1024 / 1024, // Convert to MB
        unit: 'MB',
        timestamp: Date.now(),
        category: 'memory'
      });

      this.recordMetric({
        name: 'memory_total',
        value: memory.totalJSHeapSize / 1024 / 1024,
        unit: 'MB',
        timestamp: Date.now(),
        category: 'memory'
      });
    }

    // Bundle size (approximate from resource entries)
    const bundleSize = this.calculateBundleSize();
    if (bundleSize > 0) {
      this.recordMetric({
        name: 'bundle_size',
        value: bundleSize / 1024, // Convert to KB
        unit: 'KB',
        timestamp: Date.now(),
        category: 'bundle'
      });
    }

    // Network requests count
    const networkRequests = performance.getEntriesByType('resource').length;
    this.recordMetric({
      name: 'network_requests',
      value: networkRequests,
      unit: 'count',
      timestamp: Date.now(),
      category: 'network'
    });
  }

  /**
   * Calculate bundle size from resource entries
   */
  private calculateBundleSize(): number {
    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
    return resources
      .filter(resource => resource.name.includes('.js') || resource.name.includes('.css'))
      .reduce((total, resource) => total + (resource.transferSize || 0), 0);
  }

  /**
   * Record a performance metric
   */
  recordMetric(metric: PerformanceMetric): void {
    const key = `${metric.category}-${metric.name}`;

    if (!this.metrics.has(key)) {
      this.metrics.set(key, []);
    }

    const metrics = this.metrics.get(key)!;
    metrics.push(metric);

    // Keep only recent metrics (based on retention)
    const cutoffTime = Date.now() - this.config.retentionDays * 24 * 60 * 60 * 1000;
    const filteredMetrics = metrics.filter(m => m.timestamp >= cutoffTime);
    this.metrics.set(key, filteredMetrics);
  }

  /**
   * Collect baseline performance metrics
   */
  async collectBaseline(name: string): Promise<PerformanceBaseline> {
    const timestamp = Date.now();
    const metrics: PerformanceMetric[] = [];

    // Collect all current metrics
    this.metrics.forEach(metricList => {
      const recent = metricList.filter(m => timestamp - m.timestamp < 60000); // Last minute
      metrics.push(...recent);
    });

    // Calculate summary
    const summary = this.calculateSummary(metrics);

    const baseline: PerformanceBaseline = {
      id: `baseline-${timestamp}`,
      name,
      description: `Performance baseline collected at ${new Date(timestamp).toISOString()}`,
      timestamp,
      environment: this.detectEnvironment(),
      version: this.getApplicationVersion(),
      metrics,
      summary
    };

    this.baselines.set(baseline.id, baseline);

    console.log(`Performance baseline '${name}' collected:`, summary);
    return baseline;
  }

  /**
   * Calculate performance summary
   */
  private calculateSummary(metrics: PerformanceMetric[]): PerformanceSummary {
    const getLatestMetric = (name: string) => {
      const metric = metrics
        .filter(m => m.name === name)
        .sort((a, b) => b.timestamp - a.timestamp)[0];
      return metric?.value || 0;
    };

    const getAverageMetric = (name: string) => {
      const metricValues = metrics.filter(m => m.name === name).map(m => m.value);
      return metricValues.length > 0
        ? metricValues.reduce((sum, val) => sum + val, 0) / metricValues.length
        : 0;
    };

    return {
      loadTime: getLatestMetric('loadEventEnd') - getLatestMetric('navigationStart'),
      firstContentfulPaint: getLatestMetric('first_contentful_paint'),
      largestContentfulPaint: getLatestMetric('largest_contentful_paint'),
      firstInputDelay: getLatestMetric('first_input_delay'),
      cumulativeLayoutShift: getLatestMetric('cumulative_layout_shift'),
      bundleSize: getLatestMetric('bundle_size'),
      memoryUsage: getLatestMetric('memory_used'),
      networkRequests: getLatestMetric('network_requests'),
      errorRate: this.calculateErrorRate(metrics),
      userSatisfactionScore: this.calculateUserSatisfactionScore(metrics)
    };
  }

  /**
   * Calculate error rate
   */
  private calculateErrorRate(metrics: PerformanceMetric[]): number {
    const errorMetrics = metrics.filter(m => m.name.includes('error'));
    const totalMetrics = metrics.length;
    return totalMetrics > 0 ? (errorMetrics.length / totalMetrics) * 100 : 0;
  }

  /**
   * Calculate user satisfaction score
   */
  private calculateUserSatisfactionScore(metrics: PerformanceMetric[]): number {
    // Simplified scoring based on Web Vitals
    const fcp = metrics.find(m => m.name === 'first_contentful_paint')?.value || 0;
    const lcp = metrics.find(m => m.name === 'largest_contentful_paint')?.value || 0;
    const fid = metrics.find(m => m.name === 'first_input_delay')?.value || 0;
    const cls = metrics.find(m => m.name === 'cumulative_layout_shift')?.value || 0;

    let score = 100;

    // Deduct points for poor metrics
    if (fcp > 1800) score -= 20;
    if (lcp > 2500) score -= 25;
    if (fid > 100) score -= 25;
    if (cls > 0.1) score -= 30;

    return Math.max(0, score);
  }

  /**
   * Detect environment
   */
  private detectEnvironment(): 'development' | 'staging' | 'production' {
    if (typeof window === 'undefined') return 'development';

    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') return 'development';
    if (hostname.includes('staging')) return 'staging';
    return 'production';
  }

  /**
   * Get application version
   */
  private getApplicationVersion(): string {
    return process.env.REACT_APP_VERSION || '1.0.0';
  }

  /**
   * Compare performance with baseline
   */
  compareWithBaseline(
    baselineId: string,
    currentMetrics?: PerformanceMetric[]
  ): PerformanceComparison | null {
    const baseline = this.baselines.get(baselineId);
    if (!baseline) return null;

    // Use current metrics or collect them
    const metrics = currentMetrics || this.getCurrentMetrics();
    const currentSummary = this.calculateSummary(metrics);

    const current: PerformanceBaseline = {
      id: `current-${Date.now()}`,
      name: 'Current Performance',
      description: 'Current performance metrics',
      timestamp: Date.now(),
      environment: this.detectEnvironment(),
      version: this.getApplicationVersion(),
      metrics,
      summary: currentSummary
    };

    const improvements: Record<string, any> = {};
    const baselineSummary = baseline.summary;

    // Compare key metrics
    const metricsToCompare = [
      'loadTime',
      'firstContentfulPaint',
      'largestContentfulPaint',
      'firstInputDelay',
      'cumulativeLayoutShift',
      'bundleSize',
      'memoryUsage',
      'networkRequests',
      'errorRate',
      'userSatisfactionScore'
    ];

    metricsToCompare.forEach(metric => {
      const baselineValue = baselineSummary[metric as keyof PerformanceSummary];
      const currentValue = currentSummary[metric as keyof PerformanceSummary];

      const improvement = baselineValue - currentValue;
      const percentage = baselineValue > 0 ? (improvement / baselineValue) * 100 : 0;

      let status: 'improved' | 'degraded' | 'unchanged' = 'unchanged';
      if (Math.abs(percentage) > 5) {
        // 5% threshold
        status = improvement > 0 ? 'improved' : 'degraded';
      }

      improvements[metric] = {
        baseline: baselineValue,
        current: currentValue,
        improvement,
        percentage,
        status
      };
    });

    // Calculate overall score
    const overallScore = this.calculateOverallScore(improvements);

    return {
      baseline,
      current,
      improvements,
      overallScore
    };
  }

  /**
   * Calculate overall performance score
   */
  private calculateOverallScore(improvements: Record<string, any>): number {
    const weights = {
      loadTime: 0.2,
      firstContentfulPaint: 0.15,
      largestContentfulPaint: 0.15,
      firstInputDelay: 0.1,
      cumulativeLayoutShift: 0.1,
      bundleSize: 0.1,
      memoryUsage: 0.05,
      networkRequests: 0.05,
      errorRate: 0.05,
      userSatisfactionScore: 0.05
    };

    let weightedScore = 0;
    let totalWeight = 0;

    Object.entries(improvements).forEach(([metric, data]) => {
      const weight = weights[metric as keyof typeof weights] || 0;
      if (weight > 0) {
        // Convert percentage to score (positive is good)
        const score = Math.max(-100, Math.min(100, data.percentage));
        weightedScore += score * weight;
        totalWeight += weight;
      }
    });

    return totalWeight > 0 ? weightedScore / totalWeight : 0;
  }

  /**
   * Get current metrics
   */
  private getCurrentMetrics(): PerformanceMetric[] {
    const metrics: PerformanceMetric[] = [];
    const now = Date.now();
    const recentThreshold = 60000; // Last minute

    this.metrics.forEach(metricList => {
      const recent = metricList.filter(m => now - m.timestamp < recentThreshold);
      metrics.push(...recent);
    });

    return metrics;
  }

  /**
   * Get performance metrics by category
   */
  getMetricsByCategory(category: PerformanceMetric['category']): PerformanceMetric[] {
    const metrics: PerformanceMetric[] = [];

    this.metrics.forEach(metricList => {
      const categoryMetrics = metricList.filter(m => m.category === category);
      metrics.push(...categoryMetrics);
    });

    return metrics.sort((a, b) => b.timestamp - a.timestamp);
  }

  /**
   * Get performance summary for time range
   */
  getPerformanceSummary(startTime: number, endTime: number): PerformanceSummary {
    const metrics: PerformanceMetric[] = [];

    this.metrics.forEach(metricList => {
      const rangeMetrics = metricList.filter(
        m => m.timestamp >= startTime && m.timestamp <= endTime
      );
      metrics.push(...rangeMetrics);
    });

    return this.calculateSummary(metrics);
  }

  /**
   * Get all baselines
   */
  getBaselines(): PerformanceBaseline[] {
    return Array.from(this.baselines.values()).sort((a, b) => b.timestamp - a.timestamp);
  }

  /**
   * Get specific baseline
   */
  getBaseline(id: string): PerformanceBaseline | undefined {
    return this.baselines.get(id);
  }

  /**
   * Export performance data
   */
  exportData(): {
    config: PerformanceConfig;
    metrics: Record<string, PerformanceMetric[]>;
    baselines: PerformanceBaseline[];
    summary: PerformanceSummary;
  } {
    const metricsObj: Record<string, PerformanceMetric[]> = {};
    this.metrics.forEach((value, key) => {
      metricsObj[key] = [...value];
    });

    return {
      config: this.config,
      metrics: metricsObj,
      baselines: this.getBaselines(),
      summary: this.getPerformanceSummary(Date.now() - 3600000, Date.now()) // Last hour
    };
  }

  /**
   * Update configuration
   */
  updateConfig(updates: Partial<PerformanceConfig>): void {
    this.config = { ...this.config, ...updates };

    if (updates.enabled !== undefined) {
      if (updates.enabled && !this.collectionInterval) {
        this.startPeriodicCollection();
      } else if (!updates.enabled && this.collectionInterval) {
        this.stopCollection();
      }
    }
  }

  /**
   * Stop performance collection
   */
  stopCollection(): void {
    if (this.collectionInterval) {
      clearInterval(this.collectionInterval);
      this.collectionInterval = null;
    }

    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    this.stopCollection();
    this.metrics.clear();
    this.baselines.clear();
    this.isInitialized = false;
  }
}

// Singleton instance
export const performanceMetrics = new PerformanceMetricsCollector();

// Export default instance
export default performanceMetrics;
