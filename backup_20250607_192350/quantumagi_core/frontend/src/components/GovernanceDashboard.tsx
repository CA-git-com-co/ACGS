// frontend/src/components/GovernanceDashboard.tsx
// Comprehensive Governance Overview and Management Dashboard

import React, { useState, useEffect } from 'react';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { PublicKey } from '@solana/web3.js';
import { Program, AnchorProvider } from '@coral-xyz/anchor';
import { QuantumagiCore } from '../types/quantumagi_core';
import idl from '../idl/quantumagi_core.json';

interface DashboardStats {
  totalPolicies: number;
  activePolicies: number;
  pendingProposals: number;
  totalVotes: number;
  complianceChecks24h: number;
  averageApprovalRate: number;
  systemHealth: 'Excellent' | 'Good' | 'Warning' | 'Critical';
}

interface PolicySummary {
  id: string;
  title: string;
  category: string;
  status: 'proposed' | 'voting' | 'enacted' | 'rejected';
  votesFor: number;
  votesAgainst: number;
  deadline?: string;
  proposedBy: string;
}

interface RecentActivity {
  id: string;
  type: 'policy_proposed' | 'vote_cast' | 'policy_enacted' | 'compliance_check' | 'appeal_submitted';
  description: string;
  timestamp: string;
  actor: string;
  status: 'success' | 'warning' | 'error';
}

