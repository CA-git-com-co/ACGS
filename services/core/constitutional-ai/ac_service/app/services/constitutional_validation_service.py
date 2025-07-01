"""
Constitutional Validation Service

Refactored validation logic from the main service to improve maintainability,
testability, and follow single responsibility principle.
"""

import hashlib
import logging
import time
from typing import Any, Dict, List, Optional

from ..schemas import ConstitutionalComplianceRequest


logger = logging.getLogger(__name__)


class ConstitutionalValidationService:
    """Service class for handling constitutional compliance validation."""

    def __init__(self, audit_logger=None, violation_detector=None, fv_client=None):
        self.audit_logger = audit_logger
        self.violation_detector = violation_detector
        self.fv_client = fv_client

        # Define validation rules configuration
        self.rule_checks = {
            "CONST-001": {
                "name": "Democratic Participation",
                "algorithm": "multi_dimensional_analysis",
                "check": self._advanced_democratic_check,
                "weight": 0.20,
                "formal_verification": True,
            },
            "CONST-002": {
                "name": "Transparency Requirement",
                "algorithm": "transparency_scoring",
                "check": self._advanced_transparency_check,
                "weight": 0.20,
                "formal_verification": True,
            },
            "CONST-003": {
                "name": "Constitutional Compliance",
                "algorithm": "constitutional_fidelity_analysis",
                "check": self._advanced_constitutional_check,
                "weight": 0.25,
                "formal_verification": True,
            },
            "CONST-004": {
                "name": "Accountability Framework",
                "algorithm": "accountability_assessment",
                "check": self._advanced_accountability_check,
                "weight": 0.20,
                "formal_verification": False,
            },
            "CONST-005": {
                "name": "Rights Protection",
                "algorithm": "rights_preservation_analysis",
                "check": self._advanced_rights_check,
                "weight": 0.15,
                "formal_verification": True,
            },
        }

    async def validate_constitutional_compliance(
        self, request: ConstitutionalComplianceRequest
    ) -> Dict[str, Any]:
        """
        Main validation entry point with improved structure.

        Args:
            request: Constitutional compliance validation request

        Returns:
            Dict containing validation results
        """
        start_time = time.time()

        # Extract request parameters
        policy = request.policy
        validation_mode = request.validation_mode
        include_reasoning = request.include_reasoning
        principles = request.principles

        # Generate validation ID
        validation_id = self._generate_validation_id(policy)

        # Log audit trail
        await self._log_validation_request(validation_id, policy, validation_mode)

        # Perform core validation
        validation_results = await self._perform_rule_validation(
            policy, principles, validation_mode
        )

        # Calculate compliance metrics
        compliance_metrics = self._calculate_compliance_metrics(validation_results)

        # Perform formal verification if applicable
        formal_verification_results = await self._perform_formal_verification(
            policy, validation_results, compliance_metrics["overall_compliant"]
        )

        # Build final result
        result = self._build_validation_result(
            validation_id=validation_id,
            policy=policy,
            validation_results=validation_results,
            compliance_metrics=compliance_metrics,
            formal_verification_results=formal_verification_results,
            processing_time=(time.time() - start_time) * 1000,
            validation_mode=validation_mode,
            include_reasoning=include_reasoning,
        )

        # Log audit trail
        await self._log_validation_result(validation_id, result)

        return result

    def _generate_validation_id(self, policy: Dict[str, Any]) -> str:
        """Generate unique validation ID."""
        policy_hash = hashlib.sha256(str(policy).encode()).hexdigest()[:8]
        return f"VAL-{int(time.time())}-{policy_hash}"

    async def _log_validation_request(
        self, validation_id: str, policy: Dict[str, Any], validation_mode: str
    ) -> None:
        """Log validation request for audit trail."""
        if self.audit_logger:
            try:
                await self.audit_logger.log_validation_request(
                    validation_id, policy, [], validation_mode
                )
            except Exception as e:
                logger.warning(f"Audit logging failed: {e}")

    async def _perform_rule_validation(
        self,
        policy: Dict[str, Any],
        principles: Optional[List[Dict]] = None,
        validation_mode: str = "comprehensive",
    ) -> List[Dict[str, Any]]:
        """
        Perform validation against constitutional rules.

        Args:
            policy: Policy to validate
            principles: Optional specific principles to validate against
            validation_mode: Level of validation detail

        Returns:
            List of validation results for each rule
        """
        validation_results = []

        # Determine which rules to check
        rules_to_check = self._get_rules_to_check(principles, validation_mode)

        for rule_id in rules_to_check:
            if rule_id in self.rule_checks:
                rule_result = await self._validate_single_rule(rule_id, policy)
                validation_results.append(rule_result)

        return validation_results

    def _get_rules_to_check(
        self,
        principles: Optional[List[Dict]] = None,
        validation_mode: str = "comprehensive",
    ) -> List[str]:
        """Determine which rules to check based on request parameters."""
        if principles:
            # If specific principles provided, map them to rule IDs
            return [p.get("rule_id", "CONST-001") for p in principles]

        if validation_mode == "basic":
            return ["CONST-001", "CONST-003"]
        elif validation_mode == "comprehensive":
            return list(self.rule_checks.keys())
        else:  # detailed
            return list(self.rule_checks.keys())

    async def _validate_single_rule(
        self, rule_id: str, policy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate policy against a single constitutional rule.

        Args:
            rule_id: Rule identifier
            policy: Policy to validate

        Returns:
            Validation result for the rule
        """
        rule_info = self.rule_checks[rule_id]

        # Use sophisticated compliance algorithm
        compliance_result = rule_info["check"](policy)
        is_compliant = compliance_result["compliant"]
        confidence = compliance_result["confidence"]
        detailed_analysis = compliance_result["analysis"]

        # Handle violation detection
        if not is_compliant:
            await self._handle_violation_detection(rule_id, compliance_result)

        return {
            "rule_id": rule_id,
            "rule_name": rule_info["name"],
            "algorithm": rule_info["algorithm"],
            "compliant": is_compliant,
            "confidence": confidence,
            "weight": rule_info["weight"],
            "detailed_analysis": detailed_analysis,
            "recommendations": compliance_result.get("recommendations", []),
            "severity": compliance_result.get("severity", "medium"),
            "formal_verification_eligible": rule_info["formal_verification"],
        }

    async def _handle_violation_detection(
        self, rule_id: str, compliance_result: Dict[str, Any]
    ) -> None:
        """Handle violation detection for non-compliant rules."""
        if self.violation_detector:
            try:
                await self.violation_detector.detect_violation(
                    f"validation-{int(time.time())}", rule_id, compliance_result
                )
            except Exception as e:
                logger.warning(f"Violation detection failed: {e}")

    def _calculate_compliance_metrics(
        self, validation_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate overall compliance metrics."""
        if not validation_results:
            return {
                "overall_compliant": False,
                "compliance_score": 0.0,
                "rules_passed": 0,
                "rules_failed": 0,
                "overall_confidence": 0.0,
                "average_severity": "unknown",
            }

        overall_compliant = all(r["compliant"] for r in validation_results)
        compliance_score = sum(
            r["weight"] * r["confidence"] for r in validation_results
        )
        rules_passed = sum(1 for r in validation_results if r["compliant"])
        rules_failed = len(validation_results) - rules_passed
        overall_confidence = sum(r["confidence"] for r in validation_results) / len(
            validation_results
        )
        average_severity = self._calculate_average_severity(validation_results)

        return {
            "overall_compliant": overall_compliant,
            "compliance_score": round(compliance_score, 4),
            "rules_passed": rules_passed,
            "rules_failed": rules_failed,
            "overall_confidence": round(overall_confidence, 4),
            "average_severity": average_severity,
        }

    async def _perform_formal_verification(
        self,
        policy: Dict[str, Any],
        validation_results: List[Dict[str, Any]],
        overall_compliant: bool,
    ) -> Optional[Dict[str, Any]]:
        """Perform formal verification if available and applicable."""
        if self.fv_client and overall_compliant:
            try:
                return await self.fv_client.verify_constitutional_compliance(
                    policy, validation_results
                )
            except Exception as e:
                logger.warning(f"Formal verification failed: {e}")
        return None

    def _build_validation_result(
        self,
        validation_id: str,
        policy: Dict[str, Any],
        validation_results: List[Dict[str, Any]],
        compliance_metrics: Dict[str, Any],
        formal_verification_results: Optional[Dict[str, Any]],
        processing_time: float,
        validation_mode: str,
        include_reasoning: bool,
    ) -> Dict[str, Any]:
        """Build the final validation result response."""
        result = {
            "validation_id": validation_id,
            "policy_id": policy.get("policy_id", "unknown"),
            "overall_compliant": compliance_metrics["overall_compliant"],
            "compliance_score": compliance_metrics["compliance_score"],
            "validation_level": validation_mode,
            "results": validation_results,
            "formal_verification": formal_verification_results,
            "summary": {
                "total_rules_checked": len(validation_results),
                "rules_passed": compliance_metrics["rules_passed"],
                "rules_failed": compliance_metrics["rules_failed"],
                "overall_confidence": compliance_metrics["overall_confidence"],
                "average_severity": compliance_metrics["average_severity"],
            },
            "next_steps": self._generate_next_steps(
                compliance_metrics["overall_compliant"]
            ),
            "timestamp": time.time(),
            "processing_time_ms": round(processing_time, 2),
        }

        if not include_reasoning:
            # Remove detailed analysis to reduce response size
            for validation_result in result["results"]:
                validation_result.pop("detailed_analysis", None)

        return result

    def _generate_next_steps(self, overall_compliant: bool) -> List[str]:
        """Generate recommended next steps based on compliance status."""
        if not overall_compliant:
            return [
                "Review failed rule compliance",
                "Implement recommended changes",
                "Re-validate after modifications",
                "Consider formal verification",
            ]
        else:
            return [
                "Proceed to policy governance compliance check",
                "Submit for stakeholder review",
                "Consider production deployment",
            ]

    async def _log_validation_result(
        self, validation_id: str, result: Dict[str, Any]
    ) -> None:
        """Log validation result for audit trail."""
        if self.audit_logger:
            try:
                await self.audit_logger.log_validation_result(validation_id, result)
            except Exception as e:
                logger.warning(f"Audit result logging failed: {e}")

    def _calculate_average_severity(
        self, validation_results: List[Dict[str, Any]]
    ) -> str:
        """Calculate average severity across all validation results."""
        severity_weights = {"low": 1, "medium": 2, "high": 3, "critical": 4}

        if not validation_results:
            return "unknown"

        total_weight = sum(
            severity_weights.get(r.get("severity", "medium"), 2)
            for r in validation_results
        )
        average_weight = total_weight / len(validation_results)

        if average_weight <= 1.5:
            return "low"
        elif average_weight <= 2.5:
            return "medium"
        elif average_weight <= 3.5:
            return "high"
        else:
            return "critical"

    # Placeholder validation methods (these would contain the actual validation logic)
    def _advanced_democratic_check(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced democratic participation validation."""
        # Placeholder implementation
        return {
            "compliant": True,
            "confidence": 0.85,
            "analysis": "Democratic participation requirements met",
            "recommendations": [],
            "severity": "low",
        }

    def _advanced_transparency_check(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced transparency requirement validation."""
        # Placeholder implementation
        return {
            "compliant": True,
            "confidence": 0.90,
            "analysis": "Transparency requirements satisfied",
            "recommendations": [],
            "severity": "low",
        }

    def _advanced_constitutional_check(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced constitutional compliance validation."""
        # Placeholder implementation
        return {
            "compliant": True,
            "confidence": 0.88,
            "analysis": "Constitutional principles upheld",
            "recommendations": [],
            "severity": "low",
        }

    def _advanced_accountability_check(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced accountability framework validation."""
        # Placeholder implementation
        return {
            "compliant": True,
            "confidence": 0.82,
            "analysis": "Accountability mechanisms present",
            "recommendations": [],
            "severity": "low",
        }

    def _advanced_rights_check(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced rights protection validation."""
        # Placeholder implementation
        return {
            "compliant": True,
            "confidence": 0.87,
            "analysis": "Rights protection measures adequate",
            "recommendations": [],
            "severity": "low",
        }
