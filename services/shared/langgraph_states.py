"""
Shared LangGraph State Management for ACGS-PGP

This module provides base state classes and utilities for LangGraph workflows
across the ACGS-PGP microservices architecture. It implements patterns from
the Gemini-LangGraph quickstart for constitutional governance workflows.
"""

import operator
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any, TypedDict

try:
    from langgraph.graph import add_messages

    LANGGRAPH_AVAILABLE = True
except ImportError:
    # Fallback for environments without LangGraph
    def add_messages(x, y):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Fallback message accumulator when LangGraph is not available."""
        if isinstance(x, list) and isinstance(y, list):
            return x + y
        elif isinstance(x, list):
            return x + [y]
        elif isinstance(y, list):
            return [x] + y
        else:
            return [x, y]

    LANGGRAPH_AVAILABLE = False


class WorkflowStatus(str, Enum):
    """Standard workflow status values for ACGS-PGP workflows."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"


class BaseACGSState(TypedDict):
    """
    Base state for all ACGS-PGP LangGraph workflows.

    Provides common fields for user context, session management,
    and workflow tracking across all constitutional governance processes.
    """

    # Message handling (LangGraph standard)
    messages: Annotated[list, add_messages]

    # User and session context
    user_id: str | None
    session_id: str | None
    workflow_id: str | None

    # Temporal tracking
    created_at: str | None
    updated_at: str | None

    # Workflow management
    status: str | None  # WorkflowStatus enum value
    error_message: str | None
    retry_count: int | None

    # Metadata and configuration
    metadata: dict[str, Any] | None
    configuration: dict[str, Any] | None


class ConstitutionalCouncilState(BaseACGSState):
    """
    State for Constitutional Council amendment workflows.

    Manages the complete lifecycle of constitutional amendments including
    proposal generation, stakeholder feedback, analysis, and voting.
    """

    # Amendment proposal data
    amendment_proposal: dict[str, Any] | None
    amendment_id: str | None
    amendment_type: str | None  # "principle_addition", "principle_modification", "meta_rule_change"

    # Stakeholder engagement
    stakeholder_feedback: Annotated[list[dict[str, Any]], operator.add]
    stakeholder_notifications: Annotated[list[dict[str, Any]], operator.add]
    required_stakeholders: list[str] | None

    # Constitutional analysis
    constitutional_analysis: dict[str, Any] | None
    compliance_score: float | None
    identified_conflicts: Annotated[list[dict[str, Any]], operator.add]

    # Voting and decision process
    voting_results: dict[str, Any] | None
    voting_deadline: str | None
    quorum_met: bool | None

    # Iterative refinement
    refinement_iterations: int | None
    max_refinement_iterations: int | None
    is_constitutional: bool | None
    requires_refinement: bool | None
    escalation_required: bool | None

    # Workflow state tracking
    current_phase: str | None  # "proposal", "feedback", "analysis", "voting", "implementation"
    phase_deadlines: dict[str, str] | None
    automated_processing: bool | None


class PolicySynthesisState(BaseACGSState):
    """
    State for GS Engine policy synthesis workflows.

    Manages the translation of constitutional principles into operational
    policies with iterative refinement and constitutional compliance validation.
    """

    # Input constitutional principles
    constitutional_principles: list[dict[str, Any]] | None
    principle_ids: list[str] | None

    # Synthesis context and requirements
    synthesis_context: dict[str, Any] | None
    target_domain: str | None
    compliance_requirements: list[str] | None

    # Generated policies and validation
    generated_policies: Annotated[list[dict[str, Any]], operator.add]
    policy_templates: list[dict[str, Any]] | None
    validation_results: Annotated[list[dict[str, Any]], operator.add]

    # Quality and compliance metrics
    synthesis_iterations: int | None
    max_synthesis_iterations: int | None
    constitutional_fidelity_score: float | None
    fidelity_threshold: float | None

    # Multi-model LLM tracking
    model_responses: Annotated[list[dict[str, Any]], operator.add]
    model_performance: dict[str, Any] | None
    fallback_used: bool | None

    # Human oversight and review
    requires_human_review: bool | None
    human_feedback: Annotated[list[dict[str, Any]], operator.add]
    expert_validation: dict[str, Any] | None

    # Output and deployment
    final_policies: list[dict[str, Any]] | None
    deployment_ready: bool | None
    rego_policies: list[str] | None


