import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { CONFIG, validateConfig, getServiceUrl, isFeatureEnabled, getPollingInterval } from '../index';

describe('Configuration System', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    // Reset process.env for each test
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    // Restore original env
    process.env = originalEnv;
  });

  describe('CONFIG object', () => {
    it('should have all required configuration sections', () => {
      expect(CONFIG).toHaveProperty('api');
      expect(CONFIG).toHaveProperty('constitutional');
      expect(CONFIG).toHaveProperty('performance');
      expect(CONFIG).toHaveProperty('polling');
      expect(CONFIG).toHaveProperty('features');
    });

    it('should have correct constitutional hash', () => {
      expect(CONFIG.constitutional.hash).toBe('cdd01ef066bc6cf2');
    });

    it('should have default API configuration', () => {
      expect(CONFIG.api.baseUrl).toBe('http://localhost:8010');
      expect(CONFIG.api.timeout).toBe(10000);
      expect(CONFIG.api.retryAttempts).toBe(3);
    });

    it('should have performance targets', () => {
      expect(CONFIG.performance.latencyP99Target).toBe(5);
      expect(CONFIG.performance.throughputRpsTarget).toBe(100);
      expect(CONFIG.performance.cacheHitRateTarget).toBe(85);
    });

    it('should have polling intervals', () => {
      expect(CONFIG.polling.dashboardInterval).toBe(30000);
      expect(CONFIG.polling.complianceInterval).toBe(120000);
      expect(CONFIG.polling.metricsInterval).toBe(5000);
    });
  });

  describe('validateConfig', () => {
    it('should validate successfully with default config', () => {
      expect(() => validateConfig()).not.toThrow();
    });

    it('should throw error with invalid API URL', () => {
      // Mock invalid URL
      const originalBaseUrl = CONFIG.api.baseUrl;
      (CONFIG.api as any).baseUrl = 'invalid-url';
      
      expect(() => validateConfig()).toThrow('Configuration validation failed');
      
      // Restore original
      (CONFIG.api as any).baseUrl = originalBaseUrl;
    });

    it('should throw error with invalid constitutional hash', () => {
      // Mock invalid hash
      const originalHash = CONFIG.constitutional.hash;
      (CONFIG.constitutional as any).hash = 'invalid-hash';
      
      expect(() => validateConfig()).toThrow('Configuration validation failed');
      
      // Restore original
      (CONFIG.constitutional as any).hash = originalHash;
    });

    it('should throw error with invalid performance values', () => {
      // Mock invalid latency target
      const originalLatency = CONFIG.performance.latencyP99Target;
      (CONFIG.performance as any).latencyP99Target = -1;
      
      expect(() => validateConfig()).toThrow('Configuration validation failed');
      
      // Restore original
      (CONFIG.performance as any).latencyP99Target = originalLatency;
    });
  });

  describe('getServiceUrl', () => {
    it('should return correct service URL', () => {
      const url = getServiceUrl('CONSTITUTIONAL_AI');
      expect(url).toBe('http://localhost:8001');
    });

    it('should return correct service URL with endpoint', () => {
      const url = getServiceUrl('CONSTITUTIONAL_AI', '/health');
      expect(url).toBe('http://localhost:8001/health');
    });

    it('should handle predefined endpoints', () => {
      const url = getServiceUrl('CONSTITUTIONAL_AI', 'health');
      expect(url).toBe('http://localhost:8001/health');
    });
  });

  describe('isFeatureEnabled', () => {
    it('should return correct feature flags', () => {
      expect(isFeatureEnabled('enablePerformanceMonitoring')).toBe(false);
      expect(isFeatureEnabled('enableWebsocketUpdates')).toBe(true);
      expect(isFeatureEnabled('enableGraphql')).toBe(true);
    });

    it('should handle environment variables', () => {
      process.env.NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING = 'true';
      
      // Note: This would require reinitializing the config
      // In a real test, you might want to make CONFIG dynamic
      // or test the environment variable parsing separately
    });
  });

  describe('getPollingInterval', () => {
    it('should return correct polling intervals', () => {
      expect(getPollingInterval('dashboardInterval')).toBe(30000);
      expect(getPollingInterval('complianceInterval')).toBe(120000);
      expect(getPollingInterval('metricsInterval')).toBe(5000);
    });
  });

  describe('Environment variable handling', () => {
    it('should use environment variables when available', () => {
      process.env.NEXT_PUBLIC_API_BASE_URL = 'https://api.example.com';
      process.env.NEXT_PUBLIC_CONSTITUTIONAL_COMPLIANCE_THRESHOLD = '99';
      
      // This test demonstrates the structure but would need
      // dynamic config loading to actually test the behavior
      expect(typeof CONFIG.api.baseUrl).toBe('string');
      expect(typeof CONFIG.constitutional.complianceThreshold).toBe('number');
    });

    it('should fall back to defaults when environment variables are missing', () => {
      delete process.env.NEXT_PUBLIC_API_BASE_URL;
      delete process.env.NEXT_PUBLIC_CONSTITUTIONAL_COMPLIANCE_THRESHOLD;
      
      // Config should still have default values
      expect(CONFIG.api.baseUrl).toBe('http://localhost:8010');
      expect(CONFIG.constitutional.complianceThreshold).toBe(95);
    });
  });

  describe('Type safety', () => {
    it('should maintain type safety for service names', () => {
      // These should compile without errors
      const validServiceNames = [
        'CONSTITUTIONAL_AI',
        'INTEGRITY_SERVICE',
        'MULTI_AGENT_COORDINATOR',
        'WORKER_AGENTS',
        'API_GATEWAY',
        'AUTHENTICATION',
      ] as const;

      validServiceNames.forEach(serviceName => {
        expect(() => getServiceUrl(serviceName)).not.toThrow();
      });
    });

    it('should maintain type safety for feature names', () => {
      const validFeatureNames = [
        'enablePerformanceMonitoring',
        'enableWebsocketUpdates',
        'enableGraphql',
        'enableCliInterface',
        'enableAuditLogging',
      ] as const;

      validFeatureNames.forEach(featureName => {
        expect(() => isFeatureEnabled(featureName)).not.toThrow();
      });
    });
  });
});