const GovernanceDashboard: React.FC = () => {
  const { connection } = useConnection();
  const { publicKey } = useWallet();
  const [program, setProgram] = useState<Program<QuantumagiCore> | null>(null);
  
  const [stats, setStats] = useState<DashboardStats>({
    totalPolicies: 0,
    activePolicies: 0,
    pendingProposals: 0,
    totalVotes: 0,
    complianceChecks24h: 0,
    averageApprovalRate: 0,
    systemHealth: 'Good'
  });
  
  const [policies, setPolicies] = useState<PolicySummary[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');

  // Mock data for demonstration
  const mockStats: DashboardStats = {
    totalPolicies: 12,
    activePolicies: 8,
    pendingProposals: 3,
    totalVotes: 156,
    complianceChecks24h: 2847,
    averageApprovalRate: 78.5,
    systemHealth: 'Excellent'
  };

  const mockPolicies: PolicySummary[] = [
    {
      id: "PC-001",
      title: "No Extrajudicial State Mutation",
      category: "Prompt Constitution",
      status: "enacted",
      votesFor: 15,
      votesAgainst: 2,
      proposedBy: "Constitutional Committee"
    },
    {
      id: "GV-001",
      title: "Democratic Policy Approval",
      category: "Governance",
      status: "enacted",
      votesFor: 18,
      votesAgainst: 1,
      proposedBy: "Governance Council"
    },
    {
      id: "FN-001",
      title: "Treasury Protection",
      category: "Financial",
      status: "voting",
      votesFor: 12,
      votesAgainst: 5,
      deadline: "2025-06-10T18:00:00Z",
      proposedBy: "Treasury Committee"
    },
    {
      id: "SF-002",
      title: "Enhanced AI Safety Protocols",
      category: "Safety",
      status: "proposed",
      votesFor: 0,
      votesAgainst: 0,
      proposedBy: "Safety Working Group"
    }
  ];

  const mockRecentActivity: RecentActivity[] = [
    {
      id: "1",
      type: "compliance_check",
      description: "Treasury transfer validated against FN-001",
      timestamp: "2025-06-07T16:30:00Z",
      actor: "PGC System",
      status: "success"
    },
    {
      id: "2",
      type: "vote_cast",
      description: "Vote cast on FN-001 Treasury Protection",
      timestamp: "2025-06-07T16:15:00Z",
      actor: "Council Member #7",
      status: "success"
    },
    {
      id: "3",
      type: "policy_proposed",
      description: "SF-002 Enhanced AI Safety Protocols proposed",
      timestamp: "2025-06-07T15:45:00Z",
      actor: "Safety Working Group",
      status: "success"
    },
    {
      id: "4",
      type: "compliance_check",
      description: "Unauthorized state mutation blocked by PC-001",
      timestamp: "2025-06-07T15:30:00Z",
      actor: "PGC System",
      status: "warning"
    },
    {
      id: "5",
      type: "appeal_submitted",
      description: "Appeal submitted for policy violation",
      timestamp: "2025-06-07T15:00:00Z",
      actor: "Community Member",
      status: "warning"
    }
  ];

  useEffect(() => {
    initializeProgram();
    loadDashboardData();
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

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // In production, this would fetch real data from Solana accounts
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate loading
      
      setStats(mockStats);
      setPolicies(mockPolicies);
      setRecentActivity(mockRecentActivity);
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'enacted': return 'text-green-600 bg-green-100';
      case 'voting': return 'text-blue-600 bg-blue-100';
      case 'proposed': return 'text-yellow-600 bg-yellow-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'policy_proposed': return '📋';
      case 'vote_cast': return '🗳️';
      case 'policy_enacted': return '✅';
      case 'compliance_check': return '🔍';
      case 'appeal_submitted': return '⚖️';
      default: return '📄';
    }
  };

  const getActivityStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'Excellent': return 'text-green-600';
      case 'Good': return 'text-blue-600';
      case 'Warning': return 'text-yellow-600';
      case 'Critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading governance dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">🏛️ Governance Dashboard</h1>
        <div className="flex items-center gap-3">
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getHealthColor(stats.systemHealth)} bg-opacity-10`}>
            System: {stats.systemHealth}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Policies</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalPolicies}</p>
            </div>
            <div className="text-3xl">📋</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">{stats.activePolicies} active</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Proposals</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pendingProposals}</p>
            </div>
            <div className="text-3xl">⏳</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Awaiting votes</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Votes</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalVotes}</p>
            </div>
            <div className="text-3xl">🗳️</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">{stats.averageApprovalRate}% avg approval</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Compliance Checks</p>
              <p className="text-2xl font-bold text-gray-900">{stats.complianceChecks24h.toLocaleString()}</p>
            </div>
            <div className="text-3xl">🔍</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Last 24 hours</p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Policies */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Active Policies</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {policies.map((policy) => (
                <div key={policy.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-mono text-sm font-semibold text-gray-700">{policy.id}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(policy.status)}`}>
                          {policy.status.toUpperCase()}
                        </span>
                      </div>
                      <h3 className="font-medium text-gray-900 mb-1">{policy.title}</h3>
                      <p className="text-sm text-gray-600 mb-2">{policy.category}</p>
                      
                      {(policy.votesFor > 0 || policy.votesAgainst > 0) && (
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-green-600">👍 {policy.votesFor}</span>
                          <span className="text-red-600">👎 {policy.votesAgainst}</span>
                          {policy.deadline && (
                            <span className="text-gray-500">
                              Deadline: {new Date(policy.deadline).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3">
                  <div className="text-xl">{getActivityIcon(activity.type)}</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">{activity.description}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-500">{activity.actor}</span>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-xs text-gray-500">{formatTimeAgo(activity.timestamp)}</span>
                      <span className={`text-xs font-medium ${getActivityStatusColor(activity.status)}`}>
                        {activity.status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left">
            <div className="text-2xl mb-2">📋</div>
            <h3 className="font-medium text-gray-900">Propose New Policy</h3>
            <p className="text-sm text-gray-600">Submit a new governance proposal</p>
          </button>
          
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left">
            <div className="text-2xl mb-2">🔍</div>
            <h3 className="font-medium text-gray-900">Check Compliance</h3>
            <p className="text-sm text-gray-600">Validate actions against policies</p>
          </button>
          
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left">
            <div className="text-2xl mb-2">📊</div>
            <h3 className="font-medium text-gray-900">View Analytics</h3>
            <p className="text-sm text-gray-600">Detailed governance metrics</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default GovernanceDashboard;
