/**
 * ACGS Automated Alerting System
 *
 * Comprehensive alerting system for service failures, performance degradation,
 * and critical system events across all ACGS services.
 */

import { healthMonitor, HealthCheckResult, ServiceMetrics } from './healthMonitor';

// Alert severity levels
export enum AlertSeverity {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
  INFO = 'info'
}

// Alert types
export enum AlertType {
  SERVICE_DOWN = 'service_down',
  SERVICE_DEGRADED = 'service_degraded',
  SERVICE_RECOVERED = 'service_recovered',
  RESPONSE_TIME = 'response_time',
  ERROR_RATE = 'error_rate',
  UPTIME = 'uptime',
  CONSECUTIVE_FAILURES = 'consecutive_failures',
  QUANTUMAGI_FAILURE = 'quantumagi_failure',
  CONSTITUTIONAL_COMPLIANCE = 'constitutional_compliance',
  SYSTEM_OVERLOAD = 'system_overload',
  SECURITY_BREACH = 'security_breach'
}

// Alert interface
export interface Alert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  service?: string;
  title: string;
  message: string;
  timestamp: number;
  acknowledged: boolean;
  resolved: boolean;
  metadata?: Record<string, any>;
  actions?: AlertAction[];
}

// Alert action interface
export interface AlertAction {
  id: string;
  label: string;
  type: 'url' | 'command' | 'callback';
  target: string;
  description?: string;
}

// Alert channel interface
export interface AlertChannel {
  id: string;
  name: string;
  type: 'email' | 'slack' | 'webhook' | 'console' | 'browser';
  enabled: boolean;
  config: Record<string, any>;
  severityFilter: AlertSeverity[];
}

// Alert rule interface
export interface AlertRule {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  conditions: AlertCondition[];
  severity: AlertSeverity;
  channels: string[];
  cooldown: number; // milliseconds
  autoResolve: boolean;
}

// Alert condition interface
export interface AlertCondition {
  metric: string;
  operator: 'gt' | 'lt' | 'eq' | 'ne' | 'gte' | 'lte';
  threshold: number;
  duration?: number; // milliseconds
}

// Alert configuration
export interface AlertConfig {
  enabled: boolean;
  defaultChannels: string[];
  escalationRules: EscalationRule[];
  retentionDays: number;
  maxAlertsPerHour: number;
  suppressDuplicates: boolean;
  duplicateWindow: number; // milliseconds
}

// Escalation rule interface
export interface EscalationRule {
  id: string;
  severity: AlertSeverity;
  escalateAfter: number; // milliseconds
  escalateTo: string[]; // channel IDs
  maxEscalations: number;
}

// Default alert configuration
const DEFAULT_ALERT_CONFIG: AlertConfig = {
  enabled: true,
  defaultChannels: ['console', 'browser'],
  escalationRules: [
    {
      id: 'critical-escalation',
      severity: AlertSeverity.CRITICAL,
      escalateAfter: 300000, // 5 minutes
      escalateTo: ['email', 'slack'],
      maxEscalations: 3
    }
  ],
  retentionDays: 30,
  maxAlertsPerHour: 100,
  suppressDuplicates: true,
  duplicateWindow: 300000 // 5 minutes
};

