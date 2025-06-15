import React, { useState, useEffect } from 'react';
import { z } from 'zod';
import { ComplianceResult, ActivePolicy } from '../types/governance';
import { Spinner, LoadingButton } from './LoadingStates';
import { useLoadingState } from '../hooks/useLoadingState';
import ServiceErrorBoundary from './ServiceErrorBoundary';
import { validateProps } from '../utils/propValidation';
import { ComplianceResultSchema, ActivePolicySchema } from '../types/validation';

/**
 * Action context for compliance checking
 */
interface ActionContext {
  /** Whether the action requires governance approval */
  requiresGovernance: boolean;
  /** Whether governance approval has been obtained */
  hasGovernanceApproval: boolean;
  /** Whether the action involves financial transactions */
  involvesFunds: boolean;
  /** Transaction amount (if applicable) */
  amount: number;
  /** Authorized spending limit */
  authorizedLimit: number;
}

/**
 * Zod schema for ActionContext validation
 */
const ActionContextSchema = z.object({
  requiresGovernance: z.boolean(),
  hasGovernanceApproval: z.boolean(),
  involvesFunds: z.boolean(),
  amount: z.number().min(0, 'Amount must be non-negative'),
  authorizedLimit: z.number().min(0, 'Authorized limit must be non-negative')
});

/**
 * Props interface for ComplianceChecker component
 *
 * @example
 * ```typescript
 * <ComplianceChecker
 *   activePolicies={[{ id: "POL-001", name: "Test Policy", rules: [] }]}
 *   onComplianceCheck={(result) => console.log(result)}
 *   className="my-4"
 * />
 * ```
 */
interface ComplianceCheckerProps {
  /**
   * Array of active policies to check against
   * @default Mock policies will be used if not provided
   */
  activePolicies?: ActivePolicy[];
  /**
   * Callback function called when compliance check completes
   * @param result - The compliance check result
   */
  onComplianceCheck?: (result: ComplianceResult) => void;
  /**
   * Additional CSS classes to apply to the component
   * @default ''
   */
  className?: string;
}

/**
 * Zod schema for ComplianceChecker props validation
 */
const ComplianceCheckerPropsSchema = z.object({
  activePolicies: z.array(ActivePolicySchema).optional(),
  onComplianceCheck: z.function()
    .args(ComplianceResultSchema)
    .returns(z.void())
    .optional(),
  className: z.string().optional()
});

/**
 * ComplianceChecker component for validating actions against governance policies
 *
 * This component provides a user interface for checking whether proposed actions
 * comply with active governance policies using the PGC (Prompt Governance Compiler) service.
 *
 * @param props - Component props validated against ComplianceCheckerPropsSchema
 * @returns JSX element wrapped in ServiceErrorBoundary for PGC service
 */
