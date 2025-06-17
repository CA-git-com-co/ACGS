from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


# Base schema for Principle attributes
class PrincipleBase(BaseModel):
    name: str = Field(
        ..., min_length=3, max_length=100, description="Unique name of the principle"
    )
    description: str | None = Field(
        None, max_length=500, description="Detailed description of the principle"
    )
    content: str = Field(
        ..., description="The full content of the principle (e.g., text, JSON string)"
    )

    # Enhanced Phase 1 Constitutional Fields
    priority_weight: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Priority weight for principle prioritization (0.0 to 1.0)",
    )
    scope: list[str] | None = Field(
        None, description="List of contexts where principle applies"
    )
    normative_statement: str | None = Field(
        None,
        description="Structured normative statement for constitutional interpretation",
    )
    constraints: dict | None = Field(
        None, description="Formal constraints and requirements"
    )
    rationale: str | None = Field(
        None, description="Detailed rationale and justification for the principle"
    )
    keywords: list[str] | None = Field(
        None, description="Keywords for principle categorization"
    )
    category: str | None = Field(
        None,
        max_length=100,
        description="Category classification (e.g., Safety, Privacy, Fairness)",
    )
    validation_criteria_nl: str | None = Field(
        None, description="Natural language validation criteria for testing"
    )
    constitutional_metadata: dict | None = Field(
        None, description="Metadata for constitutional compliance tracking"
    )


# Schema for creating a new principle
class PrincipleCreate(PrincipleBase):
    # version and status will have default values in the model
    # created_by_user_id will be passed from the request context (e.g., authenticated user)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Data Privacy Protection",
                "description": "Ensure user data privacy and protection",
                "content": "All user data must be encrypted and access logged",
                "priority_weight": 0.8,
                "scope": ["data_processing", "user_management"],
                "category": "Privacy",
            }
        }


# Schema for updating an existing principle
# All fields are optional for updates
class PrincipleUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    content: str | None = None
    status: str | None = Field(
        None, description="e.g., 'draft', 'approved', 'deprecated'"
    )

    # Enhanced Phase 1 Constitutional Fields (all optional for updates)
    priority_weight: float | None = Field(
        None, ge=0.0, le=1.0, description="Priority weight for principle prioritization"
    )
    scope: list[str] | None = Field(
        None, description="List of contexts where principle applies"
    )
    normative_statement: str | None = Field(
        None, description="Structured normative statement"
    )
    constraints: dict | None = Field(
        None, description="Formal constraints and requirements"
    )
    rationale: str | None = Field(
        None, description="Detailed rationale and justification"
    )
    keywords: list[str] | None = Field(
        None, description="Keywords for categorization"
    )
    category: str | None = Field(
        None, max_length=100, description="Category classification"
    )
    validation_criteria_nl: str | None = Field(
        None, description="Natural language validation criteria"
    )
    constitutional_metadata: dict | None = Field(
        None, description="Constitutional compliance metadata"
    )
    # version might be handled automatically or via a specific versioning endpoint
    # version: Optional[int] = Field(None, gt=0)


# Schema for representing a Principle in API responses
class Principle(PrincipleBase):
    id: int
    version: int
    status: str
    created_at: datetime
    updated_at: datetime
    created_by_user_id: int | None = (
        None  # Made optional if user can be anonymous or system-created
    )

    class Config:
        from_attributes = True  # For SQLAlchemy model compatibility (Pydantic v2)


# Optional: Schema for a list of principles for responses
class PrincipleList(BaseModel):
    principles: list[Principle]
    total: int


# Placeholder for user information, to be refined with actual auth integration
class User(BaseModel):
    id: int
    username: str
    roles: list[str] = []  # e.g., ["user", "ac_admin"]


# Constitutional Council and AC Enhancement Schemas


