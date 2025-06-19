from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# --- Schemas for FV Service's own API ---


class PolicyRuleRef(BaseModel):
    id: int  # ID of the policy rule in Integrity Service
    # content: Optional[str] = None # Optionally pass content if already fetched


class ACPrincipleRef(BaseModel):
    id: int  # ID of the AC principle
    # content: Optional[str] = None # Optionally pass content if already fetched for context


class VerificationRequest(BaseModel):
    policy_rule_refs: list[PolicyRuleRef] = Field(
        ..., description="References to policy rules to be verified."
    )
    # Optionally, principles can be referenced directly if verification is triggered per principle
    ac_principle_refs: list[ACPrincipleRef] | None = Field(
        None,
        description="References to AC principles to derive proof obligations from. If not provided, obligations might be derived from principles linked to the policy rules.",
    )


class VerificationResult(BaseModel):
    policy_rule_id: int
    status: str  # e.g., "verified", "failed", "error"
    message: str | None = None
    counter_example: str | None = None  # If applicable and found by SMT solver


class VerificationResponse(BaseModel):
    results: list[VerificationResult]
    overall_status: str  # e.g., "all_verified", "some_failed", "error"
    summary_message: str | None = None


# --- Schemas for internal logic and SMT interaction ---


class ProofObligation(BaseModel):
    principle_id: int
    obligation_content: str  # e.g., a formal representation of the principle's intent
    description: str | None = None


class SMTSolverInput(BaseModel):
    datalog_rules: list[str]  # List of Datalog rule strings
    proof_obligations: list[str]  # List of proof obligation strings (formalized)


class SMTSolverOutput(BaseModel):
    is_satisfiable: (
        bool  # True if rules + NOT(obligation) is satisfiable (meaning obligation NOT entailed)
    )
    is_unsatisfiable: (
        bool  # True if rules + NOT(obligation) is unsatisfiable (meaning obligation IS entailed)
    )
    # In a real SMT solver, satisfiability refers to whether a model exists for the given assertions.
    # For verifying if Rules => Obligation, we check if Rules AND (NOT Obligation) is UNSATISFIABLE.
    # If UNSAT, then Obligation is entailed by Rules.
    counter_example: str | None = (
        None  # If satisfiable, a model might be a counter-example to the obligation
    )
    error_message: str | None = None


# --- Schemas for interacting with external services ---


# For AC Service (ac_service)
class ACPrinciple(BaseModel):  # Simplified version of AC's Principle schema
    id: int
    name: str
    content: str
    description: str | None = None


# For Integrity Service (integrity_service)
class PolicyRule(BaseModel):  # Matches Integrity Service's PolicyRule response
    id: int
    rule_content: str
    source_principle_ids: list[int] | None = []
    version: int
    verification_status: str


class PolicyRuleStatusUpdate(BaseModel):  # For updating status in Integrity Service
    verification_status: str  # "verified", "failed", "pending"
    # verified_at: Optional[datetime] # Integrity service might set this automatically


# --- Phase 3: Algorithmic Fairness Schemas ---


class BiasMetric(BaseModel):
    """Bias detection metric configuration."""

    metric_id: str
    metric_type: str  # "statistical", "counterfactual", "embedding", "llm_review"
    metric_name: str
    description: str
    threshold: float | None = None
    parameters: dict[str, Any] | None = None


class FairnessProperty(BaseModel):
    """Fairness property definition."""

    property_id: str
    property_type: (
        str  # "demographic_parity", "equalized_odds", "calibration", "individual_fairness"
    )
    property_name: str
    description: str
    protected_attributes: list[str]
    threshold: float = 0.1
    criticality_level: str = "medium"  # "low", "medium", "high", "critical"


class BiasDetectionRequest(BaseModel):
    """Request for bias detection analysis."""

    policy_rule_ids: list[int]
    bias_metrics: list[BiasMetric]
    fairness_properties: list[FairnessProperty]
    dataset: list[dict[str, Any]] | None = None
    protected_attributes: list[str]
    analysis_type: str = "comprehensive"  # "basic", "comprehensive", "expert_review"


