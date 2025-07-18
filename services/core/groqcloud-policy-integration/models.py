"""
Domain Models for GroqCloud Policy Integration Service
Constitutional Hash: cdd01ef066bc6cf2
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4


# GroqCloud Model Tiers
class GroqModelTier(Enum):
    """4-tier model architecture for policy evaluation"""

    NANO = "nano"  # 1ms target - allam-2-7b
    FAST = "fast"  # 2ms target - llama-3.1-8b-instant
    BALANCED = "balanced"  # 3ms target - qwen/qwen3-32b
    PREMIUM = "premium"  # 5ms target - llama-3.3-70b-versatile


# Policy Types
class PolicyType(Enum):
    """Types of policies that can be evaluated"""

    ACCESS_CONTROL = "access_control"
    RATE_LIMITING = "rate_limiting"
    DATA_GOVERNANCE = "data_governance"
    PRIVACY_COMPLIANCE = "privacy_compliance"
    SECURITY_VALIDATION = "security_validation"
    RESOURCE_ALLOCATION = "resource_allocation"
    COST_OPTIMIZATION = "cost_optimization"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"


# Compliance Levels
class ComplianceLevel(Enum):
    """Levels of compliance for policy evaluation"""

    CRITICAL = "critical"  # Must be 100% compliant
    HIGH = "high"  # 95%+ compliance required
    MEDIUM = "medium"  # 85%+ compliance required
    LOW = "low"  # 70%+ compliance required


# Validation Status
class ValidationStatus(Enum):
    """Status of constitutional validation"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    PENDING = "pending"
    ERROR = "error"


# Cache Status
class CacheStatus(Enum):
    """Status of cache operations"""

    HIT = "hit"
    MISS = "miss"
    EXPIRED = "expired"
    ERROR = "error"


# Core Domain Models


@dataclass
class ConstitutionalContext:
    """Constitutional context for policy evaluation"""

    constitutional_hash: str = "cdd01ef066bc6cf2"
    purpose: str = ""
    tenant_id: Optional[str] = None
    compliance_level: ComplianceLevel = ComplianceLevel.HIGH
    additional_constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstitutionalValidation:
    """Result of constitutional validation"""

    is_compliant: bool
    compliance_score: float  # 0.0 to 1.0
    violations: List[str]
    recommendations: List[str]
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)
    validator_version: str = "1.0.0"


@dataclass
class ModelConfiguration:
    """Configuration for a GroqCloud model tier"""

    tier: GroqModelTier
    model_name: str
    max_tokens: int
    temperature: float
    latency_target_ms: float
    cost_per_million_tokens: float
    capabilities: List[str]
    context_window: int = 4096
    requires_premium: bool = False
    total_parameters: Optional[str] = None  # e.g., "1T" for Kimi K2
    activated_parameters: Optional[str] = None  # e.g., "32B" for Kimi K2
    architecture_type: str = "transformer"  # "transformer", "moe", etc.


