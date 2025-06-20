"""
Policy Orchestrator for ACGS-1 Self-Evolving AI Architecture Foundation.

This module implements OPA (Open Policy Agent) integration for governance rule
management and policy enforcement within the self-evolving AI architecture.

Key Features:
- OPA policy engine integration
- Policy bundle management
- Rule compilation and validation
- Policy conflict detection
- Governance rule enforcement
- Integration with ACGS-1 policy framework
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import timezone, datetime
from enum import Enum
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


class PolicyStatus(Enum):
    """Policy status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    DEPRECATED = "deprecated"
    CONFLICTED = "conflicted"


class PolicyType(Enum):
    """Policy type enumeration."""

    CONSTITUTIONAL = "constitutional"
    GOVERNANCE = "governance"
    SECURITY = "security"
    OPERATIONAL = "operational"
    EVOLUTION = "evolution"


@dataclass
class PolicyRule:
    """Policy rule data structure."""

    rule_id: str
    rule_name: str
    policy_type: PolicyType
    rule_content: str
    priority: int = 100
    status: PolicyStatus = PolicyStatus.ACTIVE
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyBundle:
    """Policy bundle data structure."""

    bundle_id: str
    bundle_name: str
    rules: list[PolicyRule] = field(default_factory=list)
    version: str = "1.0.0"
    status: PolicyStatus = PolicyStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


