// programs/logging/src/lib.rs
// Quantumagi Logging System - Comprehensive Event Logging and Monitoring
// Provides audit trail and real-time monitoring for governance events

use anchor_lang::prelude::*;

declare_id!("yAfEigJebmeuEWrkfMiPZcAPcoiMJ3kPHvMT6LTqecG");

#[program]
pub mod logging {
    use super::*;

    /// Log a general governance event
    pub fn log_event(
        ctx: Context<LogEvent>,
        event_type: EventType,
        metadata: String,
        source_program: Pubkey,
    ) -> Result<()> {
        require!(
            metadata.len() <= MAX_METADATA_LENGTH,
            LoggingError::MetadataTooLong
        );

        let log_entry = &mut ctx.accounts.log_entry;
        let clock = Clock::get()?;

        log_entry.id = clock.unix_timestamp as u64;
        log_entry.event_type = event_type.clone();
        log_entry.metadata = metadata;
        log_entry.timestamp = clock.unix_timestamp;
        log_entry.source_program = source_program;
        log_entry.block_height = clock.slot;
        log_entry.logger = ctx.accounts.logger.key();

        // Emit event for real-time monitoring
        emit!(GovernanceEventLogged {
            log_id: log_entry.id,
            event_type: event_type.clone(),
            timestamp: log_entry.timestamp,
            source_program,
            block_height: log_entry.block_height,
        });

        msg!(
            "Event logged: {:?} from {} at {}",
            event_type,
            source_program,
            log_entry.timestamp
        );

        Ok(())
    }

    /// Log policy compliance check metadata
    pub fn emit_metadata_log(
        ctx: Context<EmitMetadataLog>,
        policy_id: u64,
        action_hash: [u8; 32],
        compliance_result: ComplianceResult,
        confidence_score: u8,
        processing_time_ms: u32,
    ) -> Result<()> {
        require!(
            confidence_score <= 100,
            LoggingError::InvalidConfidenceScore
        );

        let metadata_log = &mut ctx.accounts.metadata_log;
        let clock = Clock::get()?;

        metadata_log.id = clock.unix_timestamp as u64;
        metadata_log.policy_id = policy_id;
        metadata_log.action_hash = action_hash;
        metadata_log.compliance_result = compliance_result.clone();
        metadata_log.confidence_score = confidence_score;
        metadata_log.processing_time_ms = processing_time_ms;
        metadata_log.timestamp = clock.unix_timestamp;
        metadata_log.block_height = clock.slot;
        metadata_log.checker = ctx.accounts.checker.key();

        // Emit detailed compliance event
        emit!(ComplianceCheckLogged {
            log_id: metadata_log.id,
            policy_id,
            action_hash,
            compliance_result: compliance_result.clone(),
            confidence_score,
            processing_time_ms,
            timestamp: metadata_log.timestamp,
            checker: metadata_log.checker,
        });

        msg!(
            "Compliance check logged: Policy {} - {:?} ({}% confidence, {}ms)",
            policy_id,
            compliance_result,
            confidence_score,
            processing_time_ms
        );

        Ok(())
    }

    /// Log system performance metrics
    pub fn log_performance_metrics(
        ctx: Context<LogPerformanceMetrics>,
        metrics: PerformanceMetrics,
    ) -> Result<()> {
        let perf_log = &mut ctx.accounts.performance_log;
        let clock = Clock::get()?;

        perf_log.id = clock.unix_timestamp as u64;
        perf_log.metrics = metrics.clone();
        perf_log.timestamp = clock.unix_timestamp;
        perf_log.block_height = clock.slot;
        perf_log.reporter = ctx.accounts.reporter.key();

        // Emit performance metrics event
        emit!(PerformanceMetricsLogged {
            log_id: perf_log.id,
            avg_compliance_check_time: metrics.avg_compliance_check_time,
            total_policies_active: metrics.total_policies_active,
            compliance_success_rate: metrics.compliance_success_rate,
            system_load_percentage: metrics.system_load_percentage,
            timestamp: perf_log.timestamp,
        });

        msg!(
            "Performance metrics logged: {}ms avg, {}% success rate, {}% load",
            metrics.avg_compliance_check_time,
            metrics.compliance_success_rate,
            metrics.system_load_percentage
        );

        Ok(())
    }

    /// Log security alert
    pub fn log_security_alert(
        ctx: Context<LogSecurityAlert>,
        alert_type: SecurityAlertType,
        severity: AlertSeverity,
        description: String,
        affected_policy_id: Option<u64>,
    ) -> Result<()> {
        require!(
            description.len() <= MAX_DESCRIPTION_LENGTH,
            LoggingError::DescriptionTooLong
        );

        let security_log = &mut ctx.accounts.security_log;
        let clock = Clock::get()?;

        security_log.id = clock.unix_timestamp as u64;
        security_log.alert_type = alert_type.clone();
        security_log.severity = severity.clone();
        security_log.description = description;
        security_log.affected_policy_id = affected_policy_id;
        security_log.timestamp = clock.unix_timestamp;
        security_log.block_height = clock.slot;
        security_log.reporter = ctx.accounts.reporter.key();
        security_log.acknowledged = false;

        // Emit security alert event
        emit!(SecurityAlertLogged {
            log_id: security_log.id,
            alert_type: alert_type.clone(),
            severity: severity.clone(),
            affected_policy_id,
            timestamp: security_log.timestamp,
            reporter: security_log.reporter,
        });

        msg!(
            "SECURITY ALERT: {:?} - {:?} severity at {}",
            alert_type,
            severity,
            security_log.timestamp
        );

        Ok(())
    }

