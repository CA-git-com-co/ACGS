"""
Domain Models for A2A (Agent-to-Agent) Policy Integration Service
Constitutional Hash: cdd01ef066bc6cf2
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Set
from uuid import UUID, uuid4


# A2A Protocol Types
class A2AProtocolType(Enum):
    """Types of A2A communication protocols"""

    DIRECT_MESSAGE = "direct_message"
    BROADCAST = "broadcast"
    MULTICAST = "multicast"
    REQUEST_RESPONSE = "request_response"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    CONSENSUS_PROTOCOL = "consensus_protocol"
    COORDINATION_PROTOCOL = "coordination_protocol"


class A2AMessageType(Enum):
    """Types of A2A messages"""

    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_RESPONSE = "resource_response"
    COORDINATION_REQUEST = "coordination_request"
    COORDINATION_RESPONSE = "coordination_response"
    CONSENSUS_VOTE = "consensus_vote"
    CONSENSUS_RESULT = "consensus_result"
    POLICY_UPDATE = "policy_update"
    CAPABILITY_ADVERTISEMENT = "capability_advertisement"
    HEALTH_CHECK = "health_check"
    ERROR_NOTIFICATION = "error_notification"


class A2AAgentType(Enum):
    """Types of agents in A2A communication"""

    CLAUDE_AGENT = "claude_agent"
    OPENCODE_AGENT = "opencode_agent"
    MCP_SERVICE = "mcp_service"
    CORE_SERVICE = "core_service"
    WORKER_AGENT = "worker_agent"
    COORDINATOR_AGENT = "coordinator_agent"
    BLACKBOARD_SERVICE = "blackboard_service"
    EXTERNAL_AGENT = "external_agent"


class A2ASecurityLevel(Enum):
    """Security levels for A2A communication"""

    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"


class A2AComplianceLevel(Enum):
    """Constitutional compliance levels for A2A operations"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class A2AMessageStatus(Enum):
    """Status of A2A messages"""

    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    PROCESSED = "processed"
    FAILED = "failed"
    EXPIRED = "expired"
    REJECTED = "rejected"


class A2AAuthenticationMethod(Enum):
    """A2A authentication methods"""

    JWT_TOKEN = "jwt_token"
    CERTIFICATE = "certificate"
    API_KEY = "api_key"
    MUTUAL_TLS = "mutual_tls"
    OAUTH2 = "oauth2"
    CONSTITUTIONAL_HASH = "constitutional_hash"


# Core Domain Models


@dataclass
class ConstitutionalContext:
    """Constitutional context for A2A operations"""

    constitutional_hash: str = "cdd01ef066bc6cf2"
    purpose: str = ""
    tenant_id: Optional[str] = None
    compliance_level: A2AComplianceLevel = A2AComplianceLevel.HIGH
    additional_constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstitutionalValidation:
    """Result of constitutional validation for A2A operations"""

    is_compliant: bool
    compliance_score: float  # 0.0 to 1.0
    violations: List[str]
    recommendations: List[str]
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)
    validator_version: str = "1.0.0"


@dataclass
class A2AAgentIdentity:
    """A2A agent identity and capabilities"""

    agent_id: UUID = field(default_factory=uuid4)
    agent_name: str = ""
    agent_type: A2AAgentType = A2AAgentType.CLAUDE_AGENT
    service_url: str = ""
    port: int = 0
    version: str = "1.0.0"
    capabilities: List[str] = field(default_factory=list)
    supported_protocols: List[A2AProtocolType] = field(default_factory=list)
    supported_message_types: List[A2AMessageType] = field(default_factory=list)
    security_level: A2ASecurityLevel = A2ASecurityLevel.INTERNAL
    authentication_methods: List[A2AAuthenticationMethod] = field(default_factory=list)
    public_key: Optional[str] = None
    certificate: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class A2AMessage:
    """A2A message structure"""

    message_id: UUID = field(default_factory=uuid4)
    conversation_id: Optional[UUID] = None
    sender_id: UUID = field(default_factory=uuid4)
    recipient_id: Optional[UUID] = None
    recipient_group: Optional[str] = None
    message_type: A2AMessageType = A2AMessageType.TASK_REQUEST
    protocol_type: A2AProtocolType = A2AProtocolType.DIRECT_MESSAGE
    subject: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    security_level: A2ASecurityLevel = A2ASecurityLevel.INTERNAL
    priority: int = 5  # 1-10, 10 being highest
    ttl_seconds: int = 300  # Time to live
    requires_acknowledgment: bool = True
    requires_response: bool = False
    constitutional_context: ConstitutionalContext = field(
        default_factory=ConstitutionalContext
    )
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: A2AMessageStatus = A2AMessageStatus.PENDING
    signature: Optional[str] = None
    encryption_key: Optional[str] = None

    def __post_init__(self):
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(seconds=self.ttl_seconds)


