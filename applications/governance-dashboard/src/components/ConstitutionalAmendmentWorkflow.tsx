// governance-dashboard/src/components/ConstitutionalAmendmentWorkflow.tsx
// Constitutional Amendment Workflow with GS Engine and PGC Integration

import React, { useState, useEffect } from 'react';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { PublicKey } from '@solana/web3.js';
import { Program, AnchorProvider, BN } from '@coral-xyz/anchor';
import { QuantumagiCore } from '../types/quantumagi_core';
import idl from '../idl/quantumagi_core.json';

interface ConstitutionalPrinciple {
  id: string;
  title: string;
  content: string;
  category: string;
  rationale: string;
  status: 'enacted' | 'proposed' | 'deprecated';
  votes?: {
    for: number;
    against: number;
  };
}

interface AmendmentProposal {
  principleId: string;
  originalContent: string;
  proposedContent: string;
  rationale: string;
  category: string;
  submittedBy: string;
  impactAnalysis?: {
    affectedPolicies: string[];
    complianceRisks: string[];
    validationScore: number;
    gsEngineAnalysis: {
      semanticSimilarity: number;
      conflictDetection: string[];
      synthesisComplexity: 'Low' | 'Medium' | 'High';
    };
  };
  pgcValidation?: {
    isCompliant: boolean;
    confidence: number;
    violationReason?: string;
    processingTime: number;
  };
  votingStatus?: {
    votesFor: number;
    votesAgainst: number;
    votersRequired: number;
    deadline: string;
    status: 'pending' | 'voting' | 'approved' | 'rejected';
  };
}

interface VotingRecord {
  amendmentId: string;
  voter: string;
  vote: 'for' | 'against' | 'abstain';
  timestamp: string;
  blockchainTxId?: string;
}