@dataclass
class PolicyRequest:
    """Request for policy evaluation"""

    request_id: UUID = field(default_factory=uuid4)
    policy_type: PolicyType = PolicyType.ACCESS_CONTROL
    policy_id: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    constitutional_context: ConstitutionalContext = field(
        default_factory=ConstitutionalContext
    )
    complexity_score: float = 0.5  # 0.0 (simple) to 1.0 (complex)
    urgency_level: str = "normal"  # low, normal, high, critical
    requires_reasoning: bool = True
    cache_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyDecision:
    """Individual policy decision result"""

    decision_id: UUID = field(default_factory=uuid4)
    policy_id: str = ""
    decision: str = ""  # allow, deny, conditional
    confidence: float = 0.0  # 0.0 to 1.0
    reasoning: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    constitutional_validation: Optional[ConstitutionalValidation] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyResponse:
    """Response from policy evaluation"""

    request_id: UUID
    decision: str  # allow, deny, conditional
    confidence: float  # 0.0 to 1.0
    reasoning: List[str]
    tier_used: GroqModelTier
    execution_time_ms: float
    constitutional_validation: ConstitutionalValidation
    policy_decisions: List[PolicyDecision]
    cache_status: CacheStatus = CacheStatus.MISS
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OPAPolicy:
    """OPA policy definition"""

    policy_id: str
    name: str
    version: str
    policy_type: PolicyType
    rego_content: str
    constitutional_hash: str = "cdd01ef066bc6cf2"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyEvaluation:
    """Complete policy evaluation record"""

    evaluation_id: UUID = field(default_factory=uuid4)
    request: PolicyRequest = field(default_factory=PolicyRequest)
    response: Optional[PolicyResponse] = None
    groq_tier_used: Optional[GroqModelTier] = None
    opa_policies_evaluated: List[str] = field(default_factory=list)
    total_execution_time_ms: float = 0.0
    constitutional_compliance: bool = True
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PolicyMetrics:
    """Service metrics for monitoring"""

    total_evaluations: int = 0
    successful_evaluations: int = 0
    failed_evaluations: int = 0
    average_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    tier_distribution: Dict[str, int] = field(default_factory=dict)
    constitutional_violations: int = 0
    last_reset: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ServiceHealth:
    """Service health status"""

    status: str  # healthy, degraded, unhealthy
    version: str
    constitutional_hash: str
    uptime_seconds: float
    groq_client_healthy: bool
    opa_engine_healthy: bool
    total_evaluations: int
    average_latency_ms: float
    cache_hit_rate: float
    last_check: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PolicyCache:
    """Cache for policy evaluation results"""

    cache_key: str = ""
    result: Optional[PolicyDecision] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    hit_count: int = 0

    async def get(self, key: str) -> Optional[PolicyDecision]:
        """Get cached result"""
        # Implementation would check expiration and return result
        return self.result if self.cache_key == key else None

    async def set(self, key: str, result: PolicyDecision, ttl_seconds: int = 300):
        """Set cached result"""
        self.cache_key = key
        self.result = result
        self.created_at = datetime.utcnow()
        # Set expiration based on TTL
        from datetime import timedelta

        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)


@dataclass
class PolicyAudit:
    """Audit entry for policy evaluations"""

    audit_id: UUID = field(default_factory=uuid4)
    request_id: UUID = field(default_factory=uuid4)
    policy_id: str = ""
    decision: str = ""
    confidence: float = 0.0
    tier_used: GroqModelTier = GroqModelTier.NANO
    execution_time_ms: float = 0.0
    constitutional_compliance: bool = True
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TierSelection:
    """Result of tier selection process"""

    recommended_tier: GroqModelTier
    expected_latency_ms: float
    expected_cost_per_million: float
    reasoning: str
    alternative_tiers: List[GroqModelTier] = field(default_factory=list)
    constraints_applied: List[str] = field(default_factory=list)


@dataclass
class ModelMetrics:
    """Metrics for individual model performance"""

    model_name: str
    tier: GroqModelTier
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    total_tokens_processed: int = 0
    total_cost: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PolicyTemplate:
    """Template for common policy patterns"""

    template_id: str
    name: str
    description: str
    policy_type: PolicyType
    rego_template: str
    parameters: List[Dict[str, Any]]
    example_usage: Dict[str, Any]
    constitutional_requirements: List[str]
    recommended_tier: GroqModelTier
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PolicyBatch:
    """Batch of policies for evaluation"""

    batch_id: UUID = field(default_factory=uuid4)
    requests: List[PolicyRequest] = field(default_factory=list)
    priority: str = "normal"  # low, normal, high, critical
    max_latency_ms: float = 100.0
    constitutional_context: ConstitutionalContext = field(
        default_factory=ConstitutionalContext
    )
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_request(self, request: PolicyRequest):
        """Add request to batch"""
        self.requests.append(request)

    def size(self) -> int:
        """Get batch size"""
        return len(self.requests)