@dataclass
class A2AMessageRoute:
    """A2A message routing information"""

    route_id: UUID = field(default_factory=uuid4)
    message_id: UUID = field(default_factory=uuid4)
    sender_id: UUID = field(default_factory=uuid4)
    recipient_id: UUID = field(default_factory=uuid4)
    intermediary_agents: List[UUID] = field(default_factory=list)
    routing_strategy: str = "direct"  # direct, multi_hop, broadcast
    routing_rules: Dict[str, Any] = field(default_factory=dict)
    delivery_guarantee: str = (
        "at_least_once"  # at_most_once, at_least_once, exactly_once
    )
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    hops: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class A2AConversation:
    """A2A conversation context"""

    conversation_id: UUID = field(default_factory=uuid4)
    participants: List[UUID] = field(default_factory=list)
    conversation_type: str = "peer_to_peer"  # peer_to_peer, group, broadcast
    topic: str = ""
    purpose: str = ""
    messages: List[UUID] = field(default_factory=list)
    state: str = "active"  # active, paused, completed, failed
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    constitutional_context: ConstitutionalContext = field(
        default_factory=ConstitutionalContext
    )


@dataclass
class A2ASecurityPolicy:
    """Security policy for A2A communications"""

    policy_id: UUID = field(default_factory=uuid4)
    policy_name: str = ""
    version: str = "1.0.0"
    allowed_agent_types: Set[A2AAgentType] = field(default_factory=set)
    allowed_message_types: Set[A2AMessageType] = field(default_factory=set)
    allowed_protocols: Set[A2AProtocolType] = field(default_factory=set)
    required_security_level: A2ASecurityLevel = A2ASecurityLevel.INTERNAL
    required_authentication: List[A2AAuthenticationMethod] = field(default_factory=list)
    message_size_limit: int = 10 * 1024 * 1024  # 10MB
    rate_limit_per_minute: int = 100
    encryption_required: bool = True
    signature_required: bool = True
    allowed_domains: Set[str] = field(default_factory=set)
    blocked_domains: Set[str] = field(default_factory=set)
    quarantine_suspicious: bool = True
    constitutional_hash: str = "cdd01ef066bc6cf2"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class A2ACapabilityAdvertisement:
    """Agent capability advertisement"""

    advertisement_id: UUID = field(default_factory=uuid4)
    agent_id: UUID = field(default_factory=uuid4)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    service_endpoints: List[str] = field(default_factory=list)
    supported_operations: List[str] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    availability_schedule: Dict[str, Any] = field(default_factory=dict)
    cost_model: Dict[str, Any] = field(default_factory=dict)
    sla_commitments: Dict[str, Any] = field(default_factory=dict)
    constitutional_compliance: float = 1.0
    advertisement_ttl: int = 3600  # 1 hour
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(
                seconds=self.advertisement_ttl
            )


@dataclass
class A2AServiceDiscovery:
    """A2A service discovery information"""

    discovery_id: UUID = field(default_factory=uuid4)
    service_name: str = ""
    service_type: str = ""
    agent_id: UUID = field(default_factory=uuid4)
    endpoints: List[str] = field(default_factory=list)
    health_check_url: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    registration_time: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    heartbeat_interval: int = 30  # seconds
    ttl: int = 300  # 5 minutes
    is_healthy: bool = True
    health_score: float = 1.0


@dataclass
class A2AMetrics:
    """Metrics for A2A operations"""

    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_messages_delivered: int = 0
    total_messages_failed: int = 0
    total_conversations: int = 0
    active_conversations: int = 0
    average_message_size: float = 0.0
    average_delivery_time_ms: float = 0.0
    peak_delivery_time_ms: float = 0.0
    message_types_sent: Dict[str, int] = field(default_factory=dict)
    message_types_received: Dict[str, int] = field(default_factory=dict)
    protocol_usage: Dict[str, int] = field(default_factory=dict)
    security_violations: int = 0
    constitutional_violations: int = 0
    authentication_failures: int = 0
    rate_limit_hits: int = 0
    quarantined_messages: int = 0
    connected_agents: int = 0
    last_reset: datetime = field(default_factory=datetime.utcnow)

    def update_delivery_time(self, delivery_time_ms: float):
        """Update delivery timing metrics"""
        total_messages = self.total_messages_delivered + 1
        self.average_delivery_time_ms = (
            self.average_delivery_time_ms * self.total_messages_delivered
            + delivery_time_ms
        ) / total_messages
        self.total_messages_delivered = total_messages
        if delivery_time_ms > self.peak_delivery_time_ms:
            self.peak_delivery_time_ms = delivery_time_ms


