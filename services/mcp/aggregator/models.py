"""
Domain Models for MCP Aggregator Service
Constitutional Hash: cdd01ef066bc6cf2
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4


# MCP Protocol Enums
class MCPCapability(Enum):
    """MCP service capabilities"""
    TOOLS = "tools"
    RESOURCES = "resources"
    PROMPTS = "prompts"
    LOGGING = "logging"
    SAMPLING = "sampling"
    CONSTITUTIONAL_VALIDATION = "constitutional_validation"


class MCPMethod(Enum):
    """MCP protocol methods"""
    # Initialization
    INITIALIZE = "initialize"
    
    # Tool methods
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    
    # Resource methods
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    RESOURCES_WATCH = "resources/watch"
    
    # Prompt methods
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"
    
    # Sampling methods
    SAMPLING_CREATE_MESSAGE = "sampling/createMessage"
    
    # Constitutional methods
    CONSTITUTIONAL_VALIDATE = "constitutional/validate"
    CONSTITUTIONAL_AUDIT = "constitutional/audit"


class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    STARTING = "starting"
    STOPPING = "stopping"


class ComplianceLevel(Enum):
    """Constitutional compliance levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Core Domain Models

@dataclass
class ConstitutionalContext:
    """Constitutional context for MCP operations"""
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
class MCPTool:
    """MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    constitutional_requirements: List[str] = field(default_factory=list)
    requires_human_approval: bool = False
    execution_timeout: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPResource:
    """MCP resource definition"""
    uri: str
    name: str
    description: str
    mime_type: str
    constitutional_access_level: ComplianceLevel = ComplianceLevel.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPPrompt:
    """MCP prompt definition"""
    name: str
    description: str
    arguments: List[Dict[str, Any]] = field(default_factory=list)
    constitutional_context: Optional[ConstitutionalContext] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPService:
    """MCP service registration"""
    service_id: UUID = field(default_factory=uuid4)
    name: str = ""
    mcp_version: str = "2024-11-05"
    constitutional_hash: str = "cdd01ef066bc6cf2"
    capabilities: List[MCPCapability] = field(default_factory=list)
    endpoint: str = ""
    port: int = 3000
    status: ServiceStatus = ServiceStatus.STARTING
    health_check_url: str = ""
    tools: List[MCPTool] = field(default_factory=list)
    resources: List[MCPResource] = field(default_factory=list)
    prompts: List[MCPPrompt] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPSession:
    """MCP client session"""
    session_id: UUID = field(default_factory=uuid4)
    client_id: str = ""
    client_info: Dict[str, Any] = field(default_factory=dict)
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    active_tools: List[str] = field(default_factory=list)
    conversation_context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class MCPRequest:
    """MCP request message"""
    request_id: UUID = field(default_factory=uuid4)
    session_id: UUID = field(default_factory=uuid4)
    method: MCPMethod = MCPMethod.TOOLS_CALL
    parameters: Dict[str, Any] = field(default_factory=dict)
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    client_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "request_id": str(self.request_id),
            "session_id": str(self.session_id),
            "method": self.method.value,
            "parameters": self.parameters,
            "constitutional_context": {
                "constitutional_hash": self.constitutional_context.constitutional_hash,
                "purpose": self.constitutional_context.purpose,
                "compliance_level": self.constitutional_context.compliance_level.value
            },
            "timestamp": self.timestamp.isoformat(),
            "client_info": self.client_info,
            "metadata": self.metadata
        }


@dataclass
class MCPResponse:
    """MCP response message"""
    request_id: UUID = field(default_factory=uuid4)
    success: bool = True
    content: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    error_details: Dict[str, Any] = field(default_factory=dict)
    constitutional_validation: Optional[ConstitutionalValidation] = None
    execution_time_ms: float = 0.0
    service_info: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_error(cls, message: str, details: Dict[str, Any] = None) -> "MCPResponse":
        """Create error response"""
        return cls(
            success=False,
            error_message=message,
            error_details=details or {},
            constitutional_validation=ConstitutionalValidation(
                is_compliant=False,
                compliance_score=0.0,
                violations=[message],
                recommendations=[]
            )
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPResponse":
        """Create from dictionary"""
        return cls(
            request_id=UUID(data.get("request_id", str(uuid4()))),
            success=data.get("success", True),
            content=data.get("content", []),
            error_message=data.get("error_message"),
            error_details=data.get("error_details", {}),
            execution_time_ms=data.get("execution_time_ms", 0.0),
            service_info=data.get("service_info", {}),
            metadata=data.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "request_id": str(self.request_id),
            "success": self.success,
            "content": self.content,
            "execution_time_ms": self.execution_time_ms,
            "service_info": self.service_info,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
        
        if not self.success:
            result["error_message"] = self.error_message
            result["error_details"] = self.error_details
        
        if self.constitutional_validation:
            result["constitutional_validation"] = {
                "is_compliant": self.constitutional_validation.is_compliant,
                "compliance_score": self.constitutional_validation.compliance_score,
                "violations": self.constitutional_validation.violations,
                "recommendations": self.constitutional_validation.recommendations
            }
        
        return result


@dataclass
class ServiceHealth:
    """Service health status"""
    service_id: UUID = field(default_factory=uuid4)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    constitutional_compliance: bool = True
    health_details: Dict[str, Any] = field(default_factory=dict)
    consecutive_failures: int = 0


@dataclass
class ServiceRegistry:
    """Service registry state"""
    services: Dict[UUID, MCPService] = field(default_factory=dict)
    tool_mappings: Dict[str, UUID] = field(default_factory=dict)
    resource_mappings: Dict[str, UUID] = field(default_factory=dict)
    capability_index: Dict[MCPCapability, List[UUID]] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MCPAggregatorMetrics:
    """Metrics for MCP aggregator"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    constitutional_violations: int = 0
    active_sessions: int = 0
    registered_services: int = 0
    healthy_services: int = 0
    tool_calls: int = 0
    resource_reads: int = 0
    last_reset: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LoadBalancerState:
    """Load balancer state"""
    service_request_counts: Dict[UUID, int] = field(default_factory=dict)
    service_response_times: Dict[UUID, List[float]] = field(default_factory=dict)
    last_selection: Dict[str, UUID] = field(default_factory=dict)  # capability -> service_id
    selection_algorithm: str = "round_robin"


