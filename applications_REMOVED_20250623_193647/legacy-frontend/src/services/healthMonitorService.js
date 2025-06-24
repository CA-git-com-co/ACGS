/**
 * Health Monitor Service Integration for Legacy Frontend
 *
 * Provides health monitoring capabilities specifically for the legacy-frontend
 * application with integration to the shared health monitoring system.
 */

import { healthMonitor, ACGS_SERVICES } from '@acgs/shared/services/healthMonitor';

// Legacy-specific health monitoring configuration
const LEGACY_HEALTH_CONFIG = {
  // Monitoring intervals
  FAST_INTERVAL: 10000, // 10 seconds for critical monitoring
  NORMAL_INTERVAL: 30000, // 30 seconds for normal monitoring
  SLOW_INTERVAL: 60000, // 60 seconds for background monitoring

  // Alert thresholds for legacy frontend
  RESPONSE_TIME_THRESHOLD: 2000, // 2 seconds
  ERROR_RATE_THRESHOLD: 5, // 5%
  UPTIME_THRESHOLD: 99.5, // 99.5%
  CONSECUTIVE_FAILURES: 3, // 3 consecutive failures

  // Critical services for legacy frontend
  CRITICAL_SERVICES: ['auth', 'ac', 'gs', 'pgc'],

  // Services required for Quantumagi functionality
  QUANTUMAGI_SERVICES: ['auth', 'ac', 'pgc'],
};

// Health status cache for performance
let healthStatusCache = {
  lastUpdate: 0,
  data: {},
  cacheTimeout: 5000, // 5 seconds
};

// Alert history for deduplication
let alertHistory = new Map();

/**
 * Legacy Health Monitor Service Class
 */
class LegacyHealthMonitorService {
  constructor() {
    this.isInitialized = false;
    this.monitoringMode = 'normal'; // 'fast', 'normal', 'slow'
    this.alertCallbacks = [];
    this.statusCallbacks = [];
    this.criticalServiceFailures = new Set();

    // Bind methods
    this.handleAlert = this.handleAlert.bind(this);
    this.handleStatusChange = this.handleStatusChange.bind(this);
  }

