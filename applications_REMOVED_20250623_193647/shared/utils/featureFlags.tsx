/**
 * Feature Flag System for ACGS-PGP Legacy Deprecation
 *
 * Provides comprehensive feature flag management for gradual rollout
 * and rollback capabilities during legacy frontend migration.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Feature flag configuration interface
export interface FeatureFlags {
  // Component migration flags
  useSharedDashboard: boolean;
  useSharedQuantumagi: boolean;
  useSharedMonitoring: boolean;
  useSharedLayout: boolean;

  // Service migration flags
  useSharedConsultation: boolean;
  useSharedAmendment: boolean;
  useSharedErrorHandling: boolean;

  // Page migration flags
  useSharedPages: boolean;
  useSharedRouting: boolean;

  // Infrastructure flags
  useSharedTheme: boolean;
  useSharedAuth: boolean;

  // Emergency flags
  emergencyRollback: boolean;
  maintenanceMode: boolean;
}

// Default feature flag values
const DEFAULT_FLAGS: FeatureFlags = {
  // Component migration flags - start disabled for safety
  useSharedDashboard: false,
  useSharedQuantumagi: false,
  useSharedMonitoring: false,
  useSharedLayout: false,

  // Service migration flags - start disabled for safety
  useSharedConsultation: false,
  useSharedAmendment: false,
  useSharedErrorHandling: false,

  // Page migration flags - start disabled for safety
  useSharedPages: false,
  useSharedRouting: false,

  // Infrastructure flags - can be enabled early
  useSharedTheme: true,
  useSharedAuth: true,

  // Emergency flags - always start disabled
  emergencyRollback: false,
  maintenanceMode: false
};

// Environment-based flag overrides
const getEnvironmentFlags = (): Partial<FeatureFlags> => {
  const env = process.env;

  return {
    // Component flags
    useSharedDashboard: env.REACT_APP_USE_SHARED_DASHBOARD === 'true',
    useSharedQuantumagi: env.REACT_APP_USE_SHARED_QUANTUMAGI === 'true',
    useSharedMonitoring: env.REACT_APP_USE_SHARED_MONITORING === 'true',
    useSharedLayout: env.REACT_APP_USE_SHARED_LAYOUT === 'true',

    // Service flags
    useSharedConsultation: env.REACT_APP_USE_SHARED_CONSULTATION === 'true',
    useSharedAmendment: env.REACT_APP_USE_SHARED_AMENDMENT === 'true',
    useSharedErrorHandling: env.REACT_APP_USE_SHARED_ERROR_HANDLING === 'true',

    // Page flags
    useSharedPages: env.REACT_APP_USE_SHARED_PAGES === 'true',
    useSharedRouting: env.REACT_APP_USE_SHARED_ROUTING === 'true',

    // Infrastructure flags
    useSharedTheme: env.REACT_APP_USE_SHARED_THEME !== 'false', // Default true
    useSharedAuth: env.REACT_APP_USE_SHARED_AUTH !== 'false', // Default true

    // Emergency flags
    emergencyRollback: env.REACT_APP_EMERGENCY_ROLLBACK === 'true',
    maintenanceMode: env.REACT_APP_MAINTENANCE_MODE === 'true'
  };
};

// Feature flag context
interface FeatureFlagContextType {
  flags: FeatureFlags;
  updateFlag: (key: keyof FeatureFlags, value: boolean) => void;
  updateFlags: (updates: Partial<FeatureFlags>) => void;
  resetFlags: () => void;
  isEnabled: (key: keyof FeatureFlags) => boolean;
  isDisabled: (key: keyof FeatureFlags) => boolean;
}

const FeatureFlagContext = createContext<FeatureFlagContextType | undefined>(undefined);

// Feature flag provider props
interface FeatureFlagProviderProps {
  children: ReactNode;
  initialFlags?: Partial<FeatureFlags>;
  enableRemoteConfig?: boolean;
  remoteConfigUrl?: string;
}

// Feature flag provider component
export const FeatureFlagProvider: React.FC<FeatureFlagProviderProps> = ({
  children,
  initialFlags = {},
  enableRemoteConfig = false,
  remoteConfigUrl
}) => {
  // Merge default flags with environment and initial overrides
  const [flags, setFlags] = useState<FeatureFlags>(() => ({
    ...DEFAULT_FLAGS,
    ...getEnvironmentFlags(),
    ...initialFlags
  }));

  // Load remote configuration if enabled
  useEffect(() => {
    if (enableRemoteConfig && remoteConfigUrl) {
      loadRemoteConfig(remoteConfigUrl);
    }
  }, [enableRemoteConfig, remoteConfigUrl]);

  // Load remote configuration
  const loadRemoteConfig = async (url: string) => {
    try {
      const response = await fetch(url);
      if (response.ok) {
        const remoteFlags = await response.json();
        setFlags(current => ({ ...current, ...remoteFlags }));
      }
    } catch (error) {
      console.warn('Failed to load remote feature flag configuration:', error);
    }
  };

  // Update single flag
  const updateFlag = (key: keyof FeatureFlags, value: boolean) => {
    setFlags(current => ({ ...current, [key]: value }));
  };

  // Update multiple flags
  const updateFlags = (updates: Partial<FeatureFlags>) => {
    setFlags(current => ({ ...current, ...updates }));
  };

  // Reset flags to defaults
  const resetFlags = () => {
    setFlags({
      ...DEFAULT_FLAGS,
      ...getEnvironmentFlags(),
      ...initialFlags
    });
  };

  // Check if flag is enabled
  const isEnabled = (key: keyof FeatureFlags): boolean => {
    // Emergency rollback overrides all other flags
    if (flags.emergencyRollback && key !== 'emergencyRollback' && key !== 'maintenanceMode') {
      return false;
    }

    // Maintenance mode disables most features
    if (
      flags.maintenanceMode &&
      !['emergencyRollback', 'maintenanceMode', 'useSharedAuth'].includes(key)
    ) {
      return false;
    }

    return flags[key];
  };

  // Check if flag is disabled
  const isDisabled = (key: keyof FeatureFlags): boolean => {
    return !isEnabled(key);
  };

  const contextValue: FeatureFlagContextType = {
    flags,
    updateFlag,
    updateFlags,
    resetFlags,
    isEnabled,
    isDisabled
  };

  return <FeatureFlagContext.Provider value={contextValue}>{children}</FeatureFlagContext.Provider>;
};

// Hook to use feature flags
export const useFeatureFlags = (): FeatureFlagContextType => {
  const context = useContext(FeatureFlagContext);
  if (context === undefined) {
    throw new Error('useFeatureFlags must be used within a FeatureFlagProvider');
  }
  return context;
};

// Hook to check a specific feature flag
export const useFeatureFlag = (key: keyof FeatureFlags): boolean => {
  const { isEnabled } = useFeatureFlags();
  return isEnabled(key);
};

// Higher-order component for feature flag conditional rendering
interface WithFeatureFlagProps {
  flag: keyof FeatureFlags;
  fallback?: ReactNode;
  children: ReactNode;
}

export const WithFeatureFlag: React.FC<WithFeatureFlagProps> = ({
  flag,
  fallback = null,
  children
}) => {
  const isEnabled = useFeatureFlag(flag);
  return <>{isEnabled ? children : fallback}</>;
};

// Component for conditional rendering based on feature flags
interface FeatureToggleProps {
  flag: keyof FeatureFlags;
  enabled?: ReactNode;
  disabled?: ReactNode;
}

export const FeatureToggle: React.FC<FeatureToggleProps> = ({
  flag,
  enabled = null,
  disabled = null
}) => {
  const isEnabled = useFeatureFlag(flag);
  return <>{isEnabled ? enabled : disabled}</>;
};

// Migration helper component for gradual rollout
interface MigrationToggleProps {
  flag: keyof FeatureFlags;
  legacyComponent: ReactNode;
  sharedComponent: ReactNode;
  loadingComponent?: ReactNode;
}

export const MigrationToggle: React.FC<MigrationToggleProps> = ({
  flag,
  legacyComponent,
  sharedComponent,
  loadingComponent = null
}) => {
  const { isEnabled, flags } = useFeatureFlags();
  const [isLoading, setIsLoading] = useState(false);

  // Handle component switching with loading state
  useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => setIsLoading(false), 100);
    return () => clearTimeout(timer);
  }, [flags[flag]]);

  if (isLoading && loadingComponent) {
    return <>{loadingComponent}</>;
  }

  return <>{isEnabled(flag) ? sharedComponent : legacyComponent}</>;
};

// Emergency rollback utility
export const triggerEmergencyRollback = () => {
  const event = new CustomEvent('acgs-emergency-rollback', {
    detail: { timestamp: new Date().toISOString() }
  });
  window.dispatchEvent(event);
};

// Feature flag debugging utility (development only)
export const FeatureFlagDebugger: React.FC = () => {
  const { flags, updateFlag } = useFeatureFlags();

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: 10,
        right: 10,
        background: 'rgba(0,0,0,0.8)',
        color: 'white',
        padding: '10px',
        borderRadius: '5px',
        fontSize: '12px',
        zIndex: 9999,
        maxHeight: '300px',
        overflow: 'auto'
      }}
    >
      <h4>Feature Flags (Dev Only)</h4>
      {Object.entries(flags).map(([key, value]) => (
        <div key={key} style={{ margin: '5px 0' }}>
          <label>
            <input
              type="checkbox"
              checked={value}
              onChange={e => updateFlag(key as keyof FeatureFlags, e.target.checked)}
            />
            {key}: {value ? 'ON' : 'OFF'}
          </label>
        </div>
      ))}
    </div>
  );
};

// Export types and utilities
export type { FeatureFlags, FeatureFlagContextType };
export { DEFAULT_FLAGS, getEnvironmentFlags };
