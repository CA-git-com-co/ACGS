/**
 * ACGS Service Health Monitoring System
 * 
 * Comprehensive health monitoring for all 7 ACGS core services
 * with real-time status tracking, performance metrics, and alerting.
 */

import axios, { AxiosResponse } from 'axios';

// Service configuration interface
export interface ServiceConfig {
  name: string;
  port: number;
  baseUrl: string;
  healthEndpoint: string;
  description: string;
  critical: boolean;
  timeout: number;
}

// Health check result interface
export interface HealthCheckResult {
  service: string;
  status: 'healthy' | 'unhealthy' | 'degraded' | 'unknown';
  responseTime: number;
  timestamp: number;
  details?: any;
  error?: string;
  version?: string;
  dependencies?: Record<string, boolean>;
}

// Service metrics interface
export interface ServiceMetrics {
  service: string;
  uptime: number;
  averageResponseTime: number;
  errorRate: number;
  lastHealthCheck: number;
  healthHistory: HealthCheckResult[];
}

// Alert configuration
export interface AlertConfig {
  enabled: boolean;
  responseTimeThreshold: number; // ms
  errorRateThreshold: number; // percentage
  uptimeThreshold: number; // percentage
  consecutiveFailuresThreshold: number;
}

// ACGS Core Services Configuration
export const ACGS_SERVICES: Record<string, ServiceConfig> = {
  auth: {
    name: 'Authentication Service',
    port: 8002, // Updated based on codebase analysis
    baseUrl: process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8002',
    healthEndpoint: '/health',
    description: 'Authentication and authorization service',
    critical: true,
    timeout: 5000,
  },
  ac: {
    name: 'Constitutional AI Service',
    port: 8001,
    baseUrl: process.env.REACT_APP_AC_API_URL || 'http://localhost:8001',
    healthEndpoint: '/health',
    description: 'Constitutional AI and compliance service',
    critical: true,
    timeout: 5000,
  },
  integrity: {
    name: 'Integrity Service',
    port: 8006,
    baseUrl: process.env.REACT_APP_INTEGRITY_API_URL || 'http://localhost:8006',
    healthEndpoint: '/health',
    description: 'Cryptographic integrity and verification service',
    critical: true,
    timeout: 5000,
  },
  fv: {
    name: 'Formal Verification Service',
    port: 8004,
    baseUrl: process.env.REACT_APP_FV_API_URL || 'http://localhost:8004',
    healthEndpoint: '/health',
    description: 'Formal verification service',
    critical: false,
    timeout: 10000, // FV operations can take longer
  },
  gs: {
    name: 'Governance Synthesis Service',
    port: 8003,
    baseUrl: process.env.REACT_APP_GS_API_URL || 'http://localhost:8003',
    healthEndpoint: '/health',
    description: 'Governance synthesis service',
    critical: true,
    timeout: 5000,
  },
  pgc: {
    name: 'Policy Governance Service',
    port: 8005,
    baseUrl: process.env.REACT_APP_PGC_API_URL || 'http://localhost:8005',
    healthEndpoint: '/health',
    description: 'Policy governance and compliance service',
    critical: true,
    timeout: 5000,
  },
  ec: {
    name: 'Executive Council Service',
    port: 8007,
    baseUrl: process.env.REACT_APP_EC_API_URL || 'http://localhost:8007',
    healthEndpoint: '/health',
    description: 'Executive council and oversight service',
    critical: false,
    timeout: 5000,
  },
};

// Health Monitor Class
export class ACGSHealthMonitor {
  private metrics: Map<string, ServiceMetrics> = new Map();
  private alertConfig: AlertConfig;
  private monitoringInterval: NodeJS.Timeout | null = null;
  private alertCallbacks: Array<(alert: any) => void> = [];

  constructor(alertConfig: Partial<AlertConfig> = {}) {
    this.alertConfig = {
      enabled: true,
      responseTimeThreshold: 2000, // 2 seconds
      errorRateThreshold: 5, // 5%
      uptimeThreshold: 99.5, // 99.5%
      consecutiveFailuresThreshold: 3,
      ...alertConfig,
    };

    // Initialize metrics for all services
    Object.keys(ACGS_SERVICES).forEach(serviceKey => {
      this.metrics.set(serviceKey, {
        service: serviceKey,
        uptime: 100,
        averageResponseTime: 0,
        errorRate: 0,
        lastHealthCheck: 0,
        healthHistory: [],
      });
    });
  }

