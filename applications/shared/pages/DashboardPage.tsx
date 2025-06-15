import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import ACService from '../services/ACService';
import GSService from '../services/GSService';

interface DashboardStats {
  totalPrinciples: number;
  activePolicies: number;
  recentComplianceChecks: number;
  systemStatus: 'operational' | 'warning' | 'error';
}

interface RecentActivity {
  id: string;
  type: 'principle_created' | 'policy_synthesized' | 'compliance_check';
  title: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error';
}

const DashboardPage: React.FC = () => {
  const { currentUser, isAuthenticated } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalPrinciples: 0,
    activePolicies: 0,
    recentComplianceChecks: 0,
    systemStatus: 'operational'
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      loadDashboardData();
    }
  }, [isAuthenticated]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      // Load principles count
      const principlesData = await ACService.getPrinciples();
      
      // Mock data for other stats - in production, these would come from respective services
      const mockStats: DashboardStats = {
        totalPrinciples: principlesData.principles?.length || 0,
        activePolicies: 12,
        recentComplianceChecks: 45,
        systemStatus: 'operational'
      };

      const mockActivity: RecentActivity[] = [
        {
          id: '1',
          type: 'principle_created',
          title: 'New governance principle created',
          timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          status: 'success'
        },
        {
          id: '2',
          type: 'policy_synthesized',
          title: 'Policy synthesis completed',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
          status: 'success'
        },
        {
          id: '3',
          type: 'compliance_check',
          title: 'Compliance validation performed',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
          status: 'warning'
        }
      ];

      setStats(mockStats);
      setRecentActivity(mockActivity);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'operational': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getActivityIcon = (type: string): string => {
    switch (type) {
      case 'principle_created': return '📜';
      case 'policy_synthesized': return '⚙️';
      case 'compliance_check': return '🔍';
      default: return '📋';
    }
  };

  const formatTimeAgo = (timestamp: string): string => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes} minutes ago`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)} hours ago`;
    } else {
      return `${Math.floor(diffInMinutes / 1440)} days ago`;
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="p-8 text-center max-w-md">
          <div className="mb-4">
            <span className="text-4xl">🏛️</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Welcome to ACGS-PGP
          </h2>
          <p className="text-gray-600 mb-6">
            Artificial Constitution and Self-Synthesizing Prompt Governance Compiler
          </p>
          <div className="space-y-3">
            <Button as={Link} to="/login" variant="primary" className="w-full">
              Sign In
            </Button>
            <Button as={Link} to="/register" variant="secondary" className="w-full">
              Register
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {currentUser?.username}
          </h1>
          <p className="mt-2 text-gray-600">
            Here's what's happening in your governance system today.
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">📜</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Principles</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.totalPrinciples}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">⚙️</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Active Policies</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.activePolicies}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">🔍</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Compliance Checks</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.recentComplianceChecks}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">🟢</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">System Status</p>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(stats.systemStatus)}`}>
                  {stats.systemStatus}
                </span>
              </div>
            </div>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-1">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Button as={Link} to="/ac-management" variant="primary" className="w-full">
                  Manage Principles
                </Button>
                <Button as={Link} to="/policy-synthesis" variant="secondary" className="w-full">
                  Synthesize Policies
                </Button>
                <Button as={Link} to="/compliance-checker" variant="secondary" className="w-full">
                  Check Compliance
                </Button>
                <Button as={Link} to="/constitutional-council-dashboard" variant="secondary" className="w-full">
                  Council Dashboard
                </Button>
              </div>
            </Card>
          </div>

          {/* Recent Activity */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0">
                      <span className="text-xl">{getActivityIcon(activity.type)}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                      <p className="text-sm text-gray-500">{formatTimeAgo(activity.timestamp)}</p>
                    </div>
                    <div className="flex-shrink-0">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(activity.status)}`}>
                        {activity.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
