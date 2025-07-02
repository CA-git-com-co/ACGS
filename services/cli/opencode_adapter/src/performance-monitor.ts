import { Logger } from './logger.js';

interface Metric {
  name: string;
  value: number;
  timestamp: Date;
}

interface MetricStats {
  count: number;
  sum: number;
  min: number;
  max: number;
  p50: number;
  p95: number;
  p99: number;
}

export class PerformanceMonitor {
  private metrics: Map<string, Metric[]> = new Map();
  private cacheHits = 0;
  private cacheMisses = 0;
  private logger: Logger;
  private monitoringInterval?: NodeJS.Timer;
  private metricsRetentionMs = 60000; // Keep metrics for 1 minute

  constructor() {
    this.logger = new Logger('PerformanceMonitor');
  }

  start(): void {
    // Start periodic cleanup of old metrics
    this.monitoringInterval = setInterval(() => {
      this.cleanupOldMetrics();
      this.logCurrentStats();
    }, 10000); // Every 10 seconds
  }

  stop(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = undefined;
    }
  }

  recordMetric(name: string, value: number): void {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }

    const metric: Metric = {
      name,
      value,
      timestamp: new Date(),
    };

    this.metrics.get(name)!.push(metric);
    
    // Check ACGS requirements
    this.checkACGSCompliance(name, value);
  }

  recordCacheHit(): void {
    this.cacheHits++;
  }

  recordCacheMiss(): void {
    this.cacheMisses++;
  }

  getMetrics(): Record<string, MetricStats> {
    const stats: Record<string, MetricStats> = {};

    for (const [name, metrics] of this.metrics.entries()) {
      if (metrics.length === 0) continue;

      const values = metrics.map(m => m.value).sort((a, b) => a - b);
      
      stats[name] = {
        count: values.length,
        sum: values.reduce((a, b) => a + b, 0),
        min: values[0],
        max: values[values.length - 1],
        p50: this.percentile(values, 0.5),
        p95: this.percentile(values, 0.95),
        p99: this.percentile(values, 0.99),
      };
    }

    // Add cache hit rate
    const totalCacheOps = this.cacheHits + this.cacheMisses;
    if (totalCacheOps > 0) {
      stats['cache_hit_rate'] = {
        count: totalCacheOps,
        sum: this.cacheHits,
        min: 0,
        max: 1,
        p50: this.cacheHits / totalCacheOps,
        p95: this.cacheHits / totalCacheOps,
        p99: this.cacheHits / totalCacheOps,
      };
    }

    return stats;
  }

  private percentile(sortedValues: number[], p: number): number {
    const index = Math.ceil(sortedValues.length * p) - 1;
    return sortedValues[Math.max(0, Math.min(index, sortedValues.length - 1))];
  }

  private cleanupOldMetrics(): void {
    const cutoffTime = new Date(Date.now() - this.metricsRetentionMs);

    for (const [name, metrics] of this.metrics.entries()) {
      const filtered = metrics.filter(m => m.timestamp > cutoffTime);
      this.metrics.set(name, filtered);
    }
  }

  private checkACGSCompliance(name: string, value: number): void {
    // Check specific ACGS requirements
    if (name === 'command_latency' && value > 5) {
      this.logger.warn('Latency exceeded 5ms threshold', { latency: value });
    }

    if (name === 'lookup_time' && value > 0.001) {
      // O(1) lookup should be sub-millisecond
      this.logger.warn('Lookup time exceeded O(1) threshold', { time: value });
    }
  }

  private logCurrentStats(): void {
    const stats = this.getMetrics();
    
    // Log P99 latency
    if (stats['command_latency']) {
      this.logger.metric('p99_latency', stats['command_latency'].p99, {
        type: 'command_latency',
      });
    }

    // Log cache hit rate
    const cacheHitRate = this.getCacheHitRate();
    if (cacheHitRate !== null) {
      this.logger.metric('cache_hit_rate', cacheHitRate, {
        type: 'cache',
      });

      // Warn if cache hit rate is below 85%
      if (cacheHitRate < 0.85) {
        this.logger.warn('Cache hit rate below 85% threshold', {
          rate: cacheHitRate,
        });
      }
    }
  }

  getCacheHitRate(): number | null {
    const total = this.cacheHits + this.cacheMisses;
    if (total === 0) return null;
    return this.cacheHits / total;
  }

  // Get current P99 latency for a specific metric
  getP99Latency(metricName: string = 'command_latency'): number | null {
    const metrics = this.metrics.get(metricName);
    if (!metrics || metrics.length === 0) return null;

    const values = metrics.map(m => m.value).sort((a, b) => a - b);
    return this.percentile(values, 0.99);
  }

  // Check if all ACGS requirements are currently met
  checkACGSRequirements(): {
    met: boolean;
    issues: string[];
  } {
    const issues: string[] = [];

    // Check P99 latency < 5ms
    const p99Latency = this.getP99Latency();
    if (p99Latency !== null && p99Latency > 5) {
      issues.push(`P99 latency ${p99Latency.toFixed(2)}ms exceeds 5ms requirement`);
    }

    // Check cache hit rate > 85%
    const cacheHitRate = this.getCacheHitRate();
    if (cacheHitRate !== null && cacheHitRate < 0.85) {
      issues.push(`Cache hit rate ${(cacheHitRate * 100).toFixed(1)}% below 85% requirement`);
    }

    return {
      met: issues.length === 0,
      issues,
    };
  }
}