# Meta-Rules (R) component schemas
class ACMetaRuleBase(BaseModel):
    rule_type: str = Field(
        ...,
        description="Type of meta-rule (e.g., amendment_procedure, voting_threshold)",
    )
    name: str = Field(
        ..., min_length=3, max_length=255, description="Name of the meta-rule"
    )
    description: str | None = Field(None, description="Description of the meta-rule")
    rule_definition: dict = Field(
        ..., description="JSON structure defining the meta-governance rule"
    )
    threshold: str | None = Field(
        None, description="Voting threshold (e.g., 0.67, simple_majority)"
    )
    stakeholder_roles: list[str] | None = Field(
        None, description="Roles that can participate"
    )
    decision_mechanism: str | None = Field(
        None, description="Decision mechanism (e.g., supermajority_vote)"
    )


class ACMetaRuleCreate(ACMetaRuleBase):

    class Config:
        json_schema_extra = {
            "example": {
                "rule_type": "voting_threshold",
                "name": "Constitutional Amendment Threshold",
                "description": "Defines voting threshold for constitutional amendments",
                "threshold": "0.67",
                "stakeholder_roles": ["admin", "policy_manager"],
                "decision_mechanism": "supermajority_vote",
            }
        }


class ACMetaRuleUpdate(BaseModel):
    rule_type: str | None = None
    name: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = None
    rule_definition: dict | None = None
    threshold: str | None = None
    stakeholder_roles: list[str] | None = None
    decision_mechanism: str | None = None
    status: str | None = Field(
        None, description="Status (active, deprecated, proposed)"
    )


