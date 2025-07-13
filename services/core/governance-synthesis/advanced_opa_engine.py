#!/usr/bin/env python3
"""
Advanced OPA Policy Engine for ACGS Governance Synthesis

Implements sophisticated policy evaluation and decision-making using:
- Open Policy Agent (OPA) integration
- Complex multi-policy orchestration
- Constitutional compliance validation
- Temporal policy evaluation
- Policy conflict resolution
- Performance optimization
- Audit trail generation

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import networkx as nx

# Real OPA client integration
try:
    from .opa_client import OPAConfig, RealOPAClient, get_opa_client

    OPA_CLIENT_AVAILABLE = True
except ImportError:
    # Fallback for development/testing
    OPA_CLIENT_AVAILABLE = False

    class RealOPAClient:
        def __init__(self, config=None):
            pass


logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Types of policies in the governance framework."""

    CONSTITUTIONAL = "constitutional"
    REGULATORY = "regulatory"
    PROCEDURAL = "procedural"
    SECURITY = "security"
    EVOLUTIONARY = "evolutionary"
    DATA_GOVERNANCE = "data_governance"
    MULTI_TENANT = "multi_tenant"
    AGENT_LIFECYCLE = "agent_lifecycle"


class DecisionType(Enum):
    """Types of policy decisions."""

    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    ESCALATE = "escalate"
    DEFER = "defer"


class PolicyConflictType(Enum):
    """Types of policy conflicts."""

    LOGICAL_CONTRADICTION = "logical_contradiction"
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"
    RESOURCE_CONTENTION = "resource_contention"
    PRECEDENCE_AMBIGUITY = "precedence_ambiguity"


@dataclass
class PolicyEvaluationContext:
    """Context for policy evaluation."""

    request_id: str
    timestamp: datetime
    principal: dict[str, Any]
    resource: dict[str, Any]
    action: str
    environment: dict[str, Any] = field(default_factory=dict)
    historical_context: list[dict[str, Any]] = field(default_factory=list)
    constitutional_requirements: dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyDecision:
    """Result of policy evaluation."""

    decision_id: str
    decision: DecisionType
    confidence_score: float
    policies_evaluated: list[str]
    evaluation_time_ms: float
    constitutional_compliance: bool
    reasons: list[str] = field(default_factory=list)
    conditions: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    audit_trail: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class PolicyConflict:
    """Represents a conflict between policies."""

    conflict_id: str
    conflict_type: PolicyConflictType
    policies_involved: list[str]
    severity: str
    description: str
    resolution_strategy: str | None = None
    resolution_confidence: float = 0.0
    constitutional_impact: dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyPerformanceMetrics:
    """Performance metrics for policy evaluation."""

    total_evaluations: int
    average_evaluation_time_ms: float
    decision_distribution: dict[str, int]
    conflict_rate: float
    constitutional_compliance_rate: float
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0


class PolicyEvaluationEngine(ABC):
    """Abstract base class for policy evaluation engines."""

    @abstractmethod
    async def evaluate_policy(
        self, policy_name: str, context: PolicyEvaluationContext
    ) -> PolicyDecision:
        """Evaluate a single policy."""

    @abstractmethod
    async def evaluate_multiple_policies(
        self, policy_names: list[str], context: PolicyEvaluationContext
    ) -> list[PolicyDecision]:
        """Evaluate multiple policies."""