class ConstitutionalFidelityState(BaseACGSState):
    """
    State for constitutional fidelity monitoring and QEC-inspired error correction.

    Tracks constitutional compliance in real-time and manages error correction
    workflows for maintaining constitutional integrity.
    """

    # Fidelity monitoring
    current_fidelity_score: float | None
    fidelity_history: Annotated[list[dict[str, Any]], operator.add]
    fidelity_threshold: float | None
    alert_level: str | None  # "green", "amber", "red"

    # Constitutional violations
    detected_violations: Annotated[list[dict[str, Any]], operator.add]
    violation_severity: str | None  # "low", "medium", "high", "critical"
    violation_categories: list[str] | None

    # Error correction and recovery
    corrective_actions: Annotated[list[dict[str, Any]], operator.add]
    correction_attempts: int | None
    max_correction_attempts: int | None
    recovery_strategies: list[str] | None

    # Performance and metrics
    monitoring_metrics: dict[str, Any] | None
    performance_degradation: bool | None
    system_health: dict[str, Any] | None

    # Escalation and human intervention
    escalation_triggered: bool | None
    human_intervention_required: bool | None
    escalation_reason: str | None


class MultiModelLLMState(BaseACGSState):
    """
    State for multi-model LLM management and reliability tracking.

    Manages model selection, fallback mechanisms, and performance monitoring
    for achieving >99.9% reliability targets.
    """

    # Model configuration and selection
    primary_model: str | None
    fallback_models: list[str] | None
    model_roles: dict[str, str] | None  # role -> model mapping

    # Request and response tracking
    model_requests: Annotated[list[dict[str, Any]], operator.add]
    model_responses: Annotated[list[dict[str, Any]], operator.add]
    response_times: Annotated[list[float], operator.add]

    # Reliability and performance metrics
    success_rate: float | None
    average_response_time: float | None
    error_rate: float | None
    fallback_usage_rate: float | None

    # Error handling and recovery
    failed_requests: Annotated[list[dict[str, Any]], operator.add]
    retry_attempts: int | None
    max_retries: int | None
    circuit_breaker_status: str | None  # "closed", "open", "half_open"

    # Quality assessment
    output_quality_scores: Annotated[list[float], operator.add]
    constitutional_compliance_scores: Annotated[list[float], operator.add]
    bias_detection_results: Annotated[list[dict[str, Any]], operator.add]


def create_workflow_metadata(
    workflow_type: str,
    user_id: str | None = None,
    session_id: str | None = None,
    configuration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create standardized metadata for ACGS-PGP workflows.

    Args:
        workflow_type: Type of workflow (e.g., "constitutional_council", "policy_synthesis")
        user_id: Optional user identifier
        session_id: Optional session identifier
        configuration: Optional workflow configuration

    Returns:
        Standardized metadata dictionary
    """
    now = datetime.now(timezone.utc).isoformat()

    return {
        "workflow_type": workflow_type,
        "user_id": user_id,
        "session_id": session_id,
        "created_at": now,
        "updated_at": now,
        "status": WorkflowStatus.PENDING.value,
        "retry_count": 0,
        "configuration": configuration or {},
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "acgs_version": "1.0.0",
    }


def update_workflow_status(
    state: BaseACGSState, status: WorkflowStatus, error_message: str | None = None
) -> dict[str, Any]:
    """
    Update workflow status with timestamp and error handling.

    Args:
        state: Current workflow state
        status: New workflow status
        error_message: Optional error message for failed states

    Returns:
        State update dictionary
    """
    update = {
        "status": status.value,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    if error_message:
        update["error_message"] = error_message

    if status == WorkflowStatus.FAILED:
        retry_count = state.get("retry_count", 0)
        update["retry_count"] = retry_count + 1

    return update
