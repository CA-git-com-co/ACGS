/**
 * API Compatibility Monitoring System
 *
 * Monitors API compatibility between legacy and new implementations,
 * tracks user adoption, and identifies integration issues during migration.
 */

import { healthMonitor } from './healthMonitor';
import { alertingSystem, AlertSeverity, AlertType } from './alertingSystem';

// API endpoint interface
export interface APIEndpoint {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  service: string;
  version: string;
  deprecated?: boolean;
  deprecationDate?: string;
  replacementEndpoint?: string;
}

// API compatibility test result
export interface CompatibilityTestResult {
  endpoint: APIEndpoint;
  legacyResponse?: any;
  newResponse?: any;
  compatible: boolean;
  issues: CompatibilityIssue[];
  responseTimeDiff: number;
  timestamp: number;
}

// Compatibility issue interface
export interface CompatibilityIssue {
  type:
    | 'schema_mismatch'
    | 'response_format'
    | 'status_code'
    | 'performance'
    | 'authentication'
    | 'data_loss';
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  field?: string;
  expectedValue?: any;
  actualValue?: any;
  impact: string;
}

// User adoption metrics
export interface UserAdoptionMetrics {
  service: string;
  endpoint: string;
  legacyUsage: number;
  newUsage: number;
  adoptionRate: number; // percentage
  userCount: number;
  sessionCount: number;
  errorRate: number;
  averageResponseTime: number;
  timestamp: number;
}

// Migration progress tracking
export interface MigrationProgress {
  service: string;
  totalEndpoints: number;
  migratedEndpoints: number;
  compatibleEndpoints: number;
  deprecatedEndpoints: number;
  activeIssues: number;
  adoptionRate: number;
  estimatedCompletion: string;
  lastUpdated: number;
}

// API compatibility configuration
export interface CompatibilityConfig {
  enabled: boolean;
  testInterval: number; // milliseconds
  endpoints: APIEndpoint[];
  tolerances: {
    responseTimeDifference: number; // milliseconds
    schemaVariationThreshold: number; // percentage
    errorRateThreshold: number; // percentage
  };
  notifications: {
    compatibilityIssues: boolean;
    adoptionMilestones: boolean;
    performanceDegradation: boolean;
  };
}

// Default configuration
const DEFAULT_CONFIG: CompatibilityConfig = {
  enabled: true,
  testInterval: 300000, // 5 minutes
  endpoints: [],
  tolerances: {
    responseTimeDifference: 1000, // 1 second
    schemaVariationThreshold: 5, // 5%
    errorRateThreshold: 2 // 2%
  },
  notifications: {
    compatibilityIssues: true,
    adoptionMilestones: true,
    performanceDegradation: true
  }
};

// ACGS API endpoints for monitoring
const ACGS_API_ENDPOINTS: APIEndpoint[] = [
  // Auth Service endpoints
  {
    path: '/api/v1/auth/login',
    method: 'POST',
    service: 'auth',
    version: '1.0'
  },
  {
    path: '/api/v1/auth/logout',
    method: 'POST',
    service: 'auth',
    version: '1.0'
  },
  {
    path: '/api/v1/auth/refresh',
    method: 'POST',
    service: 'auth',
    version: '1.0'
  },

  // AC Service endpoints
  {
    path: '/api/v1/principles',
    method: 'GET',
    service: 'ac',
    version: '1.0'
  },
  {
    path: '/api/v1/principles',
    method: 'POST',
    service: 'ac',
    version: '1.0'
  },
  {
    path: '/api/v1/principles/{id}',
    method: 'PUT',
    service: 'ac',
    version: '1.0'
  },

  // GS Service endpoints
  {
    path: '/api/v1/synthesize',
    method: 'POST',
    service: 'gs',
    version: '1.0'
  },
  {
    path: '/api/v1/policies',
    method: 'GET',
    service: 'gs',
    version: '1.0'
  },

  // PGC Service endpoints
  {
    path: '/api/v1/compliance/check',
    method: 'POST',
    service: 'pgc',
    version: '1.0'
  },
  {
    path: '/api/v1/governance/workflows',
    method: 'GET',
    service: 'pgc',
    version: '1.0'
  }
];

