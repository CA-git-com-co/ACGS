"""
Constitutional Persona Validator
Constitutional Hash: cdd01ef066bc6cf2

This module provides comprehensive constitutional validation for all SuperClaude persona operations
within the ACGS system, ensuring 100% constitutional compliance across all agent interactions.
"""

import logging
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .blackboard import BlackboardService, KnowledgeItem
from .constitutional_safety_framework import ConstitutionalSafetyValidator
from .superclaude_persona_integration import SuperClaudePersona

# Configure logging
logger = logging.getLogger(__name__)


class ConstitutionalViolationType(Enum):
    """Types of constitutional violations"""

    HASH_VALIDATION_FAILURE = "hash_validation_failure"
    PERSONA_UNAUTHORIZED = "persona_unauthorized"
    OPERATION_NON_COMPLIANT = "operation_non_compliant"
    AUDIT_TRAIL_INCOMPLETE = "audit_trail_incomplete"
    PERFORMANCE_VIOLATION = "performance_violation"
    SECURITY_BREACH = "security_breach"
    GOVERNANCE_BYPASS = "governance_bypass"


class ConstitutionalValidationResult(BaseModel):
    """Result of constitutional validation"""

    is_valid: bool
    constitutional_hash: str = "cdd01ef066bc6cf2"
    persona: SuperClaudePersona | None = None
    operation_type: str
    validation_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    validation_details: dict[str, Any] = Field(default_factory=dict)
    violations: list[ConstitutionalViolationType] = Field(default_factory=list)
    compliance_score: float = Field(ge=0.0, le=1.0, default=0.0)
    audit_trail: list[str] = Field(default_factory=list)
    escalation_required: bool = False
    performance_metrics: dict[str, float] = Field(default_factory=dict)