// Default alert rules
const DEFAULT_ALERT_RULES: AlertRule[] = [
  {
    id: 'service-down',
    name: 'Service Down',
    description: 'Alert when a service becomes unavailable',
    enabled: true,
    conditions: [{ metric: 'service_status', operator: 'eq', threshold: 0 }],
    severity: AlertSeverity.CRITICAL,
    channels: ['console', 'browser', 'email'],
    cooldown: 60000, // 1 minute
    autoResolve: true
  },
  {
    id: 'high-response-time',
    name: 'High Response Time',
    description: 'Alert when response time exceeds threshold',
    enabled: true,
    conditions: [{ metric: 'response_time', operator: 'gt', threshold: 2000, duration: 120000 }],
    severity: AlertSeverity.HIGH,
    channels: ['console', 'browser'],
    cooldown: 300000, // 5 minutes
    autoResolve: true
  },
  {
    id: 'high-error-rate',
    name: 'High Error Rate',
    description: 'Alert when error rate exceeds threshold',
    enabled: true,
    conditions: [{ metric: 'error_rate', operator: 'gt', threshold: 5, duration: 180000 }],
    severity: AlertSeverity.HIGH,
    channels: ['console', 'browser'],
    cooldown: 300000, // 5 minutes
    autoResolve: true
  },
  {
    id: 'low-uptime',
    name: 'Low Uptime',
    description: 'Alert when service uptime falls below threshold',
    enabled: true,
    conditions: [{ metric: 'uptime', operator: 'lt', threshold: 99.5 }],
    severity: AlertSeverity.MEDIUM,
    channels: ['console', 'browser'],
    cooldown: 600000, // 10 minutes
    autoResolve: true
  },
  {
    id: 'quantumagi-failure',
    name: 'Quantumagi System Failure',
    description: 'Critical alert for Quantumagi Solana integration failures',
    enabled: true,
    conditions: [{ metric: 'quantumagi_health', operator: 'eq', threshold: 0 }],
    severity: AlertSeverity.CRITICAL,
    channels: ['console', 'browser', 'email', 'slack'],
    cooldown: 30000, // 30 seconds
    autoResolve: false
  }
];

// Default alert channels
const DEFAULT_ALERT_CHANNELS: AlertChannel[] = [
  {
    id: 'console',
    name: 'Console Logging',
    type: 'console',
    enabled: true,
    config: { logLevel: 'warn' },
    severityFilter: [AlertSeverity.CRITICAL, AlertSeverity.HIGH, AlertSeverity.MEDIUM]
  },
  {
    id: 'browser',
    name: 'Browser Notifications',
    type: 'browser',
    enabled: true,
    config: {
      showNotifications: true,
      playSound: true,
      persistCritical: true
    },
    severityFilter: [AlertSeverity.CRITICAL, AlertSeverity.HIGH]
  }
];

/**
 * ACGS Alerting System Class
 */
export class ACGSAlertingSystem {
  private config: AlertConfig;
  private rules: Map<string, AlertRule> = new Map();
  private channels: Map<string, AlertChannel> = new Map();
  private alerts: Map<string, Alert> = new Map();
  private alertHistory: Alert[] = [];
  private escalationTimers: Map<string, NodeJS.Timeout> = new Map();
  private suppressionCache: Map<string, number> = new Map();
  private isInitialized = false;

  constructor(config: Partial<AlertConfig> = {}) {
    this.config = { ...DEFAULT_ALERT_CONFIG, ...config };
    this.initializeDefaults();
  }

  /**
   * Initialize default rules and channels
   */
  private initializeDefaults(): void {
    // Load default rules
    DEFAULT_ALERT_RULES.forEach(rule => {
      this.rules.set(rule.id, rule);
    });

    // Load default channels
    DEFAULT_ALERT_CHANNELS.forEach(channel => {
      this.channels.set(channel.id, channel);
    });
  }

  /**
   * Initialize the alerting system
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Set up health monitor integration
      healthMonitor.onAlert(this.handleHealthMonitorAlert.bind(this));

      // Start periodic cleanup
      this.startPeriodicCleanup();

      this.isInitialized = true;
      console.log('ACGS Alerting System initialized');
    } catch (error) {
      console.error('Failed to initialize alerting system:', error);
      throw error;
    }
  }

  /**
   * Handle alerts from health monitor
   */
  private handleHealthMonitorAlert(healthAlert: any): void {
    const alert: Alert = {
      id: this.generateAlertId(),
      type: this.mapHealthAlertType(healthAlert.type),
      severity: this.mapHealthAlertSeverity(healthAlert.severity),
      service: healthAlert.service,
      title: `${healthAlert.service} Service Alert`,
      message: healthAlert.message,
      timestamp: healthAlert.timestamp || Date.now(),
      acknowledged: false,
      resolved: false,
      metadata: {
        originalAlert: healthAlert,
        responseTime: healthAlert.responseTime,
        threshold: healthAlert.threshold,
        value: healthAlert.value
      },
      actions: this.generateAlertActions(healthAlert)
    };

    this.processAlert(alert);
  }