/**
 * API Compatibility Monitor Class
 */
export class APICompatibilityMonitor {
  private config: CompatibilityConfig;
  private testResults: Map<string, CompatibilityTestResult[]> = new Map();
  private adoptionMetrics: Map<string, UserAdoptionMetrics[]> = new Map();
  private migrationProgress: Map<string, MigrationProgress> = new Map();
  private monitoringInterval: NodeJS.Timeout | null = null;
  private isInitialized = false;

  constructor(config: Partial<CompatibilityConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.config.endpoints = [...ACGS_API_ENDPOINTS, ...this.config.endpoints];
  }

  /**
   * Initialize the compatibility monitor
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Initialize migration progress for each service
      this.initializeMigrationProgress();

      // Start monitoring if enabled
      if (this.config.enabled) {
        this.startMonitoring();
      }

      this.isInitialized = true;
      console.log('API Compatibility Monitor initialized');
    } catch (error) {
      console.error('Failed to initialize API compatibility monitor:', error);
      throw error;
    }
  }

  /**
   * Initialize migration progress tracking
   */
  private initializeMigrationProgress(): void {
    const serviceEndpoints = this.groupEndpointsByService();

    for (const [service, endpoints] of serviceEndpoints.entries()) {
      this.migrationProgress.set(service, {
        service,
        totalEndpoints: endpoints.length,
        migratedEndpoints: 0,
        compatibleEndpoints: 0,
        deprecatedEndpoints: endpoints.filter(e => e.deprecated).length,
        activeIssues: 0,
        adoptionRate: 0,
        estimatedCompletion: 'Unknown',
        lastUpdated: Date.now()
      });
    }
  }

  /**
   * Group endpoints by service
   */
  private groupEndpointsByService(): Map<string, APIEndpoint[]> {
    const grouped = new Map<string, APIEndpoint[]>();

    this.config.endpoints.forEach(endpoint => {
      if (!grouped.has(endpoint.service)) {
        grouped.set(endpoint.service, []);
      }
      grouped.get(endpoint.service)!.push(endpoint);
    });

    return grouped;
  }

  /**
   * Start continuous monitoring
   */
  startMonitoring(): void {
    if (this.monitoringInterval) {
      this.stopMonitoring();
    }

    this.monitoringInterval = setInterval(async () => {
      try {
        await this.runCompatibilityTests();
        this.updateMigrationProgress();
      } catch (error) {
        console.error('Compatibility monitoring error:', error);
      }
    }, this.config.testInterval);

    console.log(`API compatibility monitoring started with ${this.config.testInterval}ms interval`);
  }

  /**
   * Stop monitoring
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
      console.log('API compatibility monitoring stopped');
    }
  }

  /**
   * Run compatibility tests for all endpoints
   */
  async runCompatibilityTests(): Promise<void> {
    const testPromises = this.config.endpoints.map(endpoint =>
      this.testEndpointCompatibility(endpoint)
    );

    const results = await Promise.allSettled(testPromises);

    results.forEach((result, index) => {
      if (result.status === 'fulfilled' && result.value) {
        this.storeTestResult(result.value);
      } else if (result.status === 'rejected') {
        console.error(`Compatibility test failed for endpoint ${index}:`, result.reason);
      }
    });
  }