class ACMetaRule(ACMetaRuleBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    created_by_user_id: int | None = None

    class Config:
        from_attributes = True


# Amendment schemas with enhanced Pydantic v2.0+ validation
class ACAmendmentBase(BaseModel):
    principle_id: int = Field(
        ..., description="ID of the principle being amended", gt=0
    )
    amendment_type: str = Field(
        ...,
        description="Type of amendment (modify, add, remove, status_change)",
        pattern="^(modify|add|remove|status_change)$",
    )
    proposed_changes: str = Field(
        ...,
        description="Description of proposed changes",
        min_length=10,
        max_length=5000,
    )
    justification: str | None = Field(
        None, description="Rationale for the amendment", max_length=2000
    )
    proposed_content: str | None = Field(
        None, description="New content if modifying/adding", max_length=10000
    )
    proposed_status: str | None = Field(
        None,
        description="New status if changing status",
        pattern="^(active|inactive|deprecated|under_review)$",
    )

    # Co-evolution metadata fields
    urgency_level: str | None = Field(
        "normal",
        description="Amendment urgency level for co-evolution handling",
        pattern="^(normal|rapid|emergency)$",
    )
    co_evolution_context: dict[str, Any] | None = Field(
        None, description="Context for rapid co-evolution scenarios"
    )
    expected_impact: str | None = Field(
        None,
        description="Expected impact assessment",
        pattern="^(low|medium|high|critical)$",
    )


class ACAmendmentCreate(ACAmendmentBase):
    consultation_period_days: int | None = Field(
        30, description="Days for public consultation", ge=1, le=365
    )
    public_comment_enabled: bool = Field(True, description="Enable public comments")
    stakeholder_groups: list[str] | None = Field(
        None, description="Stakeholder groups to invite", max_items=20
    )

    # Enhanced validation for co-evolution
    rapid_processing_requested: bool = Field(
        False, description="Request rapid processing for urgent amendments"
    )
    constitutional_significance: str | None = Field(
        "normal",
        description="Constitutional significance level",
        pattern="^(normal|significant|fundamental)$",
    )

    @field_validator("stakeholder_groups")
    @classmethod
    def validate_stakeholder_groups(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        if v is not None:
            valid_groups = {
                "citizens",
                "experts",
                "affected_parties",
                "regulatory_bodies",
                "constitutional_council",
                "policy_managers",
                "auditors",
                "privacy_advocates",
                "security_experts",
                "legal_experts",
            }
            for group in v:
                if group not in valid_groups:
                    raise ValueError(f"Invalid stakeholder group: {group}")
        return v

    @field_validator("co_evolution_context")
    @classmethod
    def validate_co_evolution_context(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        if v is not None:
            required_fields = {"trigger_event", "timeline", "stakeholders"}
            if not all(field in v for field in required_fields):
                raise ValueError(
                    f"Co-evolution context must include: {required_fields}"
                )
        return v


class ACAmendmentUpdate(BaseModel):
    amendment_type: str | None = None
    proposed_changes: str | None = None
    justification: str | None = None
    proposed_content: str | None = None
    proposed_status: str | None = None
    status: str | None = Field(None, description="Workflow status")
    consultation_period_days: int | None = None
    public_comment_enabled: bool | None = None
    stakeholder_groups: list[str] | None = None


class ACAmendment(ACAmendmentBase):
    id: int
    status: str
    voting_started_at: datetime | None = None
    voting_ends_at: datetime | None = None
    votes_for: int = 0
    votes_against: int = 0
    votes_abstain: int = 0
    required_threshold: str | None = None
    consultation_period_days: int | None = None
    public_comment_enabled: bool = True
    stakeholder_groups: list[str] | None = None
    created_at: datetime
    updated_at: datetime
    proposed_by_user_id: int

    # Co-evolution and versioning fields
    version: int = Field(1, description="Amendment version for optimistic locking")
    rapid_processing_requested: bool = False
    constitutional_significance: str | None = "normal"
    processing_metrics: dict[str, Any] | None = Field(
        None, description="Performance metrics for co-evolution tracking"
    )

    # Workflow state tracking
    workflow_state: str | None = Field(
        "proposed",
        description="Current workflow state",
        pattern="^(proposed|under_review|voting|approved|rejected|implemented)$",
    )
    state_transitions: list[dict[str, Any]] | None = Field(
        None, description="History of state transitions"
    )

    class Config:
        from_attributes = True


# Amendment vote schemas
class ACAmendmentVoteBase(BaseModel):
    vote: str = Field(..., description="Vote choice (for, against, abstain)")
    reasoning: str | None = Field(None, description="Optional explanation of vote")


class ACAmendmentVoteCreate(ACAmendmentVoteBase):
    amendment_id: int = Field(..., description="ID of the amendment being voted on")


class ACAmendmentVote(ACAmendmentVoteBase):
    id: int
    amendment_id: int
    voter_id: int
    voted_at: datetime

    class Config:
        from_attributes = True


# Amendment comment schemas
class ACAmendmentCommentBase(BaseModel):
    comment_text: str = Field(..., description="Comment content")
    sentiment: str | None = Field(
        None, description="Comment sentiment (support, oppose, neutral)"
    )
    stakeholder_group: str | None = Field(
        None, description="Stakeholder group of commenter"
    )


class ACAmendmentCommentCreate(ACAmendmentCommentBase):
    amendment_id: int = Field(..., description="ID of the amendment being commented on")
    commenter_name: str | None = Field(
        None, description="Name for anonymous commenters"
    )
    commenter_email: str | None = Field(
        None, description="Email for anonymous commenters"
    )


class ACAmendmentComment(ACAmendmentCommentBase):
    id: int
    amendment_id: int
    commenter_id: int | None = None
    commenter_name: str | None = None
    commenter_email: str | None = None
    is_public: bool = True
    is_moderated: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# Conflict resolution schemas
class ACConflictResolutionBase(BaseModel):
    conflict_type: str = Field(
        ...,
        description="Type of conflict (principle_contradiction, practical_incompatibility)",
    )
    principle_ids: list[int] = Field(
        ..., description="IDs of principles involved in conflict"
    )
    context: str | None = Field(None, description="Context of the conflict")
    conflict_description: str = Field(..., description="Description of the conflict")
    severity: str = Field(
        ..., description="Severity level (low, medium, high, critical)"
    )
    resolution_strategy: str = Field(..., description="Strategy for resolution")
    resolution_details: dict | None = Field(
        None, description="Structured resolution information"
    )
    precedence_order: list[int] | None = Field(
        None, description="Priority order of principles"
    )


class ACConflictResolutionCreate(ACConflictResolutionBase):

    class Config:
        json_schema_extra = {
            "example": {
                "conflict_type": "priority_conflict",
                "principle_ids": [1, 2],
                "context": "Privacy vs Security conflict in user authentication",
                "resolution_strategy": "weighted_priority",
                "resolution_details": {"weights": {"privacy": 0.6, "security": 0.4}},
                "precedence_order": [1, 2],
            }
        }


class ACConflictResolutionUpdate(BaseModel):
    conflict_type: str | None = None
    principle_ids: list[int] | None = None
    context: str | None = None
    conflict_description: str | None = None
    severity: str | None = None
    resolution_strategy: str | None = None
    resolution_details: dict | None = None
    precedence_order: list[int] | None = None
    status: str | None = Field(
        None, description="Status (identified, analyzed, resolved, monitoring)"
    )


class ACConflictResolution(ACConflictResolutionBase):
    id: int
    status: str
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    identified_by_user_id: int | None = None

    class Config:
        from_attributes = True


# Human-in-the-Loop Sampling Schemas


class UncertaintyMetrics(BaseModel):
    """Schema for uncertainty metrics in different dimensions."""

    constitutional: float = Field(
        ..., ge=0.0, le=1.0, description="Constitutional interpretation uncertainty"
    )
    technical: float = Field(
        ..., ge=0.0, le=1.0, description="Technical implementation uncertainty"
    )
    stakeholder: float = Field(
        ..., ge=0.0, le=1.0, description="Stakeholder consensus uncertainty"
    )
    precedent: float = Field(
        ..., ge=0.0, le=1.0, description="Historical precedent uncertainty"
    )
    complexity: float = Field(
        ..., ge=0.0, le=1.0, description="Overall complexity uncertainty"
    )


class HITLSamplingRequest(BaseModel):
    """Schema for requesting human-in-the-loop sampling assessment."""

    decision_id: str = Field(..., description="Unique identifier for the decision")
    decision_context: dict[str, Any] = Field(
        ..., description="Context information for the decision"
    )
    ai_confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="AI confidence score if available"
    )
    principle_ids: list[int] | None = Field(
        None, description="Related constitutional principle IDs"
    )

    # Decision characteristics
    decision_scope: str | None = Field(
        "local", description="Scope of decision (local, service, system, global)"
    )
    time_pressure: str | None = Field(
        "normal", description="Time pressure level (low, normal, high, critical)"
    )
    reversibility: str | None = Field(
        "reversible", description="Reversibility (reversible, difficult, irreversible)"
    )
    impact_magnitude: str | None = Field(
        "low", description="Impact magnitude (low, medium, high, critical)"
    )
    safety_critical: bool = Field(
        False, description="Whether decision is safety-critical"
    )

    # Stakeholder information
    stakeholder_count: int | None = Field(
        1, ge=1, description="Number of stakeholders involved"
    )
    stakeholder_diversity: float | None = Field(
        0.5, ge=0.0, le=1.0, description="Stakeholder diversity score"
    )
    stakeholder_conflicts: bool = Field(
        False, description="Whether stakeholder conflicts exist"
    )
    requires_public_consultation: bool = Field(
        False, description="Whether public consultation is required"
    )

    # Technical factors
    multi_service: bool = Field(False, description="Decision affects multiple services")
    database_changes: bool = Field(False, description="Requires database modifications")
    external_apis: bool = Field(False, description="Involves external API calls")
    real_time_processing: bool = Field(
        False, description="Requires real-time processing"
    )
    security_implications: bool = Field(False, description="Has security implications")
    performance_critical: bool = Field(
        False, description="Performance-critical operation"
    )
    novel_technology: bool = Field(
        False, description="Uses novel or experimental technology"
    )

    # Context flags
    novel_scenario: bool = Field(False, description="Novel scenario without precedent")
    has_training_data: bool = Field(True, description="AI has relevant training data")
    domain_expertise_available: bool = Field(
        True, description="Domain expertise is available"
    )
    clear_requirements: bool = Field(
        True, description="Requirements are clear and well-defined"
    )
    has_implementation_precedent: bool = Field(
        True, description="Implementation precedent exists"
    )
    has_stakeholder_feedback: bool = Field(
        False, description="Previous stakeholder feedback available"
    )
    escalation_required: bool = Field(
        False, description="Escalation from conflict resolution"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "policy_update_2024_001",
                "decision_context": {
                    "policy_type": "privacy_protection",
                    "affected_users": 10000,
                    "regulatory_compliance": True,
                },
                "ai_confidence": 0.72,
                "principle_ids": [1, 3, 7],
                "decision_scope": "system",
                "safety_critical": True,
                "stakeholder_count": 5,
                "stakeholder_conflicts": True,
            }
        }


class HITLSamplingResult(BaseModel):
    """Schema for human-in-the-loop sampling assessment result."""

    decision_id: str = Field(..., description="Decision identifier")
    overall_uncertainty: float = Field(
        ..., ge=0.0, le=1.0, description="Overall uncertainty score"
    )
    dimensional_uncertainties: UncertaintyMetrics = Field(
        ..., description="Uncertainty by dimension"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="AI confidence in decision"
    )

    # Sampling decision
    requires_human_oversight: bool = Field(
        ..., description="Whether human oversight is required"
    )
    recommended_oversight_level: str = Field(
        ..., description="Recommended level of oversight"
    )
    triggers_activated: list[str] = Field(
        ..., description="List of activated sampling triggers"
    )

    # Assessment metadata
    assessment_timestamp: datetime = Field(
        ..., description="When assessment was performed"
    )
    assessment_metadata: dict[str, Any] = Field(
        ..., description="Additional assessment metadata"
    )

    # Performance tracking
    processing_time_ms: float | None = Field(
        None, description="Assessment processing time in milliseconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "policy_update_2024_001",
                "overall_uncertainty": 0.78,
                "dimensional_uncertainties": {
                    "constitutional": 0.65,
                    "technical": 0.45,
                    "stakeholder": 0.85,
                    "precedent": 0.70,
                    "complexity": 0.75,
                },
                "confidence_score": 0.72,
                "requires_human_oversight": True,
                "recommended_oversight_level": "constitutional_council",
                "triggers_activated": [
                    "high_uncertainty",
                    "stakeholder_conflict",
                    "safety_critical",
                ],
                "assessment_timestamp": "2024-01-15T10:30:00Z",
            }
        }


