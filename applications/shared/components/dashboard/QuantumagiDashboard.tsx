import React, { useState, useEffect, useMemo } from 'react';
import {
  ConnectionProvider,
  WalletProvider,
  useConnection,
  useWallet
} from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { PhantomWalletAdapter, SolflareWalletAdapter } from '@solana/wallet-adapter-wallets';
import { WalletModalProvider, WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl, PublicKey } from '@solana/web3.js';
import { Program, AnchorProvider } from '@coral-xyz/anchor';

// Import wallet adapter CSS
import '@solana/wallet-adapter-react-ui/styles.css';

// Types
interface ConstitutionData {
  hash: string;
  version: string;
  status: 'Active' | 'Pending' | 'Deprecated';
  lastUpdated: string;
}

interface PolicyData {
  id: string;
  title: string;
  category: 'Governance' | 'Safety' | 'Financial' | 'Constitutional';
  status: 'Active' | 'Pending' | 'Deprecated';
  enactedAt: string;
}

interface ComplianceResult {
  id: number;
  action: string;
  result: 'PASS' | 'FAIL';
  confidence: number;
  timestamp: string;
}

interface DashboardData {
  constitution: ConstitutionData | null;
  policies: PolicyData[];
  complianceResults: ComplianceResult[];
  systemStatus: 'Loading...' | 'Operational' | 'Warning' | 'Error';
}

interface ProgramStatus {
  name: string;
  programId: string;
  status: 'Deployed' | 'Not Found' | 'Error';
}

// Program IDs for deployed Quantumagi programs
const PROGRAM_IDS = {
  QUANTUMAGI_CORE: '8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4',
  APPEALS: 'CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ',
  LOGGING: 'CjZi5hi9qggBzbXDht9YSJhN5cw7Bhz3rHhn63QQcPQo'
};