  /**
   * Test compatibility for a specific endpoint
   */
  async testEndpointCompatibility(endpoint: APIEndpoint): Promise<CompatibilityTestResult | null> {
    try {
      const legacyUrl = this.buildLegacyUrl(endpoint);
      const newUrl = this.buildNewUrl(endpoint);

      // Skip if either URL is not available
      if (!legacyUrl || !newUrl) {
        return null;
      }

      const [legacyResult, newResult] = await Promise.allSettled([
        this.makeTestRequest(legacyUrl, endpoint),
        this.makeTestRequest(newUrl, endpoint)
      ]);

      const legacyResponse = legacyResult.status === 'fulfilled' ? legacyResult.value : null;
      const newResponse = newResult.status === 'fulfilled' ? newResult.value : null;

      // Analyze compatibility
      const issues = this.analyzeCompatibility(endpoint, legacyResponse, newResponse);
      const compatible =
        issues.filter(issue => issue.severity === 'critical' || issue.severity === 'high')
          .length === 0;

      const responseTimeDiff =
        legacyResponse && newResponse ? newResponse.responseTime - legacyResponse.responseTime : 0;

      const result: CompatibilityTestResult = {
        endpoint,
        legacyResponse,
        newResponse,
        compatible,
        issues,
        responseTimeDiff,
        timestamp: Date.now()
      };

      // Send alerts for critical issues
      if (issues.some(issue => issue.severity === 'critical')) {
        this.sendCompatibilityAlert(endpoint, issues);
      }

      return result;
    } catch (error) {
      console.error(`Failed to test endpoint compatibility:`, error);
      return null;
    }
  }

