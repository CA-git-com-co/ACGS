// frontend/src/components/PrinciplesList.tsx
// Constitutional Principles Display and Management Component

import React, { useState, useEffect } from 'react';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { PublicKey } from '@solana/web3.js';
import { Program, AnchorProvider, web3 } from '@coral-xyz/anchor';
import { QuantumagiCore } from '../types/quantumagi_core';
import idl from '../idl/quantumagi_core.json';

interface ConstitutionalPrinciple {
  id: string;
  title: string;
  content: string;
  category: string;
  rationale: string;
  status: 'draft' | 'proposed' | 'enacted' | 'deprecated';
  votes?: {
    for: number;
    against: number;
  };
}

interface PrinciplesListProps {
  onPrincipleSelect?: (principle: ConstitutionalPrinciple) => void;
  onProposePolicy?: (principle: ConstitutionalPrinciple) => void;
}

const PrinciplesList: React.FC<PrinciplesListProps> = ({ onPrincipleSelect, onProposePolicy }) => {
  const { connection } = useConnection();
  const { publicKey, sendTransaction } = useWallet();
  const [principles, setPrinciples] = useState<ConstitutionalPrinciple[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPrinciple, setSelectedPrinciple] = useState<ConstitutionalPrinciple | null>(null);
  const [program, setProgram] = useState<Program<QuantumagiCore> | null>(null);

  // Mock constitutional principles for development
  const mockPrinciples: ConstitutionalPrinciple[] = [
    {
      id: 'PC-001',
      title: 'No Extrajudicial State Mutation',
      content:
        'AI systems must not perform unauthorized state mutations without proper governance approval. All state changes must be validated through the constitutional framework.',
      category: 'Prompt Constitution',
      rationale:
        'Prevents unauthorized changes to critical system state that could compromise governance integrity.',
      status: 'enacted',
      votes: { for: 15, against: 2 },
    },
    {
      id: 'GV-001',
      title: 'Democratic Policy Approval',
      content:
        'All governance policies must be approved through democratic voting process with transparent community participation and adequate deliberation time.',
      category: 'Governance',
      rationale:
        'Ensures community participation and prevents authoritarian policy implementation.',
      status: 'enacted',
      votes: { for: 18, against: 1 },
    },
    {
      id: 'FN-001',
      title: 'Treasury Protection',
      content:
        'Financial operations exceeding predefined limits require multi-signature approval from elected treasury guardians with public audit trails.',
      category: 'Financial',
      rationale:
        'Protects community treasury from unauthorized access and ensures financial transparency.',
      status: 'proposed',
      votes: { for: 12, against: 5 },
    },
    {
      id: 'SF-001',
      title: 'Safety-First AI Operations',
      content:
        'All AI system operations must undergo safety validation before deployment, with continuous monitoring and immediate halt capabilities.',
      category: 'Safety',
      rationale:
        'Ensures AI systems operate safely and can be stopped if they exhibit harmful behavior.',
      status: 'draft',
    },
    {
      id: 'TR-001',
      title: 'Transparency and Auditability',
      content:
        'All governance decisions, policy implementations, and compliance checks must be publicly auditable with immutable logging.',
      category: 'Transparency',
      rationale: 'Maintains public trust through complete transparency of governance operations.',
      status: 'proposed',
      votes: { for: 14, against: 3 },
    },
  ];

  useEffect(() => {
    initializeProgram();
    loadPrinciples();
  }, [publicKey, connection]);

  const initializeProgram = async () => {
    if (!publicKey) return;

    try {
      const provider = new AnchorProvider(
        connection,
        window.solana,
        AnchorProvider.defaultOptions()
      );

      const programId = new PublicKey('Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS');
      const program = new Program(idl as any, programId, provider) as Program<QuantumagiCore>;

      setProgram(program);
    } catch (error) {
      console.error('Failed to initialize program:', error);
    }
  };

  const loadPrinciples = async () => {
    setLoading(true);
    try {
      // In production, this would fetch from Solana program accounts
      // For now, using mock data with simulated loading
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setPrinciples(mockPrinciples);
    } catch (error) {
      console.error('Failed to load principles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePrincipleClick = (principle: ConstitutionalPrinciple) => {
    setSelectedPrinciple(principle);
    onPrincipleSelect?.(principle);
  };

  const handleProposePolicy = async (principle: ConstitutionalPrinciple) => {
    if (!program || !publicKey) {
      alert('Please connect your wallet first');
      return;
    }

    try {
      console.log(`Proposing policy for principle: ${principle.id}`);
      onProposePolicy?.(principle);

      // In production, this would call the actual Solana program
      // For demo, we'll simulate the process
      alert(`Policy proposal initiated for ${principle.title}`);
    } catch (error) {
      console.error('Failed to propose policy:', error);
      alert('Failed to propose policy. Please try again.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'enacted':
        return 'text-green-600 bg-green-100';
      case 'proposed':
        return 'text-blue-600 bg-blue-100';
      case 'draft':
        return 'text-gray-600 bg-gray-100';
      case 'deprecated':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'prompt constitution':
        return 'text-purple-600 bg-purple-100';
      case 'governance':
        return 'text-blue-600 bg-blue-100';
      case 'financial':
        return 'text-green-600 bg-green-100';
      case 'safety':
        return 'text-red-600 bg-red-100';
      case 'transparency':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading constitutional principles...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Constitutional Principles</h2>
        <div className="text-sm text-gray-500">
          {principles.length} principles • {principles.filter((p) => p.status === 'enacted').length}{' '}
          enacted
        </div>
      </div>

      <div className="space-y-4">
        {principles.map((principle) => (
          <div
            key={principle.id}
            className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 hover:shadow-md ${
              selectedPrinciple?.id === principle.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200'
            }`}
            onClick={() => handlePrincipleClick(principle)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className="font-mono text-sm font-semibold text-gray-700">
                    {principle.id}
                  </span>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(principle.status)}`}
                  >
                    {principle.status.toUpperCase()}
                  </span>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(principle.category)}`}
                  >
                    {principle.category}
                  </span>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">{principle.title}</h3>
                <p className="text-gray-600 text-sm mb-3 line-clamp-2">{principle.content}</p>

                {principle.votes && (
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <span className="text-green-600">👍</span>
                      {principle.votes.for}
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="text-red-600">👎</span>
                      {principle.votes.against}
                    </span>
                    <span className="text-gray-400">•</span>
                    <span>
                      {Math.round(
                        (principle.votes.for / (principle.votes.for + principle.votes.against)) *
                          100
                      )}
                      % approval
                    </span>
                  </div>
                )}
              </div>

              <div className="flex flex-col gap-2 ml-4">
                {principle.status !== 'enacted' && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleProposePolicy(principle);
                    }}
                    className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
                  >
                    Propose Policy
                  </button>
                )}

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePrincipleClick(principle);
                  }}
                  className="px-3 py-1 border border-gray-300 text-gray-700 text-xs rounded hover:bg-gray-50 transition-colors"
                >
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedPrinciple && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">Rationale</h4>
          <p className="text-gray-700 text-sm">{selectedPrinciple.rationale}</p>
        </div>
      )}

      {principles.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No constitutional principles found.</p>
          <p className="text-sm mt-1">Connect your wallet to view and interact with principles.</p>
        </div>
      )}
    </div>
  );
};

export default PrinciplesList;