    /// Acknowledge a security alert
    pub fn acknowledge_security_alert(
        ctx: Context<AcknowledgeSecurityAlert>,
        acknowledgment_note: String,
    ) -> Result<()> {
        require!(
            acknowledgment_note.len() <= MAX_ACK_NOTE_LENGTH,
            LoggingError::AckNoteTooLong
        );

        let security_log = &mut ctx.accounts.security_log;
        let clock = Clock::get()?;

        require!(
            !security_log.acknowledged,
            LoggingError::AlreadyAcknowledged
        );

        security_log.acknowledged = true;
        security_log.acknowledged_at = Some(clock.unix_timestamp);
        security_log.acknowledged_by = Some(ctx.accounts.acknowledger.key());
        security_log.acknowledgment_note = acknowledgment_note;

        emit!(SecurityAlertAcknowledged {
            log_id: security_log.id,
            acknowledged_by: ctx.accounts.acknowledger.key(),
            acknowledged_at: clock.unix_timestamp,
        });

        msg!(
            "Security alert {} acknowledged by {}",
            security_log.id,
            ctx.accounts.acknowledger.key()
        );

        Ok(())
    }

    /// Get logging statistics
    pub fn get_logging_stats(ctx: Context<GetLoggingStats>) -> Result<()> {
        let stats = &ctx.accounts.logging_stats;

        emit!(LoggingStatsEvent {
            total_events_logged: stats.total_events_logged,
            compliance_checks_logged: stats.compliance_checks_logged,
            security_alerts_logged: stats.security_alerts_logged,
            performance_logs_count: stats.performance_logs_count,
            average_log_processing_time: stats.average_log_processing_time,
            last_updated: stats.last_updated,
        });

        Ok(())
    }
}

// Constants
const MAX_METADATA_LENGTH: usize = 2000;
const MAX_DESCRIPTION_LENGTH: usize = 1000;
const MAX_ACK_NOTE_LENGTH: usize = 500;

// Account Structures

/// General event log entry
#[account]
pub struct LogEntry {
    pub id: u64,
    pub event_type: EventType,
    pub metadata: String,
    pub timestamp: i64,
    pub source_program: Pubkey,
    pub block_height: u64,
    pub logger: Pubkey,
}

/// Compliance check metadata log
#[account]
pub struct MetadataLog {
    pub id: u64,
    pub policy_id: u64,
    pub action_hash: [u8; 32],
    pub compliance_result: ComplianceResult,
    pub confidence_score: u8,
    pub processing_time_ms: u32,
    pub timestamp: i64,
    pub block_height: u64,
    pub checker: Pubkey,
}

/// Performance metrics log
#[account]
pub struct PerformanceLog {
    pub id: u64,
    pub metrics: PerformanceMetrics,
    pub timestamp: i64,
    pub block_height: u64,
    pub reporter: Pubkey,
}

/// Security alert log
#[account]
pub struct SecurityLog {
    pub id: u64,
    pub alert_type: SecurityAlertType,
    pub severity: AlertSeverity,
    pub description: String,
    pub affected_policy_id: Option<u64>,
    pub timestamp: i64,
    pub block_height: u64,
    pub reporter: Pubkey,
    pub acknowledged: bool,
    pub acknowledged_at: Option<i64>,
    pub acknowledged_by: Option<Pubkey>,
    pub acknowledgment_note: String,
}

/// Logging statistics
#[account]
pub struct LoggingStats {
    pub total_events_logged: u64,
    pub compliance_checks_logged: u64,
    pub security_alerts_logged: u64,
    pub performance_logs_count: u64,
    pub average_log_processing_time: u32,
    pub last_updated: i64,
}

// Data Structures

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct PerformanceMetrics {
    pub avg_compliance_check_time: u32,
    pub total_policies_active: u32,
    pub compliance_success_rate: u8,
    pub system_load_percentage: u8,
    pub memory_usage_mb: u32,
    pub cpu_usage_percentage: u8,
}