class HITLFeedbackRequest(BaseModel):
    """Schema for submitting human feedback on HITL sampling decisions."""

    assessment_id: str = Field(..., description="ID of the original assessment")
    human_decision: dict[str, Any] = Field(
        ..., description="Human decision and reasoning"
    )
    agreed_with_assessment: bool = Field(
        ..., description="Whether human agreed with AI assessment"
    )
    reasoning: str | None = Field(
        None, description="Human reasoning for the decision"
    )
    quality_score: float | None = Field(
        0.8, ge=0.0, le=1.0, description="Quality score for the decision"
    )
    feedback_metadata: dict[str, Any] | None = Field(
        None, description="Additional feedback metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "assessment_id": "policy_update_2024_001",
                "human_decision": {
                    "oversight_needed": True,
                    "final_decision": "approved_with_conditions",
                    "conditions": ["additional_stakeholder_review", "security_audit"],
                },
                "agreed_with_assessment": True,
                "reasoning": "Assessment correctly identified stakeholder conflicts requiring Constitutional Council review",
                "quality_score": 0.9,
            }
        }


class HITLPerformanceMetrics(BaseModel):
    """Schema for HITL sampling performance metrics."""

    total_assessments: int = Field(
        ..., description="Total number of assessments performed"
    )
    human_oversight_triggered: int = Field(
        ..., description="Number of times human oversight was triggered"
    )
    oversight_rate: float = Field(
        ..., ge=0.0, le=1.0, description="Rate of human oversight triggers"
    )
    accuracy_rate: float = Field(
        ..., ge=0.0, le=1.0, description="Accuracy rate of oversight predictions"
    )
    false_positive_rate: float = Field(
        ..., ge=0.0, le=1.0, description="False positive rate"
    )
    recent_accuracy: float = Field(
        ..., ge=0.0, le=1.0, description="Recent accuracy (last 50 assessments)"
    )
    recent_quality: float = Field(
        ..., ge=0.0, le=1.0, description="Recent decision quality score"
    )

    # Configuration
    current_thresholds: dict[str, float] = Field(
        ..., description="Current uncertainty and confidence thresholds"
    )
    learning_enabled: bool = Field(
        ..., description="Whether adaptive learning is enabled"
    )
    feedback_samples: int = Field(
        ..., description="Number of feedback samples collected"
    )
    threshold_adjustments_count: int = Field(
        ..., description="Number of threshold adjustments made"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_assessments": 1250,
                "human_oversight_triggered": 187,
                "oversight_rate": 0.15,
                "accuracy_rate": 0.94,
                "false_positive_rate": 0.04,
                "recent_accuracy": 0.96,
                "recent_quality": 0.88,
                "current_thresholds": {
                    "uncertainty_threshold": 0.75,
                    "confidence_threshold": 0.75,
                },
                "learning_enabled": True,
                "feedback_samples": 89,
                "threshold_adjustments_count": 3,
            }
        }