@dataclass
class HealthMonitor:
    """Health monitoring configuration"""
    check_interval_seconds: int = 30
    timeout_seconds: int = 5
    failure_threshold: int = 3
    recovery_threshold: int = 2
    enabled: bool = True


@dataclass
class SessionManager:
    """Session management configuration"""
    session_timeout_seconds: int = 3600
    max_sessions: int = 10000
    cleanup_interval_seconds: int = 300
    require_constitutional_context: bool = True


@dataclass
class LoadBalancer:
    """Load balancer configuration"""
    algorithm: str = "round_robin"  # round_robin, least_connections, response_time
    health_check_enabled: bool = True
    failover_enabled: bool = True
    circuit_breaker_enabled: bool = True


@dataclass
class ToolOrchestrator:
    """Tool orchestration state"""
    active_executions: Dict[UUID, Dict[str, Any]] = field(default_factory=dict)
    execution_queue: List[UUID] = field(default_factory=list)
    max_concurrent_executions: int = 100
    default_timeout_seconds: int = 30


@dataclass
class ResourceManager:
    """Resource management state"""
    cached_resources: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    access_controls: Dict[str, List[str]] = field(default_factory=dict)  # uri -> allowed_clients
    cache_ttl_seconds: int = 300
    max_cache_size: int = 1000


@dataclass
class MCPClientInfo:
    """MCP client information"""
    name: str
    version: str
    capabilities: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPServerInfo:
    """MCP server information"""
    name: str = "ACGS-2 MCP Aggregator"
    version: str = "1.0.0"
    constitutional_hash: str = "cdd01ef066bc6cf2"
    capabilities: Dict[str, Any] = field(default_factory=lambda: {
        "tools": True,
        "resources": True,
        "prompts": True,
        "constitutional_validation": True
    })


@dataclass
class ConstitutionalAuditEntry:
    """Audit entry for constitutional validation"""
    audit_id: UUID = field(default_factory=uuid4)
    request_id: UUID = field(default_factory=uuid4)
    session_id: UUID = field(default_factory=uuid4)
    method: MCPMethod = MCPMethod.TOOLS_CALL
    validation_result: ConstitutionalValidation = field(default_factory=ConstitutionalValidation)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    client_info: Dict[str, Any] = field(default_factory=dict)
    service_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPServiceConfiguration:
    """Configuration for MCP service integration"""
    service_discovery_enabled: bool = True
    health_monitoring_enabled: bool = True
    constitutional_validation_enabled: bool = True
    load_balancing_enabled: bool = True
    session_management_enabled: bool = True
    metrics_collection_enabled: bool = True
    audit_logging_enabled: bool = True