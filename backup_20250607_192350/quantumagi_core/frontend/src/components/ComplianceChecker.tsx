// frontend/src/components/ComplianceChecker.tsx
// Real-time PGC Compliance Validation Interface

import React, { useState, useEffect } from 'react';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { PublicKey } from '@solana/web3.js';
import { Program, AnchorProvider, BN } from '@coral-xyz/anchor';
import { QuantumagiCore } from '../types/quantumagi_core';
import idl from '../idl/quantumagi_core.json';

interface ComplianceResult {
  isCompliant: boolean;
  confidence: number;
  violationReason?: string;
  policyId: string;
  policyTitle: string;
  processingTime: number;
  timestamp: string;
}

interface ActivePolicy {
  id: string;
  title: string;
  rule: string;
  category: string;
  isActive: boolean;
}

const ComplianceChecker: React.FC = () => {
  const { connection } = useConnection();
  const { publicKey } = useWallet();
  const [program, setProgram] = useState<Program<QuantumagiCore> | null>(null);
  
  // Form state
  const [actionToCheck, setActionToCheck] = useState('');
  const [selectedPolicyId, setSelectedPolicyId] = useState('');
  const [actionContext, setActionContext] = useState({
    requiresGovernance: false,
    hasGovernanceApproval: false,
    involvesFunds: false,
    amount: 0,
    authorizedLimit: 5000,
  });

  // Compliance state
  const [checking, setChecking] = useState(false);
  const [complianceResults, setComplianceResults] = useState<ComplianceResult[]>([]);
  const [activePolicies, setActivePolicies] = useState<ActivePolicy[]>([]);
  const [realTimeMode, setRealTimeMode] = useState(false);

  // Mock active policies
  const mockActivePolicies: ActivePolicy[] = [
    {
      id: "PC-001",
      title: "No Extrajudicial State Mutation",
      rule: "DENY unauthorized_state_mutations WITHOUT governance_approval",
      category: "Prompt Constitution",
      isActive: true
    },
    {
      id: "GV-001",
      title: "Democratic Policy Approval", 
      rule: "REQUIRE governance_approval FOR policy_changes",
      category: "Governance",
      isActive: true
    },
    {
      id: "FN-001",
      title: "Treasury Protection",
      rule: "LIMIT treasury_operations TO authorized_amounts AND REQUIRE multi_sig_approval",
      category: "Financial",
      isActive: true
    },
    {
      id: "SF-001",
      title: "Safety-First AI Operations",
      rule: "REQUIRE safety_validation BEFORE ai_system_deployment",
      category: "Safety",
      isActive: true
    }
  ];

  // Predefined test scenarios
  const testScenarios = [
    {
      name: "Authorized Treasury Transfer",
      action: "treasury_transfer_with_authorization",
      context: { requiresGovernance: false, hasGovernanceApproval: true, involvesFunds: true, amount: 1000, authorizedLimit: 5000 },
      expectedResult: "PASS"
    },
    {
      name: "Unauthorized State Mutation",
      action: "unauthorized_state_mutation_bypass",
      context: { requiresGovernance: true, hasGovernanceApproval: false, involvesFunds: false, amount: 0, authorizedLimit: 0 },
      expectedResult: "FAIL"
    },
    {
      name: "Excessive Treasury Withdrawal",
      action: "treasury_withdrawal_excessive_amount",
      context: { requiresGovernance: false, hasGovernanceApproval: false, involvesFunds: true, amount: 10000, authorizedLimit: 5000 },
      expectedResult: "FAIL"
    },
    {
      name: "Governance Decision with Approval",
      action: "governance_decision_with_proper_voting",
      context: { requiresGovernance: true, hasGovernanceApproval: true, involvesFunds: false, amount: 0, authorizedLimit: 0 },
      expectedResult: "PASS"
    }
  ];

  useEffect(() => {
    initializeProgram();
    loadActivePolicies();
  }, [publicKey, connection]);

  const initializeProgram = async () => {
    if (!publicKey) return;

    try {
      const provider = new AnchorProvider(
        connection,
        window.solana,
        AnchorProvider.defaultOptions()
      );
      
      const programId = new PublicKey("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");
      const program = new Program(idl as any, programId, provider) as Program<QuantumagiCore>;
      
      setProgram(program);
    } catch (error) {
      console.error("Failed to initialize program:", error);
    }
  };

  const loadActivePolicies = async () => {
    try {
      // In production, this would fetch from Solana program accounts
      setActivePolicies(mockActivePolicies);
      if (mockActivePolicies.length > 0) {
        setSelectedPolicyId(mockActivePolicies[0].id);
      }
    } catch (error) {
      console.error("Failed to load active policies:", error);
    }
  };

  const performComplianceCheck = async (action?: string, context?: any, policyId?: string) => {
    const actionText = action || actionToCheck;
    const contextData = context || actionContext;
    const targetPolicyId = policyId || selectedPolicyId;

    if (!actionText || !targetPolicyId) {
      alert("Please enter an action and select a policy");
      return;
    }

    setChecking(true);
    const startTime = Date.now();

    try {
      console.log(`🔍 Checking compliance for: "${actionText}"`);
      console.log(`📋 Against policy: ${targetPolicyId}`);
      
      // Simulate PGC compliance checking
      await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
      
      const selectedPolicy = activePolicies.find(p => p.id === targetPolicyId);
      const processingTime = Date.now() - startTime;
      
      // Mock compliance logic based on policy rules and action context
      const complianceResult = mockPGCCheck(actionText, contextData, selectedPolicy);
      
      const result: ComplianceResult = {
        isCompliant: complianceResult.isCompliant,
        confidence: complianceResult.confidence,
        violationReason: complianceResult.violationReason,
        policyId: targetPolicyId,
        policyTitle: selectedPolicy?.title || 'Unknown Policy',
        processingTime,
        timestamp: new Date().toISOString()
      };

      setComplianceResults(prev => [result, ...prev.slice(0, 9)]); // Keep last 10 results
      
      console.log(`${result.isCompliant ? '✅ COMPLIANT' : '❌ VIOLATION'} - ${result.confidence}% confidence`);
      
    } catch (error) {
      console.error("Compliance check failed:", error);
      alert("Compliance check failed. Please try again.");
    } finally {
      setChecking(false);
    }
  };

  const mockPGCCheck = (action: string, context: any, policy?: ActivePolicy) => {
    const actionLower = action.toLowerCase();
    
    // PC-001: No unauthorized state mutations
    if (policy?.id === 'PC-001') {
      if (actionLower.includes('unauthorized') || actionLower.includes('bypass')) {
        return { isCompliant: false, confidence: 95, violationReason: 'Unauthorized state mutation detected' };
      }
    }
    
    // GV-001: Democratic governance
    if (policy?.id === 'GV-001') {
      if (context.requiresGovernance && !context.hasGovernanceApproval) {
        return { isCompliant: false, confidence: 90, violationReason: 'Governance approval required' };
      }
    }
    
    // FN-001: Treasury protection
    if (policy?.id === 'FN-001') {
      if (context.involvesFunds && context.amount > context.authorizedLimit) {
        return { isCompliant: false, confidence: 99, violationReason: 'Amount exceeds authorized limit' };
      }
    }
    
    // SF-001: Safety validation
    if (policy?.id === 'SF-001') {
      if (actionLower.includes('unsafe') || actionLower.includes('deploy') && !actionLower.includes('validated')) {
        return { isCompliant: false, confidence: 98, violationReason: 'Safety validation required' };
      }
    }
    
    // Default: compliant
    return { isCompliant: true, confidence: 85, violationReason: undefined };
  };

  const runTestScenario = async (scenario: any) => {
    setActionToCheck(scenario.action);
    setActionContext(scenario.context);
    await performComplianceCheck(scenario.action, scenario.context, selectedPolicyId);
  };

  const runAllTests = async () => {
    for (const scenario of testScenarios) {
      await performComplianceCheck(scenario.action, scenario.context, selectedPolicyId);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Delay between tests
    }
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
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">🔍 PGC Compliance Checker</h2>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={realTimeMode}
              onChange={(e) => setRealTimeMode(e.target.checked)}
              className="rounded"
            />
            Real-time Mode
          </label>
        </div>
      </div>

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
              placeholder="Enter the action you want to validate (e.g., 'treasury_transfer_with_authorization')"
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
                  {policy.id} - {policy.title}
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

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={() => performComplianceCheck()}
          disabled={checking || !actionToCheck || !selectedPolicyId}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {checking && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
          {checking ? 'Checking...' : 'Check Compliance'}
        </button>

        <button
          onClick={runAllTests}
          disabled={checking}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400"
        >
          Run All Tests
        </button>

        {testScenarios.map((scenario, index) => (
          <button
            key={index}
            onClick={() => runTestScenario(scenario)}
            disabled={checking}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:bg-gray-50"
          >
            {scenario.name}
          </button>
        ))}
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
                className={`border rounded-lg p-4 ${getResultColor(result.isCompliant)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-lg">
                        {result.isCompliant ? '✅' : '❌'}
                      </span>
                      <span className="font-semibold">
                        {result.isCompliant ? 'COMPLIANT' : 'VIOLATION DETECTED'}
                      </span>
                      <span className={`text-sm font-medium ${getConfidenceColor(result.confidence)}`}>
                        {result.confidence}% confidence
                      </span>
                    </div>
                    
                    <div className="text-sm space-y-1">
                      <div><strong>Policy:</strong> {result.policyId} - {result.policyTitle}</div>
                      {result.violationReason && (
                        <div><strong>Reason:</strong> {result.violationReason}</div>
                      )}
                      <div className="flex gap-4 text-xs text-gray-600">
                        <span>Processing: {result.processingTime}ms</span>
                        <span>Time: {new Date(result.timestamp).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ComplianceChecker;
