'use client';

import React, { useState, useEffect } from 'react';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { PublicKey } from '@solana/web3.js';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Shield,
  Activity,
  CheckCircle,
  AlertTriangle,
  Clock,
  TrendingUp,
  Wallet,
  Globe,
} from 'lucide-react';

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
  status: 'Active' | 'Pending' | 'Deprecated';
  votes: { yes: number; no: number };
}

interface ComplianceResult {
  id: string;
  action: string;
  result: 'PASS' | 'FAIL' | 'PENDING';
  confidence: number;
  timestamp: string;
}

interface ProgramStatus {
  name: string;
  programId: string;
  status: 'Deployed' | 'Not Found' | 'Error';
}

interface DashboardData {
  constitution: ConstitutionData | null;
  policies: PolicyData[];
  complianceResults: ComplianceResult[];
  systemStatus: string;
}

// Program IDs for deployed Quantumagi programs
const PROGRAM_IDS = {
  QUANTUMAGI_CORE: '8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4',
  APPEALS: 'CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ',
  LOGGING: 'CjZi5hi9qggBzbXDht9YSJhN5cw7Bhz3rHhn63QQcPQo',
};

/**
 * Quantumagi Dashboard Component
 *
 * Main dashboard for Solana-based constitutional governance system.
 * Displays real-time data about proposals, compliance, and system status.
 */
export const QuantumagiDashboard: React.FC = () => {
  const { connection } = useConnection();
  const { publicKey, connected } = useWallet();
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    constitution: null,
    policies: [],
    complianceResults: [],
    systemStatus: 'Loading...',
  });
  const [loading, setLoading] = useState(true);
  const [programStatuses, setProgramStatuses] = useState<ProgramStatus[]>([]);

  useEffect(() => {
    if (connected && publicKey) {
      loadDashboardData();
      checkProgramStatuses();
    }
  }, [connected, publicKey, connection]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Simulate loading dashboard data
      // In a real implementation, this would fetch from Solana programs
      const mockData: DashboardData = {
        constitution: {
          hash: 'QmX7Y8Z9...',
          version: '2.1.0',
          status: 'Active',
          lastUpdated: new Date().toISOString(),
        },
        policies: [
          {
            id: 'POL-001',
            title: 'Data Privacy Protection',
            status: 'Active',
            votes: { yes: 156, no: 23 },
          },
          {
            id: 'POL-002',
            title: 'AI Ethics Guidelines',
            status: 'Pending',
            votes: { yes: 89, no: 45 },
          },
        ],
        complianceResults: [
          {
            id: 'CHK-001',
            action: 'User data access',
            result: 'PASS',
            confidence: 94,
            timestamp: new Date().toISOString(),
          },
          {
            id: 'CHK-002',
            action: 'Policy modification',
            result: 'PENDING',
            confidence: 87,
            timestamp: new Date().toISOString(),
          },
        ],
        systemStatus: 'Operational',
      };

      setDashboardData(mockData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setDashboardData(prev => ({ ...prev, systemStatus: 'Error' }));
    } finally {
      setLoading(false);
    }
  };

  const checkProgramStatuses = async () => {
    const statuses: ProgramStatus[] = [];

    for (const [name, programId] of Object.entries(PROGRAM_IDS)) {
      try {
        const accountInfo = await connection.getAccountInfo(new PublicKey(programId));
        statuses.push({
          name: name.replace('_', ' '),
          programId,
          status: accountInfo ? 'Deployed' : 'Not Found',
        });
      } catch (error) {
        statuses.push({
          name: name.replace('_', ' '),
          programId,
          status: 'Error',
        });
      }
    }

    setProgramStatuses(statuses);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'operational':
      case 'active':
      case 'deployed':
        return 'text-green-600';
      case 'pending':
        return 'text-yellow-600';
      case 'error':
      case 'deprecated':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'operational':
      case 'active':
      case 'deployed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'error':
      case 'deprecated':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  if (!connected) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-blue-100 rounded-full">
              <Wallet className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          <CardTitle className="text-2xl">Connect Your Wallet</CardTitle>
          <p className="text-muted-foreground">
            Please connect your Solana wallet to access the governance dashboard.
          </p>
        </CardHeader>
        <CardContent className="text-center">
          <WalletMultiButton />
          <div className="mt-4 text-sm text-muted-foreground">
            <p>Supported wallets: Phantom, Solflare</p>
            <p className="flex items-center justify-center mt-2">
              <Globe className="h-4 w-4 mr-1" />
              Connected to Solana Devnet
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="text-2xl flex items-center">
                <Shield className="h-6 w-6 mr-2 text-blue-600" />
                Quantumagi Governance Dashboard
              </CardTitle>
              <p className="text-muted-foreground mt-1">
                Constitutional Governance System on Solana Devnet
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Network</p>
                <p className="font-semibold text-blue-600">Solana Devnet</p>
              </div>
              <WalletMultiButton />
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              {getStatusIcon(dashboardData.systemStatus)}
              <span className={`font-medium ${getStatusColor(dashboardData.systemStatus)}`}>
                {dashboardData.systemStatus}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Policies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.policies.length}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData.policies.filter(p => p.status === 'Active').length} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Compliance Checks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.complianceResults.length}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData.complianceResults.filter(c => c.result === 'PASS').length} passed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Programs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{programStatuses.length}</div>
            <p className="text-xs text-muted-foreground">
              {programStatuses.filter(p => p.status === 'Deployed').length} deployed
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="policies">Policies</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="programs">Programs</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Constitution Status</CardTitle>
              </CardHeader>
              <CardContent>
                {dashboardData.constitution ? (
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Version:</span>
                      <Badge variant="outline">{dashboardData.constitution.version}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Status:</span>
                      <Badge
                        variant={
                          dashboardData.constitution.status === 'Active' ? 'default' : 'secondary'
                        }
                      >
                        {dashboardData.constitution.status}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Hash:</span>
                      <code className="text-xs">{dashboardData.constitution.hash}</code>
                    </div>
                  </div>
                ) : (
                  <p className="text-muted-foreground">No constitution data available</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {dashboardData.complianceResults.slice(0, 3).map(result => (
                    <div key={result.id} className="flex items-center justify-between">
                      <span className="text-sm">{result.action}</span>
                      <Badge variant={result.result === 'PASS' ? 'default' : 'secondary'}>
                        {result.result}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="policies" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Policy Proposals</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardData.policies.map(policy => (
                  <div key={policy.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold">{policy.title}</h4>
                      <Badge variant={policy.status === 'Active' ? 'default' : 'secondary'}>
                        {policy.status}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                      <span>ID: {policy.id}</span>
                      <span>Yes: {policy.votes.yes}</span>
                      <span>No: {policy.votes.no}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compliance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardData.complianceResults.map(result => (
                  <div key={result.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold">{result.action}</h4>
                      <div className="flex items-center space-x-2">
                        <Badge variant={result.result === 'PASS' ? 'default' : 'secondary'}>
                          {result.result}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {result.confidence}% confidence
                        </span>
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {new Date(result.timestamp).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="programs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Program Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {programStatuses.map(program => (
                  <div key={program.programId} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold">{program.name}</h4>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(program.status)}
                        <Badge variant={program.status === 'Deployed' ? 'default' : 'secondary'}>
                          {program.status}
                        </Badge>
                      </div>
                    </div>
                    <code className="text-xs text-muted-foreground">{program.programId}</code>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