# Public Consultation Schemas


class PublicProposalCreate(BaseModel):
    """Schema for creating a public amendment proposal."""

    title: str = Field(..., min_length=10, max_length=200, description="Proposal title")
    description: str = Field(
        ..., min_length=50, max_length=2000, description="Detailed proposal description"
    )
    proposed_changes: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description="Specific changes being proposed",
    )
    justification: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description="Justification for the proposal",
    )
    submitter_name: str | None = Field(
        None, max_length=100, description="Name of the submitter"
    )
    submitter_email: str | None = Field(
        None, max_length=100, description="Email of the submitter"
    )
    submitter_organization: str | None = Field(
        None, max_length=100, description="Organization of the submitter"
    )
    stakeholder_group: str = Field(
        ..., description="Stakeholder group (citizen, expert, etc.)"
    )
    consultation_period_days: int | None = Field(
        30, ge=7, le=90, description="Consultation period in days"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Enhanced Privacy Protection Framework",
                "description": "This proposal aims to strengthen privacy protections for citizens in AI governance systems by implementing comprehensive data protection measures.",
                "proposed_changes": "Add explicit consent requirements for all data processing in governance decisions and implement data minimization principles.",
                "justification": "Current privacy protections are insufficient for modern AI governance needs and citizen trust.",
                "submitter_name": "Dr. Jane Privacy",
                "submitter_email": "jane@privacyadvocates.org",
                "submitter_organization": "Digital Rights Foundation",
                "stakeholder_group": "privacy_advocate",
                "consultation_period_days": 30,
            }
        }


