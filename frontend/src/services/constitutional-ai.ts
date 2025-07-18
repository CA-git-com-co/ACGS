/**
 * Constitutional AI Service Integration
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * Frontend integration for Constitutional AI service with validation and performance monitoring.
 */

import { apiClient } from './api-client';
import { CONFIG, getServiceUrl } from '@/config';
import type { APIResponse } from '@/types';

// Constitutional validation types
interface ConstitutionalValidationRequest {
  context: {
    component: string;
    action: string;
    userId?: string;
    sessionId?: string;
  };
  constitutionalHash: string;
  performanceTarget?: {
    p99Latency: number;
    throughput: number;
    cacheHitRate: number;
  };
}

interface ConstitutionalValidationResponse {
  isValid: boolean;
  score: number;
  violations: string[];
  confidence: number;
  evaluatedAt: string;
  performanceMetrics: {
    latency: number;
    constitutionalCompliance: number;
    cacheHit: boolean;
  };
  constitutionalHash: string;
}

interface ConstitutionalComplianceStatus {
  overall: {
    score: number;
    level: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR';
    trend: 'IMPROVING' | 'STABLE' | 'DECLINING';
  };
  components: {
    validation: number;
    performance: number;
    integrity: number;
    auditTrail: number;
  };
  metadata: {
    lastUpdated: string;
    evaluationCount: number;
    constitutionalHash: string;
  };
}

/**
 * Constitutional AI Service Client
 */
export class ConstitutionalAIService {
  private baseUrl: string;
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private readonly CACHE_TTL = 2 * 60 * 1000; // 2 minutes

  constructor() {
    this.baseUrl = getServiceUrl('CONSTITUTIONAL_AI');
  }

  /**
   * Validate constitutional compliance with ultra-fast performance
   */
  async validateCompliance(
    request: ConstitutionalValidationRequest
  ): Promise<ConstitutionalValidationResponse> {
    const startTime = performance.now();
    
    try {
      // Check cache first for sub-millisecond performance
      const cacheKey = this.generateCacheKey(request);
      const cached = this.getFromCache(cacheKey);
      if (cached) {
        return cached;
      }

      // Make API request with constitutional headers
      const response = await apiClient.post<ConstitutionalValidationResponse>(
        '/api/constitutional/validate',
        request,
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
            'X-Performance-Target': `P99<${CONFIG.performance.latencyP99Target}ms`,
            'X-Service-Name': 'constitutional-ai',
          },
        }
      );

      // Validate response constitutional hash
      if (response.data.constitutionalHash !== CONFIG.constitutional.hash) {
        throw new Error('Constitutional hash mismatch in validation response');
      }

      // Cache the result
      this.setCache(cacheKey, response.data);

      // Performance monitoring
      const duration = performance.now() - startTime;
      if (duration > CONFIG.performance.latencyP99Target) {
        console.warn(
          `Constitutional validation latency (${duration.toFixed(2)}ms) exceeded target (${CONFIG.performance.latencyP99Target}ms)`
        );
      }

      return response.data;
    } catch (error) {
      console.error('Constitutional validation failed:', error);
      
      // Return fallback validation result
      return {
        isValid: false,
        score: 0,
        violations: [`Validation error: ${error instanceof Error ? error.message : 'Unknown error'}`],
        confidence: 0,
        evaluatedAt: new Date().toISOString(),
        performanceMetrics: {
          latency: performance.now() - startTime,
          constitutionalCompliance: 0,
          cacheHit: false,
        },
        constitutionalHash: CONFIG.constitutional.hash,
      };
    }
  }

  /**
   * Validate constitutional hash directly
   */
  async validateHash(hash: string): Promise<boolean> {
    try {
      // Fast path for known constitutional hash
      if (hash === CONFIG.constitutional.hash) {
        return true;
      }

      const response = await apiClient.post<{ isValid: boolean }>(
        '/api/constitutional/validate-hash',
        { hash },
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );

      return response.data.isValid;
    } catch (error) {
      console.error('Hash validation failed:', error);
      return false;
    }
  }

  /**
   * Get constitutional compliance status
   */
  async getComplianceStatus(): Promise<ConstitutionalComplianceStatus> {
    try {
      const response = await apiClient.get<ConstitutionalComplianceStatus>(
        '/api/constitutional/compliance',
        {},
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get compliance status:', error);
      
      // Return fallback status
      return {
        overall: {
          score: 0,
          level: 'POOR',
          trend: 'DECLINING',
        },
        components: {
          validation: 0,
          performance: 0,
          integrity: 0,
          auditTrail: 0,
        },
        metadata: {
          lastUpdated: new Date().toISOString(),
          evaluationCount: 0,
          constitutionalHash: CONFIG.constitutional.hash,
        },
      };
    }
  }

  /**
   * Get performance metrics
   */
  async getPerformanceMetrics(): Promise<{
    latency: { p99: number; average: number };
    throughput: { rps: number; trend: string };
    cacheHitRate: number;
    constitutionalCompliance: number;
  }> {
    try {
      const response = await apiClient.get<any>(
        '/api/constitutional/metrics',
        {},
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get performance metrics:', error);
      
      return {
        latency: { p99: 0, average: 0 },
        throughput: { rps: 0, trend: 'STABLE' },
        cacheHitRate: 0,
        constitutionalCompliance: 0,
      };
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy' | 'degraded';
    checks: Record<string, boolean>;
    constitutionalHash: string;
  }> {
    try {
      const response = await apiClient.get<any>(
        '/health',
        {},
        { retry: false }
      );

      return {
        status: response.data.status,
        checks: response.data.checks || {},
        constitutionalHash: CONFIG.constitutional.hash,
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        checks: { connection: false },
        constitutionalHash: CONFIG.constitutional.hash,
      };
    }
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; hitRate: number } {
    return {
      size: this.cache.size,
      hitRate: 0, // TODO: Implement hit rate tracking
    };
  }

  private generateCacheKey(request: ConstitutionalValidationRequest): string {
    const key = JSON.stringify({
      component: request.context.component,
      action: request.context.action,
      userId: request.context.userId,
      hash: request.constitutionalHash,
    });
    
    return btoa(key).replace(/[^a-zA-Z0-9]/g, '');
  }

  private getFromCache(key: string): ConstitutionalValidationResponse | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    // Check if entry is still valid
    if (Date.now() - entry.timestamp > this.CACHE_TTL) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  private setCache(key: string, data: ConstitutionalValidationResponse): void {
    // Implement LRU cache eviction
    if (this.cache.size >= 1000) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }
}

// Export singleton instance
export const constitutionalAIService = new ConstitutionalAIService();

// Export types
export type {
  ConstitutionalValidationRequest,
  ConstitutionalValidationResponse,
  ConstitutionalComplianceStatus,
};
