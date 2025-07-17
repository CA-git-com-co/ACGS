'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { ConstitutionalCompliance, ConstitutionalContext, CONSTITUTIONAL_HASH } from '@/types';

interface ConstitutionalContextType {
  compliance: ConstitutionalCompliance;
  context: ConstitutionalContext;
  isLoading: boolean;
  error: string | null;
  validateAction: (action: string, data?: any) => Promise<boolean>;
  updateCompliance: (updates: Partial<ConstitutionalCompliance>) => void;
  refreshCompliance: () => Promise<void>;
}

const ConstitutionalContextContext = createContext<ConstitutionalContextType | undefined>(undefined);

export function ConstitutionalContextProvider({ children }: { children: ReactNode }) {
  const [compliance, setCompliance] = useState<ConstitutionalCompliance>({
    hash: CONSTITUTIONAL_HASH,
    compliant: true,
    score: 1.0,
    violations: [],
    lastValidated: new Date().toISOString(),
    metadata: {},
  });

  const [context, setContext] = useState<ConstitutionalContext>({
    hash: CONSTITUTIONAL_HASH,
    principles: [
      'non-maleficence',
      'beneficence',
      'autonomy',
      'justice',
      'explicability',
      'fairness',
      'accountability',
      'transparency',
      'privacy',
      'security',
    ],
    complianceLevel: 'strict',
    auditLevel: 'full',
    validationRules: [],
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateAction = async (action: string, data?: any): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      // Simulate API call to constitutional validation service
      const response = await fetch('/api/constitutional/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Constitutional-Hash': CONSTITUTIONAL_HASH,
        },
        body: JSON.stringify({
          action,
          data,
          context: context.principles,
        }),
      });

      if (!response.ok) {
        throw new Error(`Validation failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Update compliance based on validation result
      setCompliance(prev => ({
        ...prev,
        compliant: result.compliant,
        score: result.score,
        violations: result.violations || [],
        lastValidated: new Date().toISOString(),
        metadata: { ...prev.metadata, lastAction: action },
      }));

      return result.compliant;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown validation error';
      setError(errorMessage);
      
      // Default to non-compliant on error
      setCompliance(prev => ({
        ...prev,
        compliant: false,
        score: 0,
        violations: [...prev.violations, `Validation error: ${errorMessage}`],
        lastValidated: new Date().toISOString(),
      }));

      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const updateCompliance = (updates: Partial<ConstitutionalCompliance>) => {
    setCompliance(prev => ({
      ...prev,
      ...updates,
      lastValidated: new Date().toISOString(),
    }));
  };

  const refreshCompliance = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/constitutional/status', {
        headers: {
          'X-Constitutional-Hash': CONSTITUTIONAL_HASH,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to refresh compliance: ${response.statusText}`);
      }

      const result = await response.json();
      setCompliance(result.compliance);
      setContext(result.context);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Initialize constitutional context on mount
  useEffect(() => {
    refreshCompliance();
  }, []);

  // Validate constitutional hash on every render
  useEffect(() => {
    if (compliance.hash !== CONSTITUTIONAL_HASH) {
      setError('Constitutional hash mismatch - potential security issue');
      setCompliance(prev => ({
        ...prev,
        compliant: false,
        violations: [...prev.violations, 'Constitutional hash mismatch'],
      }));
    }
  }, [compliance.hash]);

  const value: ConstitutionalContextType = {
    compliance,
    context,
    isLoading,
    error,
    validateAction,
    updateCompliance,
    refreshCompliance,
  };

  return (
    <ConstitutionalContextContext.Provider value={value}>
      {children}
    </ConstitutionalContextContext.Provider>
  );
}

export function useConstitutionalContext() {
  const context = useContext(ConstitutionalContextContext);
  if (context === undefined) {
    throw new Error('useConstitutionalContext must be used within a ConstitutionalContextProvider');
  }
  return context;
}

export function useConstitutionalValidation() {
  const { validateAction, isLoading, error } = useConstitutionalContext();
  
  return {
    validateAction,
    isValidating: isLoading,
    validationError: error,
  };
}

export function useConstitutionalCompliance() {
  const { compliance, updateCompliance, refreshCompliance } = useConstitutionalContext();
  
  return {
    compliance,
    isCompliant: compliance.compliant,
    complianceScore: compliance.score,
    violations: compliance.violations,
    updateCompliance,
    refreshCompliance,
  };
}