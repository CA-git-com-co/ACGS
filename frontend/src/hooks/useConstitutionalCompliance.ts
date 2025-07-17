import { useState, useEffect, useCallback } from 'react';
import { CONFIG } from '@/config';
import { apiClient } from '@/services/api-client';

export interface ConstitutionalComplianceStatus {
  hash: string;
  isValid: boolean;
  lastValidated: string;
  complianceRate: number;
  violations: ConstitutionalViolation[];
}

export interface ConstitutionalViolation {
  id: string;
  type: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  context?: Record<string, any>;
}

export interface ConstitutionalComplianceHook {
  status: ConstitutionalComplianceStatus;
  isLoading: boolean;
  error: string | null;
  isCompliant: boolean;
  complianceRate: number;
  validateAction: (action: string, data?: any) => Promise<boolean>;
  validateCompliance: () => Promise<boolean>;
  reportViolation: (violation: Omit<ConstitutionalViolation, 'id' | 'timestamp'>) => void;
  refreshCompliance: () => Promise<void>;
}

export function useConstitutionalCompliance(): ConstitutionalComplianceHook {
  const [status, setStatus] = useState<ConstitutionalComplianceStatus>({
    hash: CONFIG.constitutional.hash,
    isValid: true,
    lastValidated: new Date().toISOString(),
    complianceRate: 100,
    violations: [],
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateAction = useCallback(async (action: string, data?: any): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await apiClient.post<{ isValid: boolean; violations?: ConstitutionalViolation[] }>(
        '/api/v1/constitutional/validate',
        {
          action,
          data,
          constitutionalHash: CONFIG.constitutional.hash,
        }
      );

      const { isValid, violations = [] } = response.data;

      if (!isValid && violations.length > 0) {
        setStatus(prev => ({
          ...prev,
          violations: [...prev.violations, ...violations],
          complianceRate: Math.max(0, prev.complianceRate - (violations.length * 5)),
          lastValidated: new Date().toISOString(),
        }));
      }

      return isValid;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Constitutional validation failed';
      setError(errorMessage);
      console.error('Constitutional validation error:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const validateCompliance = useCallback(async (): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await apiClient.get<{ isValid: boolean; complianceRate: number }>(
        '/api/v1/constitutional/validate',
        { constitutionalHash: CONFIG.constitutional.hash }
      );

      const { isValid, complianceRate } = response.data;

      setStatus(prev => ({
        ...prev,
        isValid,
        complianceRate,
        lastValidated: new Date().toISOString(),
      }));

      return isValid;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Constitutional compliance validation failed';
      setError(errorMessage);
      console.error('Constitutional compliance validation error:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reportViolation = useCallback((violation: Omit<ConstitutionalViolation, 'id' | 'timestamp'>) => {
    const newViolation: ConstitutionalViolation = {
      ...violation,
      id: `violation_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
      timestamp: new Date().toISOString(),
    };

    setStatus(prev => ({
      ...prev,
      violations: [...prev.violations, newViolation],
      complianceRate: Math.max(0, prev.complianceRate - 5),
      lastValidated: new Date().toISOString(),
    }));

    // Report to audit service if available
    if (CONFIG.features.enableAuditLogging) {
      apiClient.post('/api/v1/audit/violation', {
        violation: newViolation,
        constitutionalHash: CONFIG.constitutional.hash,
      }).catch(err => {
        console.error('Failed to report violation to audit service:', err);
      });
    }
  }, []);

  const refreshCompliance = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await apiClient.get<ConstitutionalComplianceStatus>(
        '/api/v1/constitutional/status',
        { constitutionalHash: CONFIG.constitutional.hash }
      );

      setStatus(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to refresh compliance status';
      setError(errorMessage);
      console.error('Failed to refresh compliance status:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Periodic compliance check
  useEffect(() => {
    const interval = setInterval(() => {
      refreshCompliance().catch(console.error);
    }, CONFIG.polling.complianceInterval);

    return () => clearInterval(interval);
  }, [refreshCompliance]);

  // Initial compliance check
  useEffect(() => {
    refreshCompliance().catch(console.error);
  }, [refreshCompliance]);

  // Validate constitutional hash on mount
  useEffect(() => {
    if (CONFIG.constitutional.hash !== 'cdd01ef066bc6cf2') {
      reportViolation({
        type: 'CONSTITUTIONAL_HASH_MISMATCH',
        message: 'Invalid constitutional hash detected',
        severity: 'critical',
        context: {
          expected: 'cdd01ef066bc6cf2',
          actual: CONFIG.constitutional.hash,
        },
      });
    }
  }, [reportViolation]);

  return {
    status,
    isLoading,
    error,
    isCompliant: status.isValid,
    complianceRate: status.complianceRate,
    validateAction,
    validateCompliance,
    reportViolation,
    refreshCompliance,
  };
}