class BiasDetectionResult(BaseModel):
    """Result of bias detection for a single metric."""

    metric_id: str
    policy_rule_id: int
    bias_detected: bool
    bias_score: float | None = None
    confidence: float
    explanation: str
    recommendations: list[str] | None = None
    requires_human_review: bool = False


class BiasDetectionResponse(BaseModel):
    """Response from bias detection analysis."""

    policy_rule_ids: list[int]
    results: list[BiasDetectionResult]
    overall_bias_score: float
    risk_level: str  # "low", "medium", "high", "critical"
    summary: str
    recommendations: list[str]
    human_review_required: bool


class FairnessValidationRequest(BaseModel):
    """Request for fairness validation."""

    policy_rule_ids: list[int]
    fairness_properties: list[FairnessProperty]
    validation_dataset: list[dict[str, Any]] | None = None
    simulation_parameters: dict[str, Any] | None = None


class FairnessValidationResult(BaseModel):
    """Result of fairness validation."""

    property_id: str
    policy_rule_id: int
    fairness_satisfied: bool
    fairness_score: float
    violation_details: str | None = None
    counterfactual_examples: list[dict[str, Any]] | None = None


class FairnessValidationResponse(BaseModel):
    """Response from fairness validation."""

    policy_rule_ids: list[int]
    results: list[FairnessValidationResult]
    overall_fairness_score: float
    compliance_status: str  # "compliant", "non_compliant", "requires_review"
    summary: str


# --- Enhanced Schemas for Tiered Validation Pipeline (Phase 3) ---


class ValidationTier(str, Enum):
    """Validation tiers for formal verification."""

    AUTOMATED = "automated"
    HITL = "human_in_the_loop"
    RIGOROUS = "rigorous"


class ValidationLevel(str, Enum):
    """Validation levels within each tier."""

    BASELINE = "baseline"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CRITICAL = "critical"


class SafetyProperty(BaseModel):
    """Safety property for formal verification."""

    property_id: str
    property_type: str  # "safety", "liveness", "security", "fairness"
    property_description: str
    formal_specification: str
    criticality_level: str  # "low", "medium", "high", "critical"


class TieredVerificationRequest(BaseModel):
    """Request for tiered formal verification."""

    policy_rule_refs: list[PolicyRuleRef]
    validation_tier: ValidationTier
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    safety_properties: list[SafetyProperty] | None = None
    timeout_seconds: int | None = 300
    require_proof: bool = False
    human_reviewer_id: str | None = None  # For HITL validation


class TieredVerificationResult(BaseModel):
    """Result from tiered formal verification."""

    policy_rule_id: int
    validation_tier: ValidationTier
    validation_level: ValidationLevel
    status: str  # "verified", "failed", "inconclusive", "timeout"
    confidence_score: float  # 0.0 to 1.0
    verification_method: str
    proof_trace: str | None = None
    counter_example: str | None = None
    safety_violations: list[str] | None = None
    human_review_notes: str | None = None
    verification_time_ms: int | None = None


class TieredVerificationResponse(BaseModel):
    """Response from tiered formal verification."""

    results: list[TieredVerificationResult]
    overall_status: str
    overall_confidence: float
    summary_message: str | None = None
    escalation_required: bool = False
    next_tier_recommendation: ValidationTier | None = None


# --- Schemas for Safety and Conflict Checking ---


class ConflictType(str, Enum):
    """Types of conflicts that can be detected."""

    LOGICAL_CONTRADICTION = "logical_contradiction"
    PRACTICAL_INCOMPATIBILITY = "practical_incompatibility"
    PRIORITY_CONFLICT = "priority_conflict"
    RESOURCE_CONFLICT = "resource_conflict"


class ConflictCheckRequest(BaseModel):
    """Request for conflict detection between rules."""

    rule_sets: list[str]  # Names or IDs of rule sets to check
    conflict_types: list[ConflictType]
    resolution_strategy: str | None = "principle_priority_based"
    include_suggestions: bool = True


