/**
 * ACGS Health Monitor Dashboard Component
 * 
 * Real-time dashboard for monitoring all 7 ACGS core services
 * with health status, performance metrics, and alert notifications.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { healthMonitor, ACGS_SERVICES, HealthCheckResult, ServiceMetrics } from '../../services/healthMonitor';

// Status indicator component
const StatusIndicator: React.FC<{ status: string; size?: 'sm' | 'md' | 'lg' }> = ({ 
  status, 
  size = 'md' 
}) => {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  };

  const statusColors = {
    healthy: 'bg-green-500',
    degraded: 'bg-yellow-500',
    unhealthy: 'bg-red-500',
    unknown: 'bg-gray-400'
  };

  return (
    <div className={`${sizeClasses[size]} ${statusColors[status as keyof typeof statusColors]} rounded-full animate-pulse`} />
  );
};

// Service card component
const ServiceCard: React.FC<{ 
  serviceKey: string; 
  result: HealthCheckResult; 
  metrics: ServiceMetrics;
}> = ({ serviceKey, result, metrics }) => {
  const service = ACGS_SERVICES[serviceKey];
  const isHealthy = result.status === 'healthy';
  const isDegraded = result.status === 'degraded';
  const isUnhealthy = result.status === 'unhealthy';

  return (
    <div className={`
      p-4 rounded-lg border-2 transition-all duration-200
      ${isHealthy ? 'border-green-200 bg-green-50' : ''}
      ${isDegraded ? 'border-yellow-200 bg-yellow-50' : ''}
      ${isUnhealthy ? 'border-red-200 bg-red-50' : ''}
      ${result.status === 'unknown' ? 'border-gray-200 bg-gray-50' : ''}
    `}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <StatusIndicator status={result.status} size="md" />
          <h3 className="font-semibold text-gray-900">{service.name}</h3>
          {service.critical && (
            <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
              Critical
            </span>
          )}
        </div>
        <div className="text-sm text-gray-500">
          Port {service.port}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-gray-600">Response Time</div>
          <div className={`font-mono ${result.responseTime > 2000 ? 'text-red-600' : 'text-green-600'}`}>
            {result.responseTime}ms
          </div>
        </div>
        <div>
          <div className="text-gray-600">Uptime</div>
          <div className={`font-mono ${metrics.uptime < 99 ? 'text-red-600' : 'text-green-600'}`}>
            {metrics.uptime.toFixed(1)}%
          </div>
        </div>
        <div>
          <div className="text-gray-600">Avg Response</div>
          <div className="font-mono text-gray-800">
            {metrics.averageResponseTime.toFixed(0)}ms
          </div>
        </div>
        <div>
          <div className="text-gray-600">Error Rate</div>
          <div className={`font-mono ${metrics.errorRate > 5 ? 'text-red-600' : 'text-green-600'}`}>
            {metrics.errorRate.toFixed(1)}%
          </div>
        </div>
      </div>

      {result.version && (
        <div className="mt-3 text-xs text-gray-500">
          Version: {result.version}
        </div>
      )}

      {result.error && (
        <div className="mt-3 p-2 bg-red-100 border border-red-200 rounded text-sm text-red-700">
          {result.error}
        </div>
      )}

      {result.dependencies && (
        <div className="mt-3">
          <div className="text-xs text-gray-600 mb-1">Dependencies:</div>
          <div className="flex flex-wrap gap-1">
            {Object.entries(result.dependencies).map(([dep, status]) => (
              <span
                key={dep}
                className={`px-2 py-1 text-xs rounded ${
                  status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}
              >
                {dep}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// System overview component
const SystemOverview: React.FC<{ systemHealth: any }> = ({ systemHealth }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'degraded': return 'text-yellow-600';
      case 'unhealthy': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-xl font-semibold mb-4 flex items-center">
        <StatusIndicator status={systemHealth.status} size="lg" />
        <span className="ml-2">System Overview</span>
      </h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {systemHealth.healthyServices}/{systemHealth.totalServices}
          </div>
          <div className="text-sm text-gray-600">Healthy Services</div>
        </div>
        <div className="text-center">
          <div className={`text-2xl font-bold ${getStatusColor(systemHealth.status)}`}>
            {systemHealth.status.toUpperCase()}
          </div>
          <div className="text-sm text-gray-600">System Status</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {systemHealth.averageResponseTime.toFixed(0)}ms
          </div>
          <div className="text-sm text-gray-600">Avg Response</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {systemHealth.overallUptime.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Overall Uptime</div>
        </div>
      </div>

      {systemHealth.criticalServicesDown > 0 && (
        <div className="mt-4 p-3 bg-red-100 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="text-red-800 font-medium">
              {systemHealth.criticalServicesDown} critical service{systemHealth.criticalServicesDown > 1 ? 's' : ''} down
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

// Alert notification component
const AlertNotification: React.FC<{ alert: any; onDismiss: () => void }> = ({ alert, onDismiss }) => {
  const severityColors = {
    critical: 'bg-red-100 border-red-500 text-red-700',
    warning: 'bg-yellow-100 border-yellow-500 text-yellow-700',
    info: 'bg-blue-100 border-blue-500 text-blue-700'
  };

  return (
    <div className={`p-4 border-l-4 ${severityColors[alert.severity]} mb-2`}>
      <div className="flex justify-between items-start">
        <div>
          <div className="font-medium">{alert.type.replace('_', ' ').toUpperCase()}</div>
          <div className="text-sm mt-1">{alert.message}</div>
          <div className="text-xs mt-1 opacity-75">
            {new Date(alert.timestamp).toLocaleTimeString()}
          </div>
        </div>
        <button
          onClick={onDismiss}
          className="text-gray-400 hover:text-gray-600"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  );
};

// Main dashboard component
export const HealthMonitorDashboard: React.FC = () => {
  const [healthResults, setHealthResults] = useState<Record<string, HealthCheckResult>>({});
  const [serviceMetrics, setServiceMetrics] = useState<Record<string, ServiceMetrics>>({});
  const [systemHealth, setSystemHealth] = useState<any>({});
  const [alerts, setAlerts] = useState<any[]>([]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Handle new alerts
  const handleAlert = useCallback((alert: any) => {
    setAlerts(prev => [alert, ...prev.slice(0, 9)]); // Keep last 10 alerts
  }, []);

  // Dismiss alert
  const dismissAlert = useCallback((index: number) => {
    setAlerts(prev => prev.filter((_, i) => i !== index));
  }, []);

  // Update dashboard data
  const updateDashboard = useCallback(async () => {
    try {
      const results = await healthMonitor.checkAllServices();
      const metrics = healthMonitor.getServiceMetrics() as Record<string, ServiceMetrics>;
      const system = healthMonitor.getSystemHealth();

      setHealthResults(results);
      setServiceMetrics(metrics);
      setSystemHealth(system);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to update dashboard:', error);
    }
  }, []);

  // Start/stop monitoring
  const toggleMonitoring = useCallback(() => {
    if (isMonitoring) {
      healthMonitor.stopMonitoring();
      setIsMonitoring(false);
    } else {
      healthMonitor.startMonitoring(30000); // 30 second intervals
      setIsMonitoring(true);
    }
  }, [isMonitoring]);

  // Initialize dashboard
  useEffect(() => {
    // Set up alert handler
    healthMonitor.onAlert(handleAlert);

    // Initial data load
    updateDashboard();

    // Start monitoring by default
    healthMonitor.startMonitoring(30000);
    setIsMonitoring(true);

    return () => {
      healthMonitor.stopMonitoring();
      healthMonitor.removeAlert(handleAlert);
    };
  }, [handleAlert, updateDashboard]);

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">ACGS Health Monitor</h1>
            <p className="text-gray-600 mt-1">
              Real-time monitoring of all 7 ACGS core services
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {lastUpdate && (
              <div className="text-sm text-gray-500">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </div>
            )}
            <button
              onClick={updateDashboard}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Refresh
            </button>
            <button
              onClick={toggleMonitoring}
              className={`px-4 py-2 rounded-lg transition-colors ${
                isMonitoring 
                  ? 'bg-red-600 text-white hover:bg-red-700' 
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
            </button>
          </div>
        </div>

        {/* System Overview */}
        <div className="mb-6">
          <SystemOverview systemHealth={systemHealth} />
        </div>

        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-3">Recent Alerts</h2>
            <div className="bg-white rounded-lg shadow-sm border p-4">
              {alerts.map((alert, index) => (
                <AlertNotification
                  key={`${alert.service}-${alert.type}-${alert.timestamp}`}
                  alert={alert}
                  onDismiss={() => dismissAlert(index)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Service Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {Object.keys(ACGS_SERVICES).map(serviceKey => {
            const result = healthResults[serviceKey];
            const metrics = serviceMetrics[serviceKey];
            
            if (!result || !metrics) return null;

            return (
              <ServiceCard
                key={serviceKey}
                serviceKey={serviceKey}
                result={result}
                metrics={metrics}
              />
            );
          })}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>ACGS Health Monitor v1.0 - Monitoring interval: 30 seconds</p>
          <p>Performance targets: &lt;500ms response time, &gt;99.5% uptime</p>
        </div>
      </div>
    </div>
  );
};

export default HealthMonitorDashboard;
