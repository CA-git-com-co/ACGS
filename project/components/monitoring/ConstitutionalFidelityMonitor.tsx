'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  Activity,
  TrendingUp,
  TrendingDown,
  Wifi,
  WifiOff,
  Clock,
  Shield,
  BarChart3,
  RefreshCw,
} from 'lucide-react';

// Types
interface FidelityScore {
  overall_score: number;
  component_scores: {
    [key: string]: number;
  };
  timestamp: string;
}

interface PerformanceMetrics {
  overall: {
    overall_success_rate: number;
    average_response_time: number;
    total_requests: number;
  };
  services: {
    [key: string]: {
      success_rate: number;
      response_time: number;
      requests: number;
    };
  };
}

interface AlertData {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  violations?: number;
}

interface ViolationAlert {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  details: string;
}

interface FidelityHistoryPoint {
  score: number;
  timestamp: string;
}

/**
 * Constitutional Fidelity Monitor Component
 *
 * Real-time monitoring dashboard for constitutional compliance with:
 * - Live fidelity score tracking with historical trend analysis
 * - Visual indicators for compliance levels (green: >0.85, amber: 0.70-0.85, red: <0.70)
 * - Alert notifications for violations with <30 second response time
 * - Performance metrics integration with QEC-inspired error correction
 * - WebSocket integration for real-time updates
 */
