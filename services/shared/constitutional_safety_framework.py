"""
Constitutional Safety Framework for ACGS.

This module provides constitutional compliance validation and safety checks
for multi-agent operations in the ACGS system.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class SafetyLevel(str, Enum):
    """Safety levels for constitutional compliance"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class ComplianceResult(BaseModel):
    """Result of a constitutional compliance check"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    is_compliant: bool
    safety_level: SafetyLevel
    violations: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = "cdd01ef066bc6cf2"  # ACGS constitutional compliance hash


class ConstitutionalRule(BaseModel):
    """Represents a constitutional rule for validation"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    rule_type: str  # 'ethical', 'legal', 'operational', 'security'
    severity: SafetyLevel
    validation_function: str  # Name of validation function
    enabled: bool = True


class ConstitutionalSafetyValidator:
    """
    Constitutional Safety Validator for ACGS multi-agent operations.

    Validates agent actions, decisions, and communications against
    constitutional principles and safety requirements.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules: dict[str, ConstitutionalRule] = {}
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default constitutional rules"""
        default_rules = [
            ConstitutionalRule(
                name="human_oversight_required",
                description="Critical decisions must have human oversight",
                rule_type="ethical",
                severity=SafetyLevel.CRITICAL,
                validation_function="validate_human_oversight",
            ),
            ConstitutionalRule(
                name="data_privacy_protection",
                description="Personal data must be protected",
                rule_type="legal",
                severity=SafetyLevel.HIGH,
                validation_function="validate_data_privacy",
            ),
            ConstitutionalRule(
                name="transparent_decision_making",
                description="Decisions must be explainable and transparent",
                rule_type="ethical",
                severity=SafetyLevel.MEDIUM,
                validation_function="validate_transparency",
            ),
            ConstitutionalRule(
                name="resource_usage_limits",
                description="Resource usage must be within defined limits",
                rule_type="operational",
                severity=SafetyLevel.MEDIUM,
                validation_function="validate_resource_usage",
            ),
            ConstitutionalRule(
                name="security_compliance",
                description="All operations must meet security standards",
                rule_type="security",
                severity=SafetyLevel.HIGH,
                validation_function="validate_security_compliance",
            ),
        ]

        for rule in default_rules:
            self.rules[rule.id] = rule

    async def validate_action(
        self, action_data: dict[str, Any], context: Optional[dict[str, Any]] = None
    ) -> ComplianceResult:
        """Validate an agent action against constitutional rules"""
        violations = []
        recommendations = []
        min_confidence = 1.0
        highest_severity = SafetyLevel.INFORMATIONAL

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            try:
                # Validate against this rule
                rule_result = await self._validate_against_rule(
                    rule, action_data, context
                )

                if not rule_result["is_compliant"]:
                    violations.extend(rule_result["violations"])
                    if self._is_higher_severity(rule.severity, highest_severity):
                        highest_severity = rule.severity

                recommendations.extend(rule_result.get("recommendations", []))
                min_confidence = min(min_confidence, rule_result.get("confidence", 1.0))

            except Exception as e:
                self.logger.error(f"Error validating rule {rule.name}: {e}")
                violations.append(f"Validation error for rule {rule.name}")
                highest_severity = SafetyLevel.HIGH

        is_compliant = len(violations) == 0

        return ComplianceResult(
            is_compliant=is_compliant,
            safety_level=highest_severity,
            violations=violations,
            recommendations=recommendations,
            confidence_score=min_confidence,
            constitutional_hash=self.constitutional_hash,
        )

    async def _validate_against_rule(
        self,
        rule: ConstitutionalRule,
        action_data: dict[str, Any],
        context: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Validate action data against a specific rule"""
        # This is a simplified implementation - in practice, each rule would have
        # its own validation logic

        if rule.validation_function == "validate_human_oversight":
            return await self._validate_human_oversight(action_data, context)
        elif rule.validation_function == "validate_data_privacy":
            return await self._validate_data_privacy(action_data, context)
        elif rule.validation_function == "validate_transparency":
            return await self._validate_transparency(action_data, context)
        elif rule.validation_function == "validate_resource_usage":
            return await self._validate_resource_usage(action_data, context)
        elif rule.validation_function == "validate_security_compliance":
            return await self._validate_security_compliance(action_data, context)
        else:
            return {
                "is_compliant": True,
                "violations": [],
                "recommendations": [],
                "confidence": 1.0,
            }

    async def _validate_human_oversight(
        self, action_data: dict[str, Any], context: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Validate human oversight requirements"""
        # Check if action requires human oversight
        requires_oversight = action_data.get("requires_human_oversight", False)
        has_oversight = action_data.get("human_oversight_provided", False)

        if requires_oversight and not has_oversight:
            return {
                "is_compliant": False,
                "violations": [
                    "Critical action requires human oversight but none provided"
                ],
                "recommendations": ["Obtain human oversight before proceeding"],
                "confidence": 0.95,
            }

        return {
            "is_compliant": True,
            "violations": [],
            "recommendations": [],
            "confidence": 1.0,
        }

    async def _validate_data_privacy(
        self, action_data: dict[str, Any], context: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Validate data privacy requirements"""
        # Check for personal data handling
        handles_personal_data = action_data.get("handles_personal_data", False)
        has_privacy_controls = action_data.get("privacy_controls_enabled", True)

        if handles_personal_data and not has_privacy_controls:
            return {
                "is_compliant": False,
                "violations": ["Personal data handling without privacy controls"],
                "recommendations": ["Enable privacy controls for personal data"],
                "confidence": 0.9,
            }

        return {
            "is_compliant": True,
            "violations": [],
            "recommendations": [],
            "confidence": 1.0,
        }

    async def _validate_transparency(
        self, action_data: dict[str, Any], context: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Validate transparency requirements"""
        # Check if decision is explainable
        has_explanation = "explanation" in action_data or "reasoning" in action_data

        if not has_explanation:
            return {
                "is_compliant": False,
                "violations": ["Decision lacks explanation or reasoning"],
                "recommendations": ["Provide explanation for decision"],
                "confidence": 0.8,
            }

        return {
            "is_compliant": True,
            "violations": [],
            "recommendations": [],
            "confidence": 1.0,
        }

    async def _validate_resource_usage(
        self, action_data: dict[str, Any], context: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Validate resource usage limits"""
        # Check resource usage
        cpu_usage = action_data.get("estimated_cpu_usage", 0)
        memory_usage = action_data.get("estimated_memory_usage", 0)

        violations = []
        if cpu_usage > 80:  # 80% CPU limit
            violations.append(f"CPU usage {cpu_usage}% exceeds limit")
        if memory_usage > 85:  # 85% memory limit
            violations.append(f"Memory usage {memory_usage}% exceeds limit")

        return {
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": ["Optimize resource usage"] if violations else [],
            "confidence": 0.9,
        }

    async def _validate_security_compliance(
        self, action_data: dict[str, Any], context: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Validate security compliance"""
        # Check security requirements
        has_authentication = action_data.get("authenticated", True)
        has_authorization = action_data.get("authorized", True)
        uses_encryption = action_data.get("encrypted", True)

        violations = []
        if not has_authentication:
            violations.append("Action not authenticated")
        if not has_authorization:
            violations.append("Action not authorized")
        if not uses_encryption:
            violations.append("Action not using encryption")

        return {
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": (
                ["Ensure proper security controls"] if violations else []
            ),
            "confidence": 0.95,
        }

    def _is_higher_severity(
        self, severity1: SafetyLevel, severity2: SafetyLevel
    ) -> bool:
        """Check if severity1 is higher than severity2"""
        severity_order = {
            SafetyLevel.INFORMATIONAL: 0,
            SafetyLevel.LOW: 1,
            SafetyLevel.MEDIUM: 2,
            SafetyLevel.HIGH: 3,
            SafetyLevel.CRITICAL: 4,
        }
        return severity_order[severity1] > severity_order[severity2]

    def add_rule(self, rule: ConstitutionalRule) -> None:
        """Add a new constitutional rule"""
        self.rules[rule.id] = rule
        self.logger.info(f"Added constitutional rule: {rule.name}")

    def remove_rule(self, rule_id: str) -> None:
        """Remove a constitutional rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.logger.info(f"Removed constitutional rule: {rule_id}")

    def get_rules(self) -> list[ConstitutionalRule]:
        """Get all constitutional rules"""
        return list(self.rules.values())

    def get_constitutional_hash(self) -> str:
        """Get the constitutional compliance hash"""
        return self.constitutional_hash


class ConstitutionalSafetyFramework:
    """
    High-level Constitutional Safety Framework for ACGS.

    This class provides a comprehensive framework for constitutional compliance
    across all ACGS operations, integrating multiple validators and providing
    centralized safety management.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = ConstitutionalSafetyValidator()
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.compliance_cache: dict[str, ComplianceResult] = {}
        self.cache_ttl = timedelta(minutes=10)

    async def validate_operation(
        self,
        operation_type: str,
        operation_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> ComplianceResult:
        """
        Validate any ACGS operation for constitutional compliance.

        Args:
            operation_type: Type of operation (e.g., 'agent_action', 'policy_decision')
            operation_data: Data describing the operation
            context: Additional context for validation

        Returns:
            ComplianceResult indicating compliance status
        """
        # Check cache first
        cache_key = self._generate_cache_key(operation_type, operation_data)
        if cache_key in self.compliance_cache:
            cached_result = self.compliance_cache[cache_key]
            if datetime.utcnow() - cached_result.timestamp < self.cache_ttl:
                return cached_result

        # Perform validation
        result = await self.validator.validate_action(operation_data, context)

        # Cache result
        self.compliance_cache[cache_key] = result

        # Log result
        if not result.is_compliant:
            self.logger.warning(
                f"Constitutional compliance violation in {operation_type}:"
                f" {result.violations}"
            )

        return result

    def _generate_cache_key(
        self, operation_type: str, operation_data: dict[str, Any]
    ) -> str:
        """Generate cache key for operation validation"""
        import hashlib

        data_str = f"{operation_type}:{sorted(operation_data.items())!s}"
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def get_framework_status(self) -> dict[str, Any]:
        """Get current framework status and statistics"""
        return {
            "constitutional_hash": self.constitutional_hash,
            "active_rules": len(self.validator.get_rules()),
            "cache_entries": len(self.compliance_cache),
            "validator_status": "active",
        }
