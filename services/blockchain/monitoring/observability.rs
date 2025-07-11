use anchor_lang::prelude::*;
use std::collections::{BTreeMap, VecDeque};

// Comprehensive monitoring and observability system for blockchain governance

// Real-time metrics collection
#[account]
#[derive(InitSpace)]
pub struct MetricsCollector {
    pub performance_metrics: PerformanceMetrics,
    pub business_metrics: BusinessMetrics,
    pub security_metrics: SecurityMetrics,
    pub infrastructure_metrics: InfrastructureMetrics,
    pub last_updated: i64,
    pub collection_interval: u64, // seconds
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct PerformanceMetrics {
    // Latency metrics
    pub average_response_time: u64,  // microseconds
    pub p50_response_time: u64,
    pub p95_response_time: u64,
    pub p99_response_time: u64,
    pub max_response_time: u64,
    
    // Throughput metrics
    pub requests_per_second: u32,
    pub transactions_per_second: u32,
    pub votes_per_second: u32,
    
    // Resource utilization
    pub cpu_usage_percent: u8,
    pub memory_usage_percent: u8,
    pub storage_usage_percent: u8,
    pub network_bandwidth_utilization: u32,
    
    // Error rates
    pub error_rate_percent: u16,      // basis points
    pub timeout_rate_percent: u16,
    pub retry_rate_percent: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct BusinessMetrics {
    // Governance participation
    pub daily_active_voters: u32,
    pub monthly_active_voters: u32,
    pub voter_retention_rate: u16,    // basis points
    pub average_voting_power: u64,
    
    // Proposal metrics
    pub proposals_created_24h: u32,
    pub proposals_finalized_24h: u32,
    pub proposal_success_rate: u16,   // basis points
    pub average_proposal_duration: u64, // seconds
    
    // Economic metrics
    pub total_value_locked: u64,
    pub governance_token_price: u64,
    pub market_cap: u64,
    pub trading_volume_24h: u64,
    
    // Decentralization metrics
    pub nakamoto_coefficient: u32,
    pub gini_coefficient: u16,        // basis points (0-10000)
    pub voting_power_concentration: u16, // Top 10% concentration
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct SecurityMetrics {
    // Attack detection
    pub failed_authorization_attempts: u32,
    pub suspicious_voting_patterns: u32,
    pub potential_sybil_attacks: u32,
    pub flash_loan_attacks_detected: u32,
    
    // System security
    pub circuit_breaker_activations: u32,
    pub emergency_stops_triggered: u32,
    pub governance_attacks_prevented: u32,
    pub multi_sig_violations: u32,
    
    // Audit trail
    pub total_security_events: u64,
    pub critical_security_events: u32,
    pub security_events_resolved: u32,
    pub average_resolution_time: u64, // seconds
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct InfrastructureMetrics {
    // Blockchain metrics
    pub current_slot: u64,
    pub slots_per_second: u32,
    pub transaction_confirmation_time: u32,
    pub network_congestion_level: u8, // 0-100
    
    // Program metrics
    pub program_account_count: u32,
    pub total_program_size: u64,
    pub instruction_count_24h: u64,
    pub compute_units_consumed: u64,
    
    // Storage metrics
    pub account_storage_usage: u64,
    pub program_storage_usage: u64,
    pub rent_exemption_balance: u64,
    pub storage_cost_24h: u64,
}

// Alerting system for proactive monitoring
#[account]
#[derive(InitSpace)]
pub struct AlertingSystem {
    pub alert_rules: Vec<AlertRule>,
    pub active_alerts: Vec<ActiveAlert>,
    pub alert_history: VecDeque<AlertEvent>,
    pub notification_channels: Vec<NotificationChannel>,
    pub escalation_policies: Vec<EscalationPolicy>,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AlertRule {
    pub id: u32,
    pub name: String,
    pub description: String,
    pub metric_type: MetricType,
    pub condition: AlertCondition,
    pub threshold: AlertThreshold,
    pub severity: AlertSeverity,
    pub enabled: bool,
    pub cooldown_period: u64, // seconds
    pub last_triggered: Option<i64>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum MetricType {
    Performance(PerformanceMetricType),
    Business(BusinessMetricType),
    Security(SecurityMetricType),
    Infrastructure(InfrastructureMetricType),
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum PerformanceMetricType {
    ResponseTime,
    Throughput,
    ErrorRate,
    ResourceUtilization,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum BusinessMetricType {
    VoterParticipation,
    ProposalMetrics,
    EconomicMetrics,
    DecentralizationMetrics,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum SecurityMetricType {
    AttackDetection,
    SystemSecurity,
    AuditTrail,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum InfrastructureMetricType {
    BlockchainMetrics,
    ProgramMetrics,
    StorageMetrics,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum AlertCondition {
    GreaterThan,
    LessThan,
    Equals,
    NotEquals,
    PercentageChange,
    RateOfChange,
    Anomaly,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AlertThreshold {
    pub value: f64,
    pub time_window: u64,    // seconds
    pub min_occurrences: u32, // Minimum occurrences before alert
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum AlertSeverity {
    Info,
    Warning,
    Critical,
    Emergency,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ActiveAlert {
    pub id: u64,
    pub rule_id: u32,
    pub triggered_at: i64,
    pub current_value: f64,
    pub threshold_value: f64,
    pub severity: AlertSeverity,
    pub acknowledged: bool,
    pub acknowledged_by: Option<Pubkey>,
    pub acknowledged_at: Option<i64>,
    pub resolved: bool,
    pub resolved_at: Option<i64>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AlertEvent {
    pub alert_id: u64,
    pub event_type: AlertEventType,
    pub timestamp: i64,
    pub user: Option<Pubkey>,
    pub details: String,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum AlertEventType {
    Triggered,
    Acknowledged,
    Resolved,
    Escalated,
    Suppressed,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct NotificationChannel {
    pub id: u32,
    pub name: String,
    pub channel_type: ChannelType,
    pub configuration: String, // JSON configuration
    pub enabled: bool,
    pub rate_limit: Option<RateLimit>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ChannelType {
    Email,
    Slack,
    Discord,
    Webhook,
    SMS,
    PagerDuty,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct RateLimit {
    pub max_notifications: u32,
    pub time_window: u64, // seconds
    pub current_count: u32,
    pub window_start: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct EscalationPolicy {
    pub id: u32,
    pub name: String,
    pub steps: Vec<EscalationStep>,
    pub max_escalations: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct EscalationStep {
    pub delay_minutes: u32,
    pub notification_channels: Vec<u32>,
    pub assignees: Vec<Pubkey>,
}

// Distributed tracing for request flow analysis
#[account]
#[derive(InitSpace)]
pub struct DistributedTracing {
    pub traces: BTreeMap<String, TraceSpan>,
    pub active_traces: u32,
    pub completed_traces_24h: u32,
    pub average_trace_duration: u64,
    pub trace_retention_hours: u32,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct TraceSpan {
    pub trace_id: String,
    pub span_id: String,
    pub parent_span_id: Option<String>,
    pub operation_name: String,
    pub start_time: i64,
    pub end_time: Option<i64>,
    pub duration: Option<u64>,
    pub tags: BTreeMap<String, String>,
    pub logs: Vec<LogEntry>,
    pub status: SpanStatus,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct LogEntry {
    pub timestamp: i64,
    pub level: LogLevel,
    pub message: String,
    pub fields: BTreeMap<String, String>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum LogLevel {
    Trace,
    Debug,
    Info,
    Warn,
    Error,
    Fatal,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum SpanStatus {
    InProgress,
    Completed,
    Error,
    Timeout,
}

// Health check system
#[account]
#[derive(InitSpace)]
pub struct HealthCheckSystem {
    pub health_checks: Vec<HealthCheck>,
    pub overall_health: SystemHealth,
    pub health_history: VecDeque<HealthSnapshot>,
    pub last_check: i64,
    pub check_interval: u64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct HealthCheck {
    pub id: u32,
    pub name: String,
    pub check_type: HealthCheckType,
    pub status: HealthStatus,
    pub last_success: Option<i64>,
    pub last_failure: Option<i64>,
    pub failure_count: u32,
    pub success_rate: u16, // basis points
    pub response_time: Option<u64>,
    pub enabled: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum HealthCheckType {
    Database,
    ExternalAPI,
    InternalService,
    NetworkConnectivity,
    ResourceAvailability,
    DataConsistency,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum HealthStatus {
    Healthy,
    Warning,
    Critical,
    Unknown,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct SystemHealth {
    pub overall_status: HealthStatus,
    pub healthy_checks: u32,
    pub warning_checks: u32,
    pub critical_checks: u32,
    pub unknown_checks: u32,
    pub last_updated: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct HealthSnapshot {
    pub timestamp: i64,
    pub overall_status: HealthStatus,
    pub component_statuses: BTreeMap<String, HealthStatus>,
    pub response_times: BTreeMap<String, u64>,
}

// Custom metrics for domain-specific monitoring
#[account]
#[derive(InitSpace)]
pub struct CustomMetrics {
    pub governance_metrics: GovernanceSpecificMetrics,
    pub user_experience_metrics: UserExperienceMetrics,
    pub economic_health_metrics: EconomicHealthMetrics,
    pub compliance_metrics: ComplianceMetrics,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct GovernanceSpecificMetrics {
    pub proposal_lifecycle_metrics: ProposalLifecycleMetrics,
    pub voting_pattern_metrics: VotingPatternMetrics,
    pub delegation_metrics: DelegationMetrics,
    pub reputation_metrics: ReputationMetrics,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ProposalLifecycleMetrics {
    pub average_proposal_creation_time: u64,
    pub average_voting_duration: u64,
    pub average_finalization_time: u64,
    pub proposal_abandonment_rate: u16, // basis points
    pub proposal_amendment_rate: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct VotingPatternMetrics {
    pub vote_distribution_variance: u32,
    pub last_minute_voting_percentage: u16,
    pub vote_changing_frequency: u16,
    pub abstention_rate: u16,
    pub delegate_voting_percentage: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct DelegationMetrics {
    pub total_delegations: u32,
    pub average_delegation_duration: u64,
    pub delegation_concentration: u16, // Top 10% delegates
    pub delegation_turnover_rate: u16,
    pub circular_delegation_count: u32,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ReputationMetrics {
    pub average_reputation_score: u64,
    pub reputation_variance: u32,
    pub reputation_growth_rate: i16, // Can be negative
    pub top_contributor_count: u32,
    pub reputation_decay_rate: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct UserExperienceMetrics {
    pub user_journey_metrics: UserJourneyMetrics,
    pub interface_performance: InterfacePerformance,
    pub user_satisfaction: UserSatisfaction,
    pub accessibility_metrics: AccessibilityMetrics,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct UserJourneyMetrics {
    pub proposal_creation_completion_rate: u16,
    pub voting_flow_completion_rate: u16,
    pub delegation_setup_completion_rate: u16,
    pub average_time_to_first_vote: u64,
    pub user_onboarding_completion_rate: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct InterfacePerformance {
    pub page_load_times: BTreeMap<String, u32>,
    pub interaction_response_times: BTreeMap<String, u32>,
    pub error_rates_by_feature: BTreeMap<String, u16>,
    pub mobile_performance_scores: u16,
    pub accessibility_scores: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct UserSatisfaction {
    pub net_promoter_score: i16,
    pub user_satisfaction_score: u16,
    pub feature_adoption_rates: BTreeMap<String, u16>,
    pub support_ticket_volume: u32,
    pub user_feedback_sentiment: i16, // -100 to +100
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AccessibilityMetrics {
    pub wcag_compliance_score: u16,
    pub keyboard_navigation_coverage: u16,
    pub screen_reader_compatibility: u16,
    pub mobile_accessibility_score: u16,
    pub multilingual_support_coverage: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct EconomicHealthMetrics {
    pub token_economics: TokenEconomics,
    pub liquidity_metrics: LiquidityMetrics,
    pub market_health: MarketHealth,
    pub risk_metrics: RiskMetrics,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct TokenEconomics {
    pub token_velocity: u32,
    pub stake_ratio: u16,
    pub inflation_rate: u16,
    pub burn_rate: u16,
    pub utility_score: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct LiquidityMetrics {
    pub order_book_depth: u64,
    pub bid_ask_spread: u32,
    pub market_impact: u32,
    pub liquidity_provider_count: u32,
    pub daily_trading_volume: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct MarketHealth {
    pub price_volatility: u32,
    pub market_cap_stability: u16,
    pub correlation_with_market: i16,
    pub whale_activity_level: u16,
    pub market_manipulation_score: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct RiskMetrics {
    pub concentration_risk: u16,
    pub liquidity_risk: u16,
    pub operational_risk: u16,
    pub smart_contract_risk: u16,
    pub governance_attack_risk: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ComplianceMetrics {
    pub regulatory_compliance: RegulatoryCompliance,
    pub audit_metrics: AuditMetrics,
    pub transparency_metrics: TransparencyMetrics,
    pub data_protection_metrics: DataProtectionMetrics,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct RegulatoryCompliance {
    pub kyc_completion_rate: u16,
    pub aml_screening_coverage: u16,
    pub reporting_timeliness: u16,
    pub regulatory_breach_count: u32,
    pub compliance_score: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AuditMetrics {
    pub last_audit_date: i64,
    pub audit_findings_count: u32,
    pub critical_findings_resolved: u32,
    pub audit_score: u16,
    pub time_to_resolve_findings: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct TransparencyMetrics {
    pub governance_transparency_score: u16,
    pub financial_transparency_score: u16,
    pub decision_transparency_score: u16,
    pub public_disclosure_timeliness: u16,
    pub stakeholder_communication_score: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct DataProtectionMetrics {
    pub privacy_compliance_score: u16,
    pub data_breach_count: u32,
    pub data_retention_compliance: u16,
    pub user_consent_rate: u16,
    pub data_portability_requests: u32,
}

// Implementation of monitoring system
impl MetricsCollector {
    pub fn record_performance_metric(&mut self, metric_type: &str, value: u64) -> Result<()> {
        match metric_type {
            "response_time" => {
                self.update_response_time_metrics(value)?;
            }
            "throughput" => {
                self.performance_metrics.requests_per_second = value as u32;
            }
            "error_rate" => {
                self.performance_metrics.error_rate_percent = value as u16;
            }
            _ => return Err(ProgramError::InvalidArgument.into()),
        }
        
        self.last_updated = Clock::get()?.unix_timestamp;
        Ok(())
    }

    fn update_response_time_metrics(&mut self, response_time: u64) -> Result<()> {
        // Update response time metrics using sliding window approach
        // This is a simplified implementation
        self.performance_metrics.average_response_time = 
            (self.performance_metrics.average_response_time + response_time) / 2;
        
        if response_time > self.performance_metrics.max_response_time {
            self.performance_metrics.max_response_time = response_time;
        }

        Ok(())
    }

    pub fn calculate_health_score(&self) -> u16 {
        let mut score = 10000u32; // Start with perfect score (100.00%)

        // Deduct for high error rates
        if self.performance_metrics.error_rate_percent > 100 { // > 1%
            score = score.saturating_sub(1000);
        }

        // Deduct for high response times
        if self.performance_metrics.p95_response_time > 5000 { // > 5ms
            score = score.saturating_sub(500);
        }

        // Deduct for low throughput
        if self.performance_metrics.requests_per_second < 100 {
            score = score.saturating_sub(300);
        }

        std::cmp::min(score, 10000) as u16
    }
}

impl AlertingSystem {
    pub fn evaluate_alert_rules(&mut self, metrics: &MetricsCollector) -> Result<Vec<u32>> {
        let mut triggered_alerts = Vec::new();
        let current_time = Clock::get()?.unix_timestamp;

        for rule in &self.alert_rules {
            if !rule.enabled {
                continue;
            }

            // Check cooldown period
            if let Some(last_triggered) = rule.last_triggered {
                if current_time - last_triggered < rule.cooldown_period as i64 {
                    continue;
                }
            }

            if self.should_trigger_alert(rule, metrics)? {
                triggered_alerts.push(rule.id);
                self.create_alert(rule, current_time)?;
            }
        }

        Ok(triggered_alerts)
    }

    fn should_trigger_alert(&self, rule: &AlertRule, metrics: &MetricsCollector) -> Result<bool> {
        let current_value = self.get_metric_value(rule, metrics)?;
        
        match rule.condition {
            AlertCondition::GreaterThan => Ok(current_value > rule.threshold.value),
            AlertCondition::LessThan => Ok(current_value < rule.threshold.value),
            AlertCondition::Equals => Ok((current_value - rule.threshold.value).abs() < 0.001),
            AlertCondition::NotEquals => Ok((current_value - rule.threshold.value).abs() >= 0.001),
            _ => Ok(false), // Simplified for complex conditions
        }
    }

    fn get_metric_value(&self, rule: &AlertRule, metrics: &MetricsCollector) -> Result<f64> {
        match &rule.metric_type {
            MetricType::Performance(perf_type) => match perf_type {
                PerformanceMetricType::ResponseTime => 
                    Ok(metrics.performance_metrics.average_response_time as f64),
                PerformanceMetricType::ErrorRate => 
                    Ok(metrics.performance_metrics.error_rate_percent as f64),
                PerformanceMetricType::Throughput => 
                    Ok(metrics.performance_metrics.requests_per_second as f64),
                _ => Ok(0.0),
            },
            _ => Ok(0.0), // Simplified for other metric types
        }
    }

    fn create_alert(&mut self, rule: &AlertRule, timestamp: i64) -> Result<()> {
        let alert_id = self.active_alerts.len() as u64;
        
        let alert = ActiveAlert {
            id: alert_id,
            rule_id: rule.id,
            triggered_at: timestamp,
            current_value: 0.0, // Would be calculated
            threshold_value: rule.threshold.value,
            severity: rule.severity.clone(),
            acknowledged: false,
            acknowledged_by: None,
            acknowledged_at: None,
            resolved: false,
            resolved_at: None,
        };

        self.active_alerts.push(alert);

        // Add to history
        let event = AlertEvent {
            alert_id,
            event_type: AlertEventType::Triggered,
            timestamp,
            user: None,
            details: format!("Alert rule '{}' triggered", rule.name),
        };
        
        self.alert_history.push_back(event);
        
        // Keep history bounded
        if self.alert_history.len() > 1000 {
            self.alert_history.pop_front();
        }

        Ok(())
    }

    pub fn acknowledge_alert(&mut self, alert_id: u64, user: Pubkey) -> Result<()> {
        if let Some(alert) = self.active_alerts.iter_mut().find(|a| a.id == alert_id) {
            if !alert.acknowledged {
                alert.acknowledged = true;
                alert.acknowledged_by = Some(user);
                alert.acknowledged_at = Some(Clock::get()?.unix_timestamp);

                // Add to history
                let event = AlertEvent {
                    alert_id,
                    event_type: AlertEventType::Acknowledged,
                    timestamp: Clock::get()?.unix_timestamp,
                    user: Some(user),
                    details: "Alert acknowledged".to_string(),
                };
                
                self.alert_history.push_back(event);
            }
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metrics_collection() {
        let mut collector = MetricsCollector {
            performance_metrics: PerformanceMetrics {
                average_response_time: 1000,
                error_rate_percent: 50, // 0.5%
                requests_per_second: 200,
                ..Default::default()
            },
            business_metrics: BusinessMetrics::default(),
            security_metrics: SecurityMetrics::default(),
            infrastructure_metrics: InfrastructureMetrics::default(),
            last_updated: 0,
            collection_interval: 60,
            bump: 0,
        };

        assert!(collector.record_performance_metric("response_time", 2000).is_ok());
        assert_eq!(collector.performance_metrics.average_response_time, 1500);

        let health_score = collector.calculate_health_score();
        assert!(health_score > 9000); // Should be high for good metrics
    }

    #[test]
    fn test_alert_system() {
        let mut alerting = AlertingSystem {
            alert_rules: vec![AlertRule {
                id: 1,
                name: "High Error Rate".to_string(),
                description: "Error rate exceeds threshold".to_string(),
                metric_type: MetricType::Performance(PerformanceMetricType::ErrorRate),
                condition: AlertCondition::GreaterThan,
                threshold: AlertThreshold {
                    value: 100.0, // 1%
                    time_window: 300,
                    min_occurrences: 1,
                },
                severity: AlertSeverity::Warning,
                enabled: true,
                cooldown_period: 300,
                last_triggered: None,
            }],
            active_alerts: vec![],
            alert_history: VecDeque::new(),
            notification_channels: vec![],
            escalation_policies: vec![],
            bump: 0,
        };

        let metrics = MetricsCollector {
            performance_metrics: PerformanceMetrics {
                error_rate_percent: 150, // 1.5% - should trigger alert
                ..Default::default()
            },
            business_metrics: BusinessMetrics::default(),
            security_metrics: SecurityMetrics::default(),
            infrastructure_metrics: InfrastructureMetrics::default(),
            last_updated: 0,
            collection_interval: 60,
            bump: 0,
        };

        let triggered = alerting.evaluate_alert_rules(&metrics).unwrap();
        assert_eq!(triggered.len(), 1);
        assert_eq!(triggered[0], 1);
        assert_eq!(alerting.active_alerts.len(), 1);
    }

    #[test]
    fn test_health_check_system() {
        let health_system = HealthCheckSystem {
            health_checks: vec![
                HealthCheck {
                    id: 1,
                    name: "Database Connection".to_string(),
                    check_type: HealthCheckType::Database,
                    status: HealthStatus::Healthy,
                    last_success: Some(Clock::get().unwrap_or_default().unix_timestamp),
                    last_failure: None,
                    failure_count: 0,
                    success_rate: 10000, // 100%
                    response_time: Some(50),
                    enabled: true,
                }
            ],
            overall_health: SystemHealth {
                overall_status: HealthStatus::Healthy,
                healthy_checks: 1,
                warning_checks: 0,
                critical_checks: 0,
                unknown_checks: 0,
                last_updated: Clock::get().unwrap_or_default().unix_timestamp,
            },
            health_history: VecDeque::new(),
            last_check: 0,
            check_interval: 30,
            bump: 0,
        };

        assert_eq!(health_system.overall_health.overall_status, HealthStatus::Healthy);
        assert_eq!(health_system.overall_health.healthy_checks, 1);
    }
}