// Dashboard component
const QuantumagiDashboard: React.FC = () => {
  const { connection } = useConnection();
  const { publicKey, connected } = useWallet();
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    constitution: null,
    policies: [],
    complianceResults: [],
    systemStatus: 'Loading...'
  });
  const [loading, setLoading] = useState(true);
  const [programStatuses, setProgramStatuses] = useState<ProgramStatus[]>([]);

  useEffect(() => {
    if (connected && publicKey) {
      loadDashboardData();
      checkProgramStatuses();
    }
  }, [connected, publicKey, connection]);

  const loadDashboardData = async (): Promise<void> => {
    try {
      setLoading(true);

      // Load constitution data
      const constitutionData = await loadConstitutionData();

      // Load policies
      const policiesData = await loadPoliciesData();

      // Load recent compliance results
      const complianceData = await loadComplianceData();

      setDashboardData({
        constitution: constitutionData,
        policies: policiesData,
        complianceResults: complianceData,
        systemStatus: 'Operational'
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setDashboardData(prev => ({ ...prev, systemStatus: 'Error' }));
    } finally {
      setLoading(false);
    }
  };

  const loadConstitutionData = async (): Promise<ConstitutionData> => {
    // Mock constitution data - in production, this would fetch from Solana program
    return {
      hash: 'cdd01ef066bc6cf2',
      version: '1.0.0',
      status: 'Active',
      lastUpdated: '2025-06-07T20:19:39Z'
    };
  };

  const loadPoliciesData = async (): Promise<PolicyData[]> => {
    // Mock policies data - in production, this would fetch from Solana program accounts
    return [
      {
        id: 'POL-001',
        title: 'Basic Voting Procedures',
        category: 'Governance',
        status: 'Active',
        enactedAt: '2025-06-07T20:20:00Z'
      },
      {
        id: 'POL-002',
        title: 'Emergency Response Protocol',
        category: 'Safety',
        status: 'Active',
        enactedAt: '2025-06-07T20:20:01Z'
      },
      {
        id: 'POL-003',
        title: 'Treasury Management',
        category: 'Financial',
        status: 'Active',
        enactedAt: '2025-06-07T20:20:02Z'
      }
    ];
  };

  const loadComplianceData = async (): Promise<ComplianceResult[]> => {
    // Mock compliance data - in production, this would fetch from logging program
    return [
      {
        id: 1,
        action: 'authorized_treasury_transfer',
        result: 'PASS',
        confidence: 85,
        timestamp: '2025-06-07T20:21:00Z'
      },
      {
        id: 2,
        action: 'unauthorized_state_mutation',
        result: 'FAIL',
        confidence: 96,
        timestamp: '2025-06-07T20:21:01Z'
      },
      {
        id: 3,
        action: 'governance_decision_voting',
        result: 'PASS',
        confidence: 98,
        timestamp: '2025-06-07T20:21:02Z'
      }
    ];
  };

  const checkProgramStatuses = async (): Promise<void> => {
    const statuses: ProgramStatus[] = [];

    for (const [name, programId] of Object.entries(PROGRAM_IDS)) {
      try {
        const programInfo = await connection.getAccountInfo(new PublicKey(programId));
        statuses.push({
          name: name.replace('_', ' '),
          programId,
          status: programInfo ? 'Deployed' : 'Not Found'
        });
      } catch (error) {
        statuses.push({
          name: name.replace('_', ' '),
          programId,
          status: 'Error'
        });
      }
    }

    setProgramStatuses(statuses);
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'Active':
      case 'Operational':
      case 'Deployed':
      case 'PASS':
        return 'text-green-600 bg-green-100';
      case 'Warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'Error':
      case 'FAIL':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTimestamp = (timestamp: string): string => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Quantumagi Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🏛️ Quantumagi Governance Dashboard
              </h1>
              <p className="text-gray-600 mt-2">
                Constitutional Governance System on Solana Devnet
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-500">Network</p>
                <p className="font-semibold text-blue-600">Solana Devnet</p>
              </div>
              <WalletMultiButton />
            </div>
          </div>
        </div>

        {!connected ? (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Connect Your Wallet</h2>
            <p className="text-gray-600 mb-6">
              Please connect your Solana wallet to access the governance dashboard.
            </p>
            <WalletMultiButton />
          </div>
        ) : (
          <>
            {/* System Status */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">System Status</h3>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <span className={`font-medium ${getStatusColor(dashboardData.systemStatus)}`}>
                    {dashboardData.systemStatus}
                  </span>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Constitution</h3>
                <p className="text-sm text-gray-600">Hash: {dashboardData.constitution?.hash}</p>
                <p className="text-sm text-gray-600">
                  Version: {dashboardData.constitution?.version}
                </p>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Active Policies</h3>
                <p className="text-3xl font-bold text-blue-600">{dashboardData.policies.length}</p>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Compliance Checks</h3>
                <p className="text-3xl font-bold text-green-600">
                  {dashboardData.complianceResults.length}
                </p>
              </div>
            </div>

            {/* Program Status */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">📋 Deployed Programs</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {programStatuses.map(program => (
                  <div key={program.programId} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900">{program.name}</h3>
                    <p className="text-xs text-gray-500 font-mono mt-1 break-all">
                      {program.programId}
                    </p>
                    <div className="flex items-center mt-2">
                      <div
                        className={`w-2 h-2 rounded-full mr-2 ${
                          program.status === 'Deployed'
                            ? 'bg-green-500'
                            : program.status === 'Error'
                              ? 'bg-red-500'
                              : 'bg-yellow-500'
                        }`}
                      ></div>
                      <span className={`text-sm ${getStatusColor(program.status)}`}>
                        {program.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Active Policies */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">📜 Active Policies</h2>
              <div className="space-y-3">
                {dashboardData.policies.map(policy => (
                  <div key={policy.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium text-gray-900">
                          {policy.id}: {policy.title}
                        </h3>
                        <p className="text-sm text-gray-600">Category: {policy.category}</p>
                        <p className="text-xs text-gray-500">
                          Enacted: {formatTimestamp(policy.enactedAt)}
                        </p>
                      </div>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${getStatusColor(policy.status)}`}
                      >
                        {policy.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Compliance Checks */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                🔍 Recent Compliance Checks
              </h2>
              <div className="space-y-3">
                {dashboardData.complianceResults.map(result => (
                  <div key={result.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="font-medium text-gray-900">{result.action}</h3>
                        <p className="text-sm text-gray-600">Confidence: {result.confidence}%</p>
                        <p className="text-xs text-gray-500">{formatTimestamp(result.timestamp)}</p>
                      </div>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${getStatusColor(result.result)}`}
                      >
                        {result.result}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

// Wallet Provider Wrapper
const QuantumagiApp: React.FC = () => {
  const network = WalletAdapterNetwork.Devnet;
  const endpoint = useMemo(() => clusterApiUrl(network), [network]);

  const wallets = useMemo(() => [new PhantomWalletAdapter(), new SolflareWalletAdapter()], []);

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <QuantumagiDashboard />
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
};

export default QuantumagiApp;