const ConstitutionalAmendmentWorkflow: React.FC = () => {
  const { connection } = useConnection();
  const { publicKey, sendTransaction } = useWallet();
  const [program, setProgram] = useState<Program<QuantumagiCore> | null>(null);
  
  // Form state
  const [selectedPrinciple, setSelectedPrinciple] = useState<ConstitutionalPrinciple | null>(null);
  const [proposedContent, setProposedContent] = useState('');
  const [amendmentRationale, setAmendmentRationale] = useState('');
  
  // Workflow state
  const [currentStep, setCurrentStep] = useState<'select' | 'propose' | 'analyze' | 'validate' | 'vote'>('select');
  const [processing, setProcessing] = useState(false);
  const [amendment, setAmendment] = useState<AmendmentProposal | null>(null);
  const [votingRecords, setVotingRecords] = useState<VotingRecord[]>([]);
  
  // Data state
  const [principles, setPrinciples] = useState<ConstitutionalPrinciple[]>([]);
  const [activeAmendments, setActiveAmendments] = useState<AmendmentProposal[]>([]);

  // Mock constitutional principles
  const mockPrinciples: ConstitutionalPrinciple[] = [
    {
      id: "PC-001",
      title: "No Extrajudicial State Mutation",
      content: "AI systems must not perform unauthorized state mutations without proper governance approval. All state changes must be validated through the constitutional framework.",
      category: "Prompt Constitution",
      rationale: "Prevents unauthorized changes to critical system state that could compromise governance integrity.",
      status: "enacted",
      votes: { for: 15, against: 2 }
    },
    {
      id: "GV-001", 
      title: "Democratic Policy Approval",
      content: "All governance policies must be approved through democratic voting process with transparent community participation and adequate deliberation time.",
      category: "Governance",
      rationale: "Ensures community participation and prevents authoritarian policy implementation.",
      status: "enacted",
      votes: { for: 18, against: 1 }
    },
    {
      id: "FN-001",
      title: "Treasury Protection",
      content: "Financial operations exceeding predefined limits require multi-signature approval from elected treasury guardians with public audit trails.",
      category: "Financial",
      rationale: "Protects community treasury from unauthorized access and ensures financial transparency.",
      status: "proposed",
      votes: { for: 12, against: 5 }
    }
  ];

  useEffect(() => {
    initializeProgram();
    loadPrinciples();
    loadActiveAmendments();
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

  const loadPrinciples = async () => {
    try {
      // In production, this would fetch from Solana program accounts
      await new Promise(resolve => setTimeout(resolve, 1000));
      setPrinciples(mockPrinciples);
    } catch (error) {
      console.error("Failed to load principles:", error);
    }
  };

  const loadActiveAmendments = async () => {
    try {
      // Mock active amendments
      const mockAmendments: AmendmentProposal[] = [
        {
          principleId: "PC-001",
          originalContent: mockPrinciples[0].content,
          proposedContent: "AI systems must not perform unauthorized state mutations without proper governance approval. All state changes must be validated through the constitutional framework and include mandatory audit trails for accountability.",
          rationale: "Adding audit trail requirements to enhance transparency and accountability.",
          category: "Prompt Constitution",
          submittedBy: publicKey?.toString() || "Unknown",
          votingStatus: {
            votesFor: 8,
            votesAgainst: 3,
            votersRequired: 15,
            deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'voting'
          }
        }
      ];
      setActiveAmendments(mockAmendments);
    } catch (error) {
      console.error("Failed to load active amendments:", error);
    }
  };

  const handlePrincipleSelect = (principle: ConstitutionalPrinciple) => {
    setSelectedPrinciple(principle);
    setProposedContent(principle.content);
    setCurrentStep('propose');
  };

  const handleGSEngineAnalysis = async (): Promise<AmendmentProposal['impactAnalysis']> => {
    console.log("🧠 Initiating GS Engine impact analysis...");
    
    // Simulate GS Engine multi-model analysis
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    return {
      affectedPolicies: [
        "Policy-Auth-001: User Authentication Protocol",
        "Policy-Data-003: Data Mutation Guidelines",
        "Policy-Audit-002: System Audit Requirements"
      ],
      complianceRisks: [
        "Medium risk: May require updates to existing audit systems",
        "Low risk: Compatible with current authentication frameworks"
      ],
      validationScore: Math.random() * 0.15 + 0.85, // 85-100%
      gsEngineAnalysis: {
        semanticSimilarity: Math.random() * 0.2 + 0.8, // 80-100%
        conflictDetection: ["No conflicts detected with existing principles"],
        synthesisComplexity: Math.random() > 0.7 ? 'High' : Math.random() > 0.4 ? 'Medium' : 'Low'
      }
    };
  };

  const handlePGCValidation = async (): Promise<AmendmentProposal['pgcValidation']> => {
    console.log("🔍 Running PGC compliance validation...");
    
    const startTime = Date.now();
    
    // Simulate PGC real-time compliance checking
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const processingTime = Date.now() - startTime;
    
    // Mock compliance validation based on content analysis
    const isCompliant = !proposedContent.includes('unauthorized') && 
                       proposedContent.includes('governance approval');
    
    return {
      isCompliant,
      confidence: Math.random() * 0.1 + 0.9, // 90-100%
      violationReason: isCompliant ? undefined : 'Potential governance bypass detected',
      processingTime
    };
  };

  const handleSubmitAmendment = async () => {
    if (!selectedPrinciple || !proposedContent || !amendmentRationale) {
      alert("Please complete all required fields");
      return;
    }

    setProcessing(true);
    setCurrentStep('analyze');

    try {
      // Step 1: GS Engine Impact Analysis
      console.log("📊 Step 1: Running GS Engine impact analysis...");
      const impactAnalysis = await handleGSEngineAnalysis();
      
      setCurrentStep('validate');
      
      // Step 2: PGC Compliance Validation
      console.log("🔍 Step 2: Running PGC compliance validation...");
      const pgcValidation = await handlePGCValidation();
      
      // Step 3: Create Amendment Proposal
      const newAmendment: AmendmentProposal = {
        principleId: selectedPrinciple.id,
        originalContent: selectedPrinciple.content,
        proposedContent,
        rationale: amendmentRationale,
        category: selectedPrinciple.category,
        submittedBy: publicKey?.toString() || "Unknown",
        impactAnalysis,
        pgcValidation,
        votingStatus: {
          votesFor: 0,
          votesAgainst: 0,
          votersRequired: 15, // Configurable governance parameter
          deadline: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(), // 14 days
          status: pgcValidation.isCompliant ? 'voting' : 'pending'
        }
      };

      setAmendment(newAmendment);
      setCurrentStep('vote');
      
      console.log("✅ Amendment proposal created successfully");
      
    } catch (error) {
      console.error("Amendment submission failed:", error);
      alert("Failed to submit amendment. Please try again.");
    } finally {
      setProcessing(false);
    }
  };

  const handleVote = async (vote: 'for' | 'against' | 'abstain', amendmentId: string) => {
    if (!program || !publicKey) {
      alert("Please connect your wallet first");
      return;
    }

    setProcessing(true);

    try {
      console.log(`📊 Casting ${vote} vote for amendment ${amendmentId}...`);
      
      // In production, this would call the actual Solana program
      const voteId = new BN(Date.now());
      
      // Simulate blockchain transaction
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const voteRecord: VotingRecord = {
        amendmentId,
        voter: publicKey.toString(),
        vote,
        timestamp: new Date().toISOString(),
        blockchainTxId: `tx_${Date.now()}`
      };
      
      setVotingRecords(prev => [...prev, voteRecord]);
      
      // Update amendment voting status
      setActiveAmendments(prev => 
        prev.map(amendment => {
          if (amendment.principleId === amendmentId) {
            const newVotingStatus = { ...amendment.votingStatus! };
            if (vote === 'for') newVotingStatus.votesFor += 1;
            if (vote === 'against') newVotingStatus.votesAgainst += 1;
            
            // Check if voting is complete
            const totalVotes = newVotingStatus.votesFor + newVotingStatus.votesAgainst;
            if (totalVotes >= newVotingStatus.votersRequired) {
              newVotingStatus.status = newVotingStatus.votesFor > newVotingStatus.votesAgainst ? 'approved' : 'rejected';
            }
            
            return { ...amendment, votingStatus: newVotingStatus };
          }
          return amendment;
        })
      );
      
      alert(`Vote cast successfully! Transaction ID: ${voteRecord.blockchainTxId}`);
      
    } catch (error) {
      console.error("Voting failed:", error);
      alert("Failed to cast vote. Please try again.");
    } finally {
      setProcessing(false);
    }
  };

  const getStepStatus = (step: string) => {
    const steps = ['select', 'propose', 'analyze', 'validate', 'vote'];
    const currentIndex = steps.indexOf(currentStep);
    const stepIndex = steps.indexOf(step);
    
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  const resetWorkflow = () => {
    setSelectedPrinciple(null);
    setProposedContent('');
    setAmendmentRationale('');
    setAmendment(null);
    setCurrentStep('select');
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">⚖️ Constitutional Amendment Workflow</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Step {['select', 'propose', 'analyze', 'validate', 'vote'].indexOf(currentStep) + 1} of 5</span>
          <button
            onClick={resetWorkflow}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center justify-between mb-8">
        {[
          { id: 'select', label: 'Select Principle', icon: '📋' },
          { id: 'propose', label: 'Propose Amendment', icon: '✏️' },
          { id: 'analyze', label: 'GS Analysis', icon: '🧠' },
          { id: 'validate', label: 'PGC Validation', icon: '🔍' },
          { id: 'vote', label: 'Democratic Vote', icon: '🗳️' }
        ].map((step, index) => (
          <div key={step.id} className="flex items-center">
            <div className={`flex items-center justify-center w-10 h-10 rounded-full text-sm font-medium ${
              getStepStatus(step.id) === 'completed' ? 'bg-green-600 text-white' :
              getStepStatus(step.id) === 'active' ? 'bg-blue-600 text-white' :
              'bg-gray-200 text-gray-600'
            }`}>
              {getStepStatus(step.id) === 'completed' ? '✓' : step.icon}
            </div>
            <div className="ml-2 hidden sm:block">
              <div className={`text-sm font-medium ${
                getStepStatus(step.id) === 'active' ? 'text-blue-600' : 'text-gray-600'
              }`}>
                {step.label}
              </div>
            </div>
            {index < 4 && (
              <div className={`flex-1 h-0.5 mx-4 ${
                getStepStatus(step.id) === 'completed' ? 'bg-green-600' : 'bg-gray-200'
              }`}></div>
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Select Principle */}
      {currentStep === 'select' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Select Constitutional Principle to Amend</h3>
          <div className="grid gap-4">
            {principles.map((principle) => (
              <div
                key={principle.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 cursor-pointer transition-colors"
                onClick={() => handlePrincipleSelect(principle)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-semibold text-gray-700">{principle.id}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      principle.status === 'enacted' ? 'bg-green-100 text-green-800' :
                      principle.status === 'proposed' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {principle.status.toUpperCase()}
                    </span>
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      {principle.category}
                    </span>
                  </div>
                </div>
                <h4 className="font-medium text-gray-900 mb-2">{principle.title}</h4>
                <p className="text-sm text-gray-600 mb-2">{principle.content}</p>
                {principle.votes && (
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="text-green-600">👍 {principle.votes.for}</span>
                    <span className="text-red-600">👎 {principle.votes.against}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Step 2: Propose Amendment */}
      {currentStep === 'propose' && selectedPrinciple && (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Propose Amendment</h3>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-mono text-sm font-semibold text-gray-700">{selectedPrinciple.id}</span>
                <span className="text-sm font-medium text-gray-900">{selectedPrinciple.title}</span>
              </div>
              <div className="text-sm text-gray-600">
                <strong>Original:</strong> {selectedPrinciple.content}
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Proposed Amendment Content
            </label>
            <textarea
              value={proposedContent}
              onChange={(e) => setProposedContent(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your proposed changes to this constitutional principle..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Amendment Rationale
            </label>
            <textarea
              value={amendmentRationale}
              onChange={(e) => setAmendmentRationale(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Explain why this amendment is necessary and beneficial..."
            />
          </div>

          <div className="flex justify-between">
            <button
              onClick={() => setCurrentStep('select')}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Back
            </button>
            <button
              onClick={handleSubmitAmendment}
              disabled={!proposedContent || !amendmentRationale || processing}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Submit for Analysis
            </button>
          </div>
        </div>
      )}

      {/* Step 3: GS Engine Analysis */}
      {currentStep === 'analyze' && processing && (
        <div className="space-y-6">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🧠 GS Engine Impact Analysis</h3>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <div className="space-y-2 text-sm text-gray-600">
              <p>• Analyzing semantic consistency with existing principles...</p>
              <p>• Identifying affected policies and potential conflicts...</p>
              <p>• Calculating implementation complexity score...</p>
              <p>• Running multi-model validation consensus...</p>
            </div>
          </div>
        </div>
      )}

      {/* Step 4: PGC Validation */}
      {currentStep === 'validate' && processing && (
        <div className="space-y-6">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🔍 PGC Compliance Validation</h3>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
            <div className="space-y-2 text-sm text-gray-600">
              <p>• Checking compliance with constitutional framework...</p>
              <p>• Validating governance approval requirements...</p>
              <p>• Detecting potential constitutional violations...</p>
              <p>• Generating compliance confidence score...</p>
            </div>
          </div>
        </div>
      )}

      {/* Step 5: Voting Interface */}
      {currentStep === 'vote' && amendment && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-900">🗳️ Democratic Amendment Voting</h3>
          
          {/* Amendment Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2">Amendment Summary</h4>
            <div className="space-y-2 text-sm">
              <div><strong>Principle:</strong> {selectedPrinciple?.id} - {selectedPrinciple?.title}</div>
              <div><strong>Category:</strong> {amendment.category}</div>
              <div><strong>Submitted by:</strong> {amendment.submittedBy.substring(0, 8)}...</div>
            </div>
          </div>

          {/* Analysis Results */}
          {amendment.impactAnalysis && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">🧠 GS Engine Analysis Results</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <strong>Validation Score:</strong> {(amendment.impactAnalysis.validationScore * 100).toFixed(1)}%
                </div>
                <div>
                  <strong>Synthesis Complexity:</strong> {amendment.impactAnalysis.gsEngineAnalysis.synthesisComplexity}
                </div>
              </div>
              <div className="mt-3">
                <strong>Affected Policies:</strong>
                <ul className="list-disc list-inside mt-1 text-sm text-gray-600">
                  {amendment.impactAnalysis.affectedPolicies.map((policy, index) => (
                    <li key={index}>{policy}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* PGC Validation Results */}
          {amendment.pgcValidation && (
            <div className={`border rounded-lg p-4 ${
              amendment.pgcValidation.isCompliant 
                ? 'bg-green-50 border-green-200' 
                : 'bg-red-50 border-red-200'
            }`}>
              <h4 className="font-medium mb-3">🔍 PGC Compliance Validation</h4>
              <div className="flex items-center gap-2 text-sm">
                <span className={`font-semibold ${
                  amendment.pgcValidation.isCompliant ? 'text-green-600' : 'text-red-600'
                }`}>
                  {amendment.pgcValidation.isCompliant ? '✅ COMPLIANT' : '❌ NON-COMPLIANT'}
                </span>
                <span className="text-gray-600">
                  ({(amendment.pgcValidation.confidence * 100).toFixed(1)}% confidence)
                </span>
              </div>
              {amendment.pgcValidation.violationReason && (
                <p className="text-sm text-red-600 mt-2">
                  <strong>Issue:</strong> {amendment.pgcValidation.violationReason}
                </p>
              )}
            </div>
          )}

          {/* Voting Interface */}
          {amendment.votingStatus && amendment.pgcValidation?.isCompliant && (
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-medium text-gray-900">Cast Your Vote</h4>
                <div className="text-sm text-gray-500">
                  Deadline: {new Date(amendment.votingStatus.deadline).toLocaleDateString()}
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{amendment.votingStatus.votesFor}</div>
                  <div className="text-sm text-gray-600">For</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{amendment.votingStatus.votesAgainst}</div>
                  <div className="text-sm text-gray-600">Against</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-600">{amendment.votingStatus.votersRequired}</div>
                  <div className="text-sm text-gray-600">Required</div>
                </div>
              </div>

              {amendment.votingStatus.status === 'voting' && (
                <div className="flex gap-3">
                  <button
                    onClick={() => handleVote('for', amendment.principleId)}
                    disabled={processing}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400"
                  >
                    Vote For
                  </button>
                  <button
                    onClick={() => handleVote('against', amendment.principleId)}
                    disabled={processing}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400"
                  >
                    Vote Against
                  </button>
                  <button
                    onClick={() => handleVote('abstain', amendment.principleId)}
                    disabled={processing}
                    className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:bg-gray-400"
                  >
                    Abstain
                  </button>
                </div>
              )}

              {amendment.votingStatus.status !== 'voting' && (
                <div className={`text-center py-4 rounded-md ${
                  amendment.votingStatus.status === 'approved' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  <strong>
                    {amendment.votingStatus.status === 'approved' ? '✅ Amendment Approved' : '❌ Amendment Rejected'}
                  </strong>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Active Amendments List */}
      {activeAmendments.length > 0 && (
        <div className="mt-8 border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Constitutional Amendments</h3>
          <div className="space-y-4">
            {activeAmendments.map((amendment, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-medium text-gray-900">
                      Amendment to {amendment.principleId}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {amendment.rationale}
                    </div>
                    {amendment.votingStatus && (
                      <div className="flex items-center gap-4 mt-2 text-sm">
                        <span className="text-green-600">👍 {amendment.votingStatus.votesFor}</span>
                        <span className="text-red-600">👎 {amendment.votingStatus.votesAgainst}</span>
                        <span className="text-gray-500">
                          Status: {amendment.votingStatus.status.toUpperCase()}
                        </span>
                      </div>
                    )}
                  </div>
                  {amendment.votingStatus?.status === 'voting' && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleVote('for', amendment.principleId)}
                        className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                      >
                        Vote For
                      </button>
                      <button
                        onClick={() => handleVote('against', amendment.principleId)}
                        className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        Vote Against
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConstitutionalAmendmentWorkflow;