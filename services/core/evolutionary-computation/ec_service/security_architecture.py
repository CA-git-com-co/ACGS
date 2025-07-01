"""
4-Layer Security Architecture for ACGS Evolutionary Computation Service
Implements comprehensive security layers: Sandboxing, Policy Engine, Authentication, and Audit.
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import jwt
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class SecurityLevel(Enum):
    """Security levels for operations."""

    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CLASSIFIED = "classified"


class AuthenticationMethod(Enum):
    """Authentication methods."""

    JWT_TOKEN = "jwt_token"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    MULTI_FACTOR = "multi_factor"


class AuditEventType(Enum):
    """Types of audit events."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    POLICY_EVALUATION = "policy_evaluation"
    SANDBOX_EXECUTION = "sandbox_execution"
    CONSTITUTIONAL_VALIDATION = "constitutional_validation"
    SECURITY_VIOLATION = "security_violation"


@dataclass
class SecurityContext:
    """Security context for operations."""

    user_id: str
    session_id: str
    authentication_method: AuthenticationMethod
    security_level: SecurityLevel
    permissions: Set[str] = field(default_factory=set)

    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH
    compliance_verified: bool = False

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    source_ip: Optional[str] = None


@dataclass
class AuditEvent:
    """Audit event record."""

    event_id: str
    event_type: AuditEventType
    user_id: str
    session_id: str

    # Event details
    action: str
    resource: str
    result: str  # success, failure, denied

    # Security context
    security_level: SecurityLevel
    constitutional_hash: str = CONSTITUTIONAL_HASH

    # Additional data
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class Layer1_Sandboxing:
    """Layer 1: Sandboxing and Isolation."""

    def __init__(self):
        self.setup_metrics()
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}

        # Sandbox configuration
        self.max_execution_time = 300  # 5 minutes
        self.max_memory_mb = 512
        self.max_cpu_percent = 50

        logger.info("Layer 1 Sandboxing initialized")

    def setup_metrics(self):
        """Setup metrics for sandboxing layer."""
        self.sandbox_executions_total = Counter(
            "ec_sandbox_executions_total", "Total sandbox executions", ["result"]
        )

        self.sandbox_execution_time = Histogram(
            "ec_sandbox_execution_time_seconds", "Sandbox execution time"
        )

        self.active_sandboxes_gauge = Gauge(
            "ec_active_sandboxes", "Number of active sandboxes"
        )

    async def create_sandbox(self, sandbox_id: str, config: Dict[str, Any]) -> bool:
        """Create a new sandbox environment."""
        try:
            # Validate sandbox configuration
            if not self.validate_sandbox_config(config):
                return False

            # Create sandbox
            sandbox = {
                "sandbox_id": sandbox_id,
                "config": config,
                "created_at": datetime.now(timezone.utc),
                "status": "created",
                "resource_usage": {
                    "cpu_percent": 0.0,
                    "memory_mb": 0.0,
                    "execution_time": 0.0,
                },
            }

            self.active_sandboxes[sandbox_id] = sandbox
            self.active_sandboxes_gauge.set(len(self.active_sandboxes))

            logger.info(f"Sandbox {sandbox_id} created")
            return True

        except Exception as e:
            logger.error(f"Failed to create sandbox {sandbox_id}: {e}")
            return False

    def validate_sandbox_config(self, config: Dict[str, Any]) -> bool:
        """Validate sandbox configuration."""
        required_fields = ["execution_context", "resource_limits"]

        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required sandbox config field: {field}")
                return False

        # Validate resource limits
        limits = config["resource_limits"]
        if limits.get("memory_mb", 0) > self.max_memory_mb:
            logger.error(f"Memory limit exceeds maximum: {limits.get('memory_mb')}")
            return False

        if limits.get("cpu_percent", 0) > self.max_cpu_percent:
            logger.error(f"CPU limit exceeds maximum: {limits.get('cpu_percent')}")
            return False

        return True

    async def execute_in_sandbox(
        self, sandbox_id: str, operation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute operation in sandbox."""
        start_time = time.time()

        try:
            if sandbox_id not in self.active_sandboxes:
                raise ValueError(f"Sandbox {sandbox_id} not found")

            sandbox = self.active_sandboxes[sandbox_id]
            sandbox["status"] = "executing"

            # Simulate sandbox execution (in real implementation, this would use containers)
            result = await self.simulate_sandbox_execution(operation)

            # Update resource usage
            execution_time = time.time() - start_time
            sandbox["resource_usage"]["execution_time"] = execution_time

            # Record metrics
            self.sandbox_executions_total.labels(result="success").inc()
            self.sandbox_execution_time.observe(execution_time)

            sandbox["status"] = "completed"

            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "resource_usage": sandbox["resource_usage"],
            }

        except Exception as e:
            execution_time = time.time() - start_time
            self.sandbox_executions_total.labels(result="failure").inc()
            self.sandbox_execution_time.observe(execution_time)

            logger.error(f"Sandbox execution failed for {sandbox_id}: {e}")
            return {"success": False, "error": str(e), "execution_time": execution_time}

    async def simulate_sandbox_execution(
        self, operation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate sandbox execution (placeholder for real implementation)."""
        # In real implementation, this would execute in isolated container
        await asyncio.sleep(0.1)  # Simulate execution time

        return {
            "operation_type": operation.get("type", "unknown"),
            "status": "completed",
            "output": "Sandbox execution completed successfully",
        }

    def destroy_sandbox(self, sandbox_id: str) -> bool:
        """Destroy a sandbox environment."""
        if sandbox_id in self.active_sandboxes:
            del self.active_sandboxes[sandbox_id]
            self.active_sandboxes_gauge.set(len(self.active_sandboxes))
            logger.info(f"Sandbox {sandbox_id} destroyed")
            return True

        return False


class Layer2_PolicyEngine:
    """Layer 2: Policy Engine and OPA Integration."""

    def __init__(self):
        self.setup_metrics()
        self.policies: Dict[str, Dict[str, Any]] = {}
        self.policy_cache: Dict[str, Any] = {}

        # Load default policies
        self.load_default_policies()

        logger.info("Layer 2 Policy Engine initialized")

    def setup_metrics(self):
        """Setup metrics for policy engine."""
        self.policy_evaluations_total = Counter(
            "ec_policy_evaluations_total",
            "Total policy evaluations",
            ["policy_type", "result"],
        )

        self.policy_evaluation_time = Histogram(
            "ec_policy_evaluation_time_seconds", "Policy evaluation time"
        )

    def load_default_policies(self):
        """Load default security policies."""
        default_policies = {
            "evolution_approval": {
                "name": "Evolution Approval Policy",
                "rules": {
                    "constitutional_compliance_required": True,
                    "minimum_compliance_score": 0.95,
                    "human_review_required_for_high_risk": True,
                    "auto_approval_threshold": 0.95,
                },
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
            "resource_access": {
                "name": "Resource Access Policy",
                "rules": {
                    "max_concurrent_operations": 10,
                    "max_execution_time_seconds": 300,
                    "allowed_operations": ["read", "evaluate", "validate"],
                    "restricted_operations": ["deploy", "modify", "delete"],
                },
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
            "constitutional_validation": {
                "name": "Constitutional Validation Policy",
                "rules": {
                    "hash_validation_required": True,
                    "expected_hash": CONSTITUTIONAL_HASH,
                    "validation_timeout_seconds": 30,
                },
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        }

        self.policies.update(default_policies)

    async def evaluate_policy(
        self, policy_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a policy against given context."""
        start_time = time.time()

        try:
            if policy_name not in self.policies:
                raise ValueError(f"Policy {policy_name} not found")

            policy = self.policies[policy_name]

            # Validate constitutional hash
            if policy.get("constitutional_hash") != CONSTITUTIONAL_HASH:
                raise ValueError(
                    f"Constitutional hash mismatch for policy {policy_name}"
                )

            # Evaluate policy rules
            result = await self.evaluate_policy_rules(policy["rules"], context)

            # Record metrics
            evaluation_time = time.time() - start_time
            self.policy_evaluations_total.labels(
                policy_type=policy_name,
                result="allowed" if result["allowed"] else "denied",
            ).inc()
            self.policy_evaluation_time.observe(evaluation_time)

            return {
                "policy_name": policy_name,
                "allowed": result["allowed"],
                "reason": result["reason"],
                "evaluation_time": evaluation_time,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

        except Exception as e:
            evaluation_time = time.time() - start_time
            self.policy_evaluations_total.labels(
                policy_type=policy_name, result="error"
            ).inc()

            logger.error(f"Policy evaluation failed for {policy_name}: {e}")
            return {
                "policy_name": policy_name,
                "allowed": False,
                "reason": f"Policy evaluation error: {str(e)}",
                "evaluation_time": evaluation_time,
            }

    async def evaluate_policy_rules(
        self, rules: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate policy rules against context."""
        # Constitutional compliance check
        if rules.get("constitutional_compliance_required", False):
            compliance_score = context.get("constitutional_compliance_score", 0.0)
            min_score = rules.get("minimum_compliance_score", 0.95)

            if compliance_score < min_score:
                return {
                    "allowed": False,
                    "reason": f"Constitutional compliance score {compliance_score:.2%} below minimum {min_score:.2%}",
                }

        # Resource limits check
        if "max_concurrent_operations" in rules:
            current_ops = context.get("concurrent_operations", 0)
            max_ops = rules["max_concurrent_operations"]

            if current_ops >= max_ops:
                return {
                    "allowed": False,
                    "reason": f"Maximum concurrent operations ({max_ops}) exceeded",
                }

        # Operation type check
        if "allowed_operations" in rules:
            operation = context.get("operation_type", "")
            allowed_ops = rules["allowed_operations"]

            if operation not in allowed_ops:
                return {
                    "allowed": False,
                    "reason": f"Operation '{operation}' not in allowed operations: {allowed_ops}",
                }

        # All checks passed
        return {"allowed": True, "reason": "All policy rules satisfied"}


class Layer3_Authentication:
    """Layer 3: Authentication and Authorization."""

    def __init__(self):
        self.setup_metrics()
        self.active_sessions: Dict[str, SecurityContext] = {}
        self.jwt_secret = (
            "acgs_ec_service_secret_key"  # In production, use secure key management
        )

        logger.info("Layer 3 Authentication initialized")

    def setup_metrics(self):
        """Setup metrics for authentication layer."""
        self.authentication_attempts_total = Counter(
            "ec_authentication_attempts_total",
            "Total authentication attempts",
            ["method", "result"],
        )

        self.active_sessions_gauge = Gauge(
            "ec_active_sessions", "Number of active sessions"
        )

    async def authenticate_user(
        self, credentials: Dict[str, Any]
    ) -> Optional[SecurityContext]:
        """Authenticate user and create security context."""
        try:
            auth_method = AuthenticationMethod(credentials.get("method", "jwt_token"))

            if auth_method == AuthenticationMethod.JWT_TOKEN:
                return await self.authenticate_jwt(credentials)
            elif auth_method == AuthenticationMethod.API_KEY:
                return await self.authenticate_api_key(credentials)
            else:
                logger.error(f"Unsupported authentication method: {auth_method}")
                return None

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self.authentication_attempts_total.labels(
                method=credentials.get("method", "unknown"), result="failure"
            ).inc()
            return None

    async def authenticate_jwt(
        self, credentials: Dict[str, Any]
    ) -> Optional[SecurityContext]:
        """Authenticate using JWT token."""
        try:
            token = credentials.get("token")
            if not token:
                return None

            # Decode JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])

            # Create security context
            session_id = str(uuid.uuid4())
            context = SecurityContext(
                user_id=payload["user_id"],
                session_id=session_id,
                authentication_method=AuthenticationMethod.JWT_TOKEN,
                security_level=SecurityLevel(payload.get("security_level", "internal")),
                permissions=set(payload.get("permissions", [])),
                source_ip=credentials.get("source_ip"),
            )

            # Store session
            self.active_sessions[session_id] = context
            self.active_sessions_gauge.set(len(self.active_sessions))

            self.authentication_attempts_total.labels(
                method="jwt_token", result="success"
            ).inc()

            logger.info(f"JWT authentication successful for user {context.user_id}")
            return context

        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            self.authentication_attempts_total.labels(
                method="jwt_token", result="failure"
            ).inc()
            return None

    async def authenticate_api_key(
        self, credentials: Dict[str, Any]
    ) -> Optional[SecurityContext]:
        """Authenticate using API key."""
        # Simplified API key authentication
        api_key = credentials.get("api_key")

        # In production, validate against secure key store
        if api_key == "acgs_ec_service_api_key":
            session_id = str(uuid.uuid4())
            context = SecurityContext(
                user_id="api_user",
                session_id=session_id,
                authentication_method=AuthenticationMethod.API_KEY,
                security_level=SecurityLevel.INTERNAL,
                permissions={"read", "evaluate"},
                source_ip=credentials.get("source_ip"),
            )

            self.active_sessions[session_id] = context
            self.active_sessions_gauge.set(len(self.active_sessions))

            self.authentication_attempts_total.labels(
                method="api_key", result="success"
            ).inc()

            return context

        self.authentication_attempts_total.labels(
            method="api_key", result="failure"
        ).inc()

        return None

    def authorize_operation(
        self, context: SecurityContext, operation: str, resource: str
    ) -> bool:
        """Authorize operation for given security context."""
        # Check if session is still valid
        if context.session_id not in self.active_sessions:
            return False

        # Check permissions
        required_permission = f"{operation}:{resource}"
        if required_permission in context.permissions:
            return True

        # Check wildcard permissions
        wildcard_permission = f"{operation}:*"
        if wildcard_permission in context.permissions:
            return True

        return False


class Layer4_AuditLayer:
    """Layer 4: Comprehensive Audit and Logging."""

    def __init__(self):
        self.setup_metrics()
        self.audit_events: List[AuditEvent] = []
        self.max_events = 10000  # Keep last 10k events in memory

        logger.info("Layer 4 Audit Layer initialized")

    def setup_metrics(self):
        """Setup metrics for audit layer."""
        self.audit_events_total = Counter(
            "ec_audit_events_total", "Total audit events", ["event_type", "result"]
        )

    async def log_audit_event(self, event: AuditEvent):
        """Log an audit event."""
        try:
            # Add to in-memory storage
            self.audit_events.append(event)

            # Trim if necessary
            if len(self.audit_events) > self.max_events:
                self.audit_events = self.audit_events[-self.max_events :]

            # Record metrics
            self.audit_events_total.labels(
                event_type=event.event_type.value, result=event.result
            ).inc()

            # In production, also log to persistent storage
            logger.info(f"Audit event logged: {event.event_id}")

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

    def create_audit_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        session_id: str,
        action: str,
        resource: str,
        result: str,
        **kwargs,
    ) -> AuditEvent:
        """Create an audit event."""
        return AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            action=action,
            resource=resource,
            result=result,
            security_level=kwargs.get("security_level", SecurityLevel.INTERNAL),
            details=kwargs.get("details", {}),
        )


class FourLayerSecurityArchitecture:
    """Complete 4-layer security architecture."""

    def __init__(self):
        self.layer1_sandboxing = Layer1_Sandboxing()
        self.layer2_policy = Layer2_PolicyEngine()
        self.layer3_auth = Layer3_Authentication()
        self.layer4_audit = Layer4_AuditLayer()

        logger.info("4-Layer Security Architecture initialized")

    async def secure_execute(
        self, operation: Dict[str, Any], credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute operation through all security layers."""
        # Layer 3: Authentication
        context = await self.layer3_auth.authenticate_user(credentials)
        if not context:
            await self.layer4_audit.log_audit_event(
                self.layer4_audit.create_audit_event(
                    AuditEventType.AUTHENTICATION,
                    "unknown",
                    "unknown",
                    "authenticate",
                    "ec_service",
                    "failure",
                )
            )
            return {"success": False, "error": "Authentication failed"}

        # Layer 3: Authorization
        if not self.layer3_auth.authorize_operation(
            context, operation.get("type", "unknown"), "ec_service"
        ):
            await self.layer4_audit.log_audit_event(
                self.layer4_audit.create_audit_event(
                    AuditEventType.AUTHORIZATION,
                    context.user_id,
                    context.session_id,
                    operation.get("type", "unknown"),
                    "ec_service",
                    "denied",
                )
            )
            return {"success": False, "error": "Authorization denied"}

        # Layer 2: Policy evaluation
        policy_result = await self.layer2_policy.evaluate_policy(
            "evolution_approval",
            {
                "operation_type": operation.get("type"),
                "constitutional_compliance_score": operation.get(
                    "constitutional_compliance_score", 1.0
                ),
                "concurrent_operations": len(self.layer1_sandboxing.active_sandboxes),
            },
        )

        if not policy_result["allowed"]:
            await self.layer4_audit.log_audit_event(
                self.layer4_audit.create_audit_event(
                    AuditEventType.POLICY_EVALUATION,
                    context.user_id,
                    context.session_id,
                    operation.get("type", "unknown"),
                    "ec_service",
                    "denied",
                    details={"reason": policy_result["reason"]},
                )
            )
            return {
                "success": False,
                "error": f"Policy violation: {policy_result['reason']}",
            }

        # Layer 1: Sandbox execution
        sandbox_id = str(uuid.uuid4())
        sandbox_config = {
            "execution_context": operation.get("context", {}),
            "resource_limits": {
                "memory_mb": 256,
                "cpu_percent": 25,
                "execution_time_seconds": 60,
            },
        }

        if not await self.layer1_sandboxing.create_sandbox(sandbox_id, sandbox_config):
            return {"success": False, "error": "Failed to create sandbox"}

        try:
            result = await self.layer1_sandboxing.execute_in_sandbox(
                sandbox_id, operation
            )

            # Layer 4: Audit successful execution
            await self.layer4_audit.log_audit_event(
                self.layer4_audit.create_audit_event(
                    AuditEventType.SANDBOX_EXECUTION,
                    context.user_id,
                    context.session_id,
                    operation.get("type", "unknown"),
                    "ec_service",
                    "success" if result["success"] else "failure",
                    details=result,
                )
            )

            return result

        finally:
            # Clean up sandbox
            self.layer1_sandboxing.destroy_sandbox(sandbox_id)


# Global security architecture instance
security_architecture = FourLayerSecurityArchitecture()
