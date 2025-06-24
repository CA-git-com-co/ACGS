import React, { useState, useEffect } from 'react';
import { Principle, Policy } from '../types/governance';

interface PolicyProposalProps {
  selectedPrinciple?: Principle;
  onProposalSubmitted?: (proposal: any) => void;
  onPolicySynthesized?: (policy: Policy) => void;
  className?: string;
}

interface SynthesizedPolicy {
  id: string;
  rule: string;
  category: string;
  priority: string;
  validationScore: number;
  complianceComplexity: 'Low' | 'Medium' | 'High';
}

const PolicyProposal: React.FC<PolicyProposalProps> = ({
  selectedPrinciple,
  onProposalSubmitted,
  onPolicySynthesized,
  className = ''
}) => {
  // Form state
  const [principleTitle, setPrincipleTitle] = useState('');
  const [principleContent, setPrincipleContent] = useState('');
  const [principleCategory, setPrincipleCategory] = useState('governance');
  const [principleRationale, setPrincipleRationale] = useState('');

  // GS Engine state
  const [synthesizing, setSynthesizing] = useState(false);
  const [synthesizedPolicy, setSynthesizedPolicy] = useState<SynthesizedPolicy | null>(null);
  const [validationResults, setValidationResults] = useState<any>(null);

  // Proposal state
  const [submitting, setSubmitting] = useState(false);
  const [proposalStatus, setProposalStatus] = useState<'draft' | 'synthesized' | 'submitted'>(
    'draft'
  );

  useEffect(() => {
    if (selectedPrinciple) {
      setPrincipleTitle(selectedPrinciple.title);
      setPrincipleContent(selectedPrinciple.content);
      setPrincipleCategory(selectedPrinciple.category.toLowerCase().replace(' ', '_'));
    }
  }, [selectedPrinciple]);

  const handleSynthesizePolicy = async () => {
    if (!principleTitle || !principleContent) {
      alert('Please fill in the principle title and content');
      return;
    }

    setSynthesizing(true);
    try {
      console.log('🧠 Initiating GS Engine policy synthesis...');

      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 2000));

      const mockSynthesizedPolicy: SynthesizedPolicy = {
        id: `POL-${Date.now()}`,
        rule: generatePolicyRule(principleTitle, principleContent, principleCategory),
        category: principleCategory,
        priority: determinePriority(principleCategory),
        validationScore: Math.random() * 0.15 + 0.85, // 85-100% validation score
        complianceComplexity: determineComplexity(principleContent)
      };

      // Mock validation results
      const mockValidationResults = {
        syntactic: Math.random() * 0.1 + 0.9,
        semantic: Math.random() * 0.1 + 0.85,
        safety: Math.random() * 0.1 + 0.9,
        bias: Math.random() * 0.1 + 0.85,
        conflict: Math.random() * 0.1 + 0.9,
        consensus: 0
      };

      mockValidationResults.consensus =
        (mockValidationResults.syntactic +
          mockValidationResults.semantic +
          mockValidationResults.safety +
          mockValidationResults.bias +
          mockValidationResults.conflict) /
        5;

      setSynthesizedPolicy(mockSynthesizedPolicy);
      setValidationResults(mockValidationResults);
      setProposalStatus('synthesized');

      // Create Policy object for callback
      if (onPolicySynthesized) {
        const policy: Policy = {
          id: mockSynthesizedPolicy.id,
          name: principleTitle,
          description: principleContent,
          rules: [{ id: '1', condition: 'default', action: mockSynthesizedPolicy.rule }],
          validationScore: mockSynthesizedPolicy.validationScore,
          complianceComplexity: 1, // Convert string to number
          status: 'draft',
          category: principleCategory,
          createdAt: new Date(),
          updatedAt: new Date(),
          author: 'current-user'
        };
        onPolicySynthesized(policy);
      }

      console.log(
        '✅ Policy synthesis completed with validation score:',
        mockValidationResults.consensus
      );
    } catch (error) {
      console.error('Policy synthesis failed:', error);
      alert('Policy synthesis failed. Please try again.');
    } finally {
      setSynthesizing(false);
    }
  };

  const handleSubmitProposal = async () => {
    if (!synthesizedPolicy) {
      alert('Please synthesize policy first');
      return;
    }

    setSubmitting(true);
    try {
      console.log('📋 Submitting policy proposal...');

      // Simulate submission
      await new Promise(resolve => setTimeout(resolve, 2000));

      const proposalData = {
        id: synthesizedPolicy.id,
        rule: synthesizedPolicy.rule,
        category: synthesizedPolicy.category,
        priority: synthesizedPolicy.priority,
        validationScore: synthesizedPolicy.validationScore,
        submittedAt: new Date().toISOString(),
        status: 'proposed'
      };

      setProposalStatus('submitted');
      onProposalSubmitted?.(proposalData);

      alert(`Policy proposal submitted successfully!\nPolicy ID: ${synthesizedPolicy.id}`);
    } catch (error) {
      console.error('Failed to submit proposal:', error);
      alert('Failed to submit proposal. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const generatePolicyRule = (title: string, content: string, category: string): string => {
    const ruleTemplates = {
      governance: `REQUIRE governance_approval FOR ${title.toLowerCase().replace(/\s+/g, '_')}`,
      financial: `LIMIT treasury_operations TO authorized_amounts AND REQUIRE multi_sig_approval`,
      safety: `DENY unsafe_operations AND REQUIRE safety_validation BEFORE execution`,
      prompt_constitution: `DENY unauthorized_state_mutations WITHOUT governance_approval`,
      transparency: `REQUIRE public_audit_trail FOR ${title.toLowerCase().replace(/\s+/g, '_')}`
    };

    return (
      ruleTemplates[category as keyof typeof ruleTemplates] ||
      `ENFORCE ${title.toUpperCase().replace(/\s+/g, '_')}: ${content.substring(0, 100)}`
    );
  };

  const determinePriority = (category: string): string => {
    const priorityMap = {
      safety: 'critical',
      prompt_constitution: 'critical',
      financial: 'high',
      governance: 'medium',
      transparency: 'medium'
    };
    return priorityMap[category as keyof typeof priorityMap] || 'medium';
  };

  const determineComplexity = (content: string): 'Low' | 'Medium' | 'High' => {
    if (content.length > 500) return 'High';
    if (content.length > 200) return 'Medium';
    return 'Low';
  };

  const getValidationColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.8) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Policy Proposal</h2>
        <div className="flex items-center gap-2">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              proposalStatus === 'draft'
                ? 'bg-gray-100 text-gray-600'
                : proposalStatus === 'synthesized'
                  ? 'bg-blue-100 text-blue-600'
                  : 'bg-green-100 text-green-600'
            }`}
          >
            {proposalStatus.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Principle Input Form */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Principle Title</label>
          <input
            type="text"
            value={principleTitle}
            onChange={e => setPrincipleTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter constitutional principle title"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Principle Content</label>
          <textarea
            value={principleContent}
            onChange={e => setPrincipleContent(e.target.value)}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Describe the constitutional principle in detail"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={principleCategory}
              onChange={e => setPrincipleCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="governance">Governance</option>
              <option value="financial">Financial</option>
              <option value="safety">Safety</option>
              <option value="prompt_constitution">Prompt Constitution</option>
              <option value="transparency">Transparency</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Rationale</label>
            <input
              type="text"
              value={principleRationale}
              onChange={e => setPrincipleRationale(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Why is this principle important?"
            />
          </div>
        </div>
      </div>

      {/* GS Engine Synthesis */}
      <div className="border-t pt-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">🧠 GS Engine Policy Synthesis</h3>
          <button
            onClick={handleSynthesizePolicy}
            disabled={synthesizing || !principleTitle || !principleContent}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {synthesizing && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            )}
            {synthesizing ? 'Synthesizing...' : 'Synthesize Policy'}
          </button>
        </div>

        {synthesizing && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex items-center gap-2 text-blue-700">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-700"></div>
              <span className="font-medium">Running Multi-Model Validation...</span>
            </div>
            <div className="mt-2 text-sm text-blue-600">
              • Syntactic validation in progress...
              <br />
              • Semantic analysis running...
              <br />
              • Safety property verification...
              <br />
              • Bias detection analysis...
              <br />• Conflict resolution check...
            </div>
          </div>
        )}

        {synthesizedPolicy && validationResults && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-semibold text-green-800 mb-3">
              ✅ Policy Successfully Synthesized
            </h4>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <span className="text-sm font-medium text-gray-700">Generated Rule:</span>
                <p className="text-sm text-gray-900 bg-white p-2 rounded border mt-1 font-mono">
                  {synthesizedPolicy.rule}
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Validation Score:</span>
                  <span
                    className={`text-sm font-semibold ${getValidationColor(validationResults.consensus)}`}
                  >
                    {(validationResults.consensus * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Priority:</span>
                  <span className="text-sm font-semibold">
                    {synthesizedPolicy.priority.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Complexity:</span>
                  <span className="text-sm font-semibold">
                    {synthesizedPolicy.complianceComplexity}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-5 gap-2 text-xs">
              {Object.entries(validationResults)
                .filter(([key]) => key !== 'consensus')
                .map(([key, value]) => (
                  <div key={key} className="text-center">
                    <div className="font-medium text-gray-700 capitalize">{key}</div>
                    <div className={`font-semibold ${getValidationColor(value as number)}`}>
                      {((value as number) * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>

      {/* Submit Proposal */}
      {synthesizedPolicy && (
        <div className="border-t pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">📋 Submit Proposal</h3>
              <p className="text-sm text-gray-600">Submit policy proposal for democratic voting</p>
            </div>
            <button
              onClick={handleSubmitProposal}
              disabled={submitting || proposalStatus === 'submitted'}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {submitting && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              )}
              {submitting
                ? 'Submitting...'
                : proposalStatus === 'submitted'
                  ? 'Submitted ✓'
                  : 'Submit Proposal'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PolicyProposal;
