import { z } from 'zod';

/**
 * Centralized configuration for ACGS-2 frontend
 * Constitutional Hash: cdd01ef066bc6cf2
 */

// Configuration schema for validation
const configSchema = z.object({
  api: z.object({
    baseUrl: z.string().url(),
    graphqlUrl: z.string().url(),
    wsUrl: z.string(),
    timeout: z.number().positive(),
    retryAttempts: z.number().min(1).max(10),
  }),
  constitutional: z.object({
    hash: z.literal('cdd01ef066bc6cf2'),
    complianceThreshold: z.number().min(0).max(100),
    validationEnabled: z.boolean(),
    auditEnabled: z.boolean(),
  }),
  performance: z.object({
    latencyP99Target: z.number().positive(),
    throughputRpsTarget: z.number().positive(),
    cacheHitRateTarget: z.number().min(0).max(100),
    uptimeTarget: z.number().min(0).max(100),
  }),
  polling: z.object({
    dashboardInterval: z.number().positive(),
    complianceInterval: z.number().positive(),
    metricsInterval: z.number().positive(),
    reconnectAttempts: z.number().min(1).max(10),
  }),
  features: z.object({
    enablePerformanceMonitoring: z.boolean(),
    enableWebsocketUpdates: z.boolean(),
    enableGraphql: z.boolean(),
    enableCliInterface: z.boolean(),
    enableAuditLogging: z.boolean(),
  }),
});

// Type-safe configuration object
export const CONFIG = {
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8010',
    graphqlUrl: process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8010/graphql',
    wsUrl: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8010/ws',
    timeout: Number(process.env.NEXT_PUBLIC_API_TIMEOUT) || 10000,
    retryAttempts: Number(process.env.NEXT_PUBLIC_API_RETRY_ATTEMPTS) || 3,
  },
  constitutional: {
    hash: 'cdd01ef066bc6cf2' as const,
    complianceThreshold: Number(process.env.NEXT_PUBLIC_CONSTITUTIONAL_COMPLIANCE_THRESHOLD) || 95,
    validationEnabled: process.env.NEXT_PUBLIC_ENABLE_CONSTITUTIONAL_VALIDATION !== 'false',
    auditEnabled: process.env.NEXT_PUBLIC_ENABLE_AUDIT_LOGGING !== 'false',
  },
  performance: {
    latencyP99Target: Number(process.env.NEXT_PUBLIC_LATENCY_P99_TARGET) || 5,
    throughputRpsTarget: Number(process.env.NEXT_PUBLIC_THROUGHPUT_RPS_TARGET) || 100,
    cacheHitRateTarget: Number(process.env.NEXT_PUBLIC_CACHE_HIT_RATE_TARGET) || 85,
    uptimeTarget: Number(process.env.NEXT_PUBLIC_UPTIME_TARGET) || 99.9,
  },
  polling: {
    dashboardInterval: 30 * 1000, // 30 seconds
    complianceInterval: 2 * 60 * 1000, // 2 minutes
    metricsInterval: 5 * 1000, // 5 seconds
    reconnectAttempts: 5,
  },
  features: {
    enablePerformanceMonitoring: process.env.NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING === 'true',
    enableWebsocketUpdates: process.env.NEXT_PUBLIC_ENABLE_WEBSOCKET_UPDATES !== 'false',
    enableGraphql: process.env.NEXT_PUBLIC_ENABLE_GRAPHQL !== 'false',
    enableCliInterface: process.env.NEXT_PUBLIC_ENABLE_CLI_INTERFACE !== 'false',
    enableAuditLogging: process.env.NEXT_PUBLIC_ENABLE_AUDIT_LOGGING !== 'false',
  },
} as const;

// Service endpoints configuration
export const SERVICES = {
  CONSTITUTIONAL_AI: {
    name: 'Constitutional AI',
    port: 8001,
    url: process.env.NEXT_PUBLIC_CONSTITUTIONAL_AI_URL || 'http://localhost:8001',
    endpoints: {
      health: '/health',
      validate: '/api/constitutional/validate',
      compliance: '/api/constitutional/compliance',
    },
  },
  INTEGRITY_SERVICE: {
    name: 'Integrity Service',
    port: 8002,
    url: process.env.NEXT_PUBLIC_INTEGRITY_SERVICE_URL || 'http://localhost:8002',
    endpoints: {
      health: '/health',
      audit: '/api/integrity/audit',
      logs: '/api/integrity/logs',
    },
  },
  MULTI_AGENT_COORDINATOR: {
    name: 'Multi-Agent Coordinator',
    port: 8008,
    url: process.env.NEXT_PUBLIC_MULTI_AGENT_COORDINATOR_URL || 'http://localhost:8008',
    endpoints: {
      health: '/health',
      workflows: '/api/coordinator/workflows',
      agents: '/api/coordinator/agents',
    },
  },
  WORKER_AGENTS: {
    name: 'Worker Agents',
    port: 8009,
    url: process.env.NEXT_PUBLIC_WORKER_AGENTS_URL || 'http://localhost:8009',
    endpoints: {
      health: '/health',
      status: '/api/workers/status',
      tasks: '/api/workers/tasks',
    },
  },
  API_GATEWAY: {
    name: 'API Gateway',
    port: 8010,
    url: process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost:8010',
    endpoints: {
      health: '/health',
      graphql: '/graphql',
      ws: '/ws',
    },
  },
  AUTHENTICATION: {
    name: 'Authentication Service',
    port: 8016,
    url: process.env.NEXT_PUBLIC_AUTHENTICATION_SERVICE_URL || 'http://localhost:8016',
    endpoints: {
      health: '/health',
      login: '/api/auth/login',
      refresh: '/api/auth/refresh',
    },
  },
} as const;

// Configuration validation
export function validateConfig(): void {
  try {
    configSchema.parse(CONFIG);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const issues = error.issues.map(issue => 
        `${issue.path.join('.')}: ${issue.message}`
      ).join(', ');
      throw new Error(`Configuration validation failed: ${issues}`);
    }
    throw new Error(`Configuration validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

// Helper functions
export function getServiceUrl(serviceName: keyof typeof SERVICES, endpoint?: string): string {
  const service = SERVICES[serviceName];
  const baseUrl = service.url;
  
  if (!endpoint) return baseUrl;
  
  const endpointPath = typeof endpoint === 'string' 
    ? endpoint 
    : service.endpoints[endpoint as keyof typeof service.endpoints];
  
  return `${baseUrl}${endpointPath}`;
}

export function isFeatureEnabled(feature: keyof typeof CONFIG.features): boolean {
  return CONFIG.features[feature];
}

export function getPollingInterval(type: keyof typeof CONFIG.polling): number {
  return CONFIG.polling[type];
}

// Type exports
export type ServiceName = keyof typeof SERVICES;
export type FeatureName = keyof typeof CONFIG.features;
export type PollingType = keyof typeof CONFIG.polling;

// Initialize and validate configuration on module load
if (typeof window !== 'undefined') {
  try {
    validateConfig();
  } catch (error) {
    console.error('Configuration validation failed:', error);
  }
}