  // Perform health check for a single service
  async checkServiceHealth(serviceKey: string): Promise<HealthCheckResult> {
    const service = ACGS_SERVICES[serviceKey];
    if (!service) {
      throw new Error(`Unknown service: ${serviceKey}`);
    }

    const startTime = Date.now();
    const result: HealthCheckResult = {
      service: serviceKey,
      status: 'unknown',
      responseTime: 0,
      timestamp: startTime,
    };

    try {
      const response: AxiosResponse = await axios.get(
        `${service.baseUrl}${service.healthEndpoint}`,
        {
          timeout: service.timeout,
          headers: {
            'Accept': 'application/json',
            'User-Agent': 'ACGS-Health-Monitor/1.0',
          },
        }
      );

      const responseTime = Date.now() - startTime;
      result.responseTime = responseTime;
      result.status = response.status === 200 ? 'healthy' : 'degraded';
      result.details = response.data;
      result.version = response.data?.version;
      result.dependencies = response.data?.dependencies || response.data?.services;

    } catch (error: any) {
      result.responseTime = Date.now() - startTime;
      result.status = 'unhealthy';
      result.error = error.message;

      // Classify error types
      if (error.code === 'ECONNREFUSED') {
        result.error = 'Service unavailable (connection refused)';
      } else if (error.code === 'ETIMEDOUT') {
        result.error = 'Service timeout';
      } else if (error.response?.status >= 500) {
        result.status = 'degraded';
        result.error = `Server error: ${error.response.status}`;
      }
    }

    // Update metrics
    this.updateMetrics(serviceKey, result);

    return result;
  }

  // Check health of all services
  async checkAllServices(): Promise<Record<string, HealthCheckResult>> {
    const results: Record<string, HealthCheckResult> = {};
    
    const healthChecks = Object.keys(ACGS_SERVICES).map(async (serviceKey) => {
      try {
        results[serviceKey] = await this.checkServiceHealth(serviceKey);
      } catch (error) {
        results[serviceKey] = {
          service: serviceKey,
          status: 'unhealthy',
          responseTime: 0,
          timestamp: Date.now(),
          error: error instanceof Error ? error.message : 'Unknown error',
        };
      }
    });

    await Promise.all(healthChecks);
    return results;
  }

  // Update service metrics
  private updateMetrics(serviceKey: string, result: HealthCheckResult): void {
    const metrics = this.metrics.get(serviceKey);
    if (!metrics) return;

    // Add to history (keep last 100 checks)
    metrics.healthHistory.push(result);
    if (metrics.healthHistory.length > 100) {
      metrics.healthHistory.shift();
    }

    // Update last check time
    metrics.lastHealthCheck = result.timestamp;

    // Calculate uptime (last 100 checks)
    const healthyChecks = metrics.healthHistory.filter(h => h.status === 'healthy').length;
    metrics.uptime = (healthyChecks / metrics.healthHistory.length) * 100;

    // Calculate average response time (last 20 checks)
    const recentChecks = metrics.healthHistory.slice(-20);
    const totalResponseTime = recentChecks.reduce((sum, check) => sum + check.responseTime, 0);
    metrics.averageResponseTime = totalResponseTime / recentChecks.length;

    // Calculate error rate (last 100 checks)
    const errorChecks = metrics.healthHistory.filter(h => h.status === 'unhealthy').length;
    metrics.errorRate = (errorChecks / metrics.healthHistory.length) * 100;

    // Check for alerts
    this.checkAlerts(serviceKey, metrics, result);
  }

  // Check for alert conditions
  private checkAlerts(serviceKey: string, metrics: ServiceMetrics, latestResult: HealthCheckResult): void {
    if (!this.alertConfig.enabled) return;

    const service = ACGS_SERVICES[serviceKey];
    const alerts: any[] = [];

    // Response time alert
    if (latestResult.responseTime > this.alertConfig.responseTimeThreshold) {
      alerts.push({
        type: 'response_time',
        service: serviceKey,
        severity: service.critical ? 'critical' : 'warning',
        message: `${service.name} response time (${latestResult.responseTime}ms) exceeds threshold (${this.alertConfig.responseTimeThreshold}ms)`,
        value: latestResult.responseTime,
        threshold: this.alertConfig.responseTimeThreshold,
        timestamp: latestResult.timestamp,
      });
    }

    // Error rate alert
    if (metrics.errorRate > this.alertConfig.errorRateThreshold) {
      alerts.push({
        type: 'error_rate',
        service: serviceKey,
        severity: service.critical ? 'critical' : 'warning',
        message: `${service.name} error rate (${metrics.errorRate.toFixed(1)}%) exceeds threshold (${this.alertConfig.errorRateThreshold}%)`,
        value: metrics.errorRate,
        threshold: this.alertConfig.errorRateThreshold,
        timestamp: latestResult.timestamp,
      });
    }

    // Uptime alert
    if (metrics.uptime < this.alertConfig.uptimeThreshold) {
      alerts.push({
        type: 'uptime',
        service: serviceKey,
        severity: service.critical ? 'critical' : 'warning',
        message: `${service.name} uptime (${metrics.uptime.toFixed(1)}%) below threshold (${this.alertConfig.uptimeThreshold}%)`,
        value: metrics.uptime,
        threshold: this.alertConfig.uptimeThreshold,
        timestamp: latestResult.timestamp,
      });
    }

    // Consecutive failures alert
    const recentFailures = metrics.healthHistory.slice(-this.alertConfig.consecutiveFailuresThreshold);
    if (recentFailures.length === this.alertConfig.consecutiveFailuresThreshold &&
        recentFailures.every(check => check.status === 'unhealthy')) {
      alerts.push({
        type: 'consecutive_failures',
        service: serviceKey,
        severity: 'critical',
        message: `${service.name} has ${this.alertConfig.consecutiveFailuresThreshold} consecutive failures`,
        value: this.alertConfig.consecutiveFailuresThreshold,
        threshold: this.alertConfig.consecutiveFailuresThreshold,
        timestamp: latestResult.timestamp,
      });
    }

    // Trigger alert callbacks
    alerts.forEach(alert => {
      this.alertCallbacks.forEach(callback => {
        try {
          callback(alert);
        } catch (error) {
          console.error('Alert callback error:', error);
        }
      });
    });
  }

