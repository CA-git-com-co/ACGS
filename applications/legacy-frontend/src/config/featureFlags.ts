/**
 * Feature Flag Configuration for Legacy Frontend Migration
 * 
 * This file configures feature flags specifically for the legacy-frontend
 * application during the migration to shared architecture.
 */

import { FeatureFlags } from '@acgs/shared/utils/featureFlags';

// Migration phase configurations
export const MIGRATION_PHASES = {
  PHASE_1: 'foundation', // Days 1-4: Infrastructure and low-risk components
  PHASE_2: 'services',   // Days 5-8: Service and medium-risk components  
  PHASE_3: 'critical',   // Days 9-12: Critical components and final migration
} as const;

// Current migration phase (update as migration progresses)
export const CURRENT_PHASE = process.env.REACT_APP_MIGRATION_PHASE || MIGRATION_PHASES.PHASE_1;

// Phase-specific feature flag configurations
export const getPhaseFlags = (phase: string): Partial<FeatureFlags> => {
  switch (phase) {
    case MIGRATION_PHASES.PHASE_1:
      return {
        // Enable safe infrastructure components
        useSharedTheme: true,
        useSharedAuth: true,
        useSharedLayout: false, // Start with legacy layout
        useSharedErrorHandling: false,
        
        // Keep all other components legacy
        useSharedDashboard: false,
        useSharedQuantumagi: false,
        useSharedMonitoring: false,
        useSharedConsultation: false,
        useSharedAmendment: false,
        useSharedPages: false,
        useSharedRouting: false,
        
        // Emergency flags
        emergencyRollback: false,
        maintenanceMode: false,
      };

    case MIGRATION_PHASES.PHASE_2:
      return {
        // Infrastructure components enabled
        useSharedTheme: true,
        useSharedAuth: true,
        useSharedLayout: true,
        useSharedErrorHandling: true,
        
        // Enable medium-risk components
        useSharedMonitoring: true,
        useSharedConsultation: true,
        useSharedAmendment: true,
        
        // Keep critical components legacy for now
        useSharedDashboard: false,
        useSharedQuantumagi: false, // CRITICAL - keep legacy
        useSharedPages: false,
        useSharedRouting: false,
        
        // Emergency flags
        emergencyRollback: false,
        maintenanceMode: false,
      };

    case MIGRATION_PHASES.PHASE_3:
      return {
        // All infrastructure enabled
        useSharedTheme: true,
        useSharedAuth: true,
        useSharedLayout: true,
        useSharedErrorHandling: true,
        
        // All services enabled
        useSharedMonitoring: true,
        useSharedConsultation: true,
        useSharedAmendment: true,
        
        // Enable critical components (with caution)
        useSharedDashboard: true,
        useSharedQuantumagi: true, // CRITICAL - enable with extensive testing
        useSharedPages: true,
        useSharedRouting: true,
        
        // Emergency flags
        emergencyRollback: false,
        maintenanceMode: false,
      };

    default:
      // Default to Phase 1 for safety
      return getPhaseFlags(MIGRATION_PHASES.PHASE_1);
  }
};

// Legacy-specific feature flag overrides
export const LEGACY_OVERRIDES: Partial<FeatureFlags> = {
  // Override environment variables for legacy-specific behavior
  ...getPhaseFlags(CURRENT_PHASE),
  
  // Legacy-specific overrides based on environment
  ...(process.env.REACT_APP_LEGACY_MODE === 'true' && {
    // Force all flags to false for pure legacy mode
    useSharedDashboard: false,
    useSharedQuantumagi: false,
    useSharedMonitoring: false,
    useSharedLayout: false,
    useSharedConsultation: false,
    useSharedAmendment: false,
    useSharedErrorHandling: false,
    useSharedPages: false,
    useSharedRouting: false,
  }),
};