  /**
   * Initialize the health monitoring service
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      // Configure health monitor with legacy-specific settings
      healthMonitor.alertConfig = {
        enabled: true,
        responseTimeThreshold: LEGACY_HEALTH_CONFIG.RESPONSE_TIME_THRESHOLD,
        errorRateThreshold: LEGACY_HEALTH_CONFIG.ERROR_RATE_THRESHOLD,
        uptimeThreshold: LEGACY_HEALTH_CONFIG.UPTIME_THRESHOLD,
        consecutiveFailuresThreshold: LEGACY_HEALTH_CONFIG.CONSECUTIVE_FAILURES,
      };

      // Set up alert handling
      healthMonitor.onAlert(this.handleAlert);

      // Perform initial health check
      await this.checkAllServices();

      // Start monitoring based on current mode
      this.startMonitoring();

      this.isInitialized = true;
      console.log('Legacy Health Monitor Service initialized');
    } catch (error) {
      console.error('Failed to initialize health monitor service:', error);
      throw error;
    }
  }

  /**
   * Check health of all services
   */
  async checkAllServices() {
    try {
      const results = await healthMonitor.checkAllServices();

      // Update cache
      healthStatusCache = {
        lastUpdate: Date.now(),
        data: results,
        cacheTimeout: LEGACY_HEALTH_CONFIG.NORMAL_INTERVAL / 6, // Cache for 1/6 of interval
      };

      // Check for critical service failures
      this.checkCriticalServices(results);

      // Notify status callbacks
      this.statusCallbacks.forEach((callback) => {
        try {
          callback(results);
        } catch (error) {
          console.error('Status callback error:', error);
        }
      });

      return results;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  /**
   * Get cached health status (for performance)
   */
  getCachedHealthStatus() {
    const now = Date.now();
    if (now - healthStatusCache.lastUpdate < healthStatusCache.cacheTimeout) {
      return healthStatusCache.data;
    }
    return null;
  }

  /**
   * Check specific service health
   */
  async checkService(serviceKey) {
    try {
      return await healthMonitor.checkServiceHealth(serviceKey);
    } catch (error) {
      console.error(`Health check failed for ${serviceKey}:`, error);
      throw error;
    }
  }

  /**
   * Get service metrics
   */
  getServiceMetrics(serviceKey = null) {
    return healthMonitor.getServiceMetrics(serviceKey);
  }

  /**
   * Get system health overview
   */
  getSystemHealth() {
    return healthMonitor.getSystemHealth();
  }

  /**
   * Check critical services for failures
   */
  checkCriticalServices(results) {
    const previousFailures = new Set(this.criticalServiceFailures);
    this.criticalServiceFailures.clear();

    LEGACY_HEALTH_CONFIG.CRITICAL_SERVICES.forEach((serviceKey) => {
      const result = results[serviceKey];
      if (result && result.status === 'unhealthy') {
        this.criticalServiceFailures.add(serviceKey);

        // If this is a new failure, trigger immediate alert
        if (!previousFailures.has(serviceKey)) {
          this.triggerCriticalServiceAlert(serviceKey, result);
        }
      }
    });

    // Check for recovery
    previousFailures.forEach((serviceKey) => {
      if (!this.criticalServiceFailures.has(serviceKey)) {
        this.triggerServiceRecoveryAlert(serviceKey);
      }
    });
  }

  /**
   * Check if Quantumagi services are healthy
   */
  isQuantumagiHealthy() {
    const cached = this.getCachedHealthStatus();
    if (!cached) return null;

    return LEGACY_HEALTH_CONFIG.QUANTUMAGI_SERVICES.every((serviceKey) => {
      const result = cached[serviceKey];
      return result && result.status === 'healthy';
    });
  }

  /**
   * Set monitoring mode
   */
  setMonitoringMode(mode) {
    if (!['fast', 'normal', 'slow'].includes(mode)) {
      throw new Error(`Invalid monitoring mode: ${mode}`);
    }

    this.monitoringMode = mode;

    if (this.isInitialized) {
      this.stopMonitoring();
      this.startMonitoring();
    }
  }

  /**
   * Start monitoring based on current mode
   */
  startMonitoring() {
    let interval;
    switch (this.monitoringMode) {
      case 'fast':
        interval = LEGACY_HEALTH_CONFIG.FAST_INTERVAL;
        break;
      case 'slow':
        interval = LEGACY_HEALTH_CONFIG.SLOW_INTERVAL;
        break;
      default:
        interval = LEGACY_HEALTH_CONFIG.NORMAL_INTERVAL;
    }

    healthMonitor.startMonitoring(interval);
    console.log(
      `Health monitoring started in ${this.monitoringMode} mode (${interval}ms interval)`
    );
  }

  /**
   * Stop monitoring
   */
  stopMonitoring() {
    healthMonitor.stopMonitoring();
  }

  /**
   * Handle alerts from health monitor
   */
  handleAlert(alert) {
    // Deduplicate alerts
    const alertKey = `${alert.service}-${alert.type}`;
    const lastAlert = alertHistory.get(alertKey);
    const now = Date.now();

    // Don't send duplicate alerts within 5 minutes
    if (lastAlert && now - lastAlert < 300000) {
      return;
    }

    alertHistory.set(alertKey, now);

    // Add legacy-specific context
    const enhancedAlert = {
      ...alert,
      legacyContext: {
        isCriticalService: LEGACY_HEALTH_CONFIG.CRITICAL_SERVICES.includes(alert.service),
        isQuantumagiService: LEGACY_HEALTH_CONFIG.QUANTUMAGI_SERVICES.includes(alert.service),
        serviceName: ACGS_SERVICES[alert.service]?.name || alert.service,
        recommendedAction: this.getRecommendedAction(alert),
      },
    };

    // Notify alert callbacks
    this.alertCallbacks.forEach((callback) => {
      try {
        callback(enhancedAlert);
      } catch (error) {
        console.error('Alert callback error:', error);
      }
    });

    // Log alert
    console.warn('Health Alert:', enhancedAlert);
  }

  /**
   * Handle status changes
   */
  handleStatusChange(results) {
    // This method can be extended for legacy-specific status change handling
    console.log('Health status updated:', Object.keys(results).length, 'services checked');
  }

  /**
   * Get recommended action for alert
   */
  getRecommendedAction(alert) {
    const service = ACGS_SERVICES[alert.service];

    switch (alert.type) {
      case 'response_time':
        return `Check ${service?.name || alert.service} performance and server load`;
      case 'error_rate':
        return `Review ${service?.name || alert.service} logs for errors`;
      case 'uptime':
        return `Investigate ${service?.name || alert.service} availability issues`;
      case 'consecutive_failures':
        return `Immediate attention required for ${service?.name || alert.service}`;
      default:
        return 'Monitor service status and investigate if issues persist';
    }
  }

  /**
   * Trigger critical service alert
   */
  triggerCriticalServiceAlert(serviceKey, result) {
    const alert = {
      type: 'critical_service_failure',
      service: serviceKey,
      severity: 'critical',
      message: `Critical service ${ACGS_SERVICES[serviceKey]?.name || serviceKey} is down`,
      timestamp: Date.now(),
      result,
    };

    this.handleAlert(alert);
  }

  /**
   * Trigger service recovery alert
   */
  triggerServiceRecoveryAlert(serviceKey) {
    const alert = {
      type: 'service_recovery',
      service: serviceKey,
      severity: 'info',
      message: `Service ${ACGS_SERVICES[serviceKey]?.name || serviceKey} has recovered`,
      timestamp: Date.now(),
    };

    this.handleAlert(alert);
  }

  /**
   * Add alert callback
   */
  onAlert(callback) {
    this.alertCallbacks.push(callback);
  }

  /**
   * Remove alert callback
   */
  removeAlert(callback) {
    const index = this.alertCallbacks.indexOf(callback);
    if (index > -1) {
      this.alertCallbacks.splice(index, 1);
    }
  }

  /**
   * Add status change callback
   */
  onStatusChange(callback) {
    this.statusCallbacks.push(callback);
  }

  /**
   * Remove status change callback
   */
  removeStatusChange(callback) {
    const index = this.statusCallbacks.indexOf(callback);
    if (index > -1) {
      this.statusCallbacks.splice(index, 1);
    }
  }

  /**
   * Export health data for debugging
   */
  exportHealthData() {
    return {
      config: LEGACY_HEALTH_CONFIG,
      cache: healthStatusCache,
      criticalFailures: Array.from(this.criticalServiceFailures),
      systemHealth: this.getSystemHealth(),
      serviceMetrics: this.getServiceMetrics(),
      monitoringMode: this.monitoringMode,
      isInitialized: this.isInitialized,
    };
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    this.stopMonitoring();
    healthMonitor.removeAlert(this.handleAlert);
    this.alertCallbacks = [];
    this.statusCallbacks = [];
    this.criticalServiceFailures.clear();
    this.isInitialized = false;
  }
}

// Create singleton instance
const legacyHealthMonitorService = new LegacyHealthMonitorService();

// Export service instance and utilities
export default legacyHealthMonitorService;
export { LEGACY_HEALTH_CONFIG, ACGS_SERVICES };

// Auto-initialize if in browser environment
if (typeof window !== 'undefined') {
  // Initialize after a short delay to allow other services to start
  setTimeout(() => {
    legacyHealthMonitorService.initialize().catch((error) => {
      console.error('Failed to auto-initialize health monitor:', error);
    });
  }, 1000);
}