  /**
   * Process an alert through the system
   */
  private async processAlert(alert: Alert): Promise<void> {
    // Check if alert should be suppressed
    if (this.shouldSuppressAlert(alert)) {
      return;
    }

    // Store alert
    this.alerts.set(alert.id, alert);
    this.alertHistory.unshift(alert);

    // Trim history if needed
    if (this.alertHistory.length > 1000) {
      this.alertHistory = this.alertHistory.slice(0, 1000);
    }

    // Send to channels
    await this.sendToChannels(alert);

    // Set up escalation if needed
    this.setupEscalation(alert);

    // Update suppression cache
    this.updateSuppressionCache(alert);
  }

  /**
   * Send alert to configured channels
   */
  private async sendToChannels(alert: Alert): Promise<void> {
    const applicableRules = this.getApplicableRules(alert);
    const channelIds = new Set<string>();

    // Collect channel IDs from applicable rules
    applicableRules.forEach(rule => {
      rule.channels.forEach(channelId => channelIds.add(channelId));
    });

    // Add default channels if no specific channels found
    if (channelIds.size === 0) {
      this.config.defaultChannels.forEach(channelId => channelIds.add(channelId));
    }

    // Send to each channel
    for (const channelId of channelIds) {
      const channel = this.channels.get(channelId);
      if (channel && channel.enabled && this.shouldSendToChannel(alert, channel)) {
        try {
          await this.sendToChannel(alert, channel);
        } catch (error) {
          console.error(`Failed to send alert to channel ${channelId}:`, error);
        }
      }
    }
  }

  /**
   * Send alert to specific channel
   */
  private async sendToChannel(alert: Alert, channel: AlertChannel): Promise<void> {
    switch (channel.type) {
      case 'console':
        this.sendToConsole(alert, channel);
        break;
      case 'browser':
        this.sendToBrowser(alert, channel);
        break;
      case 'email':
        await this.sendToEmail(alert, channel);
        break;
      case 'slack':
        await this.sendToSlack(alert, channel);
        break;
      case 'webhook':
        await this.sendToWebhook(alert, channel);
        break;
      default:
        console.warn(`Unknown channel type: ${channel.type}`);
    }
  }

  /**
   * Send alert to console
   */
  private sendToConsole(alert: Alert, channel: AlertChannel): void {
    const logLevel = channel.config.logLevel || 'warn';
    const message = `[${alert.severity.toUpperCase()}] ${alert.title}: ${alert.message}`;

    switch (logLevel) {
      case 'error':
        console.error(message, alert);
        break;
      case 'warn':
        console.warn(message, alert);
        break;
      case 'info':
        console.info(message, alert);
        break;
      default:
        console.log(message, alert);
    }
  }

  /**
   * Send alert to browser notifications
   */
  private sendToBrowser(alert: Alert, channel: AlertChannel): void {
    if (typeof window === 'undefined') return;

    // Show browser notification if supported and permitted
    if ('Notification' in window && Notification.permission === 'granted') {
      const notification = new Notification(alert.title, {
        body: alert.message,
        icon: this.getAlertIcon(alert.severity),
        tag: alert.id,
        requireInteraction: alert.severity === AlertSeverity.CRITICAL
      });

      // Auto-close non-critical notifications
      if (alert.severity !== AlertSeverity.CRITICAL) {
        setTimeout(() => notification.close(), 10000);
      }
    }

    // Play sound if configured
    if (channel.config.playSound && alert.severity === AlertSeverity.CRITICAL) {
      this.playAlertSound();
    }

    // Dispatch custom event for UI components
    window.dispatchEvent(
      new CustomEvent('acgs-alert', {
        detail: alert
      })
    );
  }

  /**
   * Send alert to email (placeholder - requires email service integration)
   */
  private async sendToEmail(alert: Alert, channel: AlertChannel): Promise<void> {
    // This would integrate with an email service like SendGrid, AWS SES, etc.
    console.log(`Email alert would be sent: ${alert.title}`);

    // Example implementation:
    // const emailService = new EmailService(channel.config);
    // await emailService.send({
    //   to: channel.config.recipients,
    //   subject: alert.title,
    //   body: this.formatEmailBody(alert)
    // });
  }