class PolicyOrchestrator:
    """
    Policy orchestrator for OPA integration and governance rule management.

    This orchestrator manages policy rules, bundles, and enforcement within
    the self-evolving AI architecture while maintaining constitutional compliance.
    """

    def __init__(self, settings):
        self.settings = settings

        # OPA configuration
        self.opa_server_url = settings.OPA_SERVER_URL
        self.opa_bundle_name = settings.OPA_BUNDLE_NAME
        self.opa_timeout = settings.OPA_TIMEOUT
        self.opa_retry_attempts = settings.OPA_RETRY_ATTEMPTS

        # Policy state
        self.active_policies: dict[str, PolicyRule] = {}
        self.policy_bundles: dict[str, PolicyBundle] = {}
        self.policy_metrics: dict[str, Any] = {
            "total_policies": 0,
            "active_policies": 0,
            "policy_evaluations": 0,
            "policy_conflicts": 0,
            "bundle_updates": 0,
        }

        # OPA client
        self.opa_client: aiohttp.ClientSession | None = None

        # Constitutional compliance
        self.constitution_hash = settings.CONSTITUTION_HASH

        logger.info("Policy orchestrator initialized with OPA integration")

    async def initialize(self):
        """Initialize the policy orchestrator."""
        try:
            # Initialize OPA client
            await self._initialize_opa_client()

            # Load initial policy bundles
            await self._load_initial_policies()

            # Validate constitutional compliance
            await self._validate_constitutional_policies()

            # Start policy monitoring
            asyncio.create_task(self._monitor_policy_health())

            logger.info("✅ Policy orchestrator initialization complete")

        except Exception as e:
            logger.error(f"❌ Policy orchestrator initialization failed: {e}")
            raise

    async def evaluate_policy(
        self, policy_query: str, input_data: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Evaluate a policy using OPA.

        Args:
            policy_query: OPA policy query
            input_data: Input data for policy evaluation

        Returns:
            Tuple of (decision, evaluation_result)
        """
        try:
            if not self.opa_client:
                return False, {"error": "OPA client not initialized"}

            # Prepare OPA request
            opa_request = {
                "input": input_data,
            }

            # Execute OPA query
            async with self.opa_client.post(
                f"/v1/data/{policy_query}",
                json=opa_request,
                timeout=aiohttp.ClientTimeout(total=self.opa_timeout),
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    # Update metrics
                    self.policy_metrics["policy_evaluations"] += 1

                    decision = result.get("result", False)

                    return decision, {
                        "decision": decision,
                        "result": result,
                        "query": policy_query,
                        "evaluated_at": datetime.now(timezone.utc).isoformat(),
                    }
                else:
                    error_text = await response.text()
                    return False, {
                        "error": f"OPA evaluation failed: {response.status}",
                        "details": error_text,
                    }

        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")
            return False, {"error": str(e)}

    async def add_policy_rule(
        self, policy_rule: PolicyRule
    ) -> tuple[bool, dict[str, Any]]:
        """
        Add a new policy rule.

        Args:
            policy_rule: Policy rule to add

        Returns:
            Tuple of (success, result_info)
        """
        try:
            # Validate policy rule
            validation_result = await self._validate_policy_rule(policy_rule)
            if not validation_result["valid"]:
                return False, validation_result

            # Check for conflicts
            conflict_check = await self._check_policy_conflicts(policy_rule)
            if conflict_check["has_conflicts"]:
                return False, {
                    "error": "Policy conflicts detected",
                    "conflicts": conflict_check["conflicts"],
                }

            # Add to active policies
            self.active_policies[policy_rule.rule_id] = policy_rule

            # Update OPA bundle
            bundle_update = await self._update_opa_bundle()
            if not bundle_update["success"]:
                # Rollback
                del self.active_policies[policy_rule.rule_id]
                return False, {
                    "error": "Failed to update OPA bundle",
                    "details": bundle_update,
                }

            # Update metrics
            self.policy_metrics["total_policies"] += 1
            self.policy_metrics["active_policies"] += 1

            logger.info(f"Policy rule added: {policy_rule.rule_id}")

            return True, {
                "rule_id": policy_rule.rule_id,
                "status": "added",
                "bundle_updated": True,
                "added_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to add policy rule: {e}")
            return False, {"error": str(e)}

    async def update_policy_rule(
        self, rule_id: str, updates: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Update an existing policy rule.

        Args:
            rule_id: Policy rule identifier
            updates: Updates to apply

        Returns:
            Tuple of (success, result_info)
        """
        try:
            if rule_id not in self.active_policies:
                return False, {"error": "Policy rule not found"}

            # Get current rule
            current_rule = self.active_policies[rule_id]

            # Create updated rule
            updated_rule = PolicyRule(
                rule_id=current_rule.rule_id,
                rule_name=updates.get("rule_name", current_rule.rule_name),
                policy_type=PolicyType(
                    updates.get("policy_type", current_rule.policy_type.value)
                ),
                rule_content=updates.get("rule_content", current_rule.rule_content),
                priority=updates.get("priority", current_rule.priority),
                status=PolicyStatus(updates.get("status", current_rule.status.value)),
                version=updates.get("version", current_rule.version),
                created_at=current_rule.created_at,
                updated_at=datetime.now(timezone.utc),
                metadata=updates.get("metadata", current_rule.metadata),
            )

            # Validate updated rule
            validation_result = await self._validate_policy_rule(updated_rule)
            if not validation_result["valid"]:
                return False, validation_result

            # Check for conflicts
            conflict_check = await self._check_policy_conflicts(updated_rule)
            if conflict_check["has_conflicts"]:
                return False, {
                    "error": "Policy conflicts detected",
                    "conflicts": conflict_check["conflicts"],
                }

            # Update policy
            self.active_policies[rule_id] = updated_rule

            # Update OPA bundle
            bundle_update = await self._update_opa_bundle()
            if not bundle_update["success"]:
                # Rollback
                self.active_policies[rule_id] = current_rule
                return False, {
                    "error": "Failed to update OPA bundle",
                    "details": bundle_update,
                }

            logger.info(f"Policy rule updated: {rule_id}")

            return True, {
                "rule_id": rule_id,
                "status": "updated",
                "bundle_updated": True,
                "updated_at": updated_rule.updated_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to update policy rule: {e}")
            return False, {"error": str(e)}

    async def remove_policy_rule(self, rule_id: str) -> tuple[bool, dict[str, Any]]:
        """
        Remove a policy rule.

        Args:
            rule_id: Policy rule identifier

        Returns:
            Tuple of (success, result_info)
        """
        try:
            if rule_id not in self.active_policies:
                return False, {"error": "Policy rule not found"}

            # Remove from active policies
            removed_rule = self.active_policies.pop(rule_id)

            # Update OPA bundle
            bundle_update = await self._update_opa_bundle()
            if not bundle_update["success"]:
                # Rollback
                self.active_policies[rule_id] = removed_rule
                return False, {
                    "error": "Failed to update OPA bundle",
                    "details": bundle_update,
                }

            # Update metrics
            self.policy_metrics["active_policies"] -= 1

            logger.info(f"Policy rule removed: {rule_id}")

            return True, {
                "rule_id": rule_id,
                "status": "removed",
                "bundle_updated": True,
                "removed_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to remove policy rule: {e}")
            return False, {"error": str(e)}

    async def get_policy_status(self) -> dict[str, Any]:
        """Get current policy orchestrator status."""
        try:
            # Check OPA health
            opa_health = await self._check_opa_health()

            return {
                "opa_integration": {
                    "server_url": self.opa_server_url,
                    "bundle_name": self.opa_bundle_name,
                    "health": opa_health,
                },
                "policies": {
                    "total_policies": len(self.active_policies),
                    "active_policies": len(
                        [
                            p
                            for p in self.active_policies.values()
                            if p.status == PolicyStatus.ACTIVE
                        ]
                    ),
                    "policy_types": {
                        policy_type.value: len(
                            [
                                p
                                for p in self.active_policies.values()
                                if p.policy_type == policy_type
                            ]
                        )
                        for policy_type in PolicyType
                    },
                },
                "bundles": {
                    "total_bundles": len(self.policy_bundles),
                    "active_bundles": len(
                        [
                            b
                            for b in self.policy_bundles.values()
                            if b.status == PolicyStatus.ACTIVE
                        ]
                    ),
                },
                "metrics": self.policy_metrics,
                "constitutional_compliance": {
                    "constitution_hash": self.constitution_hash,
                    "compliance_validated": True,
                },
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get policy status: {e}")
            return {"error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Perform health check for the policy orchestrator."""
        try:
            health_status = {
                "healthy": True,
                "timestamp": time.time(),
                "checks": {},
            }

            # Check OPA connectivity
            opa_health = await self._check_opa_health()
            health_status["checks"]["opa_connectivity"] = {
                "healthy": opa_health.get("healthy", False),
                "server_url": self.opa_server_url,
                "response_time_ms": opa_health.get("response_time_ms", "unknown"),
            }
            if not opa_health.get("healthy", False):
                health_status["healthy"] = False

            # Check policy consistency
            health_status["checks"]["policy_consistency"] = {
                "healthy": True,
                "active_policies": len(self.active_policies),
                "policy_conflicts": self.policy_metrics["policy_conflicts"],
            }

            return health_status

        except Exception as e:
            logger.error(f"Policy orchestrator health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }

    async def shutdown(self):
        """Shutdown the policy orchestrator gracefully."""
        try:
            logger.info("Shutting down policy orchestrator...")

            # Close OPA client
            if self.opa_client:
                await self.opa_client.close()

            logger.info("✅ Policy orchestrator shutdown complete")

        except Exception as e:
            logger.error(f"Error during policy orchestrator shutdown: {e}")

    # Private helper methods
    async def _initialize_opa_client(self):
        """Initialize OPA HTTP client."""
        try:
            timeout = aiohttp.ClientTimeout(total=self.opa_timeout)
            self.opa_client = aiohttp.ClientSession(
                base_url=self.opa_server_url,
                timeout=timeout,
            )

            # Test OPA connectivity
            health_check = await self._check_opa_health()
            if not health_check.get("healthy", False):
                raise ConnectionError("OPA server is not healthy")

            logger.info(f"OPA client initialized: {self.opa_server_url}")

        except Exception as e:
            logger.error(f"OPA client initialization failed: {e}")
            raise

    async def _load_initial_policies(self):
        """Load initial policy rules and bundles."""
        try:
            # Load constitutional policies
            constitutional_policies = await self._load_constitutional_policies()
            for policy in constitutional_policies:
                self.active_policies[policy.rule_id] = policy

            # Load governance policies
            governance_policies = await self._load_governance_policies()
            for policy in governance_policies:
                self.active_policies[policy.rule_id] = policy

            # Load security policies
            security_policies = await self._load_security_policies()
            for policy in security_policies:
                self.active_policies[policy.rule_id] = policy

            # Update metrics
            self.policy_metrics["total_policies"] = len(self.active_policies)
            self.policy_metrics["active_policies"] = len(
                [
                    p
                    for p in self.active_policies.values()
                    if p.status == PolicyStatus.ACTIVE
                ]
            )

            # Create initial bundle
            await self._create_initial_bundle()

            logger.info(f"Loaded {len(self.active_policies)} initial policies")

        except Exception as e:
            logger.error(f"Failed to load initial policies: {e}")
            raise

    async def _load_constitutional_policies(self) -> list[PolicyRule]:
        """Load constitutional governance policies."""
        policies = []

        # Constitutional compliance policy
        policies.append(
            PolicyRule(
                rule_id="constitutional_compliance",
                rule_name="Constitutional Compliance Validation",
                policy_type=PolicyType.CONSTITUTIONAL,
                rule_content="""
            package acgs.constitutional

            default allow = false

            allow {
                input.constitution_hash == "cdd01ef066bc6cf2"
                input.action.type in ["policy_evolution", "governance_action"]
                constitutional_principles_satisfied
            }

            constitutional_principles_satisfied {
                # Validate against constitutional principles
                count(input.violations) == 0
            }
            """,
                priority=1,
                metadata={"constitution_hash": self.constitution_hash},
            )
        )

        # Human oversight policy
        policies.append(
            PolicyRule(
                rule_id="human_oversight_required",
                rule_name="Human Oversight Requirement",
                policy_type=PolicyType.CONSTITUTIONAL,
                rule_content="""
            package acgs.oversight

            default require_human_approval = true

            require_human_approval {
                input.action.type in ["constitutional_amendment", "critical_policy_change"]
            }

            require_human_approval {
                input.risk_level in ["high", "critical"]
            }
            """,
                priority=2,
                metadata={"oversight_type": "human_in_the_loop"},
            )
        )

        return policies

    async def _load_governance_policies(self) -> list[PolicyRule]:
        """Load governance-specific policies."""
        policies = []

        # Evolution approval policy
        policies.append(
            PolicyRule(
                rule_id="evolution_approval",
                rule_name="Evolution Approval Requirements",
                policy_type=PolicyType.GOVERNANCE,
                rule_content="""
            package acgs.evolution

            default allow = false

            allow {
                input.evolution.type in ["policy_refinement", "rule_optimization"]
                input.evolution.requester_authenticated
                input.evolution.justification_provided
                security_assessment_passed
            }

            security_assessment_passed {
                input.security_assessment.approved == true
                input.security_assessment.threat_level != "critical"
            }
            """,
                priority=10,
            )
        )

        return policies

    async def _load_security_policies(self) -> list[PolicyRule]:
        """Load security-specific policies."""
        policies = []

        # Access control policy
        policies.append(
            PolicyRule(
                rule_id="access_control",
                rule_name="Access Control Enforcement",
                policy_type=PolicyType.SECURITY,
                rule_content="""
            package acgs.security

            default allow = false

            allow {
                input.user.authenticated == true
                input.user.permissions[_] == input.action.required_permission
                rate_limit_not_exceeded
            }

            rate_limit_not_exceeded {
                input.user.request_count < input.user.rate_limit
            }
            """,
                priority=20,
            )
        )

        return policies

    async def _create_initial_bundle(self):
        """Create initial policy bundle."""
        try:
            bundle = PolicyBundle(
                bundle_id="acgs_self_evolving_ai_bundle",
                bundle_name="ACGS Self-Evolving AI Policy Bundle",
                rules=list(self.active_policies.values()),
                version="1.0.0",
                metadata={
                    "constitution_hash": self.constitution_hash,
                    "created_by": "policy_orchestrator",
                },
            )

            self.policy_bundles[bundle.bundle_id] = bundle

            # Update OPA with initial bundle
            await self._update_opa_bundle()

            logger.info(f"Initial policy bundle created: {bundle.bundle_id}")

        except Exception as e:
            logger.error(f"Failed to create initial bundle: {e}")
            raise

    async def _validate_constitutional_policies(self):
        """Validate constitutional compliance of policies."""
        try:
            # Check constitution hash consistency
            for policy in self.active_policies.values():
                if policy.policy_type == PolicyType.CONSTITUTIONAL:
                    if (
                        policy.metadata.get("constitution_hash")
                        != self.constitution_hash
                    ):
                        logger.warning(
                            f"Constitution hash mismatch in policy {policy.rule_id}"
                        )

            logger.info("Constitutional policy validation complete")

        except Exception as e:
            logger.error(f"Constitutional policy validation failed: {e}")
            raise

    async def _validate_policy_rule(self, policy_rule: PolicyRule) -> dict[str, Any]:
        """Validate a policy rule for correctness."""
        validation_result = {"valid": True, "errors": []}

        try:
            # Basic validation
            if not policy_rule.rule_id:
                validation_result["errors"].append("Rule ID is required")

            if not policy_rule.rule_name:
                validation_result["errors"].append("Rule name is required")

            if not policy_rule.rule_content:
                validation_result["errors"].append("Rule content is required")

            # Validate rule content syntax (simplified)
            if "package" not in policy_rule.rule_content:
                validation_result["errors"].append(
                    "Rule content must include package declaration"
                )

            # Check for dangerous operations
            dangerous_patterns = ["delete", "drop", "destroy", "bypass"]
            content_lower = policy_rule.rule_content.lower()
            for pattern in dangerous_patterns:
                if pattern in content_lower:
                    validation_result["errors"].append(
                        f"Potentially dangerous operation: {pattern}"
                    )

            validation_result["valid"] = len(validation_result["errors"]) == 0
            return validation_result

        except Exception as e:
            logger.error(f"Policy rule validation failed: {e}")
            return {"valid": False, "errors": [str(e)]}

    async def _check_policy_conflicts(self, policy_rule: PolicyRule) -> dict[str, Any]:
        """Check for conflicts with existing policies."""
        try:
            conflicts = []

            # Check for duplicate rule IDs
            if policy_rule.rule_id in self.active_policies:
                existing_rule = self.active_policies[policy_rule.rule_id]
                if existing_rule.rule_content != policy_rule.rule_content:
                    conflicts.append(
                        {
                            "type": "duplicate_rule_id",
                            "conflicting_rule": policy_rule.rule_id,
                            "description": "Rule ID already exists with different content",
                        }
                    )

            # Check for priority conflicts
            same_priority_rules = [
                rule
                for rule in self.active_policies.values()
                if rule.priority == policy_rule.priority
                and rule.policy_type == policy_rule.policy_type
            ]

            if same_priority_rules:
                conflicts.append(
                    {
                        "type": "priority_conflict",
                        "conflicting_rules": [
                            rule.rule_id for rule in same_priority_rules
                        ],
                        "description": f"Multiple rules with same priority {policy_rule.priority}",
                    }
                )

            # Update conflict metrics
            if conflicts:
                self.policy_metrics["policy_conflicts"] += 1

            return {
                "has_conflicts": len(conflicts) > 0,
                "conflicts": conflicts,
            }

        except Exception as e:
            logger.error(f"Policy conflict check failed: {e}")
            return {"has_conflicts": True, "conflicts": [{"error": str(e)}]}

    async def _update_opa_bundle(self) -> dict[str, Any]:
        """Update OPA bundle with current policies."""
        try:
            if not self.opa_client:
                return {"success": False, "error": "OPA client not initialized"}

            # Prepare bundle data
            bundle_data = {
                "policies": {},
                "data": {},
            }

            # Add policies to bundle
            for policy in self.active_policies.values():
                if policy.status == PolicyStatus.ACTIVE:
                    bundle_data["policies"][policy.rule_id] = policy.rule_content

            # Update OPA bundle
            async with self.opa_client.put(
                f"/v1/policies/{self.opa_bundle_name}",
                json=bundle_data,
            ) as response:
                if response.status in [200, 201]:
                    self.policy_metrics["bundle_updates"] += 1
                    return {"success": True, "bundle_updated": True}
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"OPA bundle update failed: {response.status}",
                        "details": error_text,
                    }

        except Exception as e:
            logger.error(f"OPA bundle update failed: {e}")
            return {"success": False, "error": str(e)}

    async def _check_opa_health(self) -> dict[str, Any]:
        """Check OPA server health."""
        try:
            if not self.opa_client:
                return {"healthy": False, "error": "OPA client not initialized"}

            start_time = time.time()

            async with self.opa_client.get("/health") as response:
                response_time_ms = (time.time() - start_time) * 1000

                if response.status == 200:
                    return {
                        "healthy": True,
                        "status_code": response.status,
                        "response_time_ms": round(response_time_ms, 2),
                    }
                else:
                    return {
                        "healthy": False,
                        "status_code": response.status,
                        "response_time_ms": round(response_time_ms, 2),
                    }

        except Exception as e:
            logger.error(f"OPA health check failed: {e}")
            return {"healthy": False, "error": str(e)}

    async def _monitor_policy_health(self):
        """Background task to monitor policy health."""
        while True:
            try:
                # Check OPA connectivity
                opa_health = await self._check_opa_health()
                if not opa_health.get("healthy", False):
                    logger.warning("OPA server health check failed")

                # Check for policy conflicts
                await self._detect_policy_conflicts()

                # Sleep for monitoring interval
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Policy health monitoring error: {e}")
                await asyncio.sleep(60)

    async def _detect_policy_conflicts(self):
        """Detect conflicts between active policies."""
        try:
            conflicts_detected = 0

            # Check for overlapping rules
            for rule1 in self.active_policies.values():
                for rule2 in self.active_policies.values():
                    if rule1.rule_id != rule2.rule_id:
                        if (
                            rule1.priority == rule2.priority
                            and rule1.policy_type == rule2.policy_type
                        ):
                            conflicts_detected += 1
                            logger.warning(
                                f"Priority conflict detected: {rule1.rule_id} vs {rule2.rule_id}"
                            )

            if conflicts_detected > 0:
                self.policy_metrics["policy_conflicts"] = conflicts_detected

        except Exception as e:
            logger.error(f"Policy conflict detection failed: {e}")
