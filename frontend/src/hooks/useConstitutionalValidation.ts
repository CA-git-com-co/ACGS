/**
 * Constitutional Validation Hook for ACGS-2 Frontend
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * React hook for constitutional compliance validation with performance optimization.
 */

import { useCallback, useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { constitutionalClient } from '@/lib/constitutional-client';
import type { ConstitutionalValidationResult, ValidationContext, PerformanceMetrics } from '@/lib/constitutional-client';
import { CONFIG } from '@/config';

// Hook options
interface UseConstitutionalValidationOptions {
  enabled?: boolean;
  refetchInterval?: number;
  cacheTime?: number;
  staleTime?: number;
  component?: string;
  action?: string;
  preloadCommonValidations?: boolean;
}

// Hook return type
interface UseConstitutionalValidationReturn {
  // Validation state
  isValid: boolean;
  isLoading: boolean;
  error: Error | null;
  result: ConstitutionalValidationResult | null;
  
  // Methods
  validate: (context: ValidationContext) => Promise<ConstitutionalValidationResult>;
  validateHash: (hash: string) => Promise<boolean>;
  preloadValidations: (contexts: ValidationContext[]) => Promise<void>;
  
  // Metrics
  metrics: PerformanceMetrics;
  resetMetrics: () => void;
  clearCache: () => void;
  
  // Constitutional compliance
  constitutionalHash: string;
  isConstitutionallyCompliant: boolean;
  complianceScore: number;
}

/**
 * Constitutional validation hook with performance optimization
 */
export function useConstitutionalValidation(
  options: UseConstitutionalValidationOptions = {}
): UseConstitutionalValidationReturn {
  const {
    enabled = true,
    refetchInterval = CONFIG.polling.complianceInterval,
    cacheTime = 5 * 60 * 1000, // 5 minutes
    staleTime = 2 * 60 * 1000, // 2 minutes
    component = 'unknown',
    action = 'unknown',
    preloadCommonValidations = true,
  } = options;

  const queryClient = useQueryClient();
  const [metrics, setMetrics] = useState<PerformanceMetrics>(constitutionalClient.getMetrics());

  // Base validation context
  const baseContext: ValidationContext = {
    component,
    action,
    userId: 'frontend-user', // Would be actual user ID in real app
    sessionId: 'session-' + Date.now(), // Would be actual session ID
  };

  // Query for constitutional compliance status
  const {
    data: result,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['constitutional-validation', baseContext],
    queryFn: () => constitutionalClient.validateCompliance(baseContext),
    enabled,
    refetchInterval,
    gcTime: cacheTime,
    staleTime,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // Mutation for on-demand validation
  const validationMutation = useMutation({
    mutationFn: (context: ValidationContext) => 
      constitutionalClient.validateCompliance(context),
    onSuccess: (data) => {
      queryClient.setQueryData(['constitutional-validation', baseContext], data);
    },
  });

  // Hash validation mutation
  const hashValidationMutation = useMutation({
    mutationFn: (hash: string) => constitutionalClient.validateHash(hash),
  });

  // Update metrics periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(constitutionalClient.getMetrics());
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  // Preload common validations on mount
  useEffect(() => {
    if (preloadCommonValidations && enabled) {
      const commonContexts: ValidationContext[] = [
        { component: 'dashboard', action: 'view' },
        { component: 'dashboard', action: 'refresh' },
        { component: 'constitutional', action: 'validate' },
        { component: 'performance', action: 'monitor' },
      ];

      constitutionalClient.preloadValidations(commonContexts).catch(console.error);
    }
  }, [preloadCommonValidations, enabled]);

  // Validation function
  const validate = useCallback(async (context: ValidationContext) => {
    const result = await validationMutation.mutateAsync(context);
    setMetrics(constitutionalClient.getMetrics());
    return result;
  }, [validationMutation]);

  // Hash validation function
  const validateHash = useCallback(async (hash: string) => {
    const result = await hashValidationMutation.mutateAsync(hash);
    setMetrics(constitutionalClient.getMetrics());
    return result;
  }, [hashValidationMutation]);

  // Preload validations function
  const preloadValidations = useCallback(async (contexts: ValidationContext[]) => {
    await constitutionalClient.preloadValidations(contexts);
    setMetrics(constitutionalClient.getMetrics());
  }, []);

  // Reset metrics function
  const resetMetrics = useCallback(() => {
    constitutionalClient.resetMetrics();
    setMetrics(constitutionalClient.getMetrics());
  }, []);

  // Clear cache function
  const clearCache = useCallback(() => {
    constitutionalClient.clearCache();
    queryClient.removeQueries({ queryKey: ['constitutional-validation'] });
  }, [queryClient]);

  // Derived state
  const isValid = result?.isValid ?? false;
  const isConstitutionallyCompliant = result?.score 
    ? result.score >= (CONFIG.constitutional.complianceThreshold / 100)
    : false;
  const complianceScore = result?.score ?? 0;

  // Performance warning
  useEffect(() => {
    if (metrics.p99Latency > CONFIG.performance.latencyP99Target) {
      console.warn(
        `Constitutional validation P99 latency (${metrics.p99Latency.toFixed(2)}ms) ` +
        `exceeds target (${CONFIG.performance.latencyP99Target}ms)`
      );
    }
  }, [metrics.p99Latency]);

  return {
    // Validation state
    isValid,
    isLoading: isLoading || validationMutation.isPending,
    error: error || validationMutation.error,
    result: result || null,
    
    // Methods
    validate,
    validateHash,
    preloadValidations,
    
    // Metrics
    metrics,
    resetMetrics,
    clearCache,
    
    // Constitutional compliance
    constitutionalHash: CONFIG.constitutional.hash,
    isConstitutionallyCompliant,
    complianceScore,
  };
}

/**
 * Hook for validating constitutional hash specifically
 */
export function useConstitutionalHashValidation() {
  const { validateHash, metrics } = useConstitutionalValidation();
  
  const [isValidating, setIsValidating] = useState(false);
  const [lastValidationResult, setLastValidationResult] = useState<boolean | null>(null);

  const validateConstitutionalHash = useCallback(async (hash: string) => {
    setIsValidating(true);
    try {
      const result = await validateHash(hash);
      setLastValidationResult(result);
      return result;
    } finally {
      setIsValidating(false);
    }
  }, [validateHash]);

  // Validate current constitutional hash on mount
  useEffect(() => {
    validateConstitutionalHash(CONFIG.constitutional.hash).catch(console.error);
  }, [validateConstitutionalHash]);

  return {
    validateConstitutionalHash,
    isValidating,
    lastValidationResult,
    isCurrentHashValid: lastValidationResult,
    constitutionalHash: CONFIG.constitutional.hash,
    metrics,
  };
}

/**
 * Hook for performance monitoring of constitutional validation
 */
export function useConstitutionalPerformanceMonitoring() {
  const { metrics, resetMetrics } = useConstitutionalValidation();
  const [performanceAlerts, setPerformanceAlerts] = useState<string[]>([]);

  // Monitor performance and generate alerts
  useEffect(() => {
    const alerts: string[] = [];

    // Check P99 latency
    if (metrics.p99Latency > CONFIG.performance.latencyP99Target) {
      alerts.push(
        `P99 latency (${metrics.p99Latency.toFixed(2)}ms) exceeds target (${CONFIG.performance.latencyP99Target}ms)`
      );
    }

    // Check cache hit rate
    if (metrics.cacheHitRate < CONFIG.performance.cacheHitRateTarget) {
      alerts.push(
        `Cache hit rate (${metrics.cacheHitRate.toFixed(1)}%) below target (${CONFIG.performance.cacheHitRateTarget}%)`
      );
    }

    // Check constitutional compliance
    if (metrics.constitutionalCompliance < 1.0) {
      alerts.push(
        `Constitutional compliance (${(metrics.constitutionalCompliance * 100).toFixed(1)}%) below 100%`
      );
    }

    setPerformanceAlerts(alerts);
  }, [metrics]);

  // Performance status
  const isPerformanceGood = performanceAlerts.length === 0;
  const performanceGrade = isPerformanceGood 
    ? 'A' 
    : performanceAlerts.length === 1 
      ? 'B' 
      : performanceAlerts.length === 2 
        ? 'C' 
        : 'D';

  return {
    metrics,
    performanceAlerts,
    isPerformanceGood,
    performanceGrade,
    resetMetrics,
    targets: CONFIG.performance,
  };
}

/**
 * Hook for bulk validation operations
 */
export function useBulkConstitutionalValidation() {
  const { validate, metrics } = useConstitutionalValidation();
  const [isValidating, setIsValidating] = useState(false);
  const [results, setResults] = useState<ConstitutionalValidationResult[]>([]);

  const validateBulk = useCallback(async (contexts: ValidationContext[]) => {
    setIsValidating(true);
    setResults([]);

    try {
      const validationPromises = contexts.map(context => validate(context));
      const bulkResults = await Promise.allSettled(validationPromises);
      
      const successfulResults = bulkResults
        .filter((result): result is PromiseFulfilledResult<ConstitutionalValidationResult> => 
          result.status === 'fulfilled'
        )
        .map(result => result.value);

      setResults(successfulResults);
      return successfulResults;
    } finally {
      setIsValidating(false);
    }
  }, [validate]);

  const validationSummary = {
    total: results.length,
    valid: results.filter(r => r.isValid).length,
    invalid: results.filter(r => !r.isValid).length,
    averageScore: results.length > 0 
      ? results.reduce((sum, r) => sum + r.score, 0) / results.length 
      : 0,
  };

  return {
    validateBulk,
    isValidating,
    results,
    validationSummary,
    metrics,
  };
}

export default useConstitutionalValidation;