/**
 * ACGS-2 Service Integration Index
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * Unified interface for all ACGS-2 services with constitutional compliance.
 */

import { CONFIG } from '@/config';

// Service imports
export { apiClient, graphqlClient, wsClient, APIError, APIClient } from './api-client';
export { constitutionalAIService, ConstitutionalAIService } from './constitutional-ai';
export { integrityService, IntegrityService } from './integrity-service';
export { authService, AuthService } from './auth-service';

// Type exports
export type {
  ConstitutionalValidationRequest,
  ConstitutionalValidationResponse,
  ConstitutionalComplianceStatus,
} from './constitutional-ai';

export type {
  IntegrityAuditEntry,
  IntegrityLogQuery,
  IntegrityMetrics,
} from './integrity-service';

export type {
  User,
  AuthToken,
  LoginRequest,
  LoginResponse,
} from './auth-service';

// Service health monitoring
interface ServiceHealthStatus {
  name: string;
  status: 'healthy' | 'unhealthy' | 'degraded';
  checks: Record<string, boolean>;
  constitutionalHash: string;
  lastChecked: string;
}

/**
 * Service Manager for coordinating all ACGS-2 services
 */
export class ServiceManager {
  private services: Map<string, any> = new Map();
  private healthStatuses: Map<string, ServiceHealthStatus> = new Map();
  private healthCheckInterval: NodeJS.Timeout | null = null;

  constructor() {
    this.registerServices();
    this.startHealthMonitoring();
  }

  /**
   * Register all services
   */
  private registerServices(): void {
    this.services.set('constitutional-ai', constitutionalAIService);
    this.services.set('integrity', integrityService);
    this.services.set('auth', authService);
  }

  /**
   * Get service by name
   */
  getService<T>(name: string): T | null {
    return this.services.get(name) || null;
  }

  /**
   * Get all service health statuses
   */
  getServiceHealthStatuses(): Map<string, ServiceHealthStatus> {
    return new Map(this.healthStatuses);
  }

  /**
   * Get overall system health
   */
  getSystemHealth(): {
    status: 'healthy' | 'unhealthy' | 'degraded';
    services: ServiceHealthStatus[];
    constitutionalCompliance: {
      hash: string;
      allServicesCompliant: boolean;
      complianceScore: number;
    };
  } {
    const services = Array.from(this.healthStatuses.values());
    const healthyServices = services.filter(s => s.status === 'healthy').length;
    const totalServices = services.length;
    
    let systemStatus: 'healthy' | 'unhealthy' | 'degraded';
    if (healthyServices === totalServices) {
      systemStatus = 'healthy';
    } else if (healthyServices > totalServices / 2) {
      systemStatus = 'degraded';
    } else {
      systemStatus = 'unhealthy';
    }

    const allServicesCompliant = services.every(
      s => s.constitutionalHash === CONFIG.constitutional.hash
    );
    const complianceScore = services.length > 0 
      ? (services.filter(s => s.constitutionalHash === CONFIG.constitutional.hash).length / services.length) * 100
      : 0;

    return {
      status: systemStatus,
      services,
      constitutionalCompliance: {
        hash: CONFIG.constitutional.hash,
        allServicesCompliant,
        complianceScore,
      },
    };
  }

  /**
   * Perform health check for all services
   */
  async performHealthCheck(): Promise<void> {
    const healthPromises = Array.from(this.services.entries()).map(async ([name, service]) => {
      try {
        const healthResult = await service.healthCheck();
        
        this.healthStatuses.set(name, {
          name,
          status: healthResult.status,
          checks: healthResult.checks,
          constitutionalHash: healthResult.constitutionalHash,
          lastChecked: new Date().toISOString(),
        });
      } catch (error) {
        console.error(`Health check failed for service ${name}:`, error);
        
        this.healthStatuses.set(name, {
          name,
          status: 'unhealthy',
          checks: { connection: false },
          constitutionalHash: CONFIG.constitutional.hash,
          lastChecked: new Date().toISOString(),
        });
      }
    });

    await Promise.all(healthPromises);
  }

  /**
   * Start health monitoring
   */
  private startHealthMonitoring(): void {
    // Initial health check
    this.performHealthCheck().catch(console.error);
    
    // Set up interval for periodic health checks
    this.healthCheckInterval = setInterval(() => {
      this.performHealthCheck().catch(console.error);
    }, 30000); // Check every 30 seconds
  }

  /**
   * Stop health monitoring
   */
  stopHealthMonitoring(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }

  /**
   * Cleanup all services
   */
  cleanup(): void {
    this.stopHealthMonitoring();
    
    // Cleanup integrity service
    if (this.services.has('integrity')) {
      this.services.get('integrity').cleanup();
    }
  }
}

// Export singleton instance
export const serviceManager = new ServiceManager();

// Service availability helpers
export const isServiceAvailable = (serviceName: string): boolean => {
  const status = serviceManager.getServiceHealthStatuses().get(serviceName);
  return status?.status === 'healthy';
};

export const getServiceStatus = (serviceName: string): ServiceHealthStatus | null => {
  return serviceManager.getServiceHealthStatuses().get(serviceName) || null;
};

// Constitutional compliance helpers
export const isConstitutionallyCompliant = (): boolean => {
  const systemHealth = serviceManager.getSystemHealth();
  return systemHealth.constitutionalCompliance.allServicesCompliant;
};

export const getConstitutionalComplianceScore = (): number => {
  const systemHealth = serviceManager.getSystemHealth();
  return systemHealth.constitutionalCompliance.complianceScore;
};

// Auto-cleanup on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    serviceManager.cleanup();
  });
}

// Export service manager types
export type { ServiceHealthStatus };