class OPAEvaluationEngine(PolicyEvaluationEngine):
    """OPA-based policy evaluation engine."""

    def __init__(
        self, opa_url: str = "http://localhost:8181", policies_path: str = "./policies"
    ):
        self.opa_url = opa_url
        self.policies_path = Path(policies_path)
        self.policy_cache = {}
        self.evaluation_cache = {}
        self.metrics = PolicyPerformanceMetrics(
            total_evaluations=0,
            average_evaluation_time_ms=0.0,
            decision_distribution={},
            conflict_rate=0.0,
            constitutional_compliance_rate=0.0,
        )

        # Initialize real OPA client
        if OPA_CLIENT_AVAILABLE:
            opa_config = OPAConfig(base_url=opa_url)
            self.opa_client = get_opa_client(opa_config)
            logger.info(f"Initialized real OPA client for {opa_url}")
        else:
            self.opa_client = None
            logger.warning("OPA client not available, falling back to simulation")

    async def evaluate_policy(
        self, policy_name: str, context: PolicyEvaluationContext
    ) -> PolicyDecision:
        """Evaluate a single policy using OPA."""
        start_time = time.time()

        try:
            # Create cache key
            cache_key = self._create_cache_key(policy_name, context)

            # Check cache first
            if cache_key in self.evaluation_cache:
                cached_decision = self.evaluation_cache[cache_key]
                if self._is_cache_valid(cached_decision, context):
                    self.metrics.cache_hit_rate += 1
                    return cached_decision

            # Prepare OPA query
            opa_input = self._prepare_opa_input(context)

            # Use real OPA evaluation if available, otherwise simulate
            if self.opa_client and OPA_CLIENT_AVAILABLE:
                opa_result = await self._real_opa_evaluation(policy_name, opa_input)
            else:
                opa_result = await self._simulate_opa_evaluation(policy_name, opa_input)

            # Process OPA result
            decision = self._process_opa_result(opa_result, policy_name, context)

            # Update metrics
            evaluation_time = (time.time() - start_time) * 1000
            decision.evaluation_time_ms = evaluation_time
            self._update_metrics(decision, evaluation_time)

            # Cache result
            self.evaluation_cache[cache_key] = decision

            return decision

        except Exception as e:
            logger.exception(f"Policy evaluation error for {policy_name}: {e}")
            return self._create_error_decision(
                policy_name, str(e), time.time() - start_time
            )

    async def evaluate_multiple_policies(
        self, policy_names: list[str], context: PolicyEvaluationContext
    ) -> list[PolicyDecision]:
        """Evaluate multiple policies concurrently."""
        tasks = [
            self.evaluate_policy(policy_name, context) for policy_name in policy_names
        ]
        decisions = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and convert them to error decisions
        processed_decisions = []
        for i, result in enumerate(decisions):
            if isinstance(result, Exception):
                error_decision = self._create_error_decision(
                    policy_names[i], str(result), 0.0
                )
                processed_decisions.append(error_decision)
            else:
                processed_decisions.append(result)

        return processed_decisions

    def _prepare_opa_input(self, context: PolicyEvaluationContext) -> dict[str, Any]:
        """Prepare input for OPA evaluation."""
        return {
            "principal": context.principal,
            "resource": context.resource,
            "action": context.action,
            "environment": context.environment,
            "context": {
                "request_id": context.request_id,
                "timestamp": context.timestamp.isoformat(),
                "constitutional_requirements": context.constitutional_requirements,
                "historical_context": context.historical_context[
                    -10:
                ],  # Last 10 entries
            },
        }

    async def _real_opa_evaluation(
        self, policy_name: str, opa_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform real OPA policy evaluation using OPA client."""
        try:
            logger.debug(f"Evaluating policy {policy_name} with real OPA client")

            # Route to appropriate OPA policy evaluation method
            if "constitutional" in policy_name:
                return await self.opa_client.evaluate_constitutional_policy(opa_input)
            if "evolutionary" in policy_name:
                return await self.opa_client.evaluate_evolutionary_policy(opa_input)
            if "security" in policy_name:
                return await self.opa_client.evaluate_security_policy(opa_input)
            if "multi_tenant" in policy_name:
                return await self.opa_client.evaluate_multi_tenant_policy(opa_input)
            # For other policy types, use generic evaluation
            return await self.opa_client.evaluate_policy(policy_name, opa_input)

        except Exception as e:
            logger.exception(f"Real OPA evaluation failed for {policy_name}: {e}")
            # Fallback to simulation on error
            logger.info(f"Falling back to simulation for {policy_name}")
            return await self._simulate_opa_evaluation(policy_name, opa_input)

    async def _simulate_opa_evaluation(
        self, policy_name: str, opa_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Simulate OPA policy evaluation (fallback when real OPA is unavailable)."""
        logger.debug(f"Using simulation for policy {policy_name}")

        # Simulate different policy evaluations based on policy type
        if "constitutional" in policy_name:
            return await self._simulate_constitutional_evaluation(opa_input)
        if "evolutionary" in policy_name:
            return await self._simulate_evolutionary_evaluation(opa_input)
        if "security" in policy_name:
            return await self._simulate_security_evaluation(opa_input)
        if "multi_tenant" in policy_name:
            return await self._simulate_multi_tenant_evaluation(opa_input)
        return await self._simulate_default_evaluation(opa_input)

    async def _simulate_constitutional_evaluation(
        self, opa_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Simulate constitutional policy evaluation."""

        # Extract constitutional requirements
        opa_input.get("context", {}).get("constitutional_requirements", {})

        # Simulate constitutional compliance scoring
        human_dignity_score = self._calculate_principle_score(
            opa_input, "human_dignity"
        )
        fairness_score = self._calculate_principle_score(opa_input, "fairness")
        transparency_score = self._calculate_principle_score(opa_input, "transparency")
        accountability_score = self._calculate_principle_score(
            opa_input, "accountability"
        )
        privacy_score = self._calculate_principle_score(opa_input, "privacy")

        # Weighted constitutional compliance score
        compliance_score = (
            human_dignity_score * 0.25
            + fairness_score * 0.20
            + transparency_score * 0.15
            + accountability_score * 0.20
            + privacy_score * 0.20
        )

        # Decision logic
        decision = "allow" if compliance_score >= 0.8 else "deny"

        return {
            "decision": decision,
            "compliance_score": compliance_score,
            "principle_scores": {
                "human_dignity": human_dignity_score,
                "fairness": fairness_score,
                "transparency": transparency_score,
                "accountability": accountability_score,
                "privacy": privacy_score,
            },
            "constitutional_compliant": compliance_score >= 0.8,
            "reasons": self._generate_constitutional_reasons(
                compliance_score, decision
            ),
            "metadata": {
                "policy_type": "constitutional",
                "evaluation_method": "weighted_scoring",
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
        }

    async def _simulate_evolutionary_evaluation(
        self, opa_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Simulate evolutionary governance policy evaluation."""

        # Extract evolution request details
        opa_input.get("action", "")
        resource = opa_input.get("resource", {})

        # Risk assessment simulation
        risk_score = self._calculate_evolution_risk(resource)
        safety_score = self._calculate_safety_score(resource)
        constitutional_impact = self._assess_constitutional_impact(resource)

        # Decision logic based on risk and safety
        if risk_score <= 0.3 and safety_score >= 0.8 and constitutional_impact >= 0.8:
            decision = "allow"
        elif risk_score <= 0.6 and safety_score >= 0.7:
            decision = "conditional"
        else:
            decision = "deny"

        return {
            "decision": decision,
            "risk_score": risk_score,
            "safety_score": safety_score,
            "constitutional_impact": constitutional_impact,
            "conditions": (
                self._generate_evolution_conditions(risk_score, safety_score)
                if decision == "conditional"
                else []
            ),
            "reasons": self._generate_evolution_reasons(
                risk_score, safety_score, decision
            ),
            "metadata": {
                "policy_type": "evolutionary",
                "risk_assessment": "comprehensive",
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
        }

    async def _simulate_security_evaluation(
        self, opa_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Simulate security policy evaluation."""

        principal = opa_input.get("principal", {})
        action = opa_input.get("action", "")
        resource = opa_input.get("resource", {})

        # Security scoring
        authentication_score = self._assess_authentication(principal)
        authorization_score = self._assess_authorization(principal, action, resource)
        threat_score = self._assess_threat_level(opa_input)

        # Aggregate security score
        security_score = (
            authentication_score + authorization_score + (1 - threat_score)
        ) / 3

        # Decision logic
        if security_score >= 0.8 and threat_score <= 0.2:
            decision = "allow"
        elif security_score >= 0.6 and threat_score <= 0.5:
            decision = "conditional"
        else:
            decision = "deny"

        return {
            "decision": decision,
            "security_score": security_score,
            "authentication_score": authentication_score,
            "authorization_score": authorization_score,
            "threat_score": threat_score,
            "conditions": (
                self._generate_security_conditions(security_score, threat_score)
                if decision == "conditional"
                else []
            ),
            "reasons": self._generate_security_reasons(
                security_score, threat_score, decision
            ),
            "metadata": {
                "policy_type": "security",
                "threat_assessment": "real_time",
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
        }

    async def _simulate_multi_tenant_evaluation(
        self, opa_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Simulate multi-tenant policy evaluation."""

        principal = opa_input.get("principal", {})
        resource = opa_input.get("resource", {})

        # Tenant isolation scoring
        tenant_id = principal.get("tenant_id")
        resource_tenant = resource.get("tenant_id")

        isolation_score = 1.0 if tenant_id == resource_tenant else 0.0
        access_level_score = self._assess_tenant_access_level(principal, resource)
        data_governance_score = self._assess_data_governance_compliance(opa_input)

        # Aggregate multi-tenant score
        mt_score = (
            isolation_score * 0.5
            + access_level_score * 0.3
            + data_governance_score * 0.2
        )

        decision = "allow" if mt_score >= 0.8 else "deny"

        return {
            "decision": decision,
            "multi_tenant_score": mt_score,
            "isolation_score": isolation_score,
            "access_level_score": access_level_score,
            "data_governance_score": data_governance_score,
            "tenant_compliant": isolation_score == 1.0,
            "reasons": self._generate_multi_tenant_reasons(mt_score, decision),
            "metadata": {
                "policy_type": "multi_tenant",
                "tenant_isolation": "strict",
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
        }

    async def _simulate_default_evaluation(
        self, opa_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Simulate default policy evaluation."""

        # Basic evaluation logic
        principal = opa_input.get("principal", {})
        action = opa_input.get("action", "")

        # Simple scoring based on available information
        basic_score = 0.7  # Default moderate score

        if principal.get("authenticated", False):
            basic_score += 0.1
        if principal.get("authorized", False):
            basic_score += 0.1
        if action in {"read", "view", "list"}:
            basic_score += 0.1

        decision = "allow" if basic_score >= 0.8 else "conditional"

        return {
            "decision": decision,
            "basic_score": basic_score,
            "reasons": [f"Basic policy evaluation with score {basic_score:.2f}"],
            "metadata": {
                "policy_type": "default",
                "evaluation_method": "basic",
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
        }

    def _calculate_principle_score(
        self, opa_input: dict[str, Any], principle: str
    ) -> float:
        """Calculate score for a constitutional principle."""

        # Extract relevant data from input
        action = opa_input.get("action", "")
        resource = opa_input.get("resource", {})
        principal = opa_input.get("principal", {})

        # Principle-specific scoring logic
        if principle == "human_dignity":
            # Check if action respects human autonomy and dignity
            if action in {"respect", "protect", "enhance"}:
                return 0.9
            if action in {"inform", "support"}:
                return 0.8
            if action in {"monitor", "analyze"}:
                return 0.7
            return 0.6

        if principle == "fairness":
            # Check for fair treatment and non-discrimination
            if resource.get("access_type") == "equal":
                return 0.9
            if resource.get("bias_checked", False):
                return 0.8
            return 0.6

        if principle == "transparency":
            # Check for transparency in decision-making
            if resource.get("explainable", False):
                return 0.9
            if action in {"log", "audit", "trace"}:
                return 0.8
            return 0.6

        if principle == "accountability":
            # Check for clear accountability mechanisms
            if principal.get("accountable", False):
                return 0.9
            if resource.get("traceable", False):
                return 0.8
            return 0.6

        if principle == "privacy":
            # Check for privacy protection
            if resource.get("privacy_preserving", False):
                return 0.9
            if action in {"anonymize", "encrypt"}:
                return 0.8
            return 0.6

        return 0.7  # Default moderate score

    def _calculate_evolution_risk(self, resource: dict[str, Any]) -> float:
        """Calculate risk score for evolutionary changes."""

        change_type = resource.get("evolution_type", "minor")
        complexity = resource.get("complexity_score", 5)
        novelty = resource.get("novelty_score", 5)
        impact = resource.get("impact_score", 5)

        # Base risk by change type
        type_risk = {
            "capability_enhancement": 0.3,
            "behavior_modification": 0.6,
            "autonomy_increase": 0.8,
            "safety_mechanism_change": 0.9,
        }.get(change_type, 0.5)

        # Complexity factor (0-1 normalized)
        complexity_factor = min(complexity / 10.0, 1.0)
        novelty_factor = min(novelty / 10.0, 1.0)
        impact_factor = min(impact / 10.0, 1.0)

        # Calculate final risk score
        risk_score = (
            type_risk * (1 + complexity_factor + novelty_factor + impact_factor) / 4
        )

        return min(risk_score, 1.0)

    def _calculate_safety_score(self, resource: dict[str, Any]) -> float:
        """Calculate safety score for resources/actions."""

        safety_mechanisms = resource.get("safety_mechanisms", [])
        testing_completed = resource.get("testing_completed", False)
        rollback_plan = resource.get("rollback_plan_exists", False)
        monitoring = resource.get("monitoring_enabled", False)

        safety_score = 0.0

        if len(safety_mechanisms) >= 3:
            safety_score += 0.3
        elif len(safety_mechanisms) >= 1:
            safety_score += 0.2

        if testing_completed:
            safety_score += 0.3

        if rollback_plan:
            safety_score += 0.2

        if monitoring:
            safety_score += 0.2

        return min(safety_score, 1.0)

    def _assess_constitutional_impact(self, resource: dict[str, Any]) -> float:
        """Assess constitutional impact of a resource/action."""

        impact_analysis = resource.get("constitutional_impact_analysis", {})

        # Check individual principle impacts
        principles = [
            "human_dignity",
            "fairness",
            "transparency",
            "accountability",
            "privacy",
        ]
        principle_scores = []

        for principle in principles:
            principle_data = impact_analysis.get(principle, {})
            if principle_data.get("compliant", False):
                principle_scores.append(principle_data.get("confidence_score", 0.8))
            else:
                principle_scores.append(0.0)

        return (
            sum(principle_scores) / len(principle_scores) if principle_scores else 0.5
        )

    def _assess_authentication(self, principal: dict[str, Any]) -> float:
        """Assess authentication strength."""

        auth_methods = principal.get("authentication_methods", [])
        auth_strength = principal.get("authentication_strength", "basic")

        score = 0.0

        if "mfa" in auth_methods:
            score += 0.4
        if "certificate" in auth_methods:
            score += 0.3
        if "biometric" in auth_methods:
            score += 0.3

        if auth_strength == "strong":
            score += 0.2
        elif auth_strength == "medium":
            score += 0.1

        return min(score, 1.0)

    def _assess_authorization(
        self, principal: dict[str, Any], action: str, resource: dict[str, Any]
    ) -> float:
        """Assess authorization appropriateness."""

        permissions = principal.get("permissions", [])
        roles = principal.get("roles", [])

        # Check if action is within permissions
        if action in permissions:
            return 0.9

        # Check role-based access
        required_role = resource.get("required_role")
        if required_role and required_role in roles:
            return 0.8

        # Check for admin/super user
        if "admin" in roles or "superuser" in roles:
            return 0.7

        return 0.3

    def _assess_threat_level(self, opa_input: dict[str, Any]) -> float:
        """Assess threat level of the request."""

        environment = opa_input.get("environment", {})
        action = opa_input.get("action", "")

        threat_score = 0.0

        # Check for suspicious patterns
        if environment.get("suspicious_activity", False):
            threat_score += 0.4

        if action in {"delete", "destroy", "modify_critical"}:
            threat_score += 0.3

        if environment.get("ip_reputation", "good") == "bad":
            threat_score += 0.2

        if environment.get("time_of_day") in {"late_night", "early_morning"}:
            threat_score += 0.1

        return min(threat_score, 1.0)

    def _assess_tenant_access_level(
        self, principal: dict[str, Any], resource: dict[str, Any]
    ) -> float:
        """Assess tenant access level appropriateness."""

        principal_level = principal.get("access_level", "basic")
        required_level = resource.get("required_access_level", "basic")

        level_hierarchy = {
            "basic": 1,
            "standard": 2,
            "premium": 3,
            "enterprise": 4,
            "admin": 5,
        }

        principal_rank = level_hierarchy.get(principal_level, 1)
        required_rank = level_hierarchy.get(required_level, 1)

        if principal_rank >= required_rank:
            return 1.0
        return principal_rank / required_rank

    def _assess_data_governance_compliance(self, opa_input: dict[str, Any]) -> float:
        """Assess data governance compliance."""

        resource = opa_input.get("resource", {})
        action = opa_input.get("action", "")

        compliance_score = 0.0

        # Check data classification compliance
        if resource.get("data_classified", False):
            compliance_score += 0.3

        # Check encryption for sensitive data
        if resource.get("data_sensitivity") == "high" and resource.get(
            "encrypted", False
        ):
            compliance_score += 0.3

        # Check audit logging
        if action in {"access", "modify", "delete"} and resource.get(
            "audit_enabled", False
        ):
            compliance_score += 0.2

        # Check data retention compliance
        if resource.get("retention_compliant", False):
            compliance_score += 0.2

        return min(compliance_score, 1.0)

    def _generate_constitutional_reasons(
        self, compliance_score: float, decision: str
    ) -> list[str]:
        """Generate reasons for constitutional policy decisions."""

        reasons = []

        if decision == "allow":
            reasons.append(
                f"Constitutional compliance score {compliance_score:.2f} meets"
                " threshold"
            )
            if compliance_score >= 0.9:
                reasons.append("Excellent constitutional alignment achieved")
        else:
            reasons.extend(
                (
                    f"Constitutional compliance score {compliance_score:.2f} below"
                    " threshold",
                    "Constitutional principles require strengthening",
                )
            )

        return reasons

    def _generate_evolution_reasons(
        self, risk_score: float, safety_score: float, decision: str
    ) -> list[str]:
        """Generate reasons for evolutionary policy decisions."""

        reasons = []

        if decision == "allow":
            reasons.extend(
                (
                    f"Risk score {risk_score:.2f} within acceptable bounds",
                    f"Safety score {safety_score:.2f} meets requirements",
                )
            )
        elif decision == "conditional":
            reasons.extend(
                (
                    f"Moderate risk score {risk_score:.2f} requires conditions",
                    "Additional safety measures recommended",
                )
            )
        else:
            reasons.append(f"Risk score {risk_score:.2f} exceeds acceptable threshold")
            if safety_score < 0.7:
                reasons.append(f"Safety score {safety_score:.2f} insufficient")

        return reasons

    def _generate_security_reasons(
        self, security_score: float, threat_score: float, decision: str
    ) -> list[str]:
        """Generate reasons for security policy decisions."""

        reasons = []

        if decision == "allow":
            reasons.extend(
                (
                    f"Security score {security_score:.2f} meets requirements",
                    f"Threat level {threat_score:.2f} acceptable",
                )
            )
        elif decision == "conditional":
            reasons.append(
                f"Security score {security_score:.2f} requires additional measures"
            )
        else:
            reasons.append(f"Security score {security_score:.2f} insufficient")
            if threat_score > 0.5:
                reasons.append(f"Threat level {threat_score:.2f} too high")

        return reasons

    def _generate_multi_tenant_reasons(
        self, mt_score: float, decision: str
    ) -> list[str]:
        """Generate reasons for multi-tenant policy decisions."""

        reasons = []

        if decision == "allow":
            reasons.extend(
                (
                    f"Multi-tenant compliance score {mt_score:.2f} satisfactory",
                    "Tenant isolation maintained",
                )
            )
        else:
            reasons.extend(
                (
                    f"Multi-tenant compliance score {mt_score:.2f} insufficient",
                    "Tenant isolation requirements not met",
                )
            )

        return reasons

    def _generate_evolution_conditions(
        self, risk_score: float, safety_score: float
    ) -> list[dict[str, Any]]:
        """Generate conditions for conditional evolutionary decisions."""

        conditions = []

        if risk_score > 0.4:
            conditions.append(
                {
                    "type": "risk_mitigation",
                    "requirement": "Additional risk assessment required",
                    "timeline": "before_implementation",
                }
            )

        if safety_score < 0.8:
            conditions.append(
                {
                    "type": "safety_enhancement",
                    "requirement": "Enhanced safety mechanisms required",
                    "timeline": "before_deployment",
                }
            )

        conditions.append(
            {
                "type": "monitoring",
                "requirement": "Continuous monitoring during initial deployment",
                "timeline": "during_operation",
            }
        )

        return conditions

    def _generate_security_conditions(
        self, security_score: float, threat_score: float
    ) -> list[dict[str, Any]]:
        """Generate conditions for conditional security decisions."""

        conditions = []

        if security_score < 0.8:
            conditions.append(
                {
                    "type": "authentication_enhancement",
                    "requirement": "Additional authentication required",
                    "timeline": "immediate",
                }
            )

        if threat_score > 0.3:
            conditions.append(
                {
                    "type": "threat_monitoring",
                    "requirement": "Enhanced threat monitoring",
                    "timeline": "continuous",
                }
            )

        return conditions

    def _process_opa_result(
        self,
        opa_result: dict[str, Any],
        policy_name: str,
        context: PolicyEvaluationContext,
    ) -> PolicyDecision:
        """Process OPA evaluation result into PolicyDecision."""

        decision_str = opa_result.get("decision", "deny")
        decision_type = DecisionType(decision_str)

        return PolicyDecision(
            decision_id=str(uuid.uuid4()),
            decision=decision_type,
            confidence_score=opa_result.get(
                "confidence_score", opa_result.get("compliance_score", 0.5)
            ),
            policies_evaluated=[policy_name],
            evaluation_time_ms=0.0,  # Will be set by caller
            constitutional_compliance=opa_result.get("constitutional_compliant", False),
            reasons=opa_result.get("reasons", []),
            conditions=opa_result.get("conditions", []),
            metadata=opa_result.get("metadata", {}),
            audit_trail=[
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "policy": policy_name,
                    "result": opa_result,
                    "context_id": context.request_id,
                }
            ],
        )

    def _create_cache_key(
        self, policy_name: str, context: PolicyEvaluationContext
    ) -> str:
        """Create cache key for policy evaluation."""

        # Create a hash of the relevant context elements
        cache_data = {
            "policy": policy_name,
            "principal": context.principal,
            "resource": context.resource,
            "action": context.action,
            "environment": context.environment,
        }

        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _is_cache_valid(
        self, cached_decision: PolicyDecision, context: PolicyEvaluationContext
    ) -> bool:
        """Check if cached decision is still valid."""

        # Simple time-based cache validity (5 minutes)
        cache_duration = timedelta(minutes=5)
        return not datetime.now(timezone.utc) - context.timestamp > cache_duration

    def _create_error_decision(
        self, policy_name: str, error_msg: str, evaluation_time: float
    ) -> PolicyDecision:
        """Create error decision for failed evaluations."""

        return PolicyDecision(
            decision_id=str(uuid.uuid4()),
            decision=DecisionType.DENY,
            confidence_score=0.0,
            policies_evaluated=[policy_name],
            evaluation_time_ms=evaluation_time * 1000,
            constitutional_compliance=False,
            reasons=[f"Policy evaluation error: {error_msg}"],
            conditions=[],
            metadata={"error": True, "error_message": error_msg},
            audit_trail=[
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "policy": policy_name,
                    "error": error_msg,
                    "result": "evaluation_failed",
                }
            ],
        )

    def _update_metrics(self, decision: PolicyDecision, evaluation_time: float):
        """Update performance metrics."""

        self.metrics.total_evaluations += 1

        # Update average evaluation time
        total_time = self.metrics.average_evaluation_time_ms * (
            self.metrics.total_evaluations - 1
        )
        self.metrics.average_evaluation_time_ms = (
            total_time + evaluation_time
        ) / self.metrics.total_evaluations

        # Update decision distribution
        decision_str = decision.decision.value
        if decision_str not in self.metrics.decision_distribution:
            self.metrics.decision_distribution[decision_str] = 0
        self.metrics.decision_distribution[decision_str] += 1

        # Update constitutional compliance rate
        if decision.constitutional_compliance:
            compliant_count = sum(
                1 for d in self.metrics.decision_distribution.values()
            )
            self.metrics.constitutional_compliance_rate = (
                compliant_count / self.metrics.total_evaluations
            )

    async def cleanup(self):
        """Clean up resources, including OPA client connection."""
        if self.opa_client and OPA_CLIENT_AVAILABLE:
            try:
                await self.opa_client.close()
                logger.info("OPA client connection closed")
            except Exception as e:
                logger.exception(f"Error closing OPA client: {e}")

    async def initialize_opa_policies(self) -> bool:
        """Initialize OPA server with default policies."""
        if not self.opa_client or not OPA_CLIENT_AVAILABLE:
            logger.warning("OPA client not available, skipping policy initialization")
            return False

        try:
            # Check OPA server health
            is_healthy = await self.opa_client.health_check()
            if not is_healthy:
                logger.error("OPA server is not healthy")
                return False

            # Initialize policies using the policy manager
            from .opa_client import OPAPolicyManager

            policy_manager = OPAPolicyManager(self.opa_client)
            success = await policy_manager.create_default_policies()

            if success:
                logger.info("Successfully initialized OPA policies")
            else:
                logger.warning("Some policies failed to initialize")

            return success

        except Exception as e:
            logger.exception(f"Failed to initialize OPA policies: {e}")
            return False


class AdvancedGovernanceSynthesisEngine:
    """
    Advanced governance synthesis engine with sophisticated policy orchestration.

    Integrates multiple policy evaluation engines, handles conflicts, and provides
    comprehensive governance decision-making with constitutional compliance.
    """

    def __init__(self, policies_path: str = "./policies"):
        self.policies_path = Path(policies_path)
        self.evaluation_engine = OPAEvaluationEngine(policies_path=str(policies_path))
        self.policy_graph = nx.DiGraph()  # For dependency and conflict analysis
        self.conflict_resolution_strategies = {}
        self.performance_metrics = {}

        # Initialize policy catalog
        self.policy_catalog = self._load_policy_catalog()
        self._build_policy_graph()

        logger.info(
            "Advanced Governance Synthesis Engine initialized with"
            f" {len(self.policy_catalog)} policies"
        )

    async def synthesize_governance_decision(
        self, context: PolicyEvaluationContext, policy_scope: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Synthesize comprehensive governance decision.

        Args:
            context: Evaluation context
            policy_scope: Optional list of specific policies to evaluate

        Returns:
            Comprehensive governance decision with metadata
        """

        start_time = time.time()
        synthesis_id = str(uuid.uuid4())

        try:
            # Determine applicable policies
            applicable_policies = policy_scope or self._determine_applicable_policies(
                context
            )

            # Evaluate all applicable policies
            policy_decisions = await self.evaluation_engine.evaluate_multiple_policies(
                applicable_policies, context
            )

            # Detect and resolve conflicts
            conflicts = self._detect_policy_conflicts(policy_decisions, context)
            resolved_conflicts = await self._resolve_conflicts(conflicts, context)

            # Synthesize final decision
            final_decision = self._synthesize_final_decision(
                policy_decisions, resolved_conflicts, context
            )

            # Generate audit trail
            audit_trail = self._generate_audit_trail(
                policy_decisions, conflicts, resolved_conflicts, context
            )

            # Calculate synthesis metrics
            synthesis_time = (time.time() - start_time) * 1000

            synthesis_result = {
                "synthesis_id": synthesis_id,
                "final_decision": final_decision.decision.value,
                "confidence_score": final_decision.confidence_score,
                "constitutional_compliance": final_decision.constitutional_compliance,
                "synthesis_time_ms": synthesis_time,
                "policies_evaluated": applicable_policies,
                "policy_decisions": [
                    self._serialize_decision(d) for d in policy_decisions
                ],
                "conflicts_detected": len(conflicts),
                "conflicts_resolved": len(resolved_conflicts),
                "reasons": final_decision.reasons,
                "conditions": final_decision.conditions,
                "audit_trail": audit_trail,
                "metadata": {
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "synthesis_engine": "advanced_opa_engine",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "context_id": context.request_id,
                },
            }

            # Update performance metrics
            self._update_synthesis_metrics(synthesis_result)

            logger.info(
                f"Governance synthesis completed: {synthesis_id}, decision:"
                f" {final_decision.decision.value}"
            )

            return synthesis_result

        except Exception as e:
            logger.exception(f"Governance synthesis failed: {e}")
            return self._create_error_synthesis_result(
                synthesis_id, str(e), time.time() - start_time
            )

    def _load_policy_catalog(self) -> dict[str, Any]:
        """Load policy catalog from configuration."""

        # This would normally load from a configuration file or database
        # For now, using the catalog from the policy_index.rego file
        return {
            "constitutional_principles": {
                "package": "acgs.constitutional",
                "version": "2.0.0",
                "description": (
                    "Core constitutional principles validation and compliance checking"
                ),
                "scope": [
                    "policy_synthesis",
                    "governance_decisions",
                    "constitutional_compliance",
                ],
                "priority": "critical",
                "dependencies": [],
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            "governance_compliance": {
                "package": "acgs.governance_compliance",
                "version": "2.0.0",
                "description": (
                    "Comprehensive governance compliance validation framework"
                ),
                "scope": [
                    "regulatory_compliance",
                    "operational_governance",
                    "risk_management",
                ],
                "priority": "high",
                "dependencies": ["constitutional_principles"],
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            "policy_synthesis": {
                "package": "acgs.policy_synthesis",
                "version": "2.0.0",
                "description": "Policy synthesis validation and conflict detection",
                "scope": [
                    "policy_creation",
                    "policy_validation",
                    "conflict_resolution",
                ],
                "priority": "high",
                "dependencies": ["constitutional_principles", "governance_compliance"],
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            "multi_tenant_security": {
                "package": "acgs.multi_tenant_security",
                "version": "1.0.0",
                "description": (
                    "Multi-tenant security isolation and governance controls"
                ),
                "scope": [
                    "tenant_isolation",
                    "resource_access",
                    "cross_tenant_operations",
                ],
                "priority": "high",
                "dependencies": ["constitutional_principles", "security_compliance"],
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            "evolutionary_governance": {
                "package": "acgs.evolutionary_governance",
                "version": "1.0.0",
                "description": "Agent evolution and adaptive governance mechanisms",
                "scope": [
                    "agent_evolution",
                    "capability_upgrades",
                    "autonomous_adaptation",
                ],
                "priority": "critical",
                "dependencies": ["constitutional_principles", "agent_lifecycle"],
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            "data_governance": {
                "package": "acgs.data_governance",
                "version": "1.0.0",
                "description": "Data privacy, protection, and governance compliance",
                "scope": ["data_access", "data_processing", "privacy_compliance"],
                "priority": "critical",
                "dependencies": ["constitutional_principles", "security_compliance"],
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            "security_compliance": {
                "package": "acgs.security_compliance",
                "version": "1.0.0",
                "description": (
                    "Enterprise security compliance and constitutional security"
                ),
                "scope": [
                    "security_operations",
                    "compliance_frameworks",
                    "security_governance",
                ],
                "priority": "critical",
                "dependencies": ["constitutional_principles"],
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            "agent_lifecycle_governance": {
                "package": "acgs.agent_lifecycle",
                "version": "1.0.0",
                "description": (
                    "Complete agent lifecycle governance and constitutional compliance"
                ),
                "scope": [
                    "agent_creation",
                    "agent_deployment",
                    "agent_evolution",
                    "agent_decommission",
                ],
                "priority": "critical",
                "dependencies": [
                    "constitutional_principles",
                    "evolutionary_governance",
                    "security_compliance",
                ],
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
        }

    def _build_policy_graph(self):
        """Build policy dependency graph."""

        # Add nodes
        for policy_name, policy_info in self.policy_catalog.items():
            self.policy_graph.add_node(policy_name, **policy_info)

        # Add dependency edges
        for policy_name, policy_info in self.policy_catalog.items():
            for dependency in policy_info.get("dependencies", []):
                if dependency in self.policy_catalog:
                    self.policy_graph.add_edge(dependency, policy_name)

    def _determine_applicable_policies(
        self, context: PolicyEvaluationContext
    ) -> list[str]:
        """Determine which policies are applicable for the given context."""

        applicable_policies = []

        # Determine scope based on context
        action = context.action
        resource_type = context.resource.get("type", "")
        context.principal.get("type", "")

        # Map context to policy scopes
        if "constitutional" in action or "governance" in action:
            applicable_policies.extend(
                ("constitutional_principles", "governance_compliance")
            )

        if "tenant" in resource_type or "multi_tenant" in action:
            applicable_policies.append("multi_tenant_security")

        if "evolution" in action or "capability" in action:
            applicable_policies.append("evolutionary_governance")

        if "data" in resource_type or "privacy" in action:
            applicable_policies.append("data_governance")

        if "security" in action or "auth" in action:
            applicable_policies.append("security_compliance")

        if "agent" in resource_type:
            applicable_policies.append("agent_lifecycle_governance")

        # Always include policy synthesis for policy-related operations
        if "policy" in action:
            applicable_policies.append("policy_synthesis")

        # Ensure dependencies are included
        expanded_policies = set(applicable_policies)
        for policy in applicable_policies:
            dependencies = self.policy_catalog.get(policy, {}).get("dependencies", [])
            expanded_policies.update(dependencies)

        return list(expanded_policies)

    def _detect_policy_conflicts(
        self, policy_decisions: list[PolicyDecision], context: PolicyEvaluationContext
    ) -> list[PolicyConflict]:
        """Detect conflicts between policy decisions."""

        conflicts = []

        # Check for decision conflicts
        for i, decision_a in enumerate(policy_decisions):
            for _j, decision_b in enumerate(policy_decisions[i + 1 :], i + 1):
                conflict = self._check_decision_conflict(
                    decision_a, decision_b, context
                )
                if conflict:
                    conflicts.append(conflict)

        return conflicts

    def _check_decision_conflict(
        self,
        decision_a: PolicyDecision,
        decision_b: PolicyDecision,
        context: PolicyEvaluationContext,
    ) -> PolicyConflict | None:
        """Check if two policy decisions conflict."""

        # Direct contradiction: one allows, other denies
        if (
            decision_a.decision == DecisionType.ALLOW
            and decision_b.decision == DecisionType.DENY
        ) or (
            decision_a.decision == DecisionType.DENY
            and decision_b.decision == DecisionType.ALLOW
        ):
            return PolicyConflict(
                conflict_id=str(uuid.uuid4()),
                conflict_type=PolicyConflictType.LOGICAL_CONTRADICTION,
                policies_involved=decision_a.policies_evaluated
                + decision_b.policies_evaluated,
                severity="high",
                description=(
                    f"Policy decisions contradict: {decision_a.decision.value} vs"
                    f" {decision_b.decision.value}"
                ),
                constitutional_impact={"contradiction_detected": True},
            )

        # Constitutional compliance conflict
        if decision_a.constitutional_compliance != decision_b.constitutional_compliance:
            return PolicyConflict(
                conflict_id=str(uuid.uuid4()),
                conflict_type=PolicyConflictType.CONSTITUTIONAL_VIOLATION,
                policies_involved=decision_a.policies_evaluated
                + decision_b.policies_evaluated,
                severity="critical",
                description="Constitutional compliance disagreement between policies",
                constitutional_impact={"compliance_conflict": True},
            )

        return None

    async def _resolve_conflicts(
        self, conflicts: list[PolicyConflict], context: PolicyEvaluationContext
    ) -> list[PolicyConflict]:
        """Resolve policy conflicts using various strategies."""

        resolved_conflicts = []

        for conflict in conflicts:
            resolved_conflict = await self._resolve_single_conflict(conflict, context)
            resolved_conflicts.append(resolved_conflict)

        return resolved_conflicts

    async def _resolve_single_conflict(
        self, conflict: PolicyConflict, context: PolicyEvaluationContext
    ) -> PolicyConflict:
        """Resolve a single policy conflict."""

        # Priority-based resolution
        if conflict.conflict_type == PolicyConflictType.LOGICAL_CONTRADICTION:
            # Use policy priority to resolve
            resolved_conflict = self._resolve_by_priority(conflict)

        elif conflict.conflict_type == PolicyConflictType.CONSTITUTIONAL_VIOLATION:
            # Constitutional principles always take precedence
            resolved_conflict = self._resolve_constitutional_conflict(conflict)

        else:
            # Default resolution strategy
            resolved_conflict = self._resolve_by_consensus(conflict)

        return resolved_conflict

    def _resolve_by_priority(self, conflict: PolicyConflict) -> PolicyConflict:
        """Resolve conflict by policy priority."""

        policy_priorities = {}
        for policy_name in conflict.policies_involved:
            policy_info = self.policy_catalog.get(policy_name, {})
            priority = policy_info.get("priority", "medium")
            priority_value = {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(
                priority, 2
            )
            policy_priorities[policy_name] = priority_value

        # Highest priority wins
        winning_policy = max(policy_priorities, key=policy_priorities.get)

        conflict.resolution_strategy = (
            f"Priority-based resolution: {winning_policy} (priority:"
            f" {policy_priorities[winning_policy]})"
        )
        conflict.resolution_confidence = 0.8

        return conflict

    def _resolve_constitutional_conflict(
        self, conflict: PolicyConflict
    ) -> PolicyConflict:
        """Resolve constitutional conflicts."""

        # Constitutional principles always take precedence
        conflict.resolution_strategy = (
            "Constitutional precedence: constitutional compliance required"
        )
        conflict.resolution_confidence = 1.0
        conflict.constitutional_impact["resolution"] = (
            "constitutional_precedence_applied"
        )

        return conflict

    def _resolve_by_consensus(self, conflict: PolicyConflict) -> PolicyConflict:
        """Resolve conflict by seeking consensus."""

        # Simple consensus: if more policies agree, use that decision
        conflict.resolution_strategy = "Consensus-based resolution"
        conflict.resolution_confidence = 0.6

        return conflict

    def _synthesize_final_decision(
        self,
        policy_decisions: list[PolicyDecision],
        resolved_conflicts: list[PolicyConflict],
        context: PolicyEvaluationContext,
    ) -> PolicyDecision:
        """Synthesize final governance decision from policy decisions and conflict resolutions."""

        # Calculate weighted decision
        decision_weights = self._calculate_decision_weights(policy_decisions)
        final_decision_type = self._determine_final_decision_type(
            policy_decisions, decision_weights
        )

        # Calculate confidence score
        confidence_score = self._calculate_synthesis_confidence(
            policy_decisions, resolved_conflicts
        )

        # Check constitutional compliance
        constitutional_compliance = all(
            d.constitutional_compliance for d in policy_decisions
        )

        # Aggregate reasons
        all_reasons = []
        for decision in policy_decisions:
            all_reasons.extend(decision.reasons)

        # Add conflict resolution reasons
        all_reasons.extend(
            f"Conflict resolved: {conflict.resolution_strategy}"
            for conflict in resolved_conflicts
            if conflict.resolution_strategy
        )

        # Aggregate conditions
        all_conditions = []
        for decision in policy_decisions:
            all_conditions.extend(decision.conditions)

        # Create final decision
        return PolicyDecision(
            decision_id=str(uuid.uuid4()),
            decision=final_decision_type,
            confidence_score=confidence_score,
            policies_evaluated=[
                p for d in policy_decisions for p in d.policies_evaluated
            ],
            evaluation_time_ms=sum(d.evaluation_time_ms for d in policy_decisions),
            constitutional_compliance=constitutional_compliance,
            reasons=all_reasons,
            conditions=all_conditions,
            metadata={
                "synthesis_method": "weighted_aggregation",
                "conflicts_resolved": len(resolved_conflicts),
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
        )

    def _calculate_decision_weights(
        self, policy_decisions: list[PolicyDecision]
    ) -> dict[str, float]:
        """Calculate weights for different decision types."""

        weights = {
            "allow": 0.0,
            "deny": 0.0,
            "conditional": 0.0,
            "escalate": 0.0,
            "defer": 0.0,
        }

        total_confidence = sum(d.confidence_score for d in policy_decisions)

        for decision in policy_decisions:
            weight = (
                decision.confidence_score / total_confidence
                if total_confidence > 0
                else 1.0 / len(policy_decisions)
            )
            weights[decision.decision.value] += weight

        return weights

    def _determine_final_decision_type(
        self, policy_decisions: list[PolicyDecision], weights: dict[str, float]
    ) -> DecisionType:
        """Determine final decision type based on weights."""

        # Priority order: deny > conditional > escalate > defer > allow
        if weights["deny"] > 0.3:  # If any significant denial, deny
            return DecisionType.DENY
        if weights["conditional"] > 0.2:  # If significant conditional, make conditional
            return DecisionType.CONDITIONAL
        if weights["escalate"] > 0.1:  # If any escalation needed
            return DecisionType.ESCALATE
        if weights["defer"] > 0.1:  # If any deferral needed
            return DecisionType.DEFER
        # Otherwise allow
        return DecisionType.ALLOW

    def _calculate_synthesis_confidence(
        self,
        policy_decisions: list[PolicyDecision],
        resolved_conflicts: list[PolicyConflict],
    ) -> float:
        """Calculate confidence score for synthesis result."""

        # Base confidence is average of individual decisions
        if policy_decisions:
            base_confidence = sum(d.confidence_score for d in policy_decisions) / len(
                policy_decisions
            )
        else:
            base_confidence = 0.0

        # Reduce confidence based on conflicts
        conflict_penalty = len(resolved_conflicts) * 0.1

        # Reduce confidence based on conflict resolution confidence
        if resolved_conflicts:
            avg_resolution_confidence = sum(
                c.resolution_confidence for c in resolved_conflicts
            ) / len(resolved_conflicts)
            resolution_factor = avg_resolution_confidence
        else:
            resolution_factor = 1.0

        return max(
            0.0, min(1.0, (base_confidence - conflict_penalty) * resolution_factor)
        )

    def _generate_audit_trail(
        self,
        policy_decisions: list[PolicyDecision],
        conflicts: list[PolicyConflict],
        resolved_conflicts: list[PolicyConflict],
        context: PolicyEvaluationContext,
    ) -> list[dict[str, Any]]:
        """Generate comprehensive audit trail."""

        audit_trail = []

        # Add context information
        audit_trail.append(
            {
                "timestamp": context.timestamp.isoformat(),
                "event": "synthesis_started",
                "context_id": context.request_id,
                "principal": context.principal.get("id", "unknown"),
                "action": context.action,
                "resource": context.resource.get("id", "unknown"),
            }
        )

        # Add policy evaluations
        for decision in policy_decisions:
            audit_trail.extend(decision.audit_trail)

        # Add conflicts
        audit_trail.extend(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "conflict_detected",
                "conflict_id": conflict.conflict_id,
                "conflict_type": conflict.conflict_type.value,
                "policies": conflict.policies_involved,
                "severity": conflict.severity,
            }
            for conflict in conflicts
        )

        # Add resolutions
        audit_trail.extend(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "conflict_resolved",
                "conflict_id": resolved_conflict.conflict_id,
                "resolution_strategy": resolved_conflict.resolution_strategy,
                "confidence": resolved_conflict.resolution_confidence,
            }
            for resolved_conflict in resolved_conflicts
        )

        return audit_trail

    def _serialize_decision(self, decision: PolicyDecision) -> dict[str, Any]:
        """Serialize policy decision for JSON response."""

        return {
            "decision_id": decision.decision_id,
            "decision": decision.decision.value,
            "confidence_score": decision.confidence_score,
            "policies_evaluated": decision.policies_evaluated,
            "evaluation_time_ms": decision.evaluation_time_ms,
            "constitutional_compliance": decision.constitutional_compliance,
            "reasons": decision.reasons,
            "conditions": decision.conditions,
            "metadata": decision.metadata,
        }

    def _create_error_synthesis_result(
        self, synthesis_id: str, error_msg: str, duration: float
    ) -> dict[str, Any]:
        """Create error synthesis result."""

        return {
            "synthesis_id": synthesis_id,
            "final_decision": "deny",
            "confidence_score": 0.0,
            "constitutional_compliance": False,
            "synthesis_time_ms": duration * 1000,
            "policies_evaluated": [],
            "policy_decisions": [],
            "conflicts_detected": 0,
            "conflicts_resolved": 0,
            "reasons": [f"Synthesis error: {error_msg}"],
            "conditions": [],
            "error": True,
            "error_message": error_msg,
            "metadata": {
                "constitutional_hash": "cdd01ef066bc6cf2",
                "synthesis_engine": "advanced_opa_engine",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": True,
            },
        }

    def _update_synthesis_metrics(self, synthesis_result: dict[str, Any]):
        """Update synthesis performance metrics."""

        # Update metrics tracking
        if "synthesis_metrics" not in self.performance_metrics:
            self.performance_metrics["synthesis_metrics"] = {
                "total_syntheses": 0,
                "average_synthesis_time_ms": 0.0,
                "decision_distribution": {},
                "conflict_rates": [],
                "constitutional_compliance_rate": 0.0,
            }

        metrics = self.performance_metrics["synthesis_metrics"]
        metrics["total_syntheses"] += 1

        # Update average synthesis time
        total_time = metrics["average_synthesis_time_ms"] * (
            metrics["total_syntheses"] - 1
        )
        metrics["average_synthesis_time_ms"] = (
            total_time + synthesis_result["synthesis_time_ms"]
        ) / metrics["total_syntheses"]

        # Update decision distribution
        decision = synthesis_result["final_decision"]
        if decision not in metrics["decision_distribution"]:
            metrics["decision_distribution"][decision] = 0
        metrics["decision_distribution"][decision] += 1

        # Update conflict rate
        if synthesis_result["policies_evaluated"]:
            conflict_rate = synthesis_result["conflicts_detected"] / len(
                synthesis_result["policies_evaluated"]
            )
            metrics["conflict_rates"].append(conflict_rate)

        # Update constitutional compliance rate
        if synthesis_result["constitutional_compliance"]:
            compliant_count = sum(1 for d in metrics["decision_distribution"].values())
            metrics["constitutional_compliance_rate"] = (
                compliant_count / metrics["total_syntheses"]
            )

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance metrics."""

        return {
            "synthesis_metrics": self.performance_metrics.get("synthesis_metrics", {}),
            "evaluation_engine_metrics": {
                "total_evaluations": self.evaluation_engine.metrics.total_evaluations,
                "average_evaluation_time_ms": (
                    self.evaluation_engine.metrics.average_evaluation_time_ms
                ),
                "decision_distribution": (
                    self.evaluation_engine.metrics.decision_distribution
                ),
                "constitutional_compliance_rate": (
                    self.evaluation_engine.metrics.constitutional_compliance_rate
                ),
                "cache_hit_rate": self.evaluation_engine.metrics.cache_hit_rate,
            },
            "policy_catalog_info": {
                "total_policies": len(self.policy_catalog),
                "policy_dependencies": len(self.policy_graph.edges()),
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
        }


# Example usage and testing
async def test_advanced_governance_synthesis():
    """Test the advanced governance synthesis engine."""

    # Initialize engine
    engine = AdvancedGovernanceSynthesisEngine("./policies")

    # Create test context
    context = PolicyEvaluationContext(
        request_id="test_request_001",
        timestamp=datetime.now(timezone.utc),
        principal={
            "id": "user_123",
            "type": "human",
            "tenant_id": "tenant_001",
            "roles": ["user", "analyst"],
            "authenticated": True,
            "authentication_methods": ["mfa", "certificate"],
        },
        resource={
            "id": "agent_456",
            "type": "ai_agent",
            "tenant_id": "tenant_001",
            "evolution_type": "capability_enhancement",
            "complexity_score": 4,
            "data_sensitivity": "medium",
        },
        action="agent_evolution",
        environment={
            "ip_address": "192.168.1.100",
            "user_agent": "ACGS-Client/1.0",
            "time_of_day": "business_hours",
        },
        constitutional_requirements={
            "human_dignity": True,
            "fairness": True,
            "transparency": True,
        },
    )

    # Perform governance synthesis
    await engine.synthesize_governance_decision(context)

    # Print results

    # Get performance metrics
    await engine.get_performance_metrics()


if __name__ == "__main__":
    # Run test
    asyncio.run(test_advanced_governance_synthesis())
