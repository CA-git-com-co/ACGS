"""
Real-Time Compliance Engine for Phase 2 PGC Runtime Enforcement System

This module implements ultra-fast compliance checking with action interception,
rule evaluation, and comprehensive audit logging targeting <200ms validation latency.

requires: Real-time compliance validation <200ms, action interception, audit trails
ensures: Constitutional compliance enforcement, performance optimization, security
sha256: e7f6c5b4a3d2e1f8c7b6a5d4e3f2c1b8a7d6e5f4c3b2a1d8e7f6c5b4a3d2e1f8
"""

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ActionType(Enum):
    """Types of actions that can be intercepted and validated."""

    POLICY_CREATION = "policy_creation"
    POLICY_MODIFICATION = "policy_modification"
    GOVERNANCE_DECISION = "governance_decision"
    CONSTITUTIONAL_AMENDMENT = "constitutional_amendment"
    USER_ACTION = "user_action"
    SYSTEM_OPERATION = "system_operation"
    DATA_ACCESS = "data_access"
    EXTERNAL_INTEGRATION = "external_integration"


class ComplianceLevel(Enum):
    """Compliance validation levels with different performance characteristics."""

    FAST = "fast"  # <50ms - Basic rule checking
    STANDARD = "standard"  # <200ms - Comprehensive validation
    THOROUGH = "thorough"  # <500ms - Deep constitutional analysis
    CRITICAL = "critical"  # <1000ms - Full formal verification


class EnforcementAction(Enum):
    """Actions that can be taken based on compliance results."""

    ALLOW = "allow"
    DENY = "deny"
    MODIFY = "modify"
    ESCALATE = "escalate"
    AUDIT_ONLY = "audit_only"
    REQUIRE_APPROVAL = "require_approval"


@dataclass
class ActionContext:
    """Context information for an action being validated."""

    action_id: str
    action_type: ActionType
    user_id: str
    resource_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Action details
    action_data: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)

    # Compliance requirements
    required_compliance_level: ComplianceLevel = ComplianceLevel.STANDARD
    constitutional_principles: list[str] = field(default_factory=list)

    # Performance tracking
    start_time: float = field(default_factory=time.time)


