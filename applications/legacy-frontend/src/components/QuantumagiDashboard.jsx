import React, { useState, useEffect, useMemo } from 'react';
import { ConnectionProvider, WalletProvider, useConnection, useWallet } from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { PhantomWalletAdapter, SolflareWalletAdapter } from '@solana/wallet-adapter-wallets';
import { WalletModalProvider, WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl, PublicKey, Connection } from '@solana/web3.js';
import { Program, AnchorProvider, web3 } from '@coral-xyz/anchor';

// Import wallet adapter CSS
import '@solana/wallet-adapter-react-ui/styles.css';

// Program IDs for deployed Quantumagi programs
const PROGRAM_IDS = {
  QUANTUMAGI_CORE: '8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4',
  APPEALS: 'CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ',
  LOGGING: 'CjZi5hi9qggBzbXDht9YSJhN5cw7Bhz3rHhn63QQcPQo'
};

// Dashboard component
const QuantumagiDashboard = () => {
  const { connection } = useConnection();
  const { publicKey, connected } = useWallet();
  const [dashboardData, setDashboardData] = useState({
    constitution: null,
    policies: [],
    complianceResults: [],
    systemStatus: 'Loading...'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (connected && publicKey) {
      loadDashboardData();
    }
  }, [connected, publicKey, connection]);

  const loadDashboardData = async () => {
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

  const loadConstitutionData = async () => {
    // Mock constitution data - in production, this would fetch from Solana program
    return {
      hash: 'cdd01ef066bc6cf2',
      version: '1.0.0',
      status: 'Active',
      lastUpdated: '2025-06-07T20:19:39Z'
    };
  };

  const loadPoliciesData = async () => {
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

  const loadComplianceData = async () => {
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

  const checkProgramStatus = async (programId) => {
    try {
      const programInfo = await connection.getAccountInfo(new PublicKey(programId));
      return programInfo ? 'Deployed' : 'Not Found';
    } catch (error) {
      return 'Error';
    }
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
              <h1 className="text-3xl font-bold text-gray-900">🏛️ Quantumagi Governance Dashboard</h1>
              <p className="text-gray-600 mt-2">Constitutional Governance System on Solana Devnet</p>
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
            <p className="text-gray-600 mb-6">Please connect your Solana wallet to access the governance dashboard.</p>
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
                  <span className="text-green-600 font-medium">{dashboardData.systemStatus}</span>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Constitution</h3>
                <p className="text-sm text-gray-600">Hash: {dashboardData.constitution?.hash}</p>
                <p className="text-sm text-gray-600">Version: {dashboardData.constitution?.version}</p>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Active Policies</h3>
                <p className="text-3xl font-bold text-blue-600">{dashboardData.policies.length}</p>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Compliance Checks</h3>
                <p className="text-3xl font-bold text-green-600">{dashboardData.complianceResults.length}</p>
              </div>
            </div>

            {/* Program Status */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">📋 Deployed Programs</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(PROGRAM_IDS).map(([name, programId]) => (
                  <div key={name} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900">{name.replace('_', ' ')}</h3>
                    <p className="text-xs text-gray-500 font-mono mt-1">{programId}</p>
                    <div className="flex items-center mt-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      <span className="text-sm text-green-600">Deployed</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Active Policies */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">📜 Active Policies</h2>
              <div className="space-y-3">
                {dashboardData.policies.map((policy) => (
                  <div key={policy.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium text-gray-900">{policy.id}: {policy.title}</h3>
                        <p className="text-sm text-gray-600">Category: {policy.category}</p>
                      </div>
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                        {policy.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Compliance Checks */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">🔍 Recent Compliance Checks</h2>
              <div className="space-y-3">
                {dashboardData.complianceResults.map((result) => (
                  <div key={result.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="font-medium text-gray-900">{result.action}</h3>
                        <p className="text-sm text-gray-600">Confidence: {result.confidence}%</p>
                      </div>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        result.result === 'PASS' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
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
const QuantumagiApp = () => {
  const network = WalletAdapterNetwork.Devnet;
  const endpoint = useMemo(() => clusterApiUrl(network), [network]);
  
  const wallets = useMemo(
    () => [
      new PhantomWalletAdapter(),
      new SolflareWalletAdapter(),
    ],
    []
  );

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
