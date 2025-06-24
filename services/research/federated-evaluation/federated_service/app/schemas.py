"""
Pydantic schemas for Federated Evaluation Service

Defines request/response models for federated evaluation API endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class PlatformType(str, Enum):
    """Supported platform types for federated evaluation."""

    CLOUD_OPENAI = "cloud_openai"
    CLOUD_ANTHROPIC = "cloud_anthropic"
    CLOUD_COHERE = "cloud_cohere"
    CLOUD_GROQ = "cloud_groq"
    EDGE_LOCAL = "edge_local"
    FEDERATED_NODE = "federated_node"


class EvaluationStatus(str, Enum):
    """Status of federated evaluation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    AGGREGATING = "aggregating"


class AggregationMethod(str, Enum):
    """Supported secure aggregation methods."""

    FEDERATED_AVERAGING = "federated_averaging"
    SECURE_SUM = "secure_sum"
    DIFFERENTIAL_PRIVATE = "differential_private"
    BYZANTINE_ROBUST = "byzantine_robust"


class PrivacyMechanism(str, Enum):
    """Supported privacy mechanisms."""

    LAPLACE = "laplace"
    GAUSSIAN = "gaussian"
    EXPONENTIAL = "exponential"
    LOCAL_DP = "local_dp"


# Request/Response Models


class NodeConfiguration(BaseModel):
    """Configuration for registering a federated node."""

    platform_type: PlatformType
    endpoint_url: str = Field(..., description="API endpoint URL for the node")
    api_key: str | None = Field(None, description="API key for authentication")
    capabilities: dict[str, Any] = Field(
        default_factory=dict, description="Node capabilities and metadata"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "platform_type": "cloud_openai",
                "endpoint_url": "https://api.openai.com/v1",
                "api_key": "sk-...",
                "capabilities": {
                    "models": ["gpt-4", "gpt-3.5-turbo"],
                    "max_tokens": 4096,
                    "supports_streaming": True,
                },
            }
        }
    }


class FederatedEvaluationRequest(BaseModel):
    """Request for federated evaluation."""

    policy_content: str = Field(..., description="Policy content to evaluate")
    evaluation_criteria: dict[str, Any] = Field(
        ..., description="Evaluation criteria and parameters"
    )
    target_platforms: list[PlatformType] = Field(..., description="Target platforms for evaluation")
    privacy_requirements: dict[str, Any] = Field(
        default_factory=lambda: {"epsilon": 1.0, "mechanism": "laplace"},
        description="Privacy requirements for evaluation",
    )

    @field_validator("target_platforms")
    @classmethod
    def validate_platforms(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        if not v:
            raise ValueError("At least one target platform must be specified")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "policy_content": 'package acgs.policy\n\nallow {\n    input.action == "read"\n    input.user.role == "admin"\n}',
                "evaluation_criteria": {
                    "category": "constitutional",
                    "safety_level": "standard",
                    "metrics": ["compliance", "consistency", "performance"],
                },
                "target_platforms": ["cloud_openai", "cloud_anthropic"],
                "privacy_requirements": {"epsilon": 1.0, "mechanism": "laplace"},
            }
        }
    }


class EvaluationMetrics(BaseModel):
    """Evaluation metrics from a federated node."""

    policy_compliance_score: float = Field(..., ge=0.0, le=1.0)
    execution_time_ms: float = Field(..., ge=0.0)
    success_rate: float = Field(..., ge=0.0, le=1.0)
    consistency_score: float | None = Field(None, ge=0.0, le=1.0)
    privacy_score: float | None = Field(None, ge=0.0, le=1.0)
    additional_metrics: dict[str, Any] = Field(default_factory=dict)


class AggregatedResults(BaseModel):
    """Aggregated results from federated evaluation."""

    success: bool
    aggregation_method: AggregationMethod
    participant_nodes: list[str]
    aggregation_id: str
    aggregation_time: float

    # Aggregated metrics
    policy_compliance_score: float | None = None
    execution_time_ms: float | None = None
    success_rate: float
    consistency_score: float
    privacy_score: float

    # Statistical measures
    policy_compliance_score_std: float | None = None
    execution_time_ms_std: float | None = None

    # Privacy and security
    privacy_budget_used: float
    byzantine_nodes_detected: int
    cryptographic_verification: bool | None = None

    # Metadata
    participant_count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FederatedEvaluationResponse(BaseModel):
    """Response for federated evaluation request."""

    task_id: str
    status: EvaluationStatus
    message: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    estimated_completion_time: datetime | None = None


class EvaluationStatusResponse(BaseModel):
    """Response for evaluation status query."""

    task_id: str
    status: EvaluationStatus
    created_at: datetime
    target_platforms: list[PlatformType]
    results: AggregatedResults | None = None
    error: str | None = None
    progress: dict[str, Any] | None = None


class NodeStatusResponse(BaseModel):
    """Response for node status query."""

    node_id: str
    platform_type: PlatformType
    status: str
    last_heartbeat: datetime
    performance_metrics: dict[str, Any]
    capabilities: dict[str, Any]


class PrivacyMetricsResponse(BaseModel):
    """Response for privacy metrics query."""

    privacy_budget: dict[str, float]
    metrics: dict[str, Any]
    recent_history: list[dict[str, Any]]


class AggregationConfigRequest(BaseModel):
    """Request to configure aggregation parameters."""

    method: AggregationMethod = AggregationMethod.FEDERATED_AVERAGING
    privacy_budget: float = Field(1.0, gt=0.0, le=10.0)
    byzantine_tolerance: float = Field(0.33, ge=0.0, le=0.5)
    min_participants: int = Field(2, ge=1, le=10)
    max_participants: int = Field(10, ge=1, le=50)

    @field_validator("max_participants")
    @classmethod
    def validate_max_participants(cls, v, info):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        if (
            hasattr(info, "data")
            and "min_participants" in info.data
            and v < info.data["min_participants"]
        ):
            raise ValueError("max_participants must be >= min_participants")
        return v


class SecureShareRequest(BaseModel):
    """Request to create secure shares."""

    data: dict[str, Any]
    num_shares: int = Field(..., ge=2, le=10)
    participants: list[str]


class SecureShareResponse(BaseModel):
    """Response with secure shares."""

    shares: list[dict[str, Any]]
    verification_hashes: list[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FederatedMetricsResponse(BaseModel):
    """Response for federated evaluation metrics."""

    evaluation_metrics: dict[str, Any]
    aggregation_metrics: dict[str, Any]
    privacy_metrics: dict[str, Any]
    node_metrics: dict[str, Any]
    system_health: dict[str, Any]


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = None


# Legacy aliases for backward compatibility with test scripts
PolicyEvaluationRequest = FederatedEvaluationRequest


class FederatedLearningRequest(BaseModel):
    """Request for federated learning coordination."""

    min_participants: int = Field(..., ge=2, description="Minimum number of participants required")
    max_participants: int = Field(..., ge=2, description="Maximum number of participants allowed")
    aggregation_method: AggregationMethod = Field(
        AggregationMethod.FEDERATED_AVERAGING,
        description="Method for aggregating results",
    )
    privacy_budget: float = Field(
        1.0, ge=0.1, le=10.0, description="Privacy budget for differential privacy"
    )
    timeout_seconds: int = Field(300, ge=30, le=3600, description="Timeout for federated operation")

    model_config = {
        "json_schema_extra": {
            "example": {
                "min_participants": 3,
                "max_participants": 10,
                "aggregation_method": "federated_averaging",
                "privacy_budget": 1.0,
                "timeout_seconds": 300,
            }
        }
    }