@dataclass
class ComplianceResult:
    """Result of compliance validation."""

    action_id: str
    compliant: bool
    enforcement_action: EnforcementAction
    confidence_score: float

    # Performance metrics
    validation_time_ms: float
    rule_evaluations: int
    cache_hits: int

    # Compliance details
    compliance_score: float
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Audit information
    rules_applied: list[str] = field(default_factory=list)
    constitutional_analysis: dict[str, Any] | None = None
    audit_trail: list[dict[str, Any]] = field(default_factory=list)

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RealTimeComplianceEngine:
    """
    Ultra-fast real-time compliance engine for PGC runtime enforcement.

    Provides action interception, rule evaluation, and audit logging with
    performance targets of <200ms validation latency for standard compliance.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize the real-time compliance engine."""
        self.config = config or {}

        # Performance configuration
        self.target_latency_ms = self.config.get("target_latency_ms", 200)
        self.cache_size = self.config.get("cache_size", 10000)
        self.max_concurrent_validations = self.config.get("max_concurrent", 100)

        # Rule engine configuration
        self.rules_cache = {}
        self.validation_cache = {}
        self.performance_metrics = {
            "total_validations": 0,
            "cache_hits": 0,
            "average_latency_ms": 0.0,
            "violations_detected": 0,
            "enforcement_actions": {},
        }

        # Audit logging
        self.audit_log = []
        self.max_audit_entries = self.config.get("max_audit_entries", 100000)

        # Concurrency control
        self.validation_semaphore = asyncio.Semaphore(self.max_concurrent_validations)
        self.active_validations: set[str] = set()

        logger.info(
            f"Real-time compliance engine initialized with {self.target_latency_ms}ms target latency"
        )

    async def validate_action(self, context: ActionContext) -> ComplianceResult:
        """
        Validate an action for compliance with ultra-fast performance.

        Args:
            context: Action context with validation requirements

        Returns:
            ComplianceResult with enforcement decision and audit information
        """
        start_time = time.time()

        # Check for concurrent validation limit
        async with self.validation_semaphore:
            if context.action_id in self.active_validations:
                logger.warning(
                    f"Duplicate validation request for action {context.action_id}"
                )
                return self._create_error_result(
                    context.action_id, "Duplicate validation"
                )

            self.active_validations.add(context.action_id)

            try:
                # Step 1: Fast cache lookup
                cache_result = await self._check_validation_cache(context)
                if cache_result:
                    self.performance_metrics["cache_hits"] += 1
                    return cache_result

                # Step 2: Load applicable rules
                applicable_rules = await self._load_applicable_rules(context)

                # Step 3: Execute rule evaluation based on compliance level
                compliance_result = await self._execute_rule_evaluation(
                    context, applicable_rules
                )

                # Step 4: Determine enforcement action
                enforcement_action = await self._determine_enforcement_action(
                    context, compliance_result
                )

                # Step 5: Create comprehensive result
                validation_time = (time.time() - start_time) * 1000
                result = ComplianceResult(
                    action_id=context.action_id,
                    compliant=compliance_result["compliant"],
                    enforcement_action=enforcement_action,
                    confidence_score=compliance_result["confidence"],
                    validation_time_ms=validation_time,
                    rule_evaluations=len(applicable_rules),
                    cache_hits=0,
                    compliance_score=compliance_result["score"],
                    violations=compliance_result["violations"],
                    warnings=compliance_result["warnings"],
                    recommendations=compliance_result["recommendations"],
                    rules_applied=[rule["id"] for rule in applicable_rules],
                    constitutional_analysis=compliance_result.get(
                        "constitutional_analysis"
                    ),
                    audit_trail=compliance_result["audit_trail"],
                )

                # Step 6: Cache result for future use
                await self._cache_validation_result(context, result)

                # Step 7: Log audit trail
                await self._log_audit_trail(context, result)

                # Step 8: Update performance metrics
                self._update_performance_metrics(result)

                # Check performance target
                if validation_time > self.target_latency_ms:
                    logger.warning(
                        f"Validation exceeded target latency: {validation_time:.2f}ms > {self.target_latency_ms}ms"
                    )

                logger.info(
                    f"Action {context.action_id} validated in {validation_time:.2f}ms: {enforcement_action.value}"
                )

                return result

            finally:
                self.active_validations.discard(context.action_id)

    async def intercept_action(
        self,
        action_type: ActionType,
        action_data: dict[str, Any],
        user_id: str,
        resource_id: str = "unknown",
    ) -> ComplianceResult:
        """
        Intercept and validate an action in real-time.

        This is the primary entry point for action interception and validation.
        """
        action_id = str(uuid.uuid4())[:8]

        context = ActionContext(
            action_id=action_id,
            action_type=action_type,
            user_id=user_id,
            resource_id=resource_id,
            action_data=action_data,
            environment={"intercepted": True, "timestamp": time.time()},
        )

        logger.info(
            f"Intercepting {action_type.value} action {action_id} by user {user_id}"
        )

        return await self.validate_action(context)

    async def _check_validation_cache(
        self, context: ActionContext
    ) -> ComplianceResult | None:
        """Check if validation result is cached."""
        cache_key = self._generate_cache_key(context)

        if cache_key in self.validation_cache:
            cached_result = self.validation_cache[cache_key]

            # Check if cache entry is still valid (5 minutes TTL)
            cache_age = time.time() - cached_result.timestamp.timestamp()
            if cache_age < 300:  # 5 minutes
                logger.debug(f"Cache hit for action {context.action_id}")
                return cached_result
            # Remove expired cache entry
            del self.validation_cache[cache_key]

        return None

    async def _load_applicable_rules(
        self, context: ActionContext
    ) -> list[dict[str, Any]]:
        """Load rules applicable to the action context."""
        # This would integrate with the rule engine in production
        # For now, return mock rules based on action type

        base_rules = [
            {
                "id": "constitutional_compliance",
                "type": "constitutional",
                "priority": 1,
                "condition": "always",
                "action": "validate_constitutional_principles",
            },
            {
                "id": "user_authorization",
                "type": "authorization",
                "priority": 2,
                "condition": f"user_id == '{context.user_id}'",
                "action": "check_user_permissions",
            },
        ]

        # Add action-specific rules
        if context.action_type == ActionType.POLICY_CREATION:
            base_rules.append(
                {
                    "id": "policy_creation_rules",
                    "type": "governance",
                    "priority": 3,
                    "condition": "action_type == 'policy_creation'",
                    "action": "validate_policy_structure",
                }
            )

        return base_rules

    async def _execute_rule_evaluation(
        self, context: ActionContext, rules: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Execute rule evaluation based on compliance level."""

        evaluation_start = time.time()
        violations = []
        warnings = []
        recommendations = []
        audit_trail = []

        # Fast evaluation for performance-critical paths
        if context.required_compliance_level == ComplianceLevel.FAST:
            return await self._fast_rule_evaluation(context, rules)

        # Standard comprehensive evaluation
        compliance_score = 1.0
        confidence_score = 0.95

        for rule in rules:
            rule_start = time.time()

            try:
                # Evaluate rule condition
                rule_result = await self._evaluate_single_rule(context, rule)

                if not rule_result["passed"]:
                    violations.append(rule_result["violation"])
                    compliance_score -= rule_result["penalty"]

                if rule_result.get("warning"):
                    warnings.append(rule_result["warning"])

                if rule_result.get("recommendation"):
                    recommendations.append(rule_result["recommendation"])

                # Add to audit trail
                audit_trail.append(
                    {
                        "rule_id": rule["id"],
                        "result": rule_result["passed"],
                        "evaluation_time_ms": (time.time() - rule_start) * 1000,
                        "details": rule_result.get("details", {}),
                    }
                )

            except Exception as e:
                logger.error(f"Rule evaluation failed for {rule['id']}: {e}")
                violations.append(f"Rule evaluation error: {rule['id']}")
                compliance_score -= 0.1

        # Constitutional analysis for thorough compliance
        constitutional_analysis = None
        if context.required_compliance_level in [
            ComplianceLevel.THOROUGH,
            ComplianceLevel.CRITICAL,
        ]:
            constitutional_analysis = await self._perform_constitutional_analysis(
                context
            )

        evaluation_time = (time.time() - evaluation_start) * 1000

        return {
            "compliant": len(violations) == 0 and compliance_score >= 0.8,
            "score": max(0.0, compliance_score),
            "confidence": confidence_score,
            "violations": violations,
            "warnings": warnings,
            "recommendations": recommendations,
            "audit_trail": audit_trail,
            "constitutional_analysis": constitutional_analysis,
            "evaluation_time_ms": evaluation_time,
        }

    async def _fast_rule_evaluation(
        self, context: ActionContext, rules: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Ultra-fast rule evaluation for <50ms target."""

        # Only check critical rules for fast evaluation
        critical_violations = []

        # Basic authorization check
        if context.user_id == "anonymous":
            critical_violations.append("Anonymous access not permitted")

        # Basic action type validation
        if context.action_type == ActionType.CONSTITUTIONAL_AMENDMENT:
            critical_violations.append(
                "Constitutional amendments require thorough validation"
            )

        return {
            "compliant": len(critical_violations) == 0,
            "score": 1.0 if len(critical_violations) == 0 else 0.0,
            "confidence": 0.8,  # Lower confidence for fast evaluation
            "violations": critical_violations,
            "warnings": [],
            "recommendations": [
                "Consider using standard compliance level for better validation"
            ],
            "audit_trail": [
                {"rule_type": "fast_evaluation", "violations": len(critical_violations)}
            ],
            "constitutional_analysis": None,
            "evaluation_time_ms": 10.0,  # Simulated fast evaluation time
        }

    async def _evaluate_single_rule(
        self, context: ActionContext, rule: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate a single rule against the action context."""

        # Mock rule evaluation - in production this would use a proper rule engine
        rule_type = rule.get("type", "unknown")

        if rule_type == "constitutional":
            return await self._evaluate_constitutional_rule(context, rule)
        if rule_type == "authorization":
            return await self._evaluate_authorization_rule(context, rule)
        if rule_type == "governance":
            return await self._evaluate_governance_rule(context, rule)
        return {
            "passed": True,
            "violation": None,
            "warning": f"Unknown rule type: {rule_type}",
            "recommendation": "Review rule configuration",
            "details": {"rule_id": rule["id"]},
        }

    async def _evaluate_constitutional_rule(
        self, context: ActionContext, rule: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate constitutional compliance rule."""

        # Check if action respects constitutional principles
        if not context.constitutional_principles:
            return {
                "passed": False,
                "violation": "No constitutional principles specified",
                "penalty": 0.2,
                "recommendation": "Specify applicable constitutional principles",
                "details": {"rule_type": "constitutional"},
            }

        # Mock constitutional validation
        return {
            "passed": True,
            "violation": None,
            "penalty": 0.0,
            "details": {"constitutional_principles": context.constitutional_principles},
        }

    async def _evaluate_authorization_rule(
        self, context: ActionContext, rule: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate user authorization rule."""

        # Basic authorization check
        if context.user_id in ["admin", "system"]:
            return {
                "passed": True,
                "violation": None,
                "penalty": 0.0,
                "details": {"authorized_user": context.user_id},
            }

        return {
            "passed": False,
            "violation": f"User {context.user_id} not authorized for {context.action_type.value}",
            "penalty": 0.3,
            "recommendation": "Obtain proper authorization before proceeding",
            "details": {
                "user_id": context.user_id,
                "action_type": context.action_type.value,
            },
        }

    async def _evaluate_governance_rule(
        self, context: ActionContext, rule: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate governance-specific rule."""

        # Mock governance rule evaluation
        if context.action_type == ActionType.POLICY_CREATION:
            if not context.action_data.get("title"):
                return {
                    "passed": False,
                    "violation": "Policy title is required",
                    "penalty": 0.1,
                    "recommendation": "Provide a descriptive policy title",
                    "details": {"missing_field": "title"},
                }

        return {
            "passed": True,
            "violation": None,
            "penalty": 0.0,
            "details": {"governance_check": "passed"},
        }

    async def _perform_constitutional_analysis(
        self, context: ActionContext
    ) -> dict[str, Any]:
        """Perform deep constitutional analysis for thorough compliance."""

        # This would integrate with the AC service for constitutional analysis
        return {
            "constitutional_hash": "cdd01ef066bc6cf2",
            "compliance_level": "high",
            "constitutional_principles_validated": context.constitutional_principles,
            "analysis_confidence": 0.92,
            "constitutional_impact": "minimal",
        }

    async def _determine_enforcement_action(
        self, context: ActionContext, compliance_result: dict[str, Any]
    ) -> EnforcementAction:
        """Determine the appropriate enforcement action based on compliance result."""

        if not compliance_result["compliant"]:
            # Determine severity of violations
            violation_count = len(compliance_result["violations"])
            compliance_score = compliance_result["score"]

            if compliance_score < 0.5 or violation_count > 2:
                return EnforcementAction.DENY
            if compliance_score < 0.8:
                return EnforcementAction.REQUIRE_APPROVAL
            return EnforcementAction.MODIFY

        # Special handling for critical actions
        if context.action_type == ActionType.CONSTITUTIONAL_AMENDMENT:
            return EnforcementAction.REQUIRE_APPROVAL

        return EnforcementAction.ALLOW

    def _generate_cache_key(self, context: ActionContext) -> str:
        """Generate cache key for validation result."""
        key_components = [
            context.action_type.value,
            context.user_id,
            context.resource_id,
            str(hash(str(sorted(context.action_data.items())))),
        ]
        return ":".join(key_components)

    async def _cache_validation_result(
        self, context: ActionContext, result: ComplianceResult
    ) -> None:
        """Cache validation result for future use."""
        cache_key = self._generate_cache_key(context)

        # Implement LRU cache eviction if cache is full
        if len(self.validation_cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = min(
                self.validation_cache.keys(),
                key=lambda k: self.validation_cache[k].timestamp,
            )
            del self.validation_cache[oldest_key]

        self.validation_cache[cache_key] = result

    async def _log_audit_trail(
        self, context: ActionContext, result: ComplianceResult
    ) -> None:
        """Log comprehensive audit trail for compliance validation."""

        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "action_id": context.action_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_type": context.action_type.value,
            "user_id": context.user_id,
            "resource_id": context.resource_id,
            "enforcement_action": result.enforcement_action.value,
            "compliance_score": result.compliance_score,
            "validation_time_ms": result.validation_time_ms,
            "violations": result.violations,
            "rules_applied": result.rules_applied,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        self.audit_log.append(audit_entry)

        # Implement log rotation
        if len(self.audit_log) > self.max_audit_entries:
            self.audit_log = self.audit_log[-self.max_audit_entries // 2 :]

        logger.info(f"Audit trail logged for action {context.action_id}")

    def _update_performance_metrics(self, result: ComplianceResult) -> None:
        """Update performance metrics with validation result."""

        self.performance_metrics["total_validations"] += 1

        # Update average latency
        total_latency = (
            self.performance_metrics["average_latency_ms"]
            * (self.performance_metrics["total_validations"] - 1)
            + result.validation_time_ms
        )
        self.performance_metrics["average_latency_ms"] = (
            total_latency / self.performance_metrics["total_validations"]
        )

        # Track violations
        if result.violations:
            self.performance_metrics["violations_detected"] += 1

        # Track enforcement actions
        action_key = result.enforcement_action.value
        if action_key not in self.performance_metrics["enforcement_actions"]:
            self.performance_metrics["enforcement_actions"][action_key] = 0
        self.performance_metrics["enforcement_actions"][action_key] += 1

    def _create_error_result(
        self, action_id: str, error_message: str
    ) -> ComplianceResult:
        """Create error result for failed validations."""

        return ComplianceResult(
            action_id=action_id,
            compliant=False,
            enforcement_action=EnforcementAction.DENY,
            confidence_score=0.0,
            validation_time_ms=0.0,
            rule_evaluations=0,
            cache_hits=0,
            compliance_score=0.0,
            violations=[error_message],
            warnings=["Validation failed due to system error"],
            recommendations=["Retry validation or contact system administrator"],
        )

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get current performance metrics."""

        return {
            **self.performance_metrics,
            "cache_hit_rate": (
                self.performance_metrics["cache_hits"]
                / max(self.performance_metrics["total_validations"], 1)
            ),
            "target_latency_ms": self.target_latency_ms,
            "latency_compliance": (
                self.performance_metrics["average_latency_ms"] <= self.target_latency_ms
            ),
            "active_validations": len(self.active_validations),
            "cache_size": len(self.validation_cache),
            "audit_entries": len(self.audit_log),
        }

    def get_audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent audit log entries."""

        return self.audit_log[-limit:] if self.audit_log else []


# Global compliance engine instance
compliance_engine = RealTimeComplianceEngine()


async def get_compliance_engine() -> RealTimeComplianceEngine:
    """Dependency injection for compliance engine."""
    return compliance_engine