class PublicProposalResponse(BaseModel):
    """Schema for public proposal response."""

    id: int = Field(..., description="Unique proposal identifier")
    title: str = Field(..., description="Proposal title")
    description: str = Field(..., description="Detailed proposal description")
    proposed_changes: str = Field(..., description="Specific changes being proposed")
    justification: str = Field(..., description="Justification for the proposal")
    submitter_name: str | None = Field(None, description="Name of the submitter")
    submitter_organization: str | None = Field(
        None, description="Organization of the submitter"
    )
    stakeholder_group: str = Field(..., description="Stakeholder group")
    status: str = Field(..., description="Current proposal status")
    created_at: datetime = Field(..., description="Proposal creation timestamp")
    consultation_period_days: int = Field(
        ..., description="Consultation period in days"
    )
    public_support_count: int = Field(..., description="Number of public supporters")
    requires_review: bool = Field(
        ..., description="Whether proposal requires manual review"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Enhanced Privacy Protection Framework",
                "description": "Comprehensive proposal for strengthening privacy protections in AI governance.",
                "proposed_changes": "Add explicit consent requirements and data minimization principles.",
                "justification": "Current privacy protections are insufficient for modern AI governance needs.",
                "submitter_name": "Dr. Jane Privacy",
                "submitter_organization": "Digital Rights Foundation",
                "stakeholder_group": "privacy_advocate",
                "status": "open",
                "created_at": "2024-01-15T10:30:00Z",
                "consultation_period_days": 30,
                "public_support_count": 125,
                "requires_review": False,
            }
        }