  /**
   * Make a test request to an endpoint
   */
  private async makeTestRequest(url: string, endpoint: APIEndpoint): Promise<any> {
    const startTime = Date.now();

    try {
      const response = await fetch(url, {
        method: endpoint.method,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          'User-Agent': 'ACGS-Compatibility-Monitor/1.0'
        },
        // Add test data for POST/PUT requests
        ...(endpoint.method !== 'GET' && {
          body: JSON.stringify(this.getTestData(endpoint))
        })
      });

      const responseTime = Date.now() - startTime;
      const data = await response.json().catch(() => null);

      return {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        data,
        responseTime,
        url
      };
    } catch (error) {
      return {
        status: 0,
        statusText: 'Network Error',
        headers: {},
        data: null,
        responseTime: Date.now() - startTime,
        url,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Analyze compatibility between legacy and new responses
   */
  private analyzeCompatibility(
    endpoint: APIEndpoint,
    legacyResponse: any,
    newResponse: any
  ): CompatibilityIssue[] {
    const issues: CompatibilityIssue[] = [];

    // Check if both responses are available
    if (!legacyResponse || !newResponse) {
      issues.push({
        type: 'response_format',
        severity: 'critical',
        description: 'One or both endpoints are not responding',
        impact: 'Complete API incompatibility'
      });
      return issues;
    }

    // Status code compatibility
    if (legacyResponse.status !== newResponse.status) {
      issues.push({
        type: 'status_code',
        severity: 'high',
        description: `Status code mismatch: ${legacyResponse.status} vs ${newResponse.status}`,
        expectedValue: legacyResponse.status,
        actualValue: newResponse.status,
        impact: 'Client error handling may break'
      });
    }

    // Response time performance
    const responseTimeDiff = Math.abs(newResponse.responseTime - legacyResponse.responseTime);
    if (responseTimeDiff > this.config.tolerances.responseTimeDifference) {
      const severity = responseTimeDiff > 2000 ? 'high' : 'medium';
      issues.push({
        type: 'performance',
        severity,
        description: `Significant response time difference: ${responseTimeDiff}ms`,
        expectedValue: legacyResponse.responseTime,
        actualValue: newResponse.responseTime,
        impact: 'User experience degradation'
      });
    }

    // Data structure compatibility
    if (legacyResponse.data && newResponse.data) {
      const schemaIssues = this.compareDataSchemas(legacyResponse.data, newResponse.data);
      issues.push(...schemaIssues);
    }

    return issues;
  }

  /**
   * Compare data schemas between responses
   */
  private compareDataSchemas(legacyData: any, newData: any): CompatibilityIssue[] {
    const issues: CompatibilityIssue[] = [];

    // Simple schema comparison (can be enhanced)
    const legacyKeys = Object.keys(legacyData || {});
    const newKeys = Object.keys(newData || {});

    // Check for missing fields
    const missingFields = legacyKeys.filter(key => !newKeys.includes(key));
    missingFields.forEach(field => {
      issues.push({
        type: 'schema_mismatch',
        severity: 'high',
        description: `Missing field in new response: ${field}`,
        field,
        expectedValue: legacyData[field],
        actualValue: undefined,
        impact: 'Client code may break due to missing data'
      });
    });

    // Check for type mismatches
    legacyKeys.forEach(key => {
      if (newKeys.includes(key)) {
        const legacyType = typeof legacyData[key];
        const newType = typeof newData[key];

        if (legacyType !== newType) {
          issues.push({
            type: 'schema_mismatch',
            severity: 'medium',
            description: `Type mismatch for field ${key}: ${legacyType} vs ${newType}`,
            field: key,
            expectedValue: legacyType,
            actualValue: newType,
            impact: 'Type coercion may be required'
          });
        }
      }
    });

    return issues;
  }

  /**
   * Build legacy API URL
   */
  private buildLegacyUrl(endpoint: APIEndpoint): string | null {
    const baseUrls: Record<string, string> = {
      auth: process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8002',
      ac: process.env.REACT_APP_AC_API_URL || 'http://localhost:8001',
      gs: process.env.REACT_APP_GS_API_URL || 'http://localhost:8003',
      pgc: process.env.REACT_APP_PGC_API_URL || 'http://localhost:8005',
      integrity: process.env.REACT_APP_INTEGRITY_API_URL || 'http://localhost:8006',
      fv: process.env.REACT_APP_FV_API_URL || 'http://localhost:8004',
      ec: process.env.REACT_APP_EC_API_URL || 'http://localhost:8007'
    };

    const baseUrl = baseUrls[endpoint.service];
    return baseUrl ? `${baseUrl}${endpoint.path}` : null;
  }

  /**
   * Build new API URL (same as legacy for now, but could be different)
   */
  private buildNewUrl(endpoint: APIEndpoint): string | null {
    // For now, new URLs are the same as legacy URLs
    // In a real migration, these might point to different services
    return this.buildLegacyUrl(endpoint);
  }

  /**
   * Get test data for POST/PUT requests
   */
  private getTestData(endpoint: APIEndpoint): any {
    const testData: Record<string, any> = {
      '/api/v1/auth/login': {
        username: 'test@acgs.org',
        password: 'test123'
      },
      '/api/v1/principles': {
        title: 'Test Principle',
        content: 'This is a test principle for compatibility testing',
        category: 'test',
        priority: 1
      },
      '/api/v1/synthesize': {
        principles: [{ id: 'test-principle-1' }]
      },
      '/api/v1/compliance/check': {
        action: 'test_action',
        context: { test: true },
        policy: 'test_policy'
      }
    };

    return testData[endpoint.path] || {};
  }

  /**
   * Store test result
   */
  private storeTestResult(result: CompatibilityTestResult): void {
    const key = `${result.endpoint.service}-${result.endpoint.path}-${result.endpoint.method}`;

    if (!this.testResults.has(key)) {
      this.testResults.set(key, []);
    }

    const results = this.testResults.get(key)!;
    results.push(result);

    // Keep only last 100 results
    if (results.length > 100) {
      results.splice(0, results.length - 100);
    }
  }

  /**
   * Send compatibility alert
   */
  private sendCompatibilityAlert(endpoint: APIEndpoint, issues: CompatibilityIssue[]): void {
    const criticalIssues = issues.filter(issue => issue.severity === 'critical');
    const highIssues = issues.filter(issue => issue.severity === 'high');

    if (criticalIssues.length > 0 || highIssues.length > 0) {
      const severity = criticalIssues.length > 0 ? AlertSeverity.CRITICAL : AlertSeverity.HIGH;

      alertingSystem.createAlert({
        type: AlertType.SYSTEM_OVERLOAD, // Using closest available type
        severity,
        service: endpoint.service,
        title: `API Compatibility Issue: ${endpoint.service}`,
        message: `Compatibility issues detected for ${endpoint.method} ${endpoint.path}: ${issues.length} issues found`,
        metadata: {
          endpoint,
          issues,
          criticalCount: criticalIssues.length,
          highCount: highIssues.length
        }
      });
    }
  }

  /**
   * Update migration progress
   */
  private updateMigrationProgress(): void {
    const serviceEndpoints = this.groupEndpointsByService();

    for (const [service, endpoints] of serviceEndpoints.entries()) {
      const progress = this.migrationProgress.get(service);
      if (!progress) continue;

      let compatibleCount = 0;
      let activeIssuesCount = 0;

      endpoints.forEach(endpoint => {
        const key = `${endpoint.service}-${endpoint.path}-${endpoint.method}`;
        const results = this.testResults.get(key) || [];
        const latestResult = results[results.length - 1];

        if (latestResult) {
          if (latestResult.compatible) {
            compatibleCount++;
          }

          const criticalIssues = latestResult.issues.filter(
            issue => issue.severity === 'critical' || issue.severity === 'high'
          );
          activeIssuesCount += criticalIssues.length;
        }
      });

      // Update progress
      progress.compatibleEndpoints = compatibleCount;
      progress.activeIssues = activeIssuesCount;
      progress.adoptionRate = this.calculateAdoptionRate(service);
      progress.estimatedCompletion = this.estimateCompletion(progress);
      progress.lastUpdated = Date.now();
    }
  }

  /**
   * Calculate adoption rate for a service
   */
  private calculateAdoptionRate(service: string): number {
    const metrics = this.adoptionMetrics.get(service);
    if (!metrics || metrics.length === 0) return 0;

    const latestMetrics = metrics[metrics.length - 1];
    return latestMetrics.adoptionRate;
  }

  /**
   * Estimate completion time
   */
  private estimateCompletion(progress: MigrationProgress): string {
    const completionRate = progress.compatibleEndpoints / progress.totalEndpoints;

    if (completionRate >= 1.0) {
      return 'Complete';
    } else if (completionRate >= 0.8) {
      return '1-2 weeks';
    } else if (completionRate >= 0.6) {
      return '2-4 weeks';
    } else if (completionRate >= 0.4) {
      return '1-2 months';
    } else {
      return '2+ months';
    }
  }

  /**
   * Track user adoption metrics
   */
  trackUserAdoption(metrics: UserAdoptionMetrics): void {
    const key = `${metrics.service}-${metrics.endpoint}`;

    if (!this.adoptionMetrics.has(key)) {
      this.adoptionMetrics.set(key, []);
    }

    const metricsList = this.adoptionMetrics.get(key)!;
    metricsList.push(metrics);

    // Keep only last 1000 metrics
    if (metricsList.length > 1000) {
      metricsList.splice(0, metricsList.length - 1000);
    }

    // Check for adoption milestones
    this.checkAdoptionMilestones(metrics);
  }

  /**
   * Check for adoption milestones
   */
  private checkAdoptionMilestones(metrics: UserAdoptionMetrics): void {
    const milestones = [25, 50, 75, 90, 95];

    milestones.forEach(milestone => {
      if (metrics.adoptionRate >= milestone && this.config.notifications.adoptionMilestones) {
        alertingSystem.createAlert({
          type: AlertType.SYSTEM_OVERLOAD,
          severity: AlertSeverity.INFO,
          service: metrics.service,
          title: `Adoption Milestone: ${milestone}%`,
          message: `${metrics.service} ${metrics.endpoint} has reached ${milestone}% adoption rate`,
          metadata: {
            milestone,
            adoptionRate: metrics.adoptionRate,
            userCount: metrics.userCount,
            endpoint: metrics.endpoint
          }
        });
      }
    });
  }

  /**
   * Get compatibility report
   */
  getCompatibilityReport(): {
    summary: {
      totalEndpoints: number;
      compatibleEndpoints: number;
      incompatibleEndpoints: number;
      overallCompatibility: number;
    };
    byService: Record<
      string,
      {
        compatible: number;
        total: number;
        issues: number;
        adoptionRate: number;
      }
    >;
    recentIssues: CompatibilityIssue[];
  } {
    const serviceEndpoints = this.groupEndpointsByService();
    let totalEndpoints = 0;
    let compatibleEndpoints = 0;
    const recentIssues: CompatibilityIssue[] = [];
    const byService: Record<string, any> = {};

    for (const [service, endpoints] of serviceEndpoints.entries()) {
      let serviceCompatible = 0;
      let serviceIssues = 0;

      endpoints.forEach(endpoint => {
        totalEndpoints++;
        const key = `${endpoint.service}-${endpoint.path}-${endpoint.method}`;
        const results = this.testResults.get(key) || [];
        const latestResult = results[results.length - 1];

        if (latestResult) {
          if (latestResult.compatible) {
            compatibleEndpoints++;
            serviceCompatible++;
          }

          serviceIssues += latestResult.issues.length;

          // Collect recent critical/high issues
          const criticalIssues = latestResult.issues.filter(
            issue =>
              (issue.severity === 'critical' || issue.severity === 'high') &&
              Date.now() - latestResult.timestamp < 86400000 // Last 24 hours
          );
          recentIssues.push(...criticalIssues);
        }
      });

      const progress = this.migrationProgress.get(service);
      byService[service] = {
        compatible: serviceCompatible,
        total: endpoints.length,
        issues: serviceIssues,
        adoptionRate: progress?.adoptionRate || 0
      };
    }

    return {
      summary: {
        totalEndpoints,
        compatibleEndpoints,
        incompatibleEndpoints: totalEndpoints - compatibleEndpoints,
        overallCompatibility: totalEndpoints > 0 ? (compatibleEndpoints / totalEndpoints) * 100 : 0
      },
      byService,
      recentIssues: recentIssues.slice(0, 20) // Last 20 issues
    };
  }

  /**
   * Get migration progress
   */
  getMigrationProgress(): Record<string, MigrationProgress> {
    const progress: Record<string, MigrationProgress> = {};
    this.migrationProgress.forEach((value, key) => {
      progress[key] = { ...value };
    });
    return progress;
  }

  /**
   * Get adoption metrics
   */
  getAdoptionMetrics(service?: string): Record<string, UserAdoptionMetrics[]> {
    const metrics: Record<string, UserAdoptionMetrics[]> = {};

    this.adoptionMetrics.forEach((value, key) => {
      if (!service || key.startsWith(service)) {
        metrics[key] = [...value];
      }
    });

    return metrics;
  }

  /**
   * Get test results
   */
  getTestResults(service?: string): Record<string, CompatibilityTestResult[]> {
    const results: Record<string, CompatibilityTestResult[]> = {};

    this.testResults.forEach((value, key) => {
      if (!service || key.startsWith(service)) {
        results[key] = [...value];
      }
    });

    return results;
  }

  /**
   * Update configuration
   */
  updateConfig(updates: Partial<CompatibilityConfig>): void {
    this.config = { ...this.config, ...updates };

    if (updates.enabled !== undefined) {
      if (updates.enabled && !this.monitoringInterval) {
        this.startMonitoring();
      } else if (!updates.enabled && this.monitoringInterval) {
        this.stopMonitoring();
      }
    }
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    this.stopMonitoring();
    this.testResults.clear();
    this.adoptionMetrics.clear();
    this.migrationProgress.clear();
    this.isInitialized = false;
  }
}

// Singleton instance
export const apiCompatibilityMonitor = new APICompatibilityMonitor();

// Export default instance
export default apiCompatibilityMonitor;