  // Get service metrics
  getServiceMetrics(serviceKey?: string): ServiceMetrics | Record<string, ServiceMetrics> {
    if (serviceKey) {
      return this.metrics.get(serviceKey) || {} as ServiceMetrics;
    }
    
    const allMetrics: Record<string, ServiceMetrics> = {};
    this.metrics.forEach((metrics, key) => {
      allMetrics[key] = metrics;
    });
    return allMetrics;
  }

  // Get overall system health
  getSystemHealth(): {
    status: 'healthy' | 'degraded' | 'unhealthy';
    healthyServices: number;
    totalServices: number;
    criticalServicesDown: number;
    averageResponseTime: number;
    overallUptime: number;
  } {
    const allMetrics = this.getServiceMetrics() as Record<string, ServiceMetrics>;
    const serviceKeys = Object.keys(allMetrics);
    
    let healthyServices = 0;
    let criticalServicesDown = 0;
    let totalResponseTime = 0;
    let totalUptime = 0;

    serviceKeys.forEach(key => {
      const metrics = allMetrics[key];
      const service = ACGS_SERVICES[key];
      
      if (metrics.uptime > 95) healthyServices++;
      if (service.critical && metrics.uptime < 95) criticalServicesDown++;
      
      totalResponseTime += metrics.averageResponseTime;
      totalUptime += metrics.uptime;
    });

    const averageResponseTime = totalResponseTime / serviceKeys.length;
    const overallUptime = totalUptime / serviceKeys.length;

    let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
    if (criticalServicesDown > 0) {
      status = 'unhealthy';
    } else if (overallUptime < 99 || averageResponseTime > 1000) {
      status = 'degraded';
    }

    return {
      status,
      healthyServices,
      totalServices: serviceKeys.length,
      criticalServicesDown,
      averageResponseTime,
      overallUptime,
    };
  }

  // Start continuous monitoring
  startMonitoring(intervalMs: number = 30000): void {
    if (this.monitoringInterval) {
      this.stopMonitoring();
    }

    this.monitoringInterval = setInterval(async () => {
      try {
        await this.checkAllServices();
      } catch (error) {
        console.error('Health monitoring error:', error);
      }
    }, intervalMs);

    console.log(`Health monitoring started with ${intervalMs}ms interval`);
  }

  // Stop continuous monitoring
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
      console.log('Health monitoring stopped');
    }
  }

  // Add alert callback
  onAlert(callback: (alert: any) => void): void {
    this.alertCallbacks.push(callback);
  }

  // Remove alert callback
  removeAlert(callback: (alert: any) => void): void {
    const index = this.alertCallbacks.indexOf(callback);
    if (index > -1) {
      this.alertCallbacks.splice(index, 1);
    }
  }

  // Export metrics for external monitoring systems
  exportMetrics(): any {
    const systemHealth = this.getSystemHealth();
    const serviceMetrics = this.getServiceMetrics() as Record<string, ServiceMetrics>;

    return {
      timestamp: Date.now(),
      system: systemHealth,
      services: serviceMetrics,
      configuration: {
        alertConfig: this.alertConfig,
        services: ACGS_SERVICES,
      },
    };
  }
}

// Singleton instance
export const healthMonitor = new ACGSHealthMonitor();

// Export default instance
export default healthMonitor;