  /**
   * Send alert to Slack (placeholder - requires Slack integration)
   */
  private async sendToSlack(alert: Alert, channel: AlertChannel): Promise<void> {
    // This would integrate with Slack API
    console.log(`Slack alert would be sent: ${alert.title}`);

    // Example implementation:
    // const slackService = new SlackService(channel.config);
    // await slackService.sendMessage({
    //   channel: channel.config.channel,
    //   text: alert.message,
    //   attachments: this.formatSlackAttachment(alert)
    // });
  }

  /**
   * Send alert to webhook
   */
  private async sendToWebhook(alert: Alert, channel: AlertChannel): Promise<void> {
    try {
      const response = await fetch(channel.config.url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...channel.config.headers
        },
        body: JSON.stringify({
          alert,
          timestamp: Date.now(),
          source: 'acgs-alerting-system'
        })
      });

      if (!response.ok) {
        throw new Error(`Webhook request failed: ${response.status}`);
      }
    } catch (error) {
      console.error('Webhook alert failed:', error);
      throw error;
    }
  }

  /**
   * Utility methods
   */
  private generateAlertId(): string {
    return `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private mapHealthAlertType(type: string): AlertType {
    const typeMap: Record<string, AlertType> = {
      response_time: AlertType.RESPONSE_TIME,
      error_rate: AlertType.ERROR_RATE,
      uptime: AlertType.UPTIME,
      consecutive_failures: AlertType.CONSECUTIVE_FAILURES,
      service_down: AlertType.SERVICE_DOWN,
      service_degraded: AlertType.SERVICE_DEGRADED
    };
    return typeMap[type] || AlertType.SERVICE_DEGRADED;
  }

  private mapHealthAlertSeverity(severity: string): AlertSeverity {
    const severityMap: Record<string, AlertSeverity> = {
      critical: AlertSeverity.CRITICAL,
      high: AlertSeverity.HIGH,
      warning: AlertSeverity.MEDIUM,
      info: AlertSeverity.INFO
    };
    return severityMap[severity] || AlertSeverity.MEDIUM;
  }

  private generateAlertActions(healthAlert: any): AlertAction[] {
    const actions: AlertAction[] = [
      {
        id: 'view-service',
        label: 'View Service Details',
        type: 'url',
        target: `/health-monitor?service=${healthAlert.service}`,
        description: 'View detailed health information for this service'
      }
    ];

    if (healthAlert.service === 'quantumagi') {
      actions.push({
        id: 'check-solana',
        label: 'Check Solana Connection',
        type: 'url',
        target: '/quantumagi?tab=connection',
        description: 'Verify Solana devnet connectivity'
      });
    }

    return actions;
  }

  private shouldSuppressAlert(alert: Alert): boolean {
    if (!this.config.suppressDuplicates) return false;

    const suppressionKey = `${alert.type}-${alert.service || 'system'}`;
    const lastAlert = this.suppressionCache.get(suppressionKey);

    if (lastAlert && Date.now() - lastAlert < this.config.duplicateWindow) {
      return true;
    }

    return false;
  }

  private updateSuppressionCache(alert: Alert): void {
    const suppressionKey = `${alert.type}-${alert.service || 'system'}`;
    this.suppressionCache.set(suppressionKey, alert.timestamp);
  }

  private getApplicableRules(alert: Alert): AlertRule[] {
    return Array.from(this.rules.values()).filter(rule => {
      if (!rule.enabled) return false;

      // Check if rule applies to this alert type
      return rule.conditions.some(condition => {
        return this.evaluateCondition(condition, alert);
      });
    });
  }

  private evaluateCondition(condition: AlertCondition, alert: Alert): boolean {
    const value = this.getMetricValue(condition.metric, alert);
    if (value === undefined) return false;

    switch (condition.operator) {
      case 'gt':
        return value > condition.threshold;
      case 'lt':
        return value < condition.threshold;
      case 'eq':
        return value === condition.threshold;
      case 'ne':
        return value !== condition.threshold;
      case 'gte':
        return value >= condition.threshold;
      case 'lte':
        return value <= condition.threshold;
      default:
        return false;
    }
  }

  private getMetricValue(metric: string, alert: Alert): number | undefined {
    switch (metric) {
      case 'service_status':
        return alert.type === AlertType.SERVICE_DOWN ? 0 : 1;
      case 'response_time':
        return alert.metadata?.responseTime;
      case 'error_rate':
        return alert.metadata?.value;
      case 'uptime':
        return alert.metadata?.value;
      case 'quantumagi_health':
        return alert.service === 'quantumagi' && alert.type === AlertType.SERVICE_DOWN ? 0 : 1;
      default:
        return undefined;
    }
  }

  private shouldSendToChannel(alert: Alert, channel: AlertChannel): boolean {
    return channel.severityFilter.includes(alert.severity);
  }

  private getAlertIcon(severity: AlertSeverity): string {
    const icons = {
      [AlertSeverity.CRITICAL]: '🚨',
      [AlertSeverity.HIGH]: '⚠️',
      [AlertSeverity.MEDIUM]: '⚡',
      [AlertSeverity.LOW]: 'ℹ️',
      [AlertSeverity.INFO]: '📢'
    };
    return icons[severity] || '📢';
  }

  private playAlertSound(): void {
    if (typeof window === 'undefined') return;

    try {
      const audio = new Audio(
        'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT'
      );
      audio.play().catch(() => {
        // Ignore audio play errors (user interaction required)
      });
    } catch (error) {
      // Ignore audio errors
    }
  }

  private setupEscalation(alert: Alert): void {
    const escalationRules = this.config.escalationRules.filter(
      rule => rule.severity === alert.severity
    );

    escalationRules.forEach(rule => {
      const timer = setTimeout(() => {
        this.escalateAlert(alert, rule);
      }, rule.escalateAfter);

      this.escalationTimers.set(`${alert.id}-${rule.id}`, timer);
    });
  }

  private escalateAlert(alert: Alert, rule: EscalationRule): void {
    // Create escalated alert
    const escalatedAlert: Alert = {
      ...alert,
      id: this.generateAlertId(),
      title: `[ESCALATED] ${alert.title}`,
      message: `Alert escalated after ${rule.escalateAfter / 1000}s: ${alert.message}`,
      timestamp: Date.now(),
      metadata: {
        ...alert.metadata,
        originalAlertId: alert.id,
        escalationRule: rule.id,
        escalationLevel: (alert.metadata?.escalationLevel || 0) + 1
      }
    };

    // Send to escalation channels
    rule.escalateTo.forEach(async channelId => {
      const channel = this.channels.get(channelId);
      if (channel && channel.enabled) {
        try {
          await this.sendToChannel(escalatedAlert, channel);
        } catch (error) {
          console.error(`Failed to escalate alert to channel ${channelId}:`, error);
        }
      }
    });
  }

  private startPeriodicCleanup(): void {
    // Clean up old alerts every hour
    setInterval(() => {
      this.cleanupOldAlerts();
      this.cleanupSuppressionCache();
    }, 3600000); // 1 hour
  }

  private cleanupOldAlerts(): void {
    const cutoffTime = Date.now() - this.config.retentionDays * 24 * 60 * 60 * 1000;

    // Remove old alerts from active alerts
    for (const [id, alert] of this.alerts.entries()) {
      if (alert.timestamp < cutoffTime && alert.resolved) {
        this.alerts.delete(id);
      }
    }

    // Trim alert history
    this.alertHistory = this.alertHistory.filter(alert => alert.timestamp >= cutoffTime);
  }

  private cleanupSuppressionCache(): void {
    const cutoffTime = Date.now() - this.config.duplicateWindow;

    for (const [key, timestamp] of this.suppressionCache.entries()) {
      if (timestamp < cutoffTime) {
        this.suppressionCache.delete(key);
      }
    }
  }

  /**
   * Public API methods
   */

  // Create custom alert
  createAlert(alertData: Partial<Alert>): string {
    const alert: Alert = {
      id: this.generateAlertId(),
      type: AlertType.SYSTEM_OVERLOAD,
      severity: AlertSeverity.MEDIUM,
      title: 'Custom Alert',
      message: 'Custom alert message',
      timestamp: Date.now(),
      acknowledged: false,
      resolved: false,
      ...alertData
    };

    this.processAlert(alert);
    return alert.id;
  }

  // Acknowledge alert
  acknowledgeAlert(alertId: string, acknowledgedBy?: string): boolean {
    const alert = this.alerts.get(alertId);
    if (!alert) return false;

    alert.acknowledged = true;
    alert.metadata = {
      ...alert.metadata,
      acknowledgedBy,
      acknowledgedAt: Date.now()
    };

    // Clear escalation timers
    this.clearEscalationTimers(alertId);

    return true;
  }

  // Resolve alert
  resolveAlert(alertId: string, resolvedBy?: string, resolution?: string): boolean {
    const alert = this.alerts.get(alertId);
    if (!alert) return false;

    alert.resolved = true;
    alert.metadata = {
      ...alert.metadata,
      resolvedBy,
      resolvedAt: Date.now(),
      resolution
    };

    // Clear escalation timers
    this.clearEscalationTimers(alertId);

    return true;
  }

  private clearEscalationTimers(alertId: string): void {
    for (const [key, timer] of this.escalationTimers.entries()) {
      if (key.startsWith(alertId)) {
        clearTimeout(timer);
        this.escalationTimers.delete(key);
      }
    }
  }

  // Get alerts
  getAlerts(filters?: {
    severity?: AlertSeverity;
    service?: string;
    resolved?: boolean;
    acknowledged?: boolean;
  }): Alert[] {
    let alerts = Array.from(this.alerts.values());

    if (filters) {
      if (filters.severity) {
        alerts = alerts.filter(alert => alert.severity === filters.severity);
      }
      if (filters.service) {
        alerts = alerts.filter(alert => alert.service === filters.service);
      }
      if (filters.resolved !== undefined) {
        alerts = alerts.filter(alert => alert.resolved === filters.resolved);
      }
      if (filters.acknowledged !== undefined) {
        alerts = alerts.filter(alert => alert.acknowledged === filters.acknowledged);
      }
    }

    return alerts.sort((a, b) => b.timestamp - a.timestamp);
  }

  // Get alert statistics
  getAlertStats(): {
    total: number;
    bySeverity: Record<AlertSeverity, number>;
    byService: Record<string, number>;
    resolved: number;
    acknowledged: number;
  } {
    const alerts = Array.from(this.alerts.values());

    const stats = {
      total: alerts.length,
      bySeverity: {
        [AlertSeverity.CRITICAL]: 0,
        [AlertSeverity.HIGH]: 0,
        [AlertSeverity.MEDIUM]: 0,
        [AlertSeverity.LOW]: 0,
        [AlertSeverity.INFO]: 0
      },
      byService: {} as Record<string, number>,
      resolved: 0,
      acknowledged: 0
    };

    alerts.forEach(alert => {
      stats.bySeverity[alert.severity]++;

      if (alert.service) {
        stats.byService[alert.service] = (stats.byService[alert.service] || 0) + 1;
      }

      if (alert.resolved) stats.resolved++;
      if (alert.acknowledged) stats.acknowledged++;
    });

    return stats;
  }

  // Add/update alert rule
  addAlertRule(rule: AlertRule): void {
    this.rules.set(rule.id, rule);
  }

  // Add/update alert channel
  addAlertChannel(channel: AlertChannel): void {
    this.channels.set(channel.id, channel);
  }

  // Get configuration
  getConfig(): AlertConfig {
    return { ...this.config };
  }

  // Update configuration
  updateConfig(updates: Partial<AlertConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  // Cleanup resources
  cleanup(): void {
    // Clear all timers
    this.escalationTimers.forEach(timer => clearTimeout(timer));
    this.escalationTimers.clear();

    // Remove health monitor integration
    healthMonitor.removeAlert(this.handleHealthMonitorAlert.bind(this));

    this.isInitialized = false;
  }
}

// Singleton instance
export const alertingSystem = new ACGSAlertingSystem();

// Export default instance
export default alertingSystem;