// Enums

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum EventType {
    ConstitutionInitialized,
    ConstitutionUpdated,
    PolicyProposed,
    PolicyEnacted,
    PolicyDeactivated,
    VoteCast,
    ComplianceCheckPerformed,
    AppealSubmitted,
    AppealResolved,
    SecurityAlert,
    SystemMaintenance,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum ComplianceResult {
    Compliant,
    NonCompliant,
    RequiresReview,
    Error,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum SecurityAlertType {
    UnauthorizedAccess,
    PolicyViolation,
    SystemAnomaly,
    PerformanceDegradation,
    DataIntegrityIssue,
    ConstitutionalViolation,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum AlertSeverity {
    Low,
    Medium,
    High,
    Critical,
}

// Instruction Contexts

/// Context for logging general events
#[derive(Accounts)]
#[instruction(event_type: EventType, metadata: String)]
pub struct LogEvent<'info> {
    #[account(
        init,
        payer = logger,
        space = 8 + 8 + 1 + 4 + metadata.len() + 8 + 32 + 8 + 32,
        seeds = [b"log_entry", Clock::get().unwrap().unix_timestamp.to_le_bytes().as_ref()],
        bump
    )]
    pub log_entry: Account<'info, LogEntry>,
    #[account(mut)]
    pub logger: Signer<'info>,
    pub system_program: Program<'info, System>,
}

/// Context for logging compliance metadata
#[derive(Accounts)]
pub struct EmitMetadataLog<'info> {
    #[account(
        init,
        payer = checker,
        space = 8 + 8 + 8 + 32 + 1 + 1 + 4 + 8 + 8 + 32,
        seeds = [b"metadata_log", Clock::get().unwrap().unix_timestamp.to_le_bytes().as_ref()],
        bump
    )]
    pub metadata_log: Account<'info, MetadataLog>,
    #[account(mut)]
    pub checker: Signer<'info>,
    pub system_program: Program<'info, System>,
}

/// Context for logging performance metrics
#[derive(Accounts)]
pub struct LogPerformanceMetrics<'info> {
    #[account(
        init,
        payer = reporter,
        space = 8 + 8 + (4 + 4 + 1 + 1 + 4 + 1) + 8 + 8 + 32,
        seeds = [b"performance_log", Clock::get().unwrap().unix_timestamp.to_le_bytes().as_ref()],
        bump
    )]
    pub performance_log: Account<'info, PerformanceLog>,
    #[account(mut)]
    pub reporter: Signer<'info>,
    pub system_program: Program<'info, System>,
}

/// Context for logging security alerts
#[derive(Accounts)]
#[instruction(alert_type: SecurityAlertType, severity: AlertSeverity, description: String)]
pub struct LogSecurityAlert<'info> {
    #[account(
        init,
        payer = reporter,
        space = 8 + 8 + 1 + 1 + 4 + description.len() + 9 + 8 + 8 + 32 + 1 + 9 + 33 + 4,
        seeds = [b"security_log", Clock::get().unwrap().unix_timestamp.to_le_bytes().as_ref()],
        bump
    )]
    pub security_log: Account<'info, SecurityLog>,
    #[account(mut)]
    pub reporter: Signer<'info>,
    pub system_program: Program<'info, System>,
}

/// Context for acknowledging security alerts
#[derive(Accounts)]
pub struct AcknowledgeSecurityAlert<'info> {
    #[account(mut)]
    pub security_log: Account<'info, SecurityLog>,
    pub acknowledger: Signer<'info>,
}

/// Context for getting logging statistics
#[derive(Accounts)]
pub struct GetLoggingStats<'info> {
    pub logging_stats: Account<'info, LoggingStats>,
}

// Events

#[event]
pub struct GovernanceEventLogged {
    pub log_id: u64,
    pub event_type: EventType,
    pub timestamp: i64,
    pub source_program: Pubkey,
    pub block_height: u64,
}

#[event]
pub struct ComplianceCheckLogged {
    pub log_id: u64,
    pub policy_id: u64,
    pub action_hash: [u8; 32],
    pub compliance_result: ComplianceResult,
    pub confidence_score: u8,
    pub processing_time_ms: u32,
    pub timestamp: i64,
    pub checker: Pubkey,
}

#[event]
pub struct PerformanceMetricsLogged {
    pub log_id: u64,
    pub avg_compliance_check_time: u32,
    pub total_policies_active: u32,
    pub compliance_success_rate: u8,
    pub system_load_percentage: u8,
    pub timestamp: i64,
}

#[event]
pub struct SecurityAlertLogged {
    pub log_id: u64,
    pub alert_type: SecurityAlertType,
    pub severity: AlertSeverity,
    pub affected_policy_id: Option<u64>,
    pub timestamp: i64,
    pub reporter: Pubkey,
}

#[event]
pub struct SecurityAlertAcknowledged {
    pub log_id: u64,
    pub acknowledged_by: Pubkey,
    pub acknowledged_at: i64,
}

#[event]
pub struct LoggingStatsEvent {
    pub total_events_logged: u64,
    pub compliance_checks_logged: u64,
    pub security_alerts_logged: u64,
    pub performance_logs_count: u64,
    pub average_log_processing_time: u32,
    pub last_updated: i64,
}

// Custom Error Codes
#[error_code]
pub enum LoggingError {
    #[msg("Metadata is too long.")]
    MetadataTooLong,
    #[msg("Description is too long.")]
    DescriptionTooLong,
    #[msg("Acknowledgment note is too long.")]
    AckNoteTooLong,
    #[msg("Invalid confidence score. Must be 0-100.")]
    InvalidConfidenceScore,
    #[msg("Security alert has already been acknowledged.")]
    AlreadyAcknowledged,
}
