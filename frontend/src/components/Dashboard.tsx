/**
 * ACGS-2 Dashboard Component
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * Main dashboard displaying system health, constitutional compliance, and performance metrics.
 */

import React, { useState, useEffect } from 'react';
import { useConstitutionalValidation } from '@/hooks/useConstitutionalValidation';
import { serviceManager, getConstitutionalComplianceScore } from '@/services';
import { CONFIG } from '@/config';

// Types
interface DashboardStats {
  totalServices: number;
  healthyServices: number;
  constitutionalCompliance: number;
  averageLatency: number;
  totalRequests: number;
  errorRate: number;
}

interface ServiceCard {
  name: string;
  status: 'healthy' | 'unhealthy' | 'degraded';
  uptime: number;
  latency: number;
  requests: number;
  constitutionalHash: string;
}

/**
 * Dashboard Component
 */
export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalServices: 0,
    healthyServices: 0,
    constitutionalCompliance: 0,
    averageLatency: 0,
    totalRequests: 0,
    errorRate: 0,
  });

  const [serviceCards, setServiceCards] = useState<ServiceCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Constitutional validation hook
  const {
    isValid,
    isConstitutionallyCompliant,
    complianceScore,
    metrics,
    validateHash,
  } = useConstitutionalValidation({
    component: 'dashboard',
    action: 'view',
    preloadCommonValidations: true,
  });

  // Load dashboard data
  useEffect(() => {
    loadDashboardData();
    
    const interval = setInterval(() => {
      loadDashboardData();
    }, CONFIG.polling.dashboardInterval);

    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Get system health
      const systemHealth = serviceManager.getSystemHealth();
      const serviceStatuses = serviceManager.getServiceHealthStatuses();
      
      // Calculate stats
      const totalServices = systemHealth.services.length;
      const healthyServices = systemHealth.services.filter(s => s.status === 'healthy').length;
      const constitutionalCompliance = getConstitutionalComplianceScore();
      
      // Mock performance data (in real implementation, this would come from metrics service)
      const averageLatency = metrics.averageLatency;
      const totalRequests = metrics.totalRequests;
      const errorRate = metrics.failedRequests / Math.max(metrics.totalRequests, 1) * 100;
      
      setStats({
        totalServices,
        healthyServices,
        constitutionalCompliance,
        averageLatency,
        totalRequests,
        errorRate,
      });
      
      // Create service cards
      const cards: ServiceCard[] = Array.from(serviceStatuses.values()).map(service => ({
        name: service.name,
        status: service.status,
        uptime: 99.9, // Mock data
        latency: Math.random() * 10 + 1, // Mock data
        requests: Math.floor(Math.random() * 1000) + 100, // Mock data
        constitutionalHash: service.constitutionalHash,
      }));
      
      setServiceCards(cards);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleValidateHash = async () => {
    const isValid = await validateHash(CONFIG.constitutional.hash);
    if (isValid) {
      alert('Constitutional hash is valid!');
    } else {
      alert('Constitutional hash validation failed!');
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'degraded': return 'text-yellow-600';
      case 'unhealthy': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'healthy': return '✅';
      case 'degraded': return '⚠️';
      case 'unhealthy': return '❌';
      default: return '❓';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            ACGS-2 Dashboard
          </h1>
          <p className="text-gray-600">
            System health and constitutional compliance monitoring
          </p>
          <div className="mt-2 text-sm text-gray-500" suppressHydrationWarning>
            Last updated: {lastUpdate.toLocaleString()}
          </div>
        </div>

        {/* Constitutional Compliance Alert */}
        {!isConstitutionallyCompliant && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <span className="text-red-500 mr-2">⚠️</span>
              <span className="text-red-700 font-medium">
                Constitutional Compliance Issue Detected
              </span>
            </div>
            <p className="text-red-600 mt-1">
              Current compliance score: {complianceScore.toFixed(1)}%
            </p>
          </div>
        )}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Services</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalServices}</p>
              </div>
              <div className="text-blue-500">
                🏢
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Healthy Services</p>
                <p className="text-2xl font-bold text-green-600">{stats.healthyServices}</p>
              </div>
              <div className="text-green-500">
                ✅
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Constitutional Compliance</p>
                <p className={`text-2xl font-bold ${
                  stats.constitutionalCompliance >= 95 ? 'text-green-600' : 
                  stats.constitutionalCompliance >= 80 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {stats.constitutionalCompliance.toFixed(1)}%
                </p>
              </div>
              <div className="text-purple-500">
                📜
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Average Latency</p>
                <p className={`text-2xl font-bold ${
                  stats.averageLatency < CONFIG.performance.latencyP99Target ? 'text-green-600' : 'text-red-600'
                }`}>
                  {stats.averageLatency.toFixed(1)}ms
                </p>
              </div>
              <div className="text-orange-500">
                ⚡
              </div>
            </div>
          </div>
        </div>

        {/* Service Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {serviceCards.map((service, index) => (
            <div key={index} className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  {service.name}
                </h3>
                <span className={`text-2xl ${getStatusColor(service.status)}`}>
                  {getStatusIcon(service.status)}
                </span>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className={`text-sm font-medium ${getStatusColor(service.status)}`}>
                    {service.status.toUpperCase()}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Uptime:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {service.uptime.toFixed(1)}%
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Latency:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {service.latency.toFixed(1)}ms
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Requests:</span>
                  <span className="text-sm font-medium text-gray-900">
                    <span suppressHydrationWarning>{service.requests.toLocaleString()}</span>
                  </span>
                </div>
                
                <div className="mt-3 pt-3 border-t">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">Constitutional Hash:</span>
                    <span className={`text-xs font-mono ${
                      service.constitutionalHash === CONFIG.constitutional.hash ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {service.constitutionalHash.substring(0, 8)}...
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Performance Metrics */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Performance Metrics
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 mb-1">
                <span suppressHydrationWarning>{stats.totalRequests.toLocaleString()}</span>
              </div>
              <div className="text-sm text-gray-600">Total Requests</div>
            </div>
            
            <div className="text-center">
              <div className={`text-2xl font-bold mb-1 ${
                stats.errorRate < 1 ? 'text-green-600' : 
                stats.errorRate < 5 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {stats.errorRate.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Error Rate</div>
            </div>
            
            <div className="text-center">
              <div className={`text-2xl font-bold mb-1 ${
                metrics.cacheHitRate >= CONFIG.performance.cacheHitRateTarget ? 'text-green-600' : 'text-red-600'
              }`}>
                {metrics.cacheHitRate.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Cache Hit Rate</div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            System Actions
          </h3>
          
          <div className="flex space-x-4">
            <button
              onClick={handleValidateHash}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Validate Constitutional Hash
            </button>
            
            <button
              onClick={loadDashboardData}
              disabled={isLoading}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {isLoading ? 'Refreshing...' : 'Refresh Data'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
