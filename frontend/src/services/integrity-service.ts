/**
 * Integrity Service Integration
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * Frontend integration for Integrity Service with audit logging and monitoring.
 */

import { apiClient } from './api-client';
import { CONFIG, getServiceUrl } from '@/config';
import type { APIResponse } from '@/types';

// Integrity types
interface IntegrityAuditEntry {
  id: string;
  timestamp: string;
  action: string;
  component: string;
  userId?: string;
  sessionId?: string;
  data: Record<string, any>;
  constitutionalHash: string;
  integrity: {
    checksum: string;
    signature: string;
    verified: boolean;
  };
}

interface IntegrityLogQuery {
  component?: string;
  action?: string;
  userId?: string;
  startTime?: string;
  endTime?: string;
  limit?: number;
  offset?: number;
}

interface IntegrityMetrics {
  totalLogs: number;
  verifiedLogs: number;
  failedVerifications: number;
  integrityScore: number;
  performanceMetrics: {
    averageLatency: number;
    p99Latency: number;
    throughput: number;
  };
  constitutionalCompliance: {
    hash: string;
    score: number;
    lastValidated: string;
  };
}

/**
 * Integrity Service Client
 */
export class IntegrityService {
  private baseUrl: string;
  private logBuffer: IntegrityAuditEntry[] = [];
  private flushInterval: NodeJS.Timeout | null = null;
  private readonly BUFFER_SIZE = 100;
  private readonly FLUSH_INTERVAL = 5000; // 5 seconds

  constructor() {
    this.baseUrl = getServiceUrl('INTEGRITY_SERVICE');
    this.startBufferFlush();
  }

  /**
   * Log audit entry with integrity validation
   */
  async logAuditEntry(
    action: string,
    component: string,
    data: Record<string, any>,
    options: {
      userId?: string;
      sessionId?: string;
      immediate?: boolean;
    } = {}
  ): Promise<void> {
    const entry: IntegrityAuditEntry = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      action,
      component,
      userId: options.userId,
      sessionId: options.sessionId,
      data,
      constitutionalHash: CONFIG.constitutional.hash,
      integrity: {
        checksum: await this.calculateChecksum(data),
        signature: await this.generateSignature(data),
        verified: false,
      },
    };

    if (options.immediate) {
      await this.sendLogEntry(entry);
    } else {
      this.logBuffer.push(entry);
      if (this.logBuffer.length >= this.BUFFER_SIZE) {
        await this.flushBuffer();
      }
    }
  }

  /**
   * Query audit logs with filtering
   */
  async queryAuditLogs(
    query: IntegrityLogQuery = {}
  ): Promise<{
    logs: IntegrityAuditEntry[];
    totalCount: number;
    hasMore: boolean;
  }> {
    try {
      const response = await apiClient.get<{
        logs: IntegrityAuditEntry[];
        totalCount: number;
        hasMore: boolean;
      }>(
        '/api/integrity/logs',
        query,
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to query audit logs:', error);
      return {
        logs: [],
        totalCount: 0,
        hasMore: false,
      };
    }
  }

  /**
   * Get integrity metrics
   */
  async getIntegrityMetrics(): Promise<IntegrityMetrics> {
    try {
      const response = await apiClient.get<IntegrityMetrics>(
        '/api/integrity/metrics',
        {},
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get integrity metrics:', error);
      
      return {
        totalLogs: 0,
        verifiedLogs: 0,
        failedVerifications: 0,
        integrityScore: 0,
        performanceMetrics: {
          averageLatency: 0,
          p99Latency: 0,
          throughput: 0,
        },
        constitutionalCompliance: {
          hash: CONFIG.constitutional.hash,
          score: 0,
          lastValidated: new Date().toISOString(),
        },
      };
    }
  }

  /**
   * Verify integrity of a specific log entry
   */
  async verifyLogIntegrity(logId: string): Promise<{
    verified: boolean;
    details: {
      checksumValid: boolean;
      signatureValid: boolean;
      constitutionalHashValid: boolean;
    };
  }> {
    try {
      const response = await apiClient.post<{
        verified: boolean;
        details: {
          checksumValid: boolean;
          signatureValid: boolean;
          constitutionalHashValid: boolean;
        };
      }>(
        '/api/integrity/verify',
        { logId },
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to verify log integrity:', error);
      return {
        verified: false,
        details: {
          checksumValid: false,
          signatureValid: false,
          constitutionalHashValid: false,
        },
      };
    }
  }

  /**
   * Get integrity status for a component
   */
  async getComponentIntegrityStatus(component: string): Promise<{
    score: number;
    status: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR';
    recentActivity: {
      totalActions: number;
      verifiedActions: number;
      failedVerifications: number;
    };
    constitutionalCompliance: {
      hash: string;
      valid: boolean;
      lastChecked: string;
    };
  }> {
    try {
      const response = await apiClient.get<any>(
        `/api/integrity/component/${component}`,
        {},
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get component integrity status:', error);
      
      return {
        score: 0,
        status: 'POOR',
        recentActivity: {
          totalActions: 0,
          verifiedActions: 0,
          failedVerifications: 0,
        },
        constitutionalCompliance: {
          hash: CONFIG.constitutional.hash,
          valid: false,
          lastChecked: new Date().toISOString(),
        },
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
   * Flush pending log entries
   */
  async flushBuffer(): Promise<void> {
    if (this.logBuffer.length === 0) return;

    const entries = [...this.logBuffer];
    this.logBuffer = [];

    try {
      await apiClient.post(
        '/api/integrity/batch-logs',
        { entries },
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );
    } catch (error) {
      console.error('Failed to flush log buffer:', error);
      // Put entries back in buffer for retry
      this.logBuffer.unshift(...entries);
    }
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    if (this.flushInterval) {
      clearInterval(this.flushInterval);
      this.flushInterval = null;
    }
    
    // Flush any remaining entries
    if (this.logBuffer.length > 0) {
      this.flushBuffer().catch(console.error);
    }
  }

  private startBufferFlush(): void {
    this.flushInterval = setInterval(() => {
      this.flushBuffer().catch(console.error);
    }, this.FLUSH_INTERVAL);
  }

  private async sendLogEntry(entry: IntegrityAuditEntry): Promise<void> {
    try {
      await apiClient.post(
        '/api/integrity/log',
        entry,
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );
    } catch (error) {
      console.error('Failed to send log entry:', error);
      throw error;
    }
  }

  private generateId(): string {
    return `log_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }

  private async calculateChecksum(data: Record<string, any>): Promise<string> {
    // Simple checksum using JSON stringification
    const jsonString = JSON.stringify(data, Object.keys(data).sort());
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(jsonString);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  private async generateSignature(data: Record<string, any>): Promise<string> {
    // Simple signature using constitutional hash
    const dataString = JSON.stringify(data, Object.keys(data).sort());
    const combined = `${CONFIG.constitutional.hash}:${dataString}`;
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(combined);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }
}

// Export singleton instance
export const integrityService = new IntegrityService();

// Export types
export type {
  IntegrityAuditEntry,
  IntegrityLogQuery,
  IntegrityMetrics,
};

// Auto-cleanup on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    integrityService.cleanup();
  });
}