// Component-specific migration configurations
export const COMPONENT_MIGRATION_CONFIG = {
  // Constitutional Council Dashboard
  dashboard: {
    flag: 'useSharedDashboard' as keyof FeatureFlags,
    riskLevel: 'HIGH',
    dependencies: ['useSharedAuth', 'useSharedTheme'],
    validationRequired: true,
    rollbackTime: '< 30 seconds',
  },
  
  // Quantumagi Dashboard (CRITICAL)
  quantumagi: {
    flag: 'useSharedQuantumagi' as keyof FeatureFlags,
    riskLevel: 'CRITICAL',
    dependencies: ['useSharedAuth', 'useSharedTheme', 'useSharedLayout'],
    validationRequired: true,
    rollbackTime: '< 10 seconds',
    specialValidation: 'Solana devnet connectivity required',
  },
  
  // Constitutional Fidelity Monitor
  monitoring: {
    flag: 'useSharedMonitoring' as keyof FeatureFlags,
    riskLevel: 'MEDIUM',
    dependencies: ['useSharedAuth'],
    validationRequired: true,
    rollbackTime: '< 60 seconds',
  },
  
  // Public Consultation Service
  consultation: {
    flag: 'useSharedConsultation' as keyof FeatureFlags,
    riskLevel: 'MEDIUM',
    dependencies: ['useSharedAuth'],
    validationRequired: true,
    rollbackTime: '< 60 seconds',
  },
  
  // Amendment Service
  amendment: {
    flag: 'useSharedAmendment' as keyof FeatureFlags,
    riskLevel: 'HIGH',
    dependencies: ['useSharedAuth', 'useSharedConsultation'],
    validationRequired: true,
    rollbackTime: '< 30 seconds',
  },
};

// Validation functions for each component
export const validateComponentMigration = async (componentKey: string): Promise<boolean> => {
  const config = COMPONENT_MIGRATION_CONFIG[componentKey as keyof typeof COMPONENT_MIGRATION_CONFIG];
  if (!config) return false;

  try {
    // Check dependencies
    for (const dep of config.dependencies) {
      const depEnabled = process.env[`REACT_APP_${dep.toUpperCase()}`] === 'true';
      if (!depEnabled) {
        console.warn(`Dependency ${dep} not enabled for ${componentKey}`);
        return false;
      }
    }

    // Special validation for Quantumagi
    if (componentKey === 'quantumagi') {
      return await validateQuantumagiIntegration();
    }

    // Special validation for dashboard
    if (componentKey === 'dashboard') {
      return await validateDashboardIntegration();
    }

    return true;
  } catch (error) {
    console.error(`Validation failed for ${componentKey}:`, error);
    return false;
  }
};

// Quantumagi-specific validation
const validateQuantumagiIntegration = async (): Promise<boolean> => {
  try {
    // Check Solana devnet connectivity
    const response = await fetch('https://api.devnet.solana.com', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'getHealth'
      })
    });
    
    return response.ok;
  } catch (error) {
    console.error('Quantumagi validation failed:', error);
    return false;
  }
};

// Dashboard-specific validation
const validateDashboardIntegration = async (): Promise<boolean> => {
  try {
    // Check AC Service connectivity
    const acResponse = await fetch(`${process.env.REACT_APP_AC_API_URL || 'http://localhost:8001'}/api/v1/health`);
    
    // Check GS Service connectivity
    const gsResponse = await fetch(`${process.env.REACT_APP_GS_API_URL || 'http://localhost:8003'}/api/v1/health`);
    
    return acResponse.ok && gsResponse.ok;
  } catch (error) {
    console.error('Dashboard validation failed:', error);
    return false;
  }
};

// Emergency rollback configuration
export const EMERGENCY_ROLLBACK_CONFIG = {
  // Automatic rollback triggers
  triggers: {
    errorRate: 0.05, // 5% error rate
    responseTime: 5000, // 5 second response time
    failedHealthChecks: 3, // 3 consecutive failed health checks
  },
  
  // Rollback actions
  actions: {
    disableAllSharedComponents: true,
    enableMaintenanceMode: false, // Don't enable maintenance mode automatically
    notifyAdministrators: true,
    logRollbackEvent: true,
  },
  
  // Recovery configuration
  recovery: {
    autoRetryAfter: 300000, // 5 minutes
    maxRetries: 3,
    requireManualApproval: true,
  },
};

// Monitoring configuration for feature flags
export const MONITORING_CONFIG = {
  // Metrics to track
  metrics: [
    'component_load_time',
    'error_rate',
    'user_satisfaction',
    'performance_impact',
    'rollback_frequency',
  ],
  
  // Alerting thresholds
  alerts: {
    errorRateThreshold: 0.02, // 2%
    performanceDegradation: 0.2, // 20% slower
    rollbackFrequency: 3, // 3 rollbacks per hour
  },
  
  // Reporting configuration
  reporting: {
    interval: 300000, // 5 minutes
    endpoint: '/api/v1/feature-flag-metrics',
    includeUserAgent: true,
    includeTiming: true,
  },
};

// Export configuration
export default {
  MIGRATION_PHASES,
  CURRENT_PHASE,
  getPhaseFlags,
  LEGACY_OVERRIDES,
  COMPONENT_MIGRATION_CONFIG,
  validateComponentMigration,
  EMERGENCY_ROLLBACK_CONFIG,
  MONITORING_CONFIG,
};
