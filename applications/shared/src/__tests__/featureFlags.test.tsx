/**
 * Feature Flag System Tests
 *
 * Comprehensive test suite for the feature flag system used in
 * ACGS-PGP legacy frontend migration.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

import {
  FeatureFlagProvider,
  useFeatureFlags,
  useFeatureFlag,
  WithFeatureFlag,
  FeatureToggle,
  MigrationToggle,
  triggerEmergencyRollback,
  DEFAULT_FLAGS,
  getEnvironmentFlags,
  type FeatureFlags
} from '../utils/featureFlags';

// Mock environment variables
const mockEnv = (envVars: Record<string, string>) => {
  const originalEnv = process.env;
  process.env = { ...originalEnv, ...envVars };
  return () => {
    process.env = originalEnv;
  };
};

// Test component that uses feature flags
const TestComponent: React.FC<{ flagKey: keyof FeatureFlags }> = ({ flagKey }) => {
  const { flags, updateFlag, isEnabled } = useFeatureFlags();
  const specificFlag = useFeatureFlag(flagKey);

  return (
    <div>
      <div data-testid="flag-value">{specificFlag ? 'enabled' : 'disabled'}</div>
      <div data-testid="all-flags">{JSON.stringify(flags)}</div>
      <button data-testid="toggle-flag" onClick={() => updateFlag(flagKey, !flags[flagKey])}>
        Toggle {flagKey}
      </button>
      <div data-testid="is-enabled">{isEnabled(flagKey) ? 'true' : 'false'}</div>
    </div>
  );
};

describe('Feature Flag System', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('FeatureFlagProvider', () => {
    it('should provide default flags when no overrides are given', () => {
      render(
        <FeatureFlagProvider>
          <TestComponent flagKey="useSharedDashboard" />
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('flag-value')).toHaveTextContent('disabled');
    });

    it('should apply initial flag overrides', () => {
      const initialFlags = { useSharedDashboard: true };

      render(
        <FeatureFlagProvider initialFlags={initialFlags}>
          <TestComponent flagKey="useSharedDashboard" />
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('flag-value')).toHaveTextContent('enabled');
    });

    it('should allow updating flags', async () => {
      render(
        <FeatureFlagProvider>
          <TestComponent flagKey="useSharedDashboard" />
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('flag-value')).toHaveTextContent('disabled');

      fireEvent.click(screen.getByTestId('toggle-flag'));

      await waitFor(() => {
        expect(screen.getByTestId('flag-value')).toHaveTextContent('enabled');
      });
    });
  });

  describe('Emergency Rollback', () => {
    it('should disable all flags when emergency rollback is active', () => {
      const initialFlags = {
        useSharedDashboard: true,
        useSharedQuantumagi: true,
        emergencyRollback: true
      };

      render(
        <FeatureFlagProvider initialFlags={initialFlags}>
          <TestComponent flagKey="useSharedDashboard" />
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('is-enabled')).toHaveTextContent('false');
    });

    it('should not disable emergency rollback and maintenance mode flags', () => {
      const initialFlags = {
        emergencyRollback: true,
        maintenanceMode: true
      };

      render(
        <FeatureFlagProvider initialFlags={initialFlags}>
          <div>
            <TestComponent flagKey="emergencyRollback" />
            <TestComponent flagKey="maintenanceMode" />
          </div>
        </FeatureFlagProvider>
      );

      const enabledElements = screen.getAllByText('true');
      expect(enabledElements).toHaveLength(2);
    });
  });

  describe('Maintenance Mode', () => {
    it('should disable most flags when maintenance mode is active', () => {
      const initialFlags = {
        useSharedDashboard: true,
        useSharedQuantumagi: true,
        maintenanceMode: true
      };

      render(
        <FeatureFlagProvider initialFlags={initialFlags}>
          <TestComponent flagKey="useSharedDashboard" />
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('is-enabled')).toHaveTextContent('false');
    });

    it('should keep auth enabled in maintenance mode', () => {
      const initialFlags = {
        useSharedAuth: true,
        maintenanceMode: true
      };

      render(
        <FeatureFlagProvider initialFlags={initialFlags}>
          <TestComponent flagKey="useSharedAuth" />
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('is-enabled')).toHaveTextContent('true');
    });
  });

  describe('Environment Configuration', () => {
    it('should read flags from environment variables', () => {
      const restoreEnv = mockEnv({
        REACT_APP_USE_SHARED_DASHBOARD: 'true',
        REACT_APP_USE_SHARED_QUANTUMAGI: 'false',
        REACT_APP_EMERGENCY_ROLLBACK: 'true'
      });

      const envFlags = getEnvironmentFlags();

      expect(envFlags.useSharedDashboard).toBe(true);
      expect(envFlags.useSharedQuantumagi).toBe(false);
      expect(envFlags.emergencyRollback).toBe(true);

      restoreEnv();
    });

    it('should default infrastructure flags to true', () => {
      const restoreEnv = mockEnv({});

      const envFlags = getEnvironmentFlags();

      expect(envFlags.useSharedTheme).toBe(true);
      expect(envFlags.useSharedAuth).toBe(true);

      restoreEnv();
    });
  });

  describe('WithFeatureFlag Component', () => {
    it('should render children when flag is enabled', () => {
      const initialFlags = { useSharedDashboard: true };

      render(
        <FeatureFlagProvider initialFlags={initialFlags}>
          <WithFeatureFlag flag="useSharedDashboard">
            <div data-testid="enabled-content">Enabled Content</div>
          </WithFeatureFlag>
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('enabled-content')).toBeInTheDocument();
    });

    it('should render fallback when flag is disabled', () => {
      const initialFlags = { useSharedDashboard: false };

      render(
        <FeatureFlagProvider initialFlags={initialFlags}>
          <WithFeatureFlag
            flag="useSharedDashboard"
            fallback={<div data-testid="fallback-content">Fallback Content</div>}
          >
            <div data-testid="enabled-content">Enabled Content</div>
          </WithFeatureFlag>
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('fallback-content')).toBeInTheDocument();
      expect(screen.queryByTestId('enabled-content')).not.toBeInTheDocument();
    });
  });

  describe('FeatureToggle Component', () => {
    it('should render enabled component when flag is true', () => {
      const initialFlags = { useSharedDashboard: true };

      render(
        <FeatureFlagProvider initialFlags={initialFlags}>
          <FeatureToggle
            flag="useSharedDashboard"
            enabled={<div data-testid="enabled">Enabled</div>}
            disabled={<div data-testid="disabled">Disabled</div>}
          />
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('enabled')).toBeInTheDocument();
      expect(screen.queryByTestId('disabled')).not.toBeInTheDocument();
    });

    it('should render disabled component when flag is false', () => {
      const initialFlags = { useSharedDashboard: false };

      render(
        <FeatureFlagProvider initialFlags={initialFlags}>
          <FeatureToggle
            flag="useSharedDashboard"
            enabled={<div data-testid="enabled">Enabled</div>}
            disabled={<div data-testid="disabled">Disabled</div>}
          />
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('disabled')).toBeInTheDocument();
      expect(screen.queryByTestId('enabled')).not.toBeInTheDocument();
    });
  });

  describe('MigrationToggle Component', () => {
    it('should render shared component when flag is enabled', () => {
      const initialFlags = { useSharedDashboard: true };

      render(
        <FeatureFlagProvider initialFlags={initialFlags}>
          <MigrationToggle
            flag="useSharedDashboard"
            legacyComponent={<div data-testid="legacy">Legacy</div>}
            sharedComponent={<div data-testid="shared">Shared</div>}
          />
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('shared')).toBeInTheDocument();
      expect(screen.queryByTestId('legacy')).not.toBeInTheDocument();
    });

    it('should render legacy component when flag is disabled', () => {
      const initialFlags = { useSharedDashboard: false };

      render(
        <FeatureFlagProvider initialFlags={initialFlags}>
          <MigrationToggle
            flag="useSharedDashboard"
            legacyComponent={<div data-testid="legacy">Legacy</div>}
            sharedComponent={<div data-testid="shared">Shared</div>}
          />
        </FeatureFlagProvider>
      );

      expect(screen.getByTestId('legacy')).toBeInTheDocument();
      expect(screen.queryByTestId('shared')).not.toBeInTheDocument();
    });
  });

  describe('Emergency Rollback Trigger', () => {
    it('should dispatch emergency rollback event', () => {
      const eventListener = jest.fn();
      window.addEventListener('acgs-emergency-rollback', eventListener);

      triggerEmergencyRollback();

      expect(eventListener).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'acgs-emergency-rollback',
          detail: expect.objectContaining({
            timestamp: expect.any(String)
          })
        })
      );

      window.removeEventListener('acgs-emergency-rollback', eventListener);
    });
  });

  describe('Default Configuration', () => {
    it('should have safe defaults for all flags', () => {
      expect(DEFAULT_FLAGS.useSharedDashboard).toBe(false);
      expect(DEFAULT_FLAGS.useSharedQuantumagi).toBe(false);
      expect(DEFAULT_FLAGS.emergencyRollback).toBe(false);
      expect(DEFAULT_FLAGS.maintenanceMode).toBe(false);

      // Infrastructure flags should default to true
      expect(DEFAULT_FLAGS.useSharedTheme).toBe(true);
      expect(DEFAULT_FLAGS.useSharedAuth).toBe(true);
    });
  });

  describe('Hook Error Handling', () => {
    it('should throw error when useFeatureFlags is used outside provider', () => {
      const TestComponentWithoutProvider = () => {
        useFeatureFlags();
        return <div>Test</div>;
      };

      // Suppress console.error for this test
      const originalError = console.error;
      console.error = jest.fn();

      expect(() => {
        render(<TestComponentWithoutProvider />);
      }).toThrow('useFeatureFlags must be used within a FeatureFlagProvider');

      console.error = originalError;
    });

    it('should throw error when useFeatureFlag is used outside provider', () => {
      const TestComponentWithoutProvider = () => {
        useFeatureFlag('useSharedDashboard');
        return <div>Test</div>;
      };

      // Suppress console.error for this test
      const originalError = console.error;
      console.error = jest.fn();

      expect(() => {
        render(<TestComponentWithoutProvider />);
      }).toThrow('useFeatureFlags must be used within a FeatureFlagProvider');

      console.error = originalError;
    });
  });
});