const ComplianceChecker: React.FC<ComplianceCheckerProps> = (props) => {
  // Validate props in development mode
  const validatedProps = validateProps(
    ComplianceCheckerPropsSchema,
    props,
    'ComplianceChecker'
  );

  const {
    activePolicies: propPolicies,
    onComplianceCheck,
    className = ''
  } = validatedProps;
  // Form state
  const [actionToCheck, setActionToCheck] = useState('');
  const [selectedPolicyId, setSelectedPolicyId] = useState('');
  const [actionContext, setActionContext] = useState<ActionContext>({
    requiresGovernance: false,
    hasGovernanceApproval: false,
    involvesFunds: false,
    amount: 0,
    authorizedLimit: 5000,
  });

  // Loading state management
  const [loadingState, loadingActions] = useLoadingState({
    timeout: 30000,
    retryAttempts: 3,
    onTimeout: () => {
      console.warn('PGC compliance check timed out');
    },
    onError: (error) => {
      console.error('PGC compliance check failed:', error);
    }
  });

  // Compliance state
  const [complianceResults, setComplianceResults] = useState<ComplianceResult[]>([]);
  const [activePolicies, setActivePolicies] = useState<ActivePolicy[]>([]);

  // Mock active policies
  const mockActivePolicies: ActivePolicy[] = [
    {
      id: "PC-001",
      name: "No Extrajudicial State Mutation",
      rules: [{ id: "1", condition: "unauthorized_state_mutations", action: "DENY" }]
    },
    {
      id: "GV-001", 
      name: "Democratic Policy Approval",
      rules: [{ id: "2", condition: "policy_changes", action: "REQUIRE governance_approval" }]
    },
    {
      id: "FN-001",
      name: "Treasury Protection", 
      rules: [{ id: "3", condition: "treasury_operations", action: "LIMIT TO authorized_amounts" }]
    }
  ];

  useEffect(() => {
    const policies = propPolicies || mockActivePolicies;
    setActivePolicies(policies);
    if (policies.length > 0) {
      setSelectedPolicyId(policies[0].id);
    }
  }, [propPolicies]);

  const performComplianceCheck = async () => {
    if (!actionToCheck || !selectedPolicyId) {
      alert("Please enter an action and select a policy");
      return;
    }

    loadingActions.startLoading();
    const startTime = Date.now();

    try {
      // Simulate compliance checking delay with progress updates
      const totalSteps = 4;
      for (let step = 1; step <= totalSteps; step++) {
        await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 200));
        loadingActions.setProgress((step / totalSteps) * 100);
      }

      const selectedPolicy = activePolicies.find(p => p.id === selectedPolicyId);
      const processingTime = Date.now() - startTime;

      // Mock compliance logic
      const complianceResult = mockPGCCheck(actionToCheck, actionContext, selectedPolicy);

      const result: ComplianceResult = {
        compliant: complianceResult.compliant,
        confidenceScore: complianceResult.confidence,
        violationReasons: complianceResult.violationReason ? [complianceResult.violationReason] : undefined
      };

      setComplianceResults(prev => [result, ...prev.slice(0, 9)]); // Keep last 10 results

      if (onComplianceCheck) {
        onComplianceCheck(result);
      }

      loadingActions.stopLoading();

    } catch (error) {
      console.error("Compliance check failed:", error);
      loadingActions.setError(error as Error);
    }
  };

  const mockPGCCheck = (action: string, context: ActionContext, policy?: ActivePolicy) => {
    const actionLower = action.toLowerCase();
    
    // PC-001: No unauthorized state mutations
    if (policy?.id === 'PC-001') {
      if (actionLower.includes('unauthorized') || actionLower.includes('bypass')) {
        return { compliant: false, confidence: 95, violationReason: 'Unauthorized state mutation detected' };
      }
    }
    
    // GV-001: Democratic governance
    if (policy?.id === 'GV-001') {
      if (context.requiresGovernance && !context.hasGovernanceApproval) {
        return { compliant: false, confidence: 90, violationReason: 'Governance approval required' };
      }
    }
    
    // FN-001: Treasury protection
    if (policy?.id === 'FN-001') {
      if (context.involvesFunds && context.amount > context.authorizedLimit) {
        return { compliant: false, confidence: 99, violationReason: 'Amount exceeds authorized limit' };
      }
    }
    
    // Default: compliant
    return { compliant: true, confidence: 85, violationReason: undefined };
  };

  const getResultColor = (isCompliant: boolean) => {
    return isCompliant ? 'text-green-600 bg-green-50 border-green-200' : 'text-red-600 bg-red-50 border-red-200';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <ServiceErrorBoundary
      serviceName="PGC"
      serviceUrl={process.env.REACT_APP_PGC_API_URL || 'http://localhost:8005'}
      className={className}
    >
      <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">🔍 PGC Compliance Checker</h2>

      {/* Input Form */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Action to Check
            </label>
            <textarea
              value={actionToCheck}
              onChange={(e) => setActionToCheck(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter the action you want to validate"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Policy to Check Against
            </label>
            <select
              value={selectedPolicyId}
              onChange={(e) => setSelectedPolicyId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {activePolicies.map(policy => (
                <option key={policy.id} value={policy.id}>
                  {policy.id} - {policy.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-sm font-medium text-gray-700">Action Context</h3>
          
          <div className="grid grid-cols-2 gap-3">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={actionContext.requiresGovernance}
                onChange={(e) => setActionContext(prev => ({ ...prev, requiresGovernance: e.target.checked }))}
                className="rounded"
              />
              Requires Governance
            </label>
            
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={actionContext.hasGovernanceApproval}
                onChange={(e) => setActionContext(prev => ({ ...prev, hasGovernanceApproval: e.target.checked }))}
                className="rounded"
              />
              Has Approval
            </label>
            
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={actionContext.involvesFunds}
                onChange={(e) => setActionContext(prev => ({ ...prev, involvesFunds: e.target.checked }))}
                className="rounded"
              />
              Involves Funds
            </label>
          </div>

          {actionContext.involvesFunds && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-600 mb-1">Amount</label>
                <input
                  type="number"
                  value={actionContext.amount}
                  onChange={(e) => setActionContext(prev => ({ ...prev, amount: parseInt(e.target.value) || 0 }))}
                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Authorized Limit</label>
                <input
                  type="number"
                  value={actionContext.authorizedLimit}
                  onChange={(e) => setActionContext(prev => ({ ...prev, authorizedLimit: parseInt(e.target.value) || 0 }))}
                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Button */}
      <div className="mb-6">
        <LoadingButton
          isLoading={loadingState.isLoading}
          onClick={performComplianceCheck}
          disabled={!actionToCheck || !selectedPolicyId}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          loadingText="Checking Compliance..."
        >
          Check Compliance
        </LoadingButton>

        {/* Progress indicator */}
        {loadingState.isLoading && loadingState.progress > 0 && (
          <div className="mt-2">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Processing...</span>
              <span>{Math.round(loadingState.progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${loadingState.progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error display */}
        {loadingState.error && (
          <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-center">
              <svg className="h-4 w-4 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm text-red-700">
                {loadingState.error.message}
              </span>
              <button
                onClick={loadingActions.retry}
                className="ml-auto text-sm text-red-600 hover:text-red-800 underline"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Timeout display */}
        {loadingState.isTimeout && (
          <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <div className="flex items-center">
              <svg className="h-4 w-4 text-yellow-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm text-yellow-700">
                Request timed out. The PGC service may be experiencing issues.
              </span>
              <button
                onClick={() => window.location.reload()}
                className="ml-auto text-sm text-yellow-600 hover:text-yellow-800 underline"
              >
                Refresh
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Compliance Results</h3>
        
        {complianceResults.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No compliance checks performed yet.</p>
            <p className="text-sm mt-1">Enter an action and click "Check Compliance" to begin.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {complianceResults.map((result, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getResultColor(result.compliant)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-lg">
                        {result.compliant ? '✅' : '❌'}
                      </span>
                      <span className="font-semibold">
                        {result.compliant ? 'COMPLIANT' : 'VIOLATION DETECTED'}
                      </span>
                      <span className={`text-sm font-medium ${getConfidenceColor(result.confidenceScore)}`}>
                        {result.confidenceScore}% confidence
                      </span>
                    </div>
                    
                    {result.violationReasons && result.violationReasons.length > 0 && (
                      <div className="text-sm">
                        <strong>Reasons:</strong> {result.violationReasons.join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
    </ServiceErrorBoundary>
  );
};

export default ComplianceChecker;