export const ConstitutionalFidelityMonitor: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [fidelityScores, setFidelityScores] = useState<{ [key: string]: FidelityScore }>({});
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connected' | 'error'>(
    'disconnected'
  );

  // Enhanced state for historical tracking and real-time monitoring
  const [fidelityHistory, setFidelityHistory] = useState<FidelityHistoryPoint[]>([]);
  const [currentFidelityScore, setCurrentFidelityScore] = useState<number | null>(null);
  const [alertLevel, setAlertLevel] = useState<'green' | 'amber' | 'red'>('green');
  const [violationCount, setViolationCount] = useState(0);
  const [violationAlerts, setViolationAlerts] = useState<ViolationAlert[]>([]);
  const [lastUpdateTime, setLastUpdateTime] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30); // 30 seconds

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const maxReconnectAttempts = 5;
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  // Fidelity thresholds for alert levels
  const FIDELITY_THRESHOLDS = {
    green: 0.85,
    amber: 0.7,
    red: 0.55,
  };

  // Enhanced WebSocket connection management with auto-refresh
  useEffect(() => {
    connectWebSocket();

    if (autoRefresh) {
      startAutoRefresh();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, []);

  // Auto-refresh management
  useEffect(() => {
    if (autoRefresh && isConnected) {
      startAutoRefresh();
    } else {
      stopAutoRefresh();
    }

    return () => stopAutoRefresh();
  }, [autoRefresh, isConnected, refreshInterval]);

  const startAutoRefresh = useCallback(() => {
    stopAutoRefresh();
    refreshIntervalRef.current = setInterval(() => {
      if (isConnected) {
        sendMessage({ type: 'get_performance_metrics' });
        sendMessage({ type: 'get_fidelity_status' });
      }
    }, refreshInterval * 1000);
  }, [isConnected, refreshInterval]);

  const stopAutoRefresh = useCallback(() => {
    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
      refreshIntervalRef.current = null;
    }
  }, []);

  const connectWebSocket = () => {
    try {
      // Use environment variable or default to localhost
      const wsUrl =
        process.env.NEXT_PUBLIC_FIDELITY_MONITOR_WS_URL ||
        `ws://localhost:8004/api/v1/ws/fidelity-monitor`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('Constitutional Fidelity Monitor WebSocket connected');
        setIsConnected(true);
        setConnectionStatus('connected');
        setReconnectAttempts(0);

        // Request initial performance metrics
        sendMessage({
          type: 'get_performance_metrics',
        });
      };

      wsRef.current.onmessage = event => {
        try {
          const message = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        console.log('Constitutional Fidelity Monitor WebSocket disconnected');
        setIsConnected(false);
        setConnectionStatus('disconnected');

        // Attempt to reconnect
        if (reconnectAttempts < maxReconnectAttempts) {
          const delay = Math.pow(2, reconnectAttempts) * 1000; // Exponential backoff
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connectWebSocket();
          }, delay);
        }
      };

      wsRef.current.onerror = error => {
        console.error('Constitutional Fidelity Monitor WebSocket error:', error);
        setConnectionStatus('error');
      };
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      setConnectionStatus('error');
    }
  };

  const sendMessage = (message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  const handleWebSocketMessage = (message: any) => {
    const timestamp = new Date();
    setLastUpdateTime(timestamp);

    switch (message.type) {
      case 'connection_established':
        console.log('Fidelity monitor connection established:', message.session_id);
        // Request initial data
        sendMessage({ type: 'get_performance_metrics' });
        sendMessage({ type: 'get_fidelity_status' });
        break;

      case 'fidelity_update':
        const fidelityScore = message.fidelity_score;
        setFidelityScores(prev => ({
          ...prev,
          [message.workflow_id]: {
            ...fidelityScore,
            timestamp: message.timestamp,
          },
        }));

        // Update current fidelity score and history
        if (fidelityScore.overall_score !== undefined) {
          setCurrentFidelityScore(fidelityScore.overall_score);
          updateFidelityHistory(fidelityScore.overall_score, message.timestamp);
          updateAlertLevel(fidelityScore.overall_score);
        }
        break;

      case 'fidelity_status':
        // Handle comprehensive fidelity status updates
        if (message.current_fidelity_score !== undefined) {
          setCurrentFidelityScore(message.current_fidelity_score);
          updateFidelityHistory(message.current_fidelity_score, timestamp.toISOString());
          updateAlertLevel(message.current_fidelity_score);
        }
        if (message.violation_count !== undefined) {
          setViolationCount(message.violation_count);
        }
        break;

      case 'performance_metrics':
        setPerformanceMetrics(message.metrics);

        // Extract overall fidelity score from performance metrics
        const overallScore = message.metrics?.overall?.overall_success_rate;
        if (overallScore !== undefined) {
          setCurrentFidelityScore(overallScore);
          updateFidelityHistory(overallScore, timestamp.toISOString());
          updateAlertLevel(overallScore);
        }
        break;

      case 'alert':
        setAlerts(prev => [message.alert, ...prev.slice(0, 19)]); // Keep last 20 alerts

        // Update violation count if alert contains violations
        if (message.alert.violations !== undefined) {
          setViolationCount(prev => prev + message.alert.violations);
        }
        break;

      case 'violation_alert':
        setViolationAlerts(prev => [message.alert, ...prev.slice(0, 19)]); // Keep last 20 violation alerts

        // Update violation count
        setViolationCount(prev => prev + 1);

        // Update alert level based on violation severity
        if (message.alert.severity === 'critical') {
          setAlertLevel('red');
        } else if (message.alert.severity === 'high' && alertLevel !== 'red') {
          setAlertLevel('amber');
        }
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  };

  const updateFidelityHistory = (score: number, timestamp: string) => {
    setFidelityHistory(prev => {
      const newPoint = { score, timestamp };
      const updated = [...prev, newPoint];
      // Keep last 50 points for performance
      return updated.slice(-50);
    });
  };

  const updateAlertLevel = (score: number) => {
    if (score >= FIDELITY_THRESHOLDS.green) {
      setAlertLevel('green');
    } else if (score >= FIDELITY_THRESHOLDS.amber) {
      setAlertLevel('amber');
    } else {
      setAlertLevel('red');
    }
  };

  const getAlertLevelColor = (level: string) => {
    switch (level) {
      case 'green':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'amber':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'red':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Wifi className="h-4 w-4 text-green-600" />;
      case 'error':
        return <WifiOff className="h-4 w-4 text-red-600" />;
      default:
        return <WifiOff className="h-4 w-4 text-gray-600" />;
    }
  };

  const handleManualRefresh = () => {
    if (isConnected) {
      sendMessage({ type: 'get_performance_metrics' });
      sendMessage({ type: 'get_fidelity_status' });
    } else {
      connectWebSocket();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Connection Status */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="text-2xl flex items-center">
                <Shield className="h-6 w-6 mr-2 text-blue-600" />
                Constitutional Fidelity Monitor
              </CardTitle>
              <p className="text-muted-foreground mt-1">
                Real-time constitutional compliance and system health monitoring
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm">Auto-refresh</label>
                <Switch checked={autoRefresh} onCheckedChange={setAutoRefresh} />
              </div>
              <div className="flex items-center space-x-2">
                {getConnectionIcon()}
                <span className="text-sm font-medium capitalize">{connectionStatus}</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleManualRefresh}
                disabled={connectionStatus === 'error'}
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Current Status Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Current Fidelity Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div className="text-2xl font-bold">
                {currentFidelityScore !== null
                  ? `${(currentFidelityScore * 100).toFixed(1)}%`
                  : '--'}
              </div>
              {currentFidelityScore !== null && (
                <div className={`p-1 rounded-full ${getAlertLevelColor(alertLevel)}`}>
                  {alertLevel === 'green' && <CheckCircle className="h-4 w-4" />}
                  {alertLevel === 'amber' && <AlertTriangle className="h-4 w-4" />}
                  {alertLevel === 'red' && <XCircle className="h-4 w-4" />}
                </div>
              )}
            </div>
            {currentFidelityScore !== null && (
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${currentFidelityScore * 100}%` }}
                />
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Violations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{violationCount}</div>
            <p className="text-xs text-muted-foreground">{violationAlerts.length} recent alerts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Response Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {performanceMetrics?.overall?.average_response_time
                ? `${performanceMetrics.overall.average_response_time.toFixed(0)}ms`
                : '--'}
            </div>
            <p className="text-xs text-muted-foreground">Average response time</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Last Update</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">
                {lastUpdateTime ? lastUpdateTime.toLocaleTimeString() : 'Never'}
              </span>
            </div>
            <p className="text-xs text-muted-foreground">
              {autoRefresh ? `Auto-refresh: ${refreshInterval}s` : 'Manual refresh only'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>System Health</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>Overall Success Rate</span>
                    <Badge
                      variant={
                        (performanceMetrics?.overall?.overall_success_rate || 0) > 0.95
                          ? 'default'
                          : 'secondary'
                      }
                    >
                      {performanceMetrics?.overall?.overall_success_rate
                        ? `${(performanceMetrics.overall.overall_success_rate * 100).toFixed(1)}%`
                        : 'N/A'}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Total Requests</span>
                    <span className="font-medium">
                      {performanceMetrics?.overall?.total_requests || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Alert Level</span>
                    <Badge variant={alertLevel === 'green' ? 'default' : 'destructive'}>
                      {alertLevel.toUpperCase()}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {alerts.slice(0, 5).map(alert => (
                    <Alert key={alert.id} className="p-3">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription className="text-sm">
                        <div className="flex justify-between items-start">
                          <span>{alert.message}</span>
                          <Badge variant="outline" className="text-xs">
                            {alert.severity}
                          </Badge>
                        </div>
                      </AlertDescription>
                    </Alert>
                  ))}
                  {alerts.length === 0 && (
                    <p className="text-muted-foreground text-sm">No recent alerts</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Service Performance Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              {performanceMetrics?.services ? (
                <div className="space-y-4">
                  {Object.entries(performanceMetrics.services).map(([service, metrics]) => (
                    <div key={service} className="border rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <h4 className="font-semibold capitalize">{service.replace('_', ' ')}</h4>
                        <Badge variant={metrics.success_rate > 0.95 ? 'default' : 'secondary'}>
                          {(metrics.success_rate * 100).toFixed(1)}% success
                        </Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Response Time</span>
                          <div className="font-medium">{metrics.response_time.toFixed(0)}ms</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Requests</span>
                          <div className="font-medium">{metrics.requests}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Success Rate</span>
                          <div className="font-medium">
                            {(metrics.success_rate * 100).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No performance data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Alert History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[...alerts, ...violationAlerts]
                  .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
                  .slice(0, 10)
                  .map(alert => (
                    <div key={alert.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold">{alert.message}</h4>
                        <Badge
                          variant={
                            alert.severity === 'critical'
                              ? 'destructive'
                              : alert.severity === 'high'
                                ? 'destructive'
                                : alert.severity === 'medium'
                                  ? 'secondary'
                                  : 'outline'
                          }
                        >
                          {alert.severity}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {new Date(alert.timestamp).toLocaleString()}
                      </div>
                      {'details' in alert && alert.details && (
                        <div className="text-sm mt-2 p-2 bg-muted rounded">{alert.details}</div>
                      )}
                    </div>
                  ))}
                {alerts.length === 0 && violationAlerts.length === 0 && (
                  <p className="text-muted-foreground">No alerts in history</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Fidelity Score History</CardTitle>
            </CardHeader>
            <CardContent>
              {fidelityHistory.length > 0 ? (
                <div className="space-y-4">
                  <div className="h-64 flex items-center justify-center border rounded">
                    <p className="text-muted-foreground">
                      Chart visualization would be implemented here
                    </p>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Current Score</span>
                      <div className="font-medium">
                        {currentFidelityScore
                          ? `${(currentFidelityScore * 100).toFixed(1)}%`
                          : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Data Points</span>
                      <div className="font-medium">{fidelityHistory.length}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Trend</span>
                      <div className="font-medium flex items-center">
                        {fidelityHistory.length > 1 &&
                        fidelityHistory[fidelityHistory.length - 1].score >
                          fidelityHistory[fidelityHistory.length - 2].score ? (
                          <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-red-600 mr-1" />
                        )}
                        {fidelityHistory.length > 1 ? 'Tracked' : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Last Update</span>
                      <div className="font-medium">
                        {lastUpdateTime ? lastUpdateTime.toLocaleTimeString() : 'Never'}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">No historical data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