class PublicFeedbackCreate(BaseModel):
    """Schema for creating public feedback."""

    proposal_id: int | None = Field(
        None, description="ID of the proposal being commented on"
    )
    amendment_id: int | None = Field(
        None, description="ID of the amendment being commented on"
    )
    feedback_type: str | None = Field(
        None, description="Type of feedback (support, oppose, suggestion, etc.)"
    )
    content: str = Field(
        ..., min_length=10, max_length=5000, description="Feedback content"
    )
    submitter_name: str | None = Field(
        None, max_length=100, description="Name of the submitter"
    )
    submitter_email: str | None = Field(
        None, max_length=100, description="Email of the submitter"
    )
    stakeholder_group: str = Field(
        ..., description="Stakeholder group of the submitter"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "proposal_id": 1,
                "feedback_type": "support",
                "content": "I strongly support this proposal as it addresses critical privacy concerns in AI governance. The proposed changes would significantly improve citizen trust.",
                "submitter_name": "John Citizen",
                "submitter_email": "john@example.com",
                "stakeholder_group": "citizen",
            }
        }


class PublicFeedbackResponse(BaseModel):
    """Schema for public feedback response."""

    id: int = Field(..., description="Unique feedback identifier")
    proposal_id: int | None = Field(None, description="ID of the related proposal")
    amendment_id: int | None = Field(None, description="ID of the related amendment")
    feedback_type: str = Field(..., description="Type of feedback")
    content: str = Field(..., description="Feedback content")
    submitter_name: str | None = Field(None, description="Name of the submitter")
    stakeholder_group: str = Field(..., description="Stakeholder group")
    sentiment_score: float | None = Field(
        None, ge=0.0, le=1.0, description="Automated sentiment score"
    )
    is_verified: bool = Field(..., description="Whether submitter is verified")
    created_at: datetime = Field(..., description="Feedback creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "proposal_id": 1,
                "feedback_type": "support",
                "content": "I strongly support this proposal as it addresses critical privacy concerns.",
                "submitter_name": "John Citizen",
                "stakeholder_group": "citizen",
                "sentiment_score": 0.85,
                "is_verified": True,
                "created_at": "2024-01-15T14:30:00Z",
            }
        }


class ConsultationMetricsResponse(BaseModel):
    """Schema for consultation metrics response."""

    total_proposals: int = Field(..., description="Total number of proposals")
    active_consultations: int = Field(..., description="Number of active consultations")
    total_participants: int = Field(..., description="Total number of participants")
    feedback_count: int = Field(..., description="Total feedback items collected")
    sentiment_distribution: dict[str, int] = Field(
        ..., description="Distribution of sentiment in feedback"
    )
    stakeholder_participation: dict[str, int] = Field(
        ..., description="Participation by stakeholder group"
    )
    engagement_rate: float = Field(
        ..., ge=0.0, le=1.0, description="Overall engagement rate"
    )
    completion_rate: float = Field(
        ..., ge=0.0, le=1.0, description="Consultation completion rate"
    )
    time_period_days: int | None = Field(
        None, description="Time period for metrics calculation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_proposals": 25,
                "active_consultations": 8,
                "total_participants": 342,
                "feedback_count": 156,
                "sentiment_distribution": {
                    "positive": 45,
                    "neutral": 35,
                    "negative": 20,
                },
                "stakeholder_participation": {
                    "citizen": 60,
                    "expert": 25,
                    "civil_society": 10,
                    "industry": 5,
                },
                "engagement_rate": 0.75,
                "completion_rate": 0.68,
                "time_period_days": 30,
            }
        }