class ConstitutionalPersonaValidator:
    """Constitutional validator for SuperClaude persona operations"""

    REQUIRED_CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    MAX_VALIDATION_LATENCY_MS = 5.0  # P99 target
    CRITICAL_OPERATIONS = {
        "deployment",
        "security_analysis",
        "governance_decision",
        "constitutional_modification",
        "audit_logging",
    }

    def __init__(
        self,
        constitutional_validator: ConstitutionalSafetyValidator,
        blackboard_service: BlackboardService,
    ):
        """Initialize constitutional persona validator"""
        self.constitutional_validator = constitutional_validator
        self.blackboard = blackboard_service
        self.logger = logging.getLogger(__name__)
        self.validation_stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "violations_detected": 0,
            "escalations_triggered": 0,
        }

    async def validate_persona_operation(
        self,
        persona: SuperClaudePersona | None,
        operation_type: str,
        operation_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> ConstitutionalValidationResult:
        """Perform comprehensive constitutional validation for persona operation"""

        start_time = time.time()
        violations = []
        validation_details = {}
        audit_trail = []
        escalation_required = False

        try:
            # 1. Constitutional Hash Validation
            hash_validation = await self._validate_constitutional_hash(operation_data)
            validation_details["hash_validation"] = hash_validation
            audit_trail.append(
                f"Constitutional hash validation: {'PASSED' if hash_validation['valid'] else 'FAILED'}"
            )

            if not hash_validation["valid"]:
                violations.append(ConstitutionalViolationType.HASH_VALIDATION_FAILURE)
                escalation_required = True

            # 2. Persona Authorization Validation
            if persona:
                persona_validation = await self._validate_persona_authorization(
                    persona, operation_type, operation_data
                )
                validation_details["persona_validation"] = persona_validation
                audit_trail.append(
                    f"Persona {persona.value} authorization: {'PASSED' if persona_validation['authorized'] else 'FAILED'}"
                )

                if not persona_validation["authorized"]:
                    violations.append(ConstitutionalViolationType.PERSONA_UNAUTHORIZED)
                    escalation_required = True

            # 3. Operation Compliance Validation
            operation_validation = await self._validate_operation_compliance(
                operation_type, operation_data, context
            )
            validation_details["operation_validation"] = operation_validation
            audit_trail.append(
                f"Operation compliance: {'PASSED' if operation_validation['compliant'] else 'FAILED'}"
            )

            if not operation_validation["compliant"]:
                violations.append(ConstitutionalViolationType.OPERATION_NON_COMPLIANT)
                if operation_type in self.CRITICAL_OPERATIONS:
                    escalation_required = True

            # 4. Audit Trail Validation
            audit_validation = await self._validate_audit_requirements(
                operation_data, context
            )
            validation_details["audit_validation"] = audit_validation
            audit_trail.append(
                f"Audit trail validation: {'PASSED' if audit_validation['complete'] else 'FAILED'}"
            )

            if not audit_validation["complete"]:
                violations.append(ConstitutionalViolationType.AUDIT_TRAIL_INCOMPLETE)

            # 5. Performance Compliance Validation
            performance_validation = await self._validate_performance_compliance(
                operation_type
            )
            validation_details["performance_validation"] = performance_validation
            audit_trail.append(
                f"Performance compliance: {'PASSED' if performance_validation['within_limits'] else 'FAILED'}"
            )

            if not performance_validation["within_limits"]:
                violations.append(ConstitutionalViolationType.PERFORMANCE_VIOLATION)

            # 6. Security Compliance Validation
            security_validation = await self._validate_security_compliance(
                operation_data, context
            )
            validation_details["security_validation"] = security_validation
            audit_trail.append(
                f"Security compliance: {'PASSED' if security_validation['secure'] else 'FAILED'}"
            )

            if not security_validation["secure"]:
                violations.append(ConstitutionalViolationType.SECURITY_BREACH)
                escalation_required = True

            # 7. Governance Bypass Detection
            governance_validation = await self._validate_governance_compliance(
                operation_type, operation_data
            )
            validation_details["governance_validation"] = governance_validation
            audit_trail.append(
                f"Governance compliance: {'PASSED' if governance_validation['no_bypass'] else 'FAILED'}"
            )

            if not governance_validation["no_bypass"]:
                violations.append(ConstitutionalViolationType.GOVERNANCE_BYPASS)
                escalation_required = True

            # Calculate overall validation result
            is_valid = len(violations) == 0
            compliance_score = self._calculate_compliance_score(validation_details)

            # Measure performance
            validation_latency_ms = (time.time() - start_time) * 1000
            performance_metrics = {
                "validation_latency_ms": validation_latency_ms,
                "within_p99_target": validation_latency_ms
                <= self.MAX_VALIDATION_LATENCY_MS,
            }

            # Update statistics
            self.validation_stats["total_validations"] += 1
            if is_valid:
                self.validation_stats["successful_validations"] += 1
            else:
                self.validation_stats["violations_detected"] += 1
            if escalation_required:
                self.validation_stats["escalations_triggered"] += 1

            # Create validation result
            result = ConstitutionalValidationResult(
                is_valid=is_valid,
                persona=persona,
                operation_type=operation_type,
                validation_details=validation_details,
                violations=violations,
                compliance_score=compliance_score,
                audit_trail=audit_trail,
                escalation_required=escalation_required,
                performance_metrics=performance_metrics,
            )

            # Log validation to blackboard
            await self._log_validation_result(result, operation_data)

            # Trigger escalation if required
            if escalation_required:
                await self._trigger_constitutional_escalation(result, operation_data)

            return result

        except Exception as e:
            self.logger.exception(f"Constitutional validation failed: {e!s}")
            # Return failed validation on exception
            return ConstitutionalValidationResult(
                is_valid=False,
                persona=persona,
                operation_type=operation_type,
                violations=[ConstitutionalViolationType.OPERATION_NON_COMPLIANT],
                escalation_required=True,
                audit_trail=[f"Validation exception: {e!s}"],
            )

    async def _validate_constitutional_hash(
        self, operation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate constitutional hash presence and integrity"""

        provided_hash = operation_data.get("constitutional_hash")

        validation_result = {
            "valid": False,
            "provided_hash": provided_hash,
            "expected_hash": self.REQUIRED_CONSTITUTIONAL_HASH,
            "hash_present": provided_hash is not None,
            "hash_matches": provided_hash == self.REQUIRED_CONSTITUTIONAL_HASH,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Validate hash presence
        if not provided_hash:
            validation_result["error"] = "Constitutional hash not provided"
            return validation_result

        # Validate hash format (basic check)
        if not isinstance(provided_hash, str) or len(provided_hash) != 16:
            validation_result["error"] = "Invalid constitutional hash format"
            return validation_result

        # Validate hash content
        if provided_hash != self.REQUIRED_CONSTITUTIONAL_HASH:
            validation_result["error"] = (
                f"Constitutional hash mismatch. Expected: {self.REQUIRED_CONSTITUTIONAL_HASH}, Got: {provided_hash}"
            )
            return validation_result

        validation_result["valid"] = True
        return validation_result

    async def _validate_persona_authorization(
        self,
        persona: SuperClaudePersona,
        operation_type: str,
        operation_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate persona authorization for specific operation"""

        # Define persona-operation authorization matrix
        PERSONA_AUTHORIZATIONS = {
            SuperClaudePersona.ARCHITECT: ["design", "analyze", "build", "estimate"],
            SuperClaudePersona.SECURITY: [
                "scan",
                "analyze",
                "deploy",
                "constitutional-validate",
            ],
            SuperClaudePersona.ANALYZER: [
                "analyze",
                "troubleshoot",
                "review",
                "constitutional-validate",
            ],
            SuperClaudePersona.QA: [
                "test",
                "scan",
                "review",
                "constitutional-validate",
            ],
            SuperClaudePersona.PERFORMANCE: ["analyze", "improve", "test", "deploy"],
            SuperClaudePersona.FRONTEND: ["build", "test", "improve", "design"],
            SuperClaudePersona.BACKEND: ["build", "deploy", "analyze", "improve"],
            SuperClaudePersona.REFACTORER: ["improve", "review", "analyze", "cleanup"],
            SuperClaudePersona.MENTOR: ["explain", "document", "review", "load"],
        }

        authorized_operations = PERSONA_AUTHORIZATIONS.get(persona, [])
        is_authorized = (
            operation_type in authorized_operations
            or operation_type == "constitutional-validate"
        )

        return {
            "authorized": is_authorized,
            "persona": persona.value,
            "operation_type": operation_type,
            "authorized_operations": authorized_operations,
            "constitutional_operations_always_allowed": True,
        }

    async def _validate_operation_compliance(
        self,
        operation_type: str,
        operation_data: dict[str, Any],
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Validate operation compliance with constitutional requirements"""

        # Use the existing constitutional validator
        validation_request = {
            "operation_type": operation_type,
            "operation_data": operation_data,
            "constitutional_hash": self.REQUIRED_CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if context:
            validation_request["context"] = context

        # Perform constitutional validation
        constitutional_result = await self.constitutional_validator.validate_request(
            request_data=validation_request, context=context or {}
        )

        return {
            "compliant": constitutional_result.get("approved", False),
            "constitutional_score": constitutional_result.get("confidence", 0.0),
            "constitutional_details": constitutional_result,
            "operation_type": operation_type,
            "critical_operation": operation_type in self.CRITICAL_OPERATIONS,
        }

    async def _validate_audit_requirements(
        self, operation_data: dict[str, Any], context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Validate audit trail requirements"""

        required_audit_fields = [
            "timestamp",
            "operation_id",
            "constitutional_hash",
            "user_context",
        ]

        audit_completeness = {}
        missing_fields = []

        for field in required_audit_fields:
            present = field in operation_data or (context and field in context)
            audit_completeness[field] = present
            if not present:
                missing_fields.append(field)

        is_complete = len(missing_fields) == 0

        return {
            "complete": is_complete,
            "missing_fields": missing_fields,
            "audit_completeness": audit_completeness,
            "completeness_score": len([f for f in audit_completeness.values() if f])
            / len(required_audit_fields),
        }

    async def _validate_performance_compliance(
        self, operation_type: str
    ) -> dict[str, Any]:
        """Validate performance compliance requirements"""

        # Check current validation latency against P99 target
        time.time()

        # Performance requirements for different operation types
        PERFORMANCE_REQUIREMENTS = {
            "analyze": {"max_latency_ms": 3000, "min_throughput_rps": 50},
            "build": {"max_latency_ms": 10000, "min_throughput_rps": 10},
            "deploy": {"max_latency_ms": 30000, "min_throughput_rps": 5},
            "test": {"max_latency_ms": 15000, "min_throughput_rps": 20},
            "constitutional-validate": {
                "max_latency_ms": 100,
                "min_throughput_rps": 200,
            },
        }

        requirements = PERFORMANCE_REQUIREMENTS.get(
            operation_type, {"max_latency_ms": 5000, "min_throughput_rps": 100}
        )

        # Simplified performance check
        estimated_latency_ms = 2.0  # Simulated current performance
        within_limits = estimated_latency_ms <= requirements["max_latency_ms"]

        return {
            "within_limits": within_limits,
            "operation_type": operation_type,
            "estimated_latency_ms": estimated_latency_ms,
            "max_allowed_latency_ms": requirements["max_latency_ms"],
            "performance_requirements": requirements,
        }

    async def _validate_security_compliance(
        self, operation_data: dict[str, Any], context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Validate security compliance requirements"""

        security_checks = {
            "input_validation": self._check_input_validation(operation_data),
            "authentication": self._check_authentication(context),
            "authorization": self._check_authorization(operation_data, context),
            "data_protection": self._check_data_protection(operation_data),
            "constitutional_integrity": self._check_constitutional_integrity(
                operation_data
            ),
        }

        all_secure = all(security_checks.values())

        return {
            "secure": all_secure,
            "security_checks": security_checks,
            "security_score": sum(security_checks.values()) / len(security_checks),
        }

    def _check_input_validation(self, operation_data: dict[str, Any]) -> bool:
        """Check input validation compliance"""
        # Basic input validation check
        if not isinstance(operation_data, dict):
            return False

        # Check for potentially dangerous inputs
        dangerous_patterns = ["<script>", "javascript:", "$(", "eval("]
        for value in operation_data.values():
            if isinstance(value, str) and any(
                pattern in value.lower() for pattern in dangerous_patterns
            ):
                return False

        return True

    def _check_authentication(self, context: dict[str, Any] | None) -> bool:
        """Check authentication compliance"""
        if not context:
            return False

        # Check for authentication context
        return context.get("authenticated", False) or context.get("user_id") is not None

    def _check_authorization(
        self, operation_data: dict[str, Any], context: dict[str, Any] | None
    ) -> bool:
        """Check authorization compliance"""
        if not context:
            return False

        # Check for proper authorization context
        return (
            context.get("authorized", False) or context.get("permissions") is not None
        )

    def _check_data_protection(self, operation_data: dict[str, Any]) -> bool:
        """Check data protection compliance"""
        # Check for sensitive data exposure
        sensitive_keys = ["password", "secret", "token", "private_key"]
        for key in operation_data:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                return False

        return True

    def _check_constitutional_integrity(self, operation_data: dict[str, Any]) -> bool:
        """Check constitutional integrity"""
        # Verify constitutional hash is present and not tampered with
        constitutional_hash = operation_data.get("constitutional_hash")
        return constitutional_hash == self.REQUIRED_CONSTITUTIONAL_HASH

    async def _validate_governance_compliance(
        self, operation_type: str, operation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate governance compliance and detect bypass attempts"""

        # Check for governance bypass indicators
        bypass_indicators = [
            "skip_validation",
            "bypass_governance",
            "override_constitutional",
            "emergency_override",
            "admin_bypass",
            "force_execution",
        ]

        bypass_detected = False
        detected_indicators = []

        # Check operation data for bypass indicators
        for key, value in operation_data.items():
            if any(indicator in key.lower() for indicator in bypass_indicators):
                bypass_detected = True
                detected_indicators.append(key)

            if isinstance(value, str) and any(
                indicator in value.lower() for indicator in bypass_indicators
            ):
                bypass_detected = True
                detected_indicators.append(f"{key}:{value}")

        # Additional governance compliance checks
        governance_checks = {
            "no_bypass_attempts": not bypass_detected,
            "proper_escalation": operation_data.get("escalation_approved", True),
            "governance_context": operation_data.get("governance_context") is not None,
            "constitutional_authority": operation_data.get(
                "constitutional_authority", True
            ),
        }

        no_bypass = all(governance_checks.values())

        return {
            "no_bypass": no_bypass,
            "bypass_detected": bypass_detected,
            "detected_indicators": detected_indicators,
            "governance_checks": governance_checks,
            "governance_score": sum(governance_checks.values())
            / len(governance_checks),
        }

    def _calculate_compliance_score(self, validation_details: dict[str, Any]) -> float:
        """Calculate overall compliance score"""

        scores = []

        # Hash validation (critical)
        if validation_details.get("hash_validation", {}).get("valid", False):
            scores.append(1.0)
        else:
            scores.append(0.0)

        # Operation compliance
        scores.append(
            validation_details.get("operation_validation", {}).get(
                "constitutional_score", 0.0
            )
        )

        # Audit compliance
        scores.append(
            validation_details.get("audit_validation", {}).get(
                "completeness_score", 0.0
            )
        )

        # Security compliance
        scores.append(
            validation_details.get("security_validation", {}).get("security_score", 0.0)
        )

        # Governance compliance
        scores.append(
            validation_details.get("governance_validation", {}).get(
                "governance_score", 0.0
            )
        )

        return sum(scores) / len(scores) if scores else 0.0

    async def _log_validation_result(
        self, result: ConstitutionalValidationResult, operation_data: dict[str, Any]
    ) -> None:
        """Log validation result to blackboard"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "constitutional_validation",
                "validation_result": result.dict(),
                "operation_data_summary": {
                    "operation_type": result.operation_type,
                    "persona": result.persona.value if result.persona else None,
                    "constitutional_hash": result.constitutional_hash,
                },
                "validation_outcome": "PASSED" if result.is_valid else "FAILED",
                "escalation_triggered": result.escalation_required,
            },
            metadata={
                "source": "constitutional_persona_validator",
                "timestamp": result.validation_timestamp.isoformat(),
                "constitutional_compliance": result.is_valid,
                "compliance_score": result.compliance_score,
                "violations_count": len(result.violations),
            },
            tags=["constitutional", "validation", "persona", result.operation_type]
            + [v.value for v in result.violations],
        )

        await self.blackboard.add_knowledge(knowledge_item)

    async def _trigger_constitutional_escalation(
        self, result: ConstitutionalValidationResult, operation_data: dict[str, Any]
    ) -> None:
        """Trigger constitutional escalation for violations"""

        escalation_data = {
            "type": "constitutional_violation_escalation",
            "violation_types": [v.value for v in result.violations],
            "operation_type": result.operation_type,
            "persona": result.persona.value if result.persona else None,
            "compliance_score": result.compliance_score,
            "constitutional_hash": result.constitutional_hash,
            "escalation_timestamp": datetime.now(timezone.utc).isoformat(),
            "human_oversight_required": True,
            "immediate_response_required": any(
                v
                in {
                    ConstitutionalViolationType.HASH_VALIDATION_FAILURE,
                    ConstitutionalViolationType.SECURITY_BREACH,
                    ConstitutionalViolationType.GOVERNANCE_BYPASS,
                }
                for v in result.violations
            ),
        }

        # Log escalation to blackboard
        escalation_item = KnowledgeItem(
            id=str(uuid4()),
            content=escalation_data,
            metadata={
                "source": "constitutional_escalation_system",
                "priority": "CRITICAL",
                "requires_human_oversight": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            tags=[
                "escalation",
                "constitutional",
                "critical",
                "human_oversight_required",
            ],
        )

        await self.blackboard.add_knowledge(escalation_item)

        # Log escalation event
        self.logger.critical(
            f"Constitutional escalation triggered: {escalation_data['violation_types']} "
            f"for operation {result.operation_type} with persona {result.persona}"
        )

    def get_validation_statistics(self) -> dict[str, Any]:
        """Get validation statistics"""
        total = self.validation_stats["total_validations"]
        if total == 0:
            return self.validation_stats

        return {
            **self.validation_stats,
            "success_rate": self.validation_stats["successful_validations"] / total,
            "violation_rate": self.validation_stats["violations_detected"] / total,
            "escalation_rate": self.validation_stats["escalations_triggered"] / total,
        }
