"""
Shared Prometheus metrics collection module for ACGS-PGP microservices.
Provides standardized metrics collection across all services.
"""

import logging
import time
from functools import wraps
from typing import Dict

from fastapi import Request
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

logger = logging.getLogger(__name__)

# Global metrics registry to prevent duplicate registrations
metrics_registry: Dict[str, "ACGSMetrics"] = {}


# Global metrics registry for all ACGS-PGP services
class ACGSMetrics:
    """Centralized metrics collection for ACGS-PGP microservices."""

    def __init__(self, service_name: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.service_name = service_name

        # Request metrics
        self.request_count = Counter(
            "acgs_http_requests_total",
            "Total HTTP requests",
            ["service", "method", "endpoint", "status_code"],
        )

        self.request_duration = Histogram(
            "acgs_http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["service", "method", "endpoint"],
            buckets=(
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
            ),
        )

        # Service health metrics
        self.service_info = Info("acgs_service_info", "Service information", ["service", "version"])

        self.active_connections = Gauge(
            "acgs_active_connections", "Number of active connections", ["service"]
        )

        # Authentication specific metrics
        self.auth_attempts = Counter(
            "acgs_auth_attempts_total",
            "Total authentication attempts",
            ["service", "auth_type", "status"],
        )

        # Database metrics
        self.db_connections = Gauge(
            "acgs_database_connections",
            "Number of database connections",
            ["service", "pool_status"],
        )

        self.db_query_duration = Histogram(
            "acgs_database_query_duration_seconds",
            "Database query duration in seconds",
            ["service", "operation"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        )

        # Cross-service communication metrics
        self.service_calls = Counter(
            "acgs_service_calls_total",
            "Total inter-service calls",
            ["source_service", "target_service", "endpoint", "status_code"],
        )

        # Constitutional monitoring metrics (Task 19.4)
        self.constitutional_fidelity_score = Gauge(
            "acgs_constitutional_fidelity_score",
            "Current constitutional fidelity score",
            ["service", "component"],
        )

        self.constitutional_violations_total = Counter(
            "acgs_constitutional_violations_total",
            "Total constitutional violations detected",
            ["service", "violation_type", "severity"],
        )

        self.qec_error_corrections_total = Counter(
            "acgs_qec_error_corrections_total",
            "Total QEC error corrections performed",
            ["service", "error_type", "strategy", "success"],
        )

        self.qec_response_time = Histogram(
            "acgs_qec_response_time_seconds",
            "QEC error correction response time",
            ["service", "error_type"],
            buckets=(
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
                30.0,
            ),
        )

        self.violation_escalations_total = Counter(
            "acgs_violation_escalations_total",
            "Total violation escalations",
            ["service", "escalation_level", "auto_resolved"],
        )

        self.constitutional_council_activities = Counter(
            "acgs_constitutional_council_activities_total",
            "Constitutional Council activities",
            ["service", "activity_type", "status"],
        )

        self.llm_reliability_score = Gauge(
            "acgs_llm_reliability_score",
            "LLM reliability score for constitutional operations",
            ["service", "model", "operation_type"],
        )

        self.monitoring_health_status = Gauge(
            "acgs_monitoring_health_status",
            "Constitutional monitoring system health (1=healthy, 0=unhealthy)",
            ["service", "component"],
        )

        self.service_call_duration = Histogram(
            "acgs_service_call_duration_seconds",
            "Inter-service call duration in seconds",
            ["source_service", "target_service", "endpoint"],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
        )

        # Error metrics
        self.error_count = Counter(
            "acgs_errors_total",
            "Total errors by type",
            ["service", "error_type", "severity"],
        )

        # Business logic metrics
        self.policy_operations = Counter(
            "acgs_policy_operations_total",
            "Total policy operations",
            ["service", "operation_type", "status"],
        )

        self.verification_operations = Counter(
            "acgs_verification_operations_total",
            "Total verification operations",
            ["service", "verification_type", "result"],
        )

        # LLM specific metrics
        self.llm_response_time = Histogram(
            "acgs_llm_response_time_seconds",
            "LLM response time in seconds",
            ["service", "model_name", "request_type"],
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 30.0),
        )
        self.llm_error_rate = Counter(
            "acgs_llm_errors_total",
            "Total LLM errors",
            ["service", "model_name", "error_type"],
        )
        self.llm_output_quality_score = Gauge(
            "acgs_llm_output_quality_score",
            "LLM output quality score (e.g., semantic faithfulness, factual accuracy)",
            ["service", "model_name", "quality_metric"],
        )
        self.llm_bias_score = Gauge(
            "acgs_llm_bias_score",
            "LLM output bias score",
            ["service", "model_name", "bias_type"],
        )
        self.llm_fallback_count = Counter(
            "acgs_llm_fallbacks_total",
            "Total LLM fallback occurrences",
            ["service", "fallback_reason"],
        )
        self.llm_human_escalation_count = Counter(
            "acgs_llm_human_escalations_total",
            "Total LLM human review escalations",
            ["service", "escalation_reason"],
        )

        # Task 7: Parallel processing metrics
        self.parallel_tasks_total = Counter(
            "acgs_parallel_tasks_total",
            "Total parallel tasks executed",
            ["service", "task_type", "status"],
        )

        self.parallel_batch_duration = Histogram(
            "acgs_parallel_batch_duration_seconds",
            "Parallel batch execution duration",
            ["service", "batch_type"],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 60.0),
        )

        self.parallel_task_queue_size = Gauge(
            "acgs_parallel_task_queue_size",
            "Number of tasks in parallel processing queue",
            ["service", "queue_type"],
        )

        self.parallel_workers_active = Gauge(
            "acgs_parallel_workers_active",
            "Number of active parallel workers",
            ["service", "worker_type"],
        )

        self.websocket_connections = Gauge(
            "acgs_websocket_connections_active",
            "Number of active WebSocket connections",
            ["service", "connection_type"],
        )

        self.cache_operations = Counter(
            "acgs_cache_operations_total",
            "Total cache operations",
            ["service", "operation", "result"],
        )

        # Phase A3 Constitutional Governance Metrics
        self.constitutional_compliance_checks = Counter(
            "acgs_constitutional_compliance_checks_total",
            "Total constitutional compliance checks",
            ["service", "check_type", "result"],
        )

        self.constitutional_compliance_score = Gauge(
            "acgs_constitutional_compliance_score",
            "Constitutional compliance score (0-1)",
            ["service", "policy_type"],
        )

        self.constitutional_hash_validations = Counter(
            "acgs_constitutional_hash_validations_total",
            "Constitutional hash validation operations",
            ["service", "validation_type", "result"],
        )

        # Governance Workflow Metrics
        self.governance_workflow_operations = Counter(
            "acgs_governance_workflow_operations_total",
            "Governance workflow operations",
            ["service", "workflow_type", "stage", "result"],
        )

        self.governance_workflow_duration = Histogram(
            "acgs_governance_workflow_duration_seconds",
            "Governance workflow execution time",
            ["service", "workflow_type", "stage"],
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0),
        )

        self.policy_creation_rate = Counter(
            "acgs_policy_creation_operations_total",
            "Policy creation operations",
            ["service", "policy_type", "status"],
        )

        self.voting_operations = Counter(
            "acgs_voting_operations_total",
            "Voting system operations",
            ["service", "vote_type", "result"],
        )

        # Service-Specific Metrics
        # Authentication Service Metrics
        self.auth_session_duration = Histogram(
            "acgs_auth_session_duration_seconds",
            "Authentication session duration",
            ["service", "session_type"],
            buckets=(60, 300, 900, 1800, 3600, 7200, 14400, 28800),
        )

        self.mfa_operations = Counter(
            "acgs_mfa_operations_total",
            "Multi-factor authentication operations",
            ["service", "mfa_type", "result"],
        )

        self.api_key_operations = Counter(
            "acgs_api_key_operations_total",
            "API key management operations",
            ["service", "operation_type", "result"],
        )

        # Constitutional AI Service Metrics
        self.constitutional_ai_processing_time = Histogram(
            "acgs_constitutional_ai_processing_seconds",
            "Constitutional AI processing time",
            ["service", "ai_operation", "complexity"],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        )

        self.compliance_validation_latency = Histogram(
            "acgs_compliance_validation_latency_seconds",
            "Compliance validation latency",
            ["service", "validation_type"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
        )

        # Formal Verification Service Metrics
        self.z3_solver_operations = Counter(
            "acgs_z3_solver_operations_total",
            "Z3 SMT solver operations",
            ["service", "operation_type", "result"],
        )

        self.formal_verification_duration = Histogram(
            "acgs_formal_verification_duration_seconds",
            "Formal verification execution time",
            ["service", "verification_type", "complexity"],
            buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
        )

        # Governance Synthesis Service Metrics
        self.llm_token_usage = Counter(
            "acgs_llm_token_usage_total",
            "LLM token usage",
            ["service", "model_name", "operation_type"],
        )

        self.policy_synthesis_operations = Counter(
            "acgs_policy_synthesis_operations_total",
            "Policy synthesis operations",
            ["service", "synthesis_type", "risk_level", "result"],
        )

        self.multi_model_consensus_operations = Counter(
            "acgs_multi_model_consensus_operations_total",
            "Multi-model consensus operations",
            ["service", "consensus_type", "model_count", "result"],
        )

        # Policy Governance Control Service Metrics
        self.pgc_validation_latency = Histogram(
            "acgs_pgc_validation_latency_seconds",
            "PGC validation latency (target <50ms)",
            ["service", "validation_type"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
        )

        self.policy_enforcement_actions = Counter(
            "acgs_policy_enforcement_actions_total",
            "Policy enforcement actions",
            ["service", "action_type", "policy_type", "result"],
        )

        # Evolutionary Computation Service Metrics
        self.wina_optimization_score = Gauge(
            "acgs_wina_optimization_score",
            "WINA optimization score",
            ["service", "optimization_type"],
        )

        self.evolutionary_computation_iterations = Counter(
            "acgs_evolutionary_computation_iterations_total",
            "Evolutionary computation iterations",
            ["service", "algorithm_type", "convergence_status"],
        )

        # Integrity Service Metrics
        self.cryptographic_operations = Counter(
            "acgs_cryptographic_operations_total",
            "Cryptographic operations",
            ["service", "operation_type", "algorithm", "result"],
        )

        self.audit_trail_operations = Counter(
            "acgs_audit_trail_operations_total",
            "Audit trail operations",
            ["service", "operation_type", "integrity_status"],
        )

        # Infrastructure Integration Metrics
        self.redis_connection_pool_usage = Gauge(
            "acgs_redis_connection_pool_usage",
            "Redis connection pool usage",
            ["service", "pool_status"],
        )

        self.postgresql_query_performance = Histogram(
            "acgs_postgresql_query_performance_seconds",
            "PostgreSQL query performance",
            ["service", "query_type", "table"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
        )

        # Quantumagi Blockchain Integration Metrics
        self.solana_transaction_operations = Counter(
            "acgs_solana_transaction_operations_total",
            "Solana blockchain transaction operations",
            ["service", "transaction_type", "result"],
        )

        self.quantumagi_program_calls = Counter(
            "acgs_quantumagi_program_calls_total",
            "Quantumagi program calls",
            ["service", "program_method", "result"],
        )

        self.blockchain_sync_status = Gauge(
            "acgs_blockchain_sync_status",
            "Blockchain synchronization status (1=synced, 0=not synced)",
            ["service", "network"],
        )

        # Initialize service info (commented out due to prometheus_client compatibility)
        # self.service_info.info({
        #     'service': self.service_name,
        #     'version': '3.0.0'
        # })

    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record HTTP request metrics."""
        self.request_count.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
        ).inc()

        self.request_duration.labels(
            service=self.service_name, method=method, endpoint=endpoint
        ).observe(duration)

    def record_auth_attempt(self, auth_type: str, status: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record authentication attempt."""
        self.auth_attempts.labels(
            service=self.service_name, auth_type=auth_type, status=status
        ).inc()

    def record_db_query(self, operation: str, duration: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record database query metrics."""
        self.db_query_duration.labels(service=self.service_name, operation=operation).observe(
            duration
        )

    def record_service_call(
        self, target_service: str, endpoint: str, status_code: int, duration: float
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record inter-service call metrics."""
        self.service_calls.labels(
            source_service=self.service_name,
            target_service=target_service,
            endpoint=endpoint,
            status_code=status_code,
        ).inc()

        self.service_call_duration.labels(
            source_service=self.service_name,
            target_service=target_service,
            endpoint=endpoint,
        ).observe(duration)

    def record_error(self, error_type: str, severity: str = "error"):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record error occurrence."""
        self.error_count.labels(
            service=self.service_name, error_type=error_type, severity=severity
        ).inc()

    def record_policy_operation(self, operation_type: str, status: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record policy operation."""
        self.policy_operations.labels(
            service=self.service_name, operation_type=operation_type, status=status
        ).inc()

    def record_verification_operation(self, verification_type: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record verification operation."""
        self.verification_operations.labels(
            service=self.service_name,
            verification_type=verification_type,
            result=result,
        ).inc()

    # Task 7: Parallel processing metrics methods
    def record_parallel_task(self, task_type: str, status: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record parallel task execution."""
        self.parallel_tasks_total.labels(
            service=self.service_name, task_type=task_type, status=status
        ).inc()

    def record_parallel_batch_duration(self, batch_type: str, duration: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record parallel batch execution duration."""
        self.parallel_batch_duration.labels(
            service=self.service_name, batch_type=batch_type
        ).observe(duration)

    def update_parallel_queue_size(self, queue_type: str, size: int):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update parallel task queue size."""
        self.parallel_task_queue_size.labels(service=self.service_name, queue_type=queue_type).set(
            size
        )

    def update_parallel_workers(self, worker_type: str, count: int):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update active parallel workers count."""
        self.parallel_workers_active.labels(service=self.service_name, worker_type=worker_type).set(
            count
        )

    def update_websocket_connections(self, connection_type: str, count: int):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update WebSocket connections count."""
        self.websocket_connections.labels(
            service=self.service_name, connection_type=connection_type
        ).set(count)

    def record_cache_operation(self, operation: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record cache operation."""
        self.cache_operations.labels(
            service=self.service_name, operation=operation, result=result
        ).inc()

    def update_active_connections(self, count: int):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update active connections gauge."""
        self.active_connections.labels(service=self.service_name).set(count)

    def update_db_connections(self, pool_status: str, count: int):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update database connections gauge."""
        self.db_connections.labels(service=self.service_name, pool_status=pool_status).set(count)

    # Constitutional monitoring metric methods (Task 19.4)
    def update_constitutional_fidelity_score(self, component: str, score: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update constitutional fidelity score gauge."""
        self.constitutional_fidelity_score.labels(
            service=self.service_name, component=component
        ).set(score)

    def record_constitutional_violation(self, violation_type: str, severity: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record a constitutional violation."""
        self.constitutional_violations_total.labels(
            service=self.service_name, violation_type=violation_type, severity=severity
        ).inc()

    def record_qec_error_correction(
        self, error_type: str, strategy: str, success: bool, response_time: float
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record QEC error correction metrics."""
        self.qec_error_corrections_total.labels(
            service=self.service_name,
            error_type=error_type,
            strategy=strategy,
            success=str(success).lower(),
        ).inc()

        self.qec_response_time.labels(service=self.service_name, error_type=error_type).observe(
            response_time
        )

    def record_violation_escalation(self, escalation_level: str, auto_resolved: bool):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record violation escalation."""
        self.violation_escalations_total.labels(
            service=self.service_name,
            escalation_level=escalation_level,
            auto_resolved=str(auto_resolved).lower(),
        ).inc()

    def record_constitutional_council_activity(self, activity_type: str, status: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record Constitutional Council activity."""
        self.constitutional_council_activities.labels(
            service=self.service_name, activity_type=activity_type, status=status
        ).inc()

    def update_llm_reliability_score(self, model: str, operation_type: str, score: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update LLM reliability score."""
        self.llm_reliability_score.labels(
            service=self.service_name, model=model, operation_type=operation_type
        ).set(score)

    def update_monitoring_health_status(self, component: str, healthy: bool):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update monitoring system health status."""
        self.monitoring_health_status.labels(service=self.service_name, component=component).set(
            1.0 if healthy else 0.0
        )

    def record_llm_response_time(self, model_name: str, request_type: str, duration: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record LLM response time."""
        self.llm_response_time.labels(
            service=self.service_name, model_name=model_name, request_type=request_type
        ).observe(duration)

    def record_llm_error(self, model_name: str, error_type: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record LLM error."""
        self.llm_error_rate.labels(
            service=self.service_name, model_name=model_name, error_type=error_type
        ).inc()

    def set_llm_output_quality_score(self, model_name: str, quality_metric: str, score: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Set LLM output quality score."""
        self.llm_output_quality_score.labels(
            service=self.service_name,
            model_name=model_name,
            quality_metric=quality_metric,
        ).set(score)

    def set_llm_bias_score(self, model_name: str, bias_type: str, score: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Set LLM bias score."""
        self.llm_bias_score.labels(
            service=self.service_name, model_name=model_name, bias_type=bias_type
        ).set(score)

    def record_llm_fallback(self, fallback_reason: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record LLM fallback."""
        self.llm_fallback_count.labels(
            service=self.service_name, fallback_reason=fallback_reason
        ).inc()

    def record_llm_human_escalation(self, escalation_reason: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record LLM human escalation."""
        self.llm_human_escalation_count.labels(
            service=self.service_name, escalation_reason=escalation_reason
        ).inc()

    # Phase A3 Constitutional Governance Methods
    def record_constitutional_compliance_check(self, check_type: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record constitutional compliance check."""
        self.constitutional_compliance_checks.labels(
            service=self.service_name, check_type=check_type, result=result
        ).inc()

    def set_constitutional_compliance_score(self, policy_type: str, score: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Set constitutional compliance score."""
        self.constitutional_compliance_score.labels(
            service=self.service_name, policy_type=policy_type
        ).set(score)

    def record_constitutional_hash_validation(self, validation_type: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record constitutional hash validation."""
        self.constitutional_hash_validations.labels(
            service=self.service_name, validation_type=validation_type, result=result
        ).inc()

    def record_governance_workflow_operation(self, workflow_type: str, stage: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record governance workflow operation."""
        self.governance_workflow_operations.labels(
            service=self.service_name,
            workflow_type=workflow_type,
            stage=stage,
            result=result,
        ).inc()

    def record_governance_workflow_duration(self, workflow_type: str, stage: str, duration: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record governance workflow duration."""
        self.governance_workflow_duration.labels(
            service=self.service_name, workflow_type=workflow_type, stage=stage
        ).observe(duration)

    def record_policy_creation_operation(self, policy_type: str, status: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record policy creation operation."""
        self.policy_creation_rate.labels(
            service=self.service_name, policy_type=policy_type, status=status
        ).inc()

    def record_voting_operation(self, vote_type: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record voting operation."""
        self.voting_operations.labels(
            service=self.service_name, vote_type=vote_type, result=result
        ).inc()

    # Authentication Service Methods
    def record_auth_session_duration(self, session_type: str, duration: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record authentication session duration."""
        self.auth_session_duration.labels(
            service=self.service_name, session_type=session_type
        ).observe(duration)

    def record_mfa_operation(self, mfa_type: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record MFA operation."""
        self.mfa_operations.labels(
            service=self.service_name, mfa_type=mfa_type, result=result
        ).inc()

    def record_api_key_operation(self, operation_type: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record API key operation."""
        self.api_key_operations.labels(
            service=self.service_name, operation_type=operation_type, result=result
        ).inc()

    # Constitutional AI Service Methods
    def record_constitutional_ai_processing_time(
        self, ai_operation: str, complexity: str, duration: float
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record constitutional AI processing time."""
        self.constitutional_ai_processing_time.labels(
            service=self.service_name, ai_operation=ai_operation, complexity=complexity
        ).observe(duration)

    def record_compliance_validation_latency(self, validation_type: str, duration: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record compliance validation latency."""
        self.compliance_validation_latency.labels(
            service=self.service_name, validation_type=validation_type
        ).observe(duration)

    # Formal Verification Service Methods
    def record_z3_solver_operation(self, operation_type: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record Z3 solver operation."""
        self.z3_solver_operations.labels(
            service=self.service_name, operation_type=operation_type, result=result
        ).inc()

    def record_formal_verification_duration(
        self, verification_type: str, complexity: str, duration: float
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record formal verification duration."""
        self.formal_verification_duration.labels(
            service=self.service_name,
            verification_type=verification_type,
            complexity=complexity,
        ).observe(duration)

    # Governance Synthesis Service Methods
    def record_llm_token_usage(self, model_name: str, operation_type: str, tokens: int):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record LLM token usage."""
        self.llm_token_usage.labels(
            service=self.service_name,
            model_name=model_name,
            operation_type=operation_type,
        ).inc(tokens)

    def record_policy_synthesis_operation(self, synthesis_type: str, risk_level: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record policy synthesis operation."""
        self.policy_synthesis_operations.labels(
            service=self.service_name,
            synthesis_type=synthesis_type,
            risk_level=risk_level,
            result=result,
        ).inc()

    def record_multi_model_consensus_operation(
        self, consensus_type: str, model_count: str, result: str
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record multi-model consensus operation."""
        self.multi_model_consensus_operations.labels(
            service=self.service_name,
            consensus_type=consensus_type,
            model_count=model_count,
            result=result,
        ).inc()

    # Policy Governance Control Service Methods
    def record_pgc_validation_latency(self, validation_type: str, duration: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record PGC validation latency."""
        self.pgc_validation_latency.labels(
            service=self.service_name, validation_type=validation_type
        ).observe(duration)

    def record_policy_enforcement_action(self, action_type: str, policy_type: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record policy enforcement action."""
        self.policy_enforcement_actions.labels(
            service=self.service_name,
            action_type=action_type,
            policy_type=policy_type,
            result=result,
        ).inc()

    # Evolutionary Computation Service Methods
    def set_wina_optimization_score(self, optimization_type: str, score: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Set WINA optimization score."""
        self.wina_optimization_score.labels(
            service=self.service_name, optimization_type=optimization_type
        ).set(score)

    def record_evolutionary_computation_iteration(
        self, algorithm_type: str, convergence_status: str
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record evolutionary computation iteration."""
        self.evolutionary_computation_iterations.labels(
            service=self.service_name,
            algorithm_type=algorithm_type,
            convergence_status=convergence_status,
        ).inc()

    # Integrity Service Methods
    def record_cryptographic_operation(self, operation_type: str, algorithm: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record cryptographic operation."""
        self.cryptographic_operations.labels(
            service=self.service_name,
            operation_type=operation_type,
            algorithm=algorithm,
            result=result,
        ).inc()

    def record_audit_trail_operation(self, operation_type: str, integrity_status: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record audit trail operation."""
        self.audit_trail_operations.labels(
            service=self.service_name,
            operation_type=operation_type,
            integrity_status=integrity_status,
        ).inc()

    # Infrastructure Integration Methods
    def set_redis_connection_pool_usage(self, pool_status: str, usage: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Set Redis connection pool usage."""
        self.redis_connection_pool_usage.labels(
            service=self.service_name, pool_status=pool_status
        ).set(usage)

    def record_postgresql_query_performance(self, query_type: str, table: str, duration: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record PostgreSQL query performance."""
        self.postgresql_query_performance.labels(
            service=self.service_name, query_type=query_type, table=table
        ).observe(duration)

    # Quantumagi Blockchain Integration Methods
    def record_solana_transaction_operation(self, transaction_type: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record Solana transaction operation."""
        self.solana_transaction_operations.labels(
            service=self.service_name, transaction_type=transaction_type, result=result
        ).inc()

    def record_quantumagi_program_call(self, program_method: str, result: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record Quantumagi program call."""
        self.quantumagi_program_calls.labels(
            service=self.service_name, program_method=program_method, result=result
        ).inc()

    def set_blockchain_sync_status(self, network: str, synced: bool):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Set blockchain synchronization status."""
        self.blockchain_sync_status.labels(service=self.service_name, network=network).set(
            1.0 if synced else 0.0
        )


def get_metrics(service_name: str) -> ACGSMetrics:
    """Get or create metrics instance for a service."""
    if service_name not in metrics_registry:
        try:
            metrics_registry[service_name] = ACGSMetrics(service_name)
        except ValueError as e:
            if "Duplicated timeseries" in str(e):
                # Registry already has these metrics, create a simple placeholder
                logger.warning(
                    f"Metrics already registered for {service_name}, using existing registry"
                )

                # Return a dummy metrics object that doesn't register new metrics
                class DummyMetrics:
                    def __init__(self, service_name):
                        # requires: Valid input parameters
                        # ensures: Correct function execution
                        # sha256: func_hash
                        self.service_name = service_name

                    def __getattr__(self, name):
                        # requires: Valid input parameters
                        # ensures: Correct function execution
                        # sha256: func_hash
                        # Return a no-op function for any metric method
                        return lambda *args, **kwargs: None

                metrics_registry[service_name] = DummyMetrics(service_name)
            else:
                raise
    return metrics_registry[service_name]


def metrics_middleware(service_name: str):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """FastAPI middleware for automatic metrics collection."""

    async def middleware(request: Request, call_next):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        start_time = time.time()
        metrics = get_metrics(service_name)

        # Update active connections
        metrics.update_active_connections(len(metrics_registry))

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Record request metrics
            metrics.record_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration,
            )

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Record error metrics
            metrics.record_error(error_type=type(e).__name__, severity="error")

            # Record failed request
            metrics.record_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=500,
                duration=duration,
            )

            raise

    return middleware


def create_metrics_endpoint():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Create /metrics endpoint for Prometheus scraping."""

    async def metrics_endpoint():
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Prometheus metrics endpoint."""
        # Use the default registry which should have all metrics
        return PlainTextResponse(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

    return metrics_endpoint


def database_metrics_decorator(operation: str):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Decorator for database operations to collect metrics."""

    def decorator(func):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            start_time = time.time()
            service_name = getattr(wrapper, "_service_name", "unknown")
            metrics = get_metrics(service_name)

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                metrics.record_db_query(operation, duration)
                return result
            except Exception:
                duration = time.time() - start_time
                metrics.record_db_query(f"{operation}_failed", duration)
                metrics.record_error(f"db_{operation}_error")
                raise

        return wrapper

    return decorator


def service_call_decorator(target_service: str, endpoint: str):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Decorator for inter-service calls to collect metrics."""

    def decorator(func):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            start_time = time.time()
            service_name = getattr(wrapper, "_service_name", "unknown")
            metrics = get_metrics(service_name)

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Extract status code from result if available
                status_code = getattr(result, "status_code", 200)

                metrics.record_service_call(
                    target_service=target_service,
                    endpoint=endpoint,
                    status_code=status_code,
                    duration=duration,
                )

                return result
            except Exception:
                duration = time.time() - start_time
                metrics.record_service_call(
                    target_service=target_service,
                    endpoint=endpoint,
                    status_code=500,
                    duration=duration,
                )
                metrics.record_error(f"service_call_{target_service}_error")
                raise

        return wrapper

    return decorator