@dataclass
class A2AOperation:
    """A2A operation record"""

    operation_id: UUID = field(default_factory=uuid4)
    operation_type: str = ""
    agent_id: UUID = field(default_factory=uuid4)
    target_agent_id: Optional[UUID] = None
    message_id: Optional[UUID] = None
    constitutional_context: ConstitutionalContext = field(
        default_factory=ConstitutionalContext
    )
    validation_result: Optional[ConstitutionalValidation] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class A2AAuditEntry:
    """Audit entry for A2A operations"""

    audit_id: UUID = field(default_factory=uuid4)
    operation: A2AOperation = field(default_factory=A2AOperation)
    message: Optional[A2AMessage] = None
    security_context: Dict[str, Any] = field(default_factory=dict)
    constitutional_context: ConstitutionalContext = field(
        default_factory=ConstitutionalContext
    )
    validation_result: ConstitutionalValidation = field(
        default_factory=ConstitutionalValidation
    )
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary"""
        return {
            "audit_id": str(self.audit_id),
            "operation_id": str(self.operation.operation_id),
            "operation_type": self.operation.operation_type,
            "agent_id": str(self.operation.agent_id),
            "target_agent_id": (
                str(self.operation.target_agent_id)
                if self.operation.target_agent_id
                else None
            ),
            "message_id": str(self.message.message_id) if self.message else None,
            "message_type": self.message.message_type.value if self.message else None,
            "success": self.operation.success,
            "execution_time_ms": self.operation.execution_time_ms,
            "constitutional_compliance": self.validation_result.is_compliant,
            "compliance_score": self.validation_result.compliance_score,
            "violations": self.validation_result.violations,
            "timestamp": self.timestamp.isoformat(),
            "constitutional_hash": self.constitutional_context.constitutional_hash,
        }


@dataclass
class A2AConfiguration:
    """Configuration for A2A Policy Integration service"""

    service_name: str = "A2A Policy Integration Service"
    service_version: str = "1.0.0"
    constitutional_hash: str = "cdd01ef066bc6cf2"
    security_policy: A2ASecurityPolicy = field(default_factory=A2ASecurityPolicy)
    enable_audit_logging: bool = True
    enable_metrics: bool = True
    enable_constitutional_validation: bool = True
    enable_encryption: bool = True
    enable_message_signing: bool = True
    max_concurrent_conversations: int = 1000
    message_queue_size: int = 10000
    heartbeat_interval_seconds: int = 30
    discovery_refresh_interval_seconds: int = 60
    default_message_ttl_seconds: int = 300
    max_message_size: int = 10 * 1024 * 1024  # 10MB
    compression_enabled: bool = True
    retry_policy: Dict[str, Any] = field(
        default_factory=lambda: {
            "max_retries": 3,
            "initial_delay_ms": 100,
            "backoff_multiplier": 2.0,
            "max_delay_ms": 5000,
        }
    )


@dataclass
class A2ACapabilities:
    """Capabilities of the A2A Policy Integration service"""

    supports_direct_messaging: bool = True
    supports_broadcast: bool = True
    supports_multicast: bool = True
    supports_publish_subscribe: bool = True
    supports_consensus_protocols: bool = True
    supports_encryption: bool = True
    supports_digital_signatures: bool = True
    supports_service_discovery: bool = True
    supports_load_balancing: bool = True
    supports_circuit_breaker: bool = True
    supports_rate_limiting: bool = True
    supports_message_queuing: bool = True
    supports_dead_letter_queue: bool = True
    supports_message_replay: bool = True
    supports_constitutional_validation: bool = True
    supports_audit_logging: bool = True
    max_concurrent_connections: int = 1000
    max_message_throughput: int = 10000  # messages per second
    supported_protocols: List[str] = field(
        default_factory=lambda: ["http", "https", "websocket", "grpc", "mqtt", "amqp"]
    )
    supported_serialization: List[str] = field(
        default_factory=lambda: ["json", "protobuf", "avro", "msgpack"]
    )
    constitutional_compliance: bool = True
    security_certification: str = "ACGS-2-Constitutional-Compliance"
