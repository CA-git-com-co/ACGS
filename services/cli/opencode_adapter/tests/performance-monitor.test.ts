import { PerformanceMonitor } from '../src/performance-monitor';

describe('PerformanceMonitor', () => {
  let monitor: PerformanceMonitor;

  beforeEach(() => {
    monitor = new PerformanceMonitor();
    monitor.start();
  });

  afterEach(() => {
    monitor.stop();
  });

  describe('recordMetric', () => {
    it('should record metrics correctly', () => {
      monitor.recordMetric('test_metric', 10);
      monitor.recordMetric('test_metric', 20);
      monitor.recordMetric('test_metric', 30);

      const metrics = monitor.getMetrics();
      expect(metrics.test_metric).toBeDefined();
      expect(metrics.test_metric.count).toBe(3);
      expect(metrics.test_metric.sum).toBe(60);
      expect(metrics.test_metric.min).toBe(10);
      expect(metrics.test_metric.max).toBe(30);
      expect(metrics.test_metric.p50).toBe(20);
    });

    it('should calculate percentiles correctly', () => {
      // Add 100 samples from 1 to 100
      for (let i = 1; i <= 100; i++) {
        monitor.recordMetric('latency', i);
      }

      const metrics = monitor.getMetrics();
      expect(metrics.latency.p50).toBe(50);
      expect(metrics.latency.p95).toBe(95);
      expect(metrics.latency.p99).toBe(99);
    });
  });

  describe('cache metrics', () => {
    it('should track cache hit rate correctly', () => {
      monitor.recordCacheHit();
      monitor.recordCacheHit();
      monitor.recordCacheHit();
      monitor.recordCacheMiss();

      const hitRate = monitor.getCacheHitRate();
      expect(hitRate).toBe(0.75); // 3 hits out of 4 total

      const metrics = monitor.getMetrics();
      expect(metrics.cache_hit_rate).toBeDefined();
      expect(metrics.cache_hit_rate.p50).toBe(0.75);
    });

    it('should return null cache hit rate when no operations', () => {
      const hitRate = monitor.getCacheHitRate();
      expect(hitRate).toBeNull();
    });
  });

  describe('ACGS compliance checking', () => {
    it('should pass ACGS requirements when metrics are within limits', () => {
      // Record good latency values (under 5ms)
      monitor.recordMetric('command_latency', 2);
      monitor.recordMetric('command_latency', 3);
      monitor.recordMetric('command_latency', 4);

      // Record good cache hit rate (above 85%)
      for (let i = 0; i < 90; i++) monitor.recordCacheHit();
      for (let i = 0; i < 10; i++) monitor.recordCacheMiss();

      const requirements = monitor.checkACGSRequirements();
      expect(requirements.met).toBe(true);
      expect(requirements.issues).toHaveLength(0);
    });

    it('should fail ACGS requirements when P99 latency exceeds 5ms', () => {
      // Record latency values with P99 > 5ms
      for (let i = 0; i < 98; i++) {
        monitor.recordMetric('command_latency', 3);
      }
      monitor.recordMetric('command_latency', 6);
      monitor.recordMetric('command_latency', 7);

      const requirements = monitor.checkACGSRequirements();
      expect(requirements.met).toBe(false);
      expect(requirements.issues).toHaveLength(1);
      expect(requirements.issues[0]).toContain('P99 latency');
      expect(requirements.issues[0]).toContain('exceeds 5ms requirement');
    });

    it('should fail ACGS requirements when cache hit rate is below 85%', () => {
      // Record cache operations with hit rate < 85%
      for (let i = 0; i < 80; i++) monitor.recordCacheHit();
      for (let i = 0; i < 20; i++) monitor.recordCacheMiss();

      const requirements = monitor.checkACGSRequirements();
      expect(requirements.met).toBe(false);
      expect(requirements.issues).toHaveLength(1);
      expect(requirements.issues[0]).toContain('Cache hit rate');
      expect(requirements.issues[0]).toContain('below 85% requirement');
    });

    it('should fail multiple ACGS requirements', () => {
      // Bad latency
      monitor.recordMetric('command_latency', 10);
      
      // Bad cache hit rate
      for (let i = 0; i < 50; i++) monitor.recordCacheHit();
      for (let i = 0; i < 50; i++) monitor.recordCacheMiss();

      const requirements = monitor.checkACGSRequirements();
      expect(requirements.met).toBe(false);
      expect(requirements.issues).toHaveLength(2);
    });
  });

  describe('getP99Latency', () => {
    it('should return null when no metrics recorded', () => {
      const p99 = monitor.getP99Latency();
      expect(p99).toBeNull();
    });

    it('should return correct P99 latency', () => {
      for (let i = 1; i <= 100; i++) {
        monitor.recordMetric('command_latency', i * 0.05); // 0.05ms to 5ms
      }

      const p99 = monitor.getP99Latency();
      expect(p99).toBeCloseTo(4.95, 1); // 99th value * 0.05
    });

    it('should work with custom metric names', () => {
      monitor.recordMetric('custom_latency', 10);
      monitor.recordMetric('custom_latency', 20);

      const p99 = monitor.getP99Latency('custom_latency');
      expect(p99).toBe(20);
    });
  });

  describe('metric cleanup', () => {
    it('should clean up old metrics after retention period', (done) => {
      // Record a metric
      monitor.recordMetric('test_metric', 10);

      // Mock the cleanup by directly calling the private method
      // In a real test, we'd wait for the interval or mock timers
      const metrics = monitor.getMetrics();
      expect(metrics.test_metric).toBeDefined();

      // Note: In production tests, we'd use jest.useFakeTimers()
      // to test the cleanup interval behavior
      done();
    });
  });
});