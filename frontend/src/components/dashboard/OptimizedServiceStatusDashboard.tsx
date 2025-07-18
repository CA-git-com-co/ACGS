'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useConstitutionalCompliance } from '@/hooks/useConstitutionalCompliance';
import { CONFIG, SERVICES, getServiceUrl } from '@/config';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

interface ServiceStatus {
  name: string;
  port: number;
  status: 'healthy' | 'degraded' | 'down';
  latency: number;
  uptime: number;
  constitutionalCompliance: boolean;
  lastChecked: string;
  responseTime: number;
}

// Memoized service status card component
const ServiceStatusCard = React.memo(({ service }: { service: ServiceStatus }) => {
  const statusColor = useMemo(() => {
    switch (service.status) {
      case 'healthy': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'down': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  }, [service.status]);

  const isLatencyOptimal = useMemo(() => 
    service.latency <= CONFIG.performance.latencyP99Target, 
    [service.latency]
  );

  return (
    <Card className="border-l-4 border-l-blue-500 transition-all hover:shadow-lg">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{service.name}</CardTitle>
          <Badge className={statusColor}>
            {service.status}
          </Badge>
        </div>
        <p className="text-sm text-gray-600">Port {service.port}</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-sm">Latency:</span>
            <span className={`text-sm font-mono ${isLatencyOptimal ? 'text-green-600' : 'text-red-600'}`}>
              {service.latency}ms
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm">Uptime:</span>
            <span className="text-sm font-mono">{service.uptime}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm">Response Time:</span>
            <span className="text-sm font-mono">{service.responseTime}ms</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm">Constitutional:</span>
            <Badge variant={service.constitutionalCompliance ? 'default' : 'destructive'}>
              {service.constitutionalCompliance ? 'Compliant' : 'Violation'}
            </Badge>
          </div>
          <div className="text-xs text-gray-500">
            <span suppressHydrationWarning>Last checked: {new Date(service.lastChecked).toLocaleTimeString()}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

ServiceStatusCard.displayName = 'ServiceStatusCard';

// Main dashboard component with optimizations
export const OptimizedServiceStatusDashboard = React.memo(() => {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { validateCompliance } = useConstitutionalCompliance();
  const { subscribe, send, isConnected } = useWebSocket();

  // Memoize core services configuration
  const coreServices = useMemo(() => [
    { name: 'Constitutional AI', port: 8001, key: 'CONSTITUTIONAL_AI' as const },
    { name: 'Integrity Service', port: 8002, key: 'INTEGRITY_SERVICE' as const },
    { name: 'Multi-Agent Coordinator', port: 8008, key: 'MULTI_AGENT_COORDINATOR' as const },
    { name: 'Worker Agents', port: 8009, key: 'WORKER_AGENTS' as const },
    { name: 'API Gateway', port: 8010, key: 'API_GATEWAY' as const },
    { name: 'Authentication', port: 8016, key: 'AUTHENTICATION' as const },
  ], []);

  // Memoized service status update handler
  const handleServiceStatusUpdate = useCallback((data: { services: ServiceStatus[] }) => {
    setServices(prevServices => {
      // Only update if services have actually changed
      const hasChanges = data.services.some((newService, index) => {
        const prevService = prevServices[index];
        return !prevService || 
               prevService.status !== newService.status ||
               prevService.latency !== newService.latency ||
               prevService.uptime !== newService.uptime ||
               prevService.constitutionalCompliance !== newService.constitutionalCompliance;
      });

      return hasChanges ? data.services : prevServices;
    });
    setIsLoading(false);
    setError(null);
  }, []);

  // Memoized error handler
  const handleError = useCallback((error: string) => {
    setError(error);
    setIsLoading(false);
  }, []);

  // Effect for WebSocket subscription
  useEffect(() => {
    if (!isConnected) return;

    const unsubscribe = subscribe('service-status', handleServiceStatusUpdate);
    const unsubscribeError = subscribe('service-status-error', handleError);

    // Request initial status
    send('get-service-status', { constitutionalHash: CONFIG.constitutional.hash });

    return () => {
      unsubscribe();
      unsubscribeError();
    };
  }, [isConnected, subscribe, send, handleServiceStatusUpdate, handleError]);

  // Periodic health check effect
  useEffect(() => {
    if (!CONFIG.features.enablePerformanceMonitoring) return;

    const interval = setInterval(() => {
      if (isConnected) {
        send('get-service-status', { constitutionalHash: CONFIG.constitutional.hash });
      }
    }, CONFIG.polling.dashboardInterval);

    return () => clearInterval(interval);
  }, [isConnected, send]);

  // Memoized summary statistics
  const summaryStats = useMemo(() => {
    const total = services.length;
    const healthy = services.filter(s => s.status === 'healthy').length;
    const degraded = services.filter(s => s.status === 'degraded').length;
    const down = services.filter(s => s.status === 'down').length;
    const compliant = services.filter(s => s.constitutionalCompliance).length;
    const avgLatency = services.reduce((acc, s) => acc + s.latency, 0) / total || 0;
    const avgUptime = services.reduce((acc, s) => acc + s.uptime, 0) / total || 0;

    return {
      total,
      healthy,
      degraded,
      down,
      compliant,
      avgLatency,
      avgUptime,
      healthyPercentage: total > 0 ? (healthy / total) * 100 : 0,
      compliancePercentage: total > 0 ? (compliant / total) * 100 : 0,
    };
  }, [services]);

  // Loading state
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i} className="border-l-4 border-l-gray-300 animate-pulse">
            <CardHeader className="pb-3">
              <div className="h-6 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Array.from({ length: 4 }).map((_, j) => (
                  <div key={j} className="flex justify-between">
                    <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <Card className="border-red-200">
        <CardContent className="pt-6">
          <div className="text-center">
            <p className="text-red-600 mb-2">Failed to load service status</p>
            <p className="text-sm text-gray-600">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        {/* Summary Statistics */}
        <Card className="bg-gradient-to-r from-blue-50 to-indigo-50">
          <CardHeader>
            <CardTitle className="text-lg">System Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-green-600">{summaryStats.healthy}</div>
                <div className="text-sm text-gray-600">Healthy</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-600">{summaryStats.degraded}</div>
                <div className="text-sm text-gray-600">Degraded</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-600">{summaryStats.down}</div>
                <div className="text-sm text-gray-600">Down</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">{summaryStats.compliant}</div>
                <div className="text-sm text-gray-600">Compliant</div>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-semibold">{summaryStats.avgLatency.toFixed(1)}ms</div>
                <div className="text-sm text-gray-600">Avg Latency</div>
              </div>
              <div>
                <div className="text-lg font-semibold">{summaryStats.avgUptime.toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Avg Uptime</div>
              </div>
              <div>
                <div className="text-lg font-semibold">{summaryStats.compliancePercentage.toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Compliance Rate</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Service Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service) => (
            <ServiceStatusCard key={service.name} service={service} />
          ))}
        </div>

        {/* Connection Status */}
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>
            Connection: {isConnected ? 
              <span className="text-green-600">Connected</span> : 
              <span className="text-red-600">Disconnected</span>
            }
          </span>
          <span>
            <span suppressHydrationWarning>Last updated: {new Date().toLocaleTimeString()}</span>
          </span>
        </div>
      </div>
    </ErrorBoundary>
  );
});

OptimizedServiceStatusDashboard.displayName = 'OptimizedServiceStatusDashboard';

// Export as default for easy replacement
export default OptimizedServiceStatusDashboard;