class ConflictDetectionResult(BaseModel):
    """Result of conflict detection."""

    conflict_id: str
    conflict_type: ConflictType
    conflicting_rules: list[int]  # Rule IDs
    conflict_description: str
    severity: str  # "low", "medium", "high", "critical"
    resolution_suggestion: str | None = None
    affected_principles: list[int] | None = None


class ConflictCheckResponse(BaseModel):
    """Response from conflict checking."""

    conflicts: list[ConflictDetectionResult]
    total_conflicts: int
    critical_conflicts: int
    resolution_required: bool
    summary: str


class SafetyCheckRequest(BaseModel):
    """Request for safety property validation."""

    system_model: str
    safety_properties: list[SafetyProperty]
    verification_method: str = "bounded_model_checking"
    depth_limit: int | None = 100
    time_limit_seconds: int | None = 600


class SafetyCheckResult(BaseModel):
    """Result of safety property checking."""

    property_id: str
    status: str  # "satisfied", "violated", "unknown"
    witness_trace: str | None = None
    counter_example_trace: str | None = None
    verification_depth: int | None = None
    verification_time_ms: int | None = None


class SafetyCheckResponse(BaseModel):
    """Response from safety property checking."""

    results: list[SafetyCheckResult]
    overall_safety_status: str
    critical_violations: list[str]
    summary: str


# Placeholder for User (if FV Service needs to be auth-aware for its own endpoints)
class User(BaseModel):
    id: str
    roles: list[str] = []


# --- Enhanced Multi-Model Validation Schemas ---


class ValidationResult(BaseModel):
    """Result of a validation operation."""

    rule_id: int
    principle_id: int
    validation_type: str
    is_valid: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    error_details: str | None = None
    suggestions: list[str] | None = None
    metadata: dict[str, Any] | None = None


class ValidationContext(BaseModel):
    """Context for multi-model validation."""

    request_id: str
    models: dict[str, list[dict[str, Any]]]
    validation_rules: list[str] | None = None
    performance_budget: dict[str, float] | None = None


class MultiModelValidationResult(BaseModel):
    """Result of multi-model validation."""

    request_id: str
    overall_valid: bool
    validation_results: list[ValidationResult]
    performance_metrics: dict[str, float]
    recommendations: list[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConflictCheckResult(BaseModel):
    """Result of conflict checking between models."""

    has_conflicts: bool
    conflict_details: list[str]
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    resolution_suggestions: list[str]
    affected_principles: list[int]


# --- Task 13: Cross-Domain Principle Testing Framework Schemas ---


class DomainContextBase(BaseModel):
    """Base schema for domain context."""

    domain_name: str = Field(
        ..., max_length=100, description="Domain name (e.g., healthcare, finance)"
    )
    domain_description: str | None = Field(None, description="Description of the domain")
    regulatory_frameworks: list[str] | None = Field(
        None, description="Applicable regulatory frameworks"
    )
    compliance_requirements: dict[str, Any] | None = Field(
        None, description="Specific compliance requirements"
    )
    cultural_contexts: dict[str, Any] | None = Field(
        None, description="Cultural and social context factors"
    )
    domain_constraints: dict[str, Any] | None = Field(
        None, description="Technical and operational constraints"
    )
    risk_factors: list[str] | None = Field(None, description="Domain-specific risk factors")
    stakeholder_groups: list[str] | None = Field(None, description="Relevant stakeholder groups")


class DomainContextCreate(DomainContextBase):
    """Schema for creating domain context."""


class DomainContextUpdate(BaseModel):
    """Schema for updating domain context."""

    domain_description: str | None = None
    regulatory_frameworks: list[str] | None = None
    compliance_requirements: dict[str, Any] | None = None
    cultural_contexts: dict[str, Any] | None = None
    domain_constraints: dict[str, Any] | None = None
    risk_factors: list[str] | None = None
    stakeholder_groups: list[str] | None = None
    is_active: bool | None = None


class DomainContext(DomainContextBase):
    """Schema for domain context response."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by_user_id: int | None = None

    class Config:
        from_attributes = True


class CrossDomainTestScenarioBase(BaseModel):
    """Base schema for cross-domain test scenario."""

    scenario_name: str = Field(..., max_length=255, description="Name of the test scenario")
    scenario_description: str | None = Field(None, description="Description of the test scenario")
    primary_domain_id: int = Field(..., description="Primary domain ID for testing")
    secondary_domains: list[int] | None = Field(None, description="Secondary domain IDs")
    test_type: str = Field(
        ..., description="Type of test (consistency, adaptation, conflict_detection)"
    )
    test_parameters: dict[str, Any] | None = Field(None, description="Configurable test parameters")
    expected_outcomes: dict[str, Any] | None = Field(None, description="Expected test results")
    principle_ids: list[int] = Field(..., description="List of principle IDs to test")
    principle_adaptations: dict[str, Any] | None = Field(
        None, description="Domain-specific adaptations"
    )


class CrossDomainTestScenarioCreate(CrossDomainTestScenarioBase):
    """Schema for creating cross-domain test scenario."""


class CrossDomainTestScenarioUpdate(BaseModel):
    """Schema for updating cross-domain test scenario."""

    scenario_description: str | None = None
    secondary_domains: list[int] | None = None
    test_parameters: dict[str, Any] | None = None
    expected_outcomes: dict[str, Any] | None = None
    principle_adaptations: dict[str, Any] | None = None
    status: str | None = None


class CrossDomainTestScenario(CrossDomainTestScenarioBase):
    """Schema for cross-domain test scenario response."""

    id: int
    status: str
    last_run_at: datetime | None = None
    accuracy_score: float | None = None
    consistency_score: float | None = None
    created_at: datetime
    updated_at: datetime
    created_by_user_id: int | None = None

    class Config:
        from_attributes = True


class CrossDomainTestResultBase(BaseModel):
    """Base schema for cross-domain test result."""

    scenario_id: int = Field(..., description="Test scenario ID")
    test_run_id: str = Field(..., description="Unique test run identifier")
    domain_id: int = Field(..., description="Domain ID being tested")
    principle_id: int = Field(..., description="Principle ID being tested")
    test_type: str = Field(..., description="Type of test performed")
    is_consistent: bool = Field(
        ..., description="Whether the principle is consistent across domains"
    )
    consistency_score: float = Field(
        ..., ge=0.0, le=1.0, description="Consistency score (0.0 to 1.0)"
    )
    adaptation_required: bool = Field(..., description="Whether adaptation is required")
    adaptation_suggestions: list[str] | None = Field(None, description="Suggested adaptations")
    validation_details: dict[str, Any] | None = Field(
        None, description="Detailed validation results"
    )
    conflict_detected: bool = Field(False, description="Whether conflicts were detected")
    conflict_details: dict[str, Any] | None = Field(None, description="Details of conflicts found")
    execution_time_ms: int | None = Field(None, description="Execution time in milliseconds")
    memory_usage_mb: float | None = Field(None, description="Memory usage in MB")


class CrossDomainTestResult(CrossDomainTestResultBase):
    """Schema for cross-domain test result response."""

    id: int
    executed_at: datetime
    executed_by_user_id: int | None = None

    class Config:
        from_attributes = True


class CrossDomainTestRequest(BaseModel):
    """Schema for requesting cross-domain testing."""

    scenario_ids: list[int] = Field(..., description="List of scenario IDs to execute")
    target_accuracy: float = Field(0.9, ge=0.0, le=1.0, description="Target accuracy threshold")
    enable_parallel: bool = Field(True, description="Enable parallel execution")
    max_execution_time_seconds: int = Field(300, description="Maximum execution time per scenario")


class CrossDomainTestResponse(BaseModel):
    """Schema for cross-domain testing response."""

    test_run_id: str = Field(..., description="Unique test run identifier")
    scenarios_executed: int = Field(..., description="Number of scenarios executed")
    overall_accuracy: float = Field(..., description="Overall accuracy across all tests")
    overall_consistency: float = Field(..., description="Overall consistency score")
    results: list[CrossDomainTestResult] = Field(..., description="Detailed test results")
    execution_summary: dict[str, Any] = Field(..., description="Execution summary and metrics")
    recommendations: list[str] = Field(..., description="Recommendations based on results")
