/**
 * Alert Notification Center Component
 * 
 * Real-time alert notifications and management interface for ACGS services.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { alertingSystem, Alert, AlertSeverity, AlertType } from '../../services/alertingSystem';

// Alert notification component
const AlertNotification: React.FC<{
  alert: Alert;
  onAcknowledge: (id: string) => void;
  onResolve: (id: string) => void;
  onDismiss: (id: string) => void;
}> = ({ alert, onAcknowledge, onResolve, onDismiss }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getSeverityStyles = (severity: AlertSeverity) => {
    switch (severity) {
      case AlertSeverity.CRITICAL:
        return 'bg-red-100 border-red-500 text-red-900';
      case AlertSeverity.HIGH:
        return 'bg-orange-100 border-orange-500 text-orange-900';
      case AlertSeverity.MEDIUM:
        return 'bg-yellow-100 border-yellow-500 text-yellow-900';
      case AlertSeverity.LOW:
        return 'bg-blue-100 border-blue-500 text-blue-900';
      case AlertSeverity.INFO:
        return 'bg-gray-100 border-gray-500 text-gray-900';
      default:
        return 'bg-gray-100 border-gray-500 text-gray-900';
    }
  };

  const getSeverityIcon = (severity: AlertSeverity) => {
    switch (severity) {
      case AlertSeverity.CRITICAL:
        return '🚨';
      case AlertSeverity.HIGH:
        return '⚠️';
      case AlertSeverity.MEDIUM:
        return '⚡';
      case AlertSeverity.LOW:
        return 'ℹ️';
      case AlertSeverity.INFO:
        return '📢';
      default:
        return '📢';
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className={`border-l-4 p-4 mb-3 rounded-r-lg ${getSeverityStyles(alert.severity)}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <span className="text-2xl">{getSeverityIcon(alert.severity)}</span>
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <h4 className="font-semibold">{alert.title}</h4>
              <span className="px-2 py-1 text-xs bg-white bg-opacity-50 rounded">
                {alert.severity.toUpperCase()}
              </span>
              {alert.service && (
                <span className="px-2 py-1 text-xs bg-white bg-opacity-50 rounded">
                  {alert.service}
                </span>
              )}
            </div>
            <p className="mt-1 text-sm">{alert.message}</p>
            <div className="mt-2 text-xs opacity-75">
              {formatTimestamp(alert.timestamp)}
            </div>
            
            {isExpanded && alert.metadata && (
              <div className="mt-3 p-2 bg-white bg-opacity-30 rounded text-xs">
                <div className="font-medium mb-1">Details:</div>
                <pre className="whitespace-pre-wrap">
                  {JSON.stringify(alert.metadata, null, 2)}
                </pre>
              </div>
            )}

            {alert.actions && alert.actions.length > 0 && (
              <div className="mt-3 space-x-2">
                {alert.actions.map(action => (
                  <button
                    key={action.id}
                    onClick={() => {
                      if (action.type === 'url') {
                        window.open(action.target, '_blank');
                      }
                    }}
                    className="px-3 py-1 text-xs bg-white bg-opacity-50 hover:bg-opacity-75 rounded transition-colors"
                    title={action.description}
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2 ml-4">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 hover:bg-white hover:bg-opacity-30 rounded"
            title="Toggle details"
          >
            <svg className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>

          {!alert.acknowledged && (
            <button
              onClick={() => onAcknowledge(alert.id)}
              className="px-2 py-1 text-xs bg-white bg-opacity-50 hover:bg-opacity-75 rounded transition-colors"
              title="Acknowledge alert"
            >
              ACK
            </button>
          )}

          {!alert.resolved && (
            <button
              onClick={() => onResolve(alert.id)}
              className="px-2 py-1 text-xs bg-white bg-opacity-50 hover:bg-opacity-75 rounded transition-colors"
              title="Resolve alert"
            >
              Resolve
            </button>
          )}

          <button
            onClick={() => onDismiss(alert.id)}
            className="p-1 hover:bg-white hover:bg-opacity-30 rounded"
            title="Dismiss alert"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

      {alert.acknowledged && (
        <div className="mt-2 text-xs opacity-75">
          ✓ Acknowledged {alert.metadata?.acknowledgedBy ? `by ${alert.metadata.acknowledgedBy}` : ''}
          {alert.metadata?.acknowledgedAt && ` at ${formatTimestamp(alert.metadata.acknowledgedAt)}`}
        </div>
      )}

      {alert.resolved && (
        <div className="mt-2 text-xs opacity-75">
          ✅ Resolved {alert.metadata?.resolvedBy ? `by ${alert.metadata.resolvedBy}` : ''}
          {alert.metadata?.resolvedAt && ` at ${formatTimestamp(alert.metadata.resolvedAt)}`}
          {alert.metadata?.resolution && `: ${alert.metadata.resolution}`}
        </div>
      )}
    </div>
  );
};

// Alert statistics component
const AlertStats: React.FC<{ stats: any }> = ({ stats }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
      <div className="bg-white p-3 rounded-lg shadow-sm border text-center">
        <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
        <div className="text-sm text-gray-600">Total Alerts</div>
      </div>
      <div className="bg-red-50 p-3 rounded-lg shadow-sm border text-center">
        <div className="text-2xl font-bold text-red-600">{stats.bySeverity.critical}</div>
        <div className="text-sm text-red-700">Critical</div>
      </div>
      <div className="bg-orange-50 p-3 rounded-lg shadow-sm border text-center">
        <div className="text-2xl font-bold text-orange-600">{stats.bySeverity.high}</div>
        <div className="text-sm text-orange-700">High</div>
      </div>
      <div className="bg-green-50 p-3 rounded-lg shadow-sm border text-center">
        <div className="text-2xl font-bold text-green-600">{stats.resolved}</div>
        <div className="text-sm text-green-700">Resolved</div>
      </div>
      <div className="bg-blue-50 p-3 rounded-lg shadow-sm border text-center">
        <div className="text-2xl font-bold text-blue-600">{stats.acknowledged}</div>
        <div className="text-sm text-blue-700">Acknowledged</div>
      </div>
    </div>
  );
};

// Main alert notification center component
export const AlertNotificationCenter: React.FC<{
  showStats?: boolean;
  maxAlerts?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}> = ({ 
  showStats = true, 
  maxAlerts = 50, 
  autoRefresh = true, 
  refreshInterval = 30000 
}) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<any>({});
  const [filter, setFilter] = useState<{
    severity?: AlertSeverity;
    service?: string;
    resolved?: boolean;
    acknowledged?: boolean;
  }>({});
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize alerting system
  useEffect(() => {
    const initializeAlerting = async () => {
      try {
        await alertingSystem.initialize();
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize alerting system:', error);
      }
    };

    initializeAlerting();

    return () => {
      alertingSystem.cleanup();
    };
  }, []);

  // Load alerts and stats
  const loadData = useCallback(() => {
    if (!isInitialized) return;

    const filteredAlerts = alertingSystem.getAlerts(filter);
    setAlerts(filteredAlerts.slice(0, maxAlerts));
    
    if (showStats) {
      setStats(alertingSystem.getAlertStats());
    }
  }, [isInitialized, filter, maxAlerts, showStats]);

  // Auto-refresh
  useEffect(() => {
    loadData();

    if (autoRefresh) {
      const interval = setInterval(loadData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [loadData, autoRefresh, refreshInterval]);

  // Listen for new alerts
  useEffect(() => {
    const handleNewAlert = (event: CustomEvent) => {
      loadData(); // Refresh data when new alert arrives
    };

    window.addEventListener('acgs-alert', handleNewAlert as EventListener);
    return () => {
      window.removeEventListener('acgs-alert', handleNewAlert as EventListener);
    };
  }, [loadData]);

  // Alert actions
  const handleAcknowledge = useCallback((alertId: string) => {
    alertingSystem.acknowledgeAlert(alertId, 'User');
    loadData();
  }, [loadData]);

  const handleResolve = useCallback((alertId: string) => {
    const resolution = prompt('Enter resolution details (optional):');
    alertingSystem.resolveAlert(alertId, 'User', resolution || undefined);
    loadData();
  }, [loadData]);

  const handleDismiss = useCallback((alertId: string) => {
    // For UI purposes, we'll just acknowledge the alert
    alertingSystem.acknowledgeAlert(alertId, 'User');
    loadData();
  }, [loadData]);

  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600">Initializing alert system...</span>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Alert Center</h1>
            <p className="text-gray-600 mt-1">
              Real-time alerts and notifications for ACGS services
            </p>
          </div>
          <button
            onClick={loadData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>

        {/* Statistics */}
        {showStats && <AlertStats stats={stats} />}

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg shadow-sm border mb-6">
          <div className="flex flex-wrap gap-4">
            <select
              value={filter.severity || ''}
              onChange={(e) => setFilter({ ...filter, severity: e.target.value as AlertSeverity || undefined })}
              className="px-3 py-2 border rounded-md"
            >
              <option value="">All Severities</option>
              <option value={AlertSeverity.CRITICAL}>Critical</option>
              <option value={AlertSeverity.HIGH}>High</option>
              <option value={AlertSeverity.MEDIUM}>Medium</option>
              <option value={AlertSeverity.LOW}>Low</option>
              <option value={AlertSeverity.INFO}>Info</option>
            </select>

            <select
              value={filter.resolved === undefined ? '' : filter.resolved.toString()}
              onChange={(e) => setFilter({ ...filter, resolved: e.target.value === '' ? undefined : e.target.value === 'true' })}
              className="px-3 py-2 border rounded-md"
            >
              <option value="">All Statuses</option>
              <option value="false">Active</option>
              <option value="true">Resolved</option>
            </select>

            <select
              value={filter.acknowledged === undefined ? '' : filter.acknowledged.toString()}
              onChange={(e) => setFilter({ ...filter, acknowledged: e.target.value === '' ? undefined : e.target.value === 'true' })}
              className="px-3 py-2 border rounded-md"
            >
              <option value="">All Acknowledgments</option>
              <option value="false">Unacknowledged</option>
              <option value="true">Acknowledged</option>
            </select>
          </div>
        </div>

        {/* Alerts */}
        <div className="space-y-4">
          {alerts.length === 0 ? (
            <div className="bg-white p-8 rounded-lg shadow-sm border text-center">
              <div className="text-gray-500">
                <svg className="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-lg font-medium">No alerts found</p>
                <p className="text-sm mt-1">All systems are operating normally</p>
              </div>
            </div>
          ) : (
            alerts.map(alert => (
              <AlertNotification
                key={alert.id}
                alert={alert}
                onAcknowledge={handleAcknowledge}
                onResolve={handleResolve}
                onDismiss={handleDismiss}
              />
            ))
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>ACGS Alert Notification Center v1.0</p>
          <p>Auto-refresh: {autoRefresh ? `${refreshInterval / 1000}s` : 'Disabled'}</p>
        </div>
      </div>
    </div>
  );
};

export default AlertNotificationCenter;
