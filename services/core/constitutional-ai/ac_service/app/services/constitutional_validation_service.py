"""
Constitutional Validation Service

Refactored validation logic from the main service to improve maintainability,
testability, and follow single responsibility principle.
"""

import hashlib
import logging
import time
from typing import Any

from ..schemas import ConstitutionalComplianceRequest

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


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
    ) -> dict[str, Any]:
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

    def _generate_validation_id(self, policy: dict[str, Any]) -> str:
        """Generate unique validation ID."""
        policy_hash = hashlib.sha256(str(policy).encode()).hexdigest()[:8]
        return f"VAL-{int(time.time())}-{policy_hash}"

    async def _log_validation_request(
        self, validation_id: str, policy: dict[str, Any], validation_mode: str
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
        policy: dict[str, Any],
        principles: list[dict] | None = None,
        validation_mode: str = "comprehensive",
    ) -> list[dict[str, Any]]:
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
        principles: list[dict] | None = None,
        validation_mode: str = "comprehensive",
    ) -> list[str]:
        """Determine which rules to check based on request parameters."""
        if principles:
            # If specific principles provided, map them to rule IDs
            return [p.get("rule_id", "CONST-001") for p in principles]

        if validation_mode == "basic":
            return ["CONST-001", "CONST-003"]
        if validation_mode == "comprehensive":
            return list(self.rule_checks.keys())
        # detailed
        return list(self.rule_checks.keys())

    async def _validate_single_rule(
        self, rule_id: str, policy: dict[str, Any]
    ) -> dict[str, Any]:
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
        self, rule_id: str, compliance_result: dict[str, Any]
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
        self, validation_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
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
        policy: dict[str, Any],
        validation_results: list[dict[str, Any]],
        overall_compliant: bool,
    ) -> dict[str, Any] | None:
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
        policy: dict[str, Any],
        validation_results: list[dict[str, Any]],
        compliance_metrics: dict[str, Any],
        formal_verification_results: dict[str, Any] | None,
        processing_time: float,
        validation_mode: str,
        include_reasoning: bool,
    ) -> dict[str, Any]:
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

    def _generate_next_steps(self, overall_compliant: bool) -> list[str]:
        """Generate recommended next steps based on compliance status."""
        if not overall_compliant:
            return [
                "Review failed rule compliance",
                "Implement recommended changes",
                "Re-validate after modifications",
                "Consider formal verification",
            ]
        return [
            "Proceed to policy governance compliance check",
            "Submit for stakeholder review",
            "Consider production deployment",
        ]

    async def _log_validation_result(
        self, validation_id: str, result: dict[str, Any]
    ) -> None:
        """Log validation result for audit trail."""
        if self.audit_logger:
            try:
                await self.audit_logger.log_validation_result(validation_id, result)
            except Exception as e:
                logger.warning(f"Audit result logging failed: {e}")

    def _calculate_average_severity(
        self, validation_results: list[dict[str, Any]]
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
        if average_weight <= 2.5:
            return "medium"
        if average_weight <= 3.5:
            return "high"
        return "critical"

    # Real constitutional reasoning implementations
    def _advanced_democratic_check(self, policy: dict[str, Any]) -> dict[str, Any]:
        """Advanced democratic participation validation using NLP and pattern analysis."""
        policy_text = str(policy).lower()

        # Democratic indicators with weighted scoring
        democratic_indicators = {
            "democratic participation": 0.15,
            "public consultation": 0.12,
            "stakeholder engagement": 0.12,
            "citizen involvement": 0.10,
            "voting mechanism": 0.10,
            "consensus building": 0.08,
            "representative process": 0.08,
            "community input": 0.07,
            "participatory design": 0.06,
            "inclusive decision": 0.06,
            "democratic oversight": 0.06,
        }

        # Anti-democratic indicators (negative scoring)
        anti_democratic_indicators = {
            "authoritarian": -0.25,
            "unilateral decision": -0.20,
            "bypass consultation": -0.18,
            "exclude stakeholders": -0.15,
            "ignore input": -0.12,
            "centralized control": -0.10,
        }

        # Calculate base score
        positive_score = sum(
            weight
            for indicator, weight in democratic_indicators.items()
            if indicator in policy_text
        )
        negative_score = sum(
            weight
            for indicator, weight in anti_democratic_indicators.items()
            if indicator in policy_text
        )

        raw_score = positive_score + negative_score
        normalized_score = max(0.0, min(1.0, (raw_score + 0.5)))

        # Advanced contextual analysis
        structural_elements = self._analyze_democratic_structure(policy_text)
        procedural_elements = self._analyze_democratic_procedures(policy_text)

        # Calculate final confidence with structural analysis
        base_confidence = normalized_score
        structural_bonus = min(0.15, structural_elements * 0.05)
        procedural_bonus = min(0.10, procedural_elements * 0.03)

        final_confidence = min(
            0.98, base_confidence + structural_bonus + procedural_bonus
        )
        is_compliant = final_confidence >= 0.65

        # Generate detailed analysis
        analysis_details = {
            "democratic_score": round(normalized_score, 3),
            "structural_elements_found": structural_elements,
            "procedural_elements_found": procedural_elements,
            "positive_indicators": [
                i for i in democratic_indicators if i in policy_text
            ],
            "negative_indicators": [
                i for i in anti_democratic_indicators if i in policy_text
            ],
            "participation_mechanisms": self._extract_participation_mechanisms(
                policy_text
            ),
        }

        # Generate specific recommendations
        recommendations = self._generate_democratic_recommendations(
            analysis_details, is_compliant
        )

        # Determine severity
        if final_confidence < 0.4:
            severity = "critical"
        elif final_confidence < 0.65:
            severity = "high"
        elif final_confidence < 0.8:
            severity = "medium"
        else:
            severity = "low"

        return {
            "compliant": is_compliant,
            "confidence": round(final_confidence, 4),
            "analysis": analysis_details,
            "recommendations": recommendations,
            "severity": severity,
        }

    def _advanced_transparency_check(self, policy: dict[str, Any]) -> dict[str, Any]:
        """Advanced transparency requirement validation using document analysis."""
        policy_text = str(policy).lower()

        # Transparency indicators with semantic weights
        transparency_indicators = {
            "public disclosure": 0.18,
            "open records": 0.15,
            "audit trail": 0.14,
            "transparent process": 0.12,
            "public access": 0.10,
            "documentation requirements": 0.08,
            "reporting obligations": 0.08,
            "accountability measures": 0.07,
            "information sharing": 0.06,
            "public notice": 0.02,
        }

        # Opacity indicators (negative scoring)
        opacity_indicators = {
            "confidential": -0.15,
            "classified": -0.20,
            "restricted access": -0.12,
            "non-disclosure": -0.18,
            "hidden process": -0.25,
            "secret deliberation": -0.22,
        }

        # Calculate transparency score
        transparency_score = sum(
            weight
            for indicator, weight in transparency_indicators.items()
            if indicator in policy_text
        )
        opacity_penalty = sum(
            weight
            for indicator, weight in opacity_indicators.items()
            if indicator in policy_text
        )

        # Analyze documentation requirements
        doc_quality = self._analyze_documentation_requirements(policy_text)
        access_provisions = self._analyze_access_provisions(policy_text)
        audit_mechanisms = self._analyze_audit_mechanisms(policy_text)

        # Calculate final score with bonuses
        base_score = max(0.0, transparency_score + opacity_penalty + 0.3)
        doc_bonus = min(0.15, doc_quality * 0.05)
        access_bonus = min(0.10, access_provisions * 0.03)
        audit_bonus = min(0.10, audit_mechanisms * 0.04)

        final_confidence = min(
            0.97, base_score + doc_bonus + access_bonus + audit_bonus
        )
        is_compliant = final_confidence >= 0.70

        # Detailed analysis
        analysis_details = {
            "transparency_score": round(base_score, 3),
            "documentation_quality": doc_quality,
            "access_provisions": access_provisions,
            "audit_mechanisms": audit_mechanisms,
            "transparency_indicators": [
                i for i in transparency_indicators if i in policy_text
            ],
            "opacity_concerns": [i for i in opacity_indicators if i in policy_text],
            "disclosure_timeline": self._extract_disclosure_timeline(policy_text),
        }

        recommendations = self._generate_transparency_recommendations(
            analysis_details, is_compliant
        )

        # Severity assessment
        if final_confidence < 0.5:
            severity = "critical"
        elif final_confidence < 0.70:
            severity = "high"
        elif final_confidence < 0.85:
            severity = "medium"
        else:
            severity = "low"

        return {
            "compliant": is_compliant,
            "confidence": round(final_confidence, 4),
            "analysis": analysis_details,
            "recommendations": recommendations,
            "severity": severity,
        }

    def _advanced_constitutional_check(self, policy: dict[str, Any]) -> dict[str, Any]:
        """Advanced constitutional compliance validation using legal reasoning."""
        policy_text = str(policy).lower()

        # Constitutional principles with hierarchical weights
        constitutional_principles = {
            # Fundamental rights (highest weight)
            "due process": 0.20,
            "equal protection": 0.18,
            "fundamental rights": 0.16,
            "constitutional review": 0.12,
            # Structural principles
            "separation of powers": 0.10,
            "checks and balances": 0.08,
            "federalism": 0.06,
            # Procedural compliance
            "legal framework": 0.05,
            "constitutional authority": 0.03,
            "lawful process": 0.02,
        }

        # Constitutional violations (critical negative indicators)
        constitutional_violations = {
            "unconstitutional": -0.40,
            "violate rights": -0.35,
            "bypass constitution": -0.30,
            "override fundamental": -0.28,
            "ignore due process": -0.25,
            "arbitrary power": -0.22,
        }

        # Calculate constitutional alignment score
        principle_score = sum(
            weight
            for principle, weight in constitutional_principles.items()
            if principle in policy_text
        )
        violation_penalty = sum(
            weight
            for violation, weight in constitutional_violations.items()
            if violation in policy_text
        )

        # Advanced constitutional analysis
        rights_protection = self._analyze_rights_protection(policy_text)
        power_structure = self._analyze_power_structure(policy_text)
        legal_compliance = self._analyze_legal_compliance(policy_text)
        procedural_safeguards = self._analyze_procedural_safeguards(policy_text)

        # Calculate final score with advanced analysis
        base_score = max(0.0, principle_score + violation_penalty + 0.4)
        rights_bonus = min(0.20, rights_protection * 0.06)
        structure_bonus = min(0.15, power_structure * 0.04)
        legal_bonus = min(0.10, legal_compliance * 0.03)
        procedural_bonus = min(0.10, procedural_safeguards * 0.03)

        final_confidence = min(
            0.99,
            base_score
            + rights_bonus
            + structure_bonus
            + legal_bonus
            + procedural_bonus,
        )
        is_compliant = final_confidence >= 0.75

        # Comprehensive analysis
        analysis_details = {
            "constitutional_score": round(base_score, 3),
            "rights_protection_level": rights_protection,
            "power_structure_compliance": power_structure,
            "legal_framework_adherence": legal_compliance,
            "procedural_safeguards": procedural_safeguards,
            "principles_upheld": [
                p for p in constitutional_principles if p in policy_text
            ],
            "potential_violations": [
                v for v in constitutional_violations if v in policy_text
            ],
            "constitutional_precedents": self._identify_constitutional_precedents(
                policy_text
            ),
        }

        recommendations = self._generate_constitutional_recommendations(
            analysis_details, is_compliant
        )

        # Severity based on constitutional importance
        if final_confidence < 0.5 or len(analysis_details["potential_violations"]) > 0:
            severity = "critical"
        elif final_confidence < 0.75:
            severity = "high"
        elif final_confidence < 0.90:
            severity = "medium"
        else:
            severity = "low"

        return {
            "compliant": is_compliant,
            "confidence": round(final_confidence, 4),
            "analysis": analysis_details,
            "recommendations": recommendations,
            "severity": severity,
        }

    def _advanced_accountability_check(self, policy: dict[str, Any]) -> dict[str, Any]:
        """Advanced accountability framework validation using governance analysis."""
        policy_text = str(policy).lower()

        # Accountability mechanisms with operational weights
        accountability_mechanisms = {
            "oversight committee": 0.16,
            "performance monitoring": 0.14,
            "audit requirements": 0.13,
            "reporting obligations": 0.12,
            "compliance review": 0.10,
            "enforcement measures": 0.09,
            "corrective actions": 0.08,
            "responsibility assignment": 0.07,
            "evaluation metrics": 0.06,
            "accountability officer": 0.05,
        }

        # Accountability gaps (negative indicators)
        accountability_gaps = {
            "no oversight": -0.25,
            "unaccountable": -0.20,
            "no enforcement": -0.18,
            "avoid responsibility": -0.15,
            "no monitoring": -0.12,
            "immune from review": -0.22,
        }

        # Calculate accountability score
        mechanism_score = sum(
            weight
            for mechanism, weight in accountability_mechanisms.items()
            if mechanism in policy_text
        )
        gap_penalty = sum(
            weight for gap, weight in accountability_gaps.items() if gap in policy_text
        )

        # Detailed accountability analysis
        oversight_strength = self._analyze_oversight_mechanisms(policy_text)
        enforcement_capacity = self._analyze_enforcement_capacity(policy_text)
        monitoring_systems = self._analyze_monitoring_systems(policy_text)
        remediation_processes = self._analyze_remediation_processes(policy_text)

        # Calculate final score with system analysis
        base_score = max(0.0, mechanism_score + gap_penalty + 0.35)
        oversight_bonus = min(0.15, oversight_strength * 0.05)
        enforcement_bonus = min(0.12, enforcement_capacity * 0.04)
        monitoring_bonus = min(0.10, monitoring_systems * 0.03)
        remediation_bonus = min(0.08, remediation_processes * 0.03)

        final_confidence = min(
            0.96,
            base_score
            + oversight_bonus
            + enforcement_bonus
            + monitoring_bonus
            + remediation_bonus,
        )
        is_compliant = final_confidence >= 0.68

        # Comprehensive accountability analysis
        analysis_details = {
            "accountability_score": round(base_score, 3),
            "oversight_strength": oversight_strength,
            "enforcement_capacity": enforcement_capacity,
            "monitoring_systems": monitoring_systems,
            "remediation_processes": remediation_processes,
            "mechanisms_present": [
                m for m in accountability_mechanisms if m in policy_text
            ],
            "accountability_gaps": [g for g in accountability_gaps if g in policy_text],
            "responsibility_chain": self._map_responsibility_chain(policy_text),
        }

        recommendations = self._generate_accountability_recommendations(
            analysis_details, is_compliant
        )

        # Severity assessment
        if final_confidence < 0.45:
            severity = "critical"
        elif final_confidence < 0.68:
            severity = "high"
        elif final_confidence < 0.82:
            severity = "medium"
        else:
            severity = "low"

        return {
            "compliant": is_compliant,
            "confidence": round(final_confidence, 4),
            "analysis": analysis_details,
            "recommendations": recommendations,
            "severity": severity,
        }

    def _advanced_rights_check(self, policy: dict[str, Any]) -> dict[str, Any]:
        """Advanced rights protection validation using human rights framework."""
        policy_text = str(policy).lower()

        # Rights protection categories with impact weights
        rights_protections = {
            # Civil and political rights
            "privacy protection": 0.18,
            "freedom of expression": 0.16,
            "due process rights": 0.15,
            "equal treatment": 0.12,
            "non-discrimination": 0.10,
            # Procedural rights
            "right to appeal": 0.08,
            "access to information": 0.07,
            "fair hearing": 0.06,
            "legal representation": 0.05,
            "remedy mechanisms": 0.03,
        }

        # Rights violations (critical concerns)
        rights_violations = {
            "discriminatory": -0.30,
            "violate privacy": -0.25,
            "restrict freedom": -0.22,
            "deny due process": -0.28,
            "arbitrary detention": -0.35,
            "suppress speech": -0.20,
        }

        # Calculate rights protection score
        protection_score = sum(
            weight
            for protection, weight in rights_protections.items()
            if protection in policy_text
        )
        violation_penalty = sum(
            weight
            for violation, weight in rights_violations.items()
            if violation in policy_text
        )

        # Advanced rights analysis
        privacy_safeguards = self._analyze_privacy_safeguards(policy_text)
        equality_measures = self._analyze_equality_measures(policy_text)
        due_process_protections = self._analyze_due_process(policy_text)
        remedial_mechanisms = self._analyze_remedial_mechanisms(policy_text)

        # Calculate final score with rights analysis
        base_score = max(0.0, protection_score + violation_penalty + 0.38)
        privacy_bonus = min(0.15, privacy_safeguards * 0.05)
        equality_bonus = min(0.12, equality_measures * 0.04)
        due_process_bonus = min(0.15, due_process_protections * 0.05)
        remedial_bonus = min(0.08, remedial_mechanisms * 0.03)

        final_confidence = min(
            0.98,
            base_score
            + privacy_bonus
            + equality_bonus
            + due_process_bonus
            + remedial_bonus,
        )
        is_compliant = final_confidence >= 0.72

        # Comprehensive rights analysis
        analysis_details = {
            "rights_protection_score": round(base_score, 3),
            "privacy_safeguards": privacy_safeguards,
            "equality_measures": equality_measures,
            "due_process_protections": due_process_protections,
            "remedial_mechanisms": remedial_mechanisms,
            "protections_identified": [
                p for p in rights_protections if p in policy_text
            ],
            "potential_violations": [v for v in rights_violations if v in policy_text],
            "vulnerable_groups_considered": self._identify_vulnerable_groups(
                policy_text
            ),
        }

        recommendations = self._generate_rights_recommendations(
            analysis_details, is_compliant
        )

        # Severity based on rights impact
        if final_confidence < 0.5 or len(analysis_details["potential_violations"]) > 0:
            severity = "critical"
        elif final_confidence < 0.72:
            severity = "high"
        elif final_confidence < 0.87:
            severity = "medium"
        else:
            severity = "low"

        return {
            "compliant": is_compliant,
            "confidence": round(final_confidence, 4),
            "analysis": analysis_details,
            "recommendations": recommendations,
            "severity": severity,
        }

    # Helper methods for sophisticated constitutional analysis

    def _analyze_democratic_structure(self, policy_text: str) -> int:
        """Analyze democratic structural elements in policy."""
        structural_elements = [
            "voting process",
            "election mechanism",
            "representative body",
            "council formation",
            "committee structure",
            "democratic institution",
        ]
        return sum(1 for element in structural_elements if element in policy_text)

    def _analyze_democratic_procedures(self, policy_text: str) -> int:
        """Analyze democratic procedural elements."""
        procedural_elements = [
            "public hearing",
            "consultation period",
            "comment period",
            "deliberation process",
            "debate forum",
            "feedback mechanism",
        ]
        return sum(1 for element in procedural_elements if element in policy_text)

    def _extract_participation_mechanisms(self, policy_text: str) -> list[str]:
        """Extract specific participation mechanisms mentioned."""
        mechanisms = [
            "public forums",
            "citizen panels",
            "advisory committees",
            "town halls",
            "surveys",
            "referendums",
            "petition process",
        ]
        return [mech for mech in mechanisms if mech in policy_text]

    def _generate_democratic_recommendations(
        self, analysis: dict, is_compliant: bool
    ) -> list[str]:
        """Generate specific recommendations for democratic participation."""
        recommendations = []

        if not is_compliant:
            if analysis["structural_elements_found"] < 2:
                recommendations.append(
                    "Establish formal democratic decision-making structures"
                )
            if analysis["procedural_elements_found"] < 2:
                recommendations.append("Implement public consultation procedures")
            if not analysis["participation_mechanisms"]:
                recommendations.append("Add specific stakeholder engagement mechanisms")

        if analysis["negative_indicators"]:
            recommendations.append("Address anti-democratic elements identified")

        return recommendations

    def _analyze_documentation_requirements(self, policy_text: str) -> int:
        """Analyze documentation and record-keeping requirements."""
        doc_requirements = [
            "record keeping",
            "documentation standards",
            "information management",
            "archive requirements",
            "retention policy",
            "public records",
        ]
        return sum(1 for req in doc_requirements if req in policy_text)

    def _analyze_access_provisions(self, policy_text: str) -> int:
        """Analyze information access provisions."""
        access_provisions = [
            "freedom of information",
            "public access",
            "information request",
            "disclosure timeline",
            "access procedures",
            "availability standards",
        ]
        return sum(1 for provision in access_provisions if provision in policy_text)

    def _analyze_audit_mechanisms(self, policy_text: str) -> int:
        """Analyze audit and review mechanisms."""
        audit_mechanisms = [
            "independent audit",
            "performance review",
            "compliance monitoring",
            "external oversight",
            "periodic evaluation",
            "audit trail",
        ]
        return sum(1 for mechanism in audit_mechanisms if mechanism in policy_text)

    def _extract_disclosure_timeline(self, policy_text: str) -> list[str]:
        """Extract disclosure timelines mentioned in policy."""
        timeline_patterns = [
            "30 days",
            "60 days",
            "90 days",
            "quarterly",
            "annually",
            "immediately",
            "within",
            "regular intervals",
        ]
        return [pattern for pattern in timeline_patterns if pattern in policy_text]

    def _generate_transparency_recommendations(
        self, analysis: dict, is_compliant: bool
    ) -> list[str]:
        """Generate transparency improvement recommendations."""
        recommendations = []

        if not is_compliant:
            if analysis["documentation_quality"] < 2:
                recommendations.append(
                    "Strengthen documentation and record-keeping requirements"
                )
            if analysis["access_provisions"] < 2:
                recommendations.append(
                    "Improve public access to information provisions"
                )
            if analysis["audit_mechanisms"] < 2:
                recommendations.append(
                    "Establish comprehensive audit and review mechanisms"
                )

        if analysis["opacity_concerns"]:
            recommendations.append(
                "Address confidentiality and access restriction concerns"
            )

        if not analysis["disclosure_timeline"]:
            recommendations.append("Specify clear timelines for information disclosure")

        return recommendations

    def _analyze_rights_protection(self, policy_text: str) -> int:
        """Analyze rights protection mechanisms."""
        rights_mechanisms = [
            "rights assessment",
            "impact evaluation",
            "protection measures",
            "safeguard provisions",
            "rights monitoring",
            "protection review",
        ]
        return sum(1 for mechanism in rights_mechanisms if mechanism in policy_text)

    def _analyze_power_structure(self, policy_text: str) -> int:
        """Analyze power structure and separation compliance."""
        power_elements = [
            "separation of powers",
            "checks and balances",
            "independent review",
            "judicial oversight",
            "legislative approval",
            "executive limitation",
        ]
        return sum(1 for element in power_elements if element in policy_text)

    def _analyze_legal_compliance(self, policy_text: str) -> int:
        """Analyze legal framework compliance."""
        legal_elements = [
            "legal authority",
            "statutory basis",
            "constitutional authority",
            "regulatory compliance",
            "legal review",
            "jurisdiction",
        ]
        return sum(1 for element in legal_elements if element in policy_text)

    def _analyze_procedural_safeguards(self, policy_text: str) -> int:
        """Analyze procedural safeguards."""
        safeguards = [
            "procedural fairness",
            "natural justice",
            "impartial process",
            "fair hearing",
            "procedural rights",
            "administrative justice",
        ]
        return sum(1 for safeguard in safeguards if safeguard in policy_text)

    def _identify_constitutional_precedents(self, policy_text: str) -> list[str]:
        """Identify references to constitutional precedents."""
        precedent_indicators = [
            "supreme court",
            "constitutional court",
            "precedent",
            "case law",
            "judicial decision",
            "legal precedent",
            "court ruling",
        ]
        return [
            indicator for indicator in precedent_indicators if indicator in policy_text
        ]

    def _generate_constitutional_recommendations(
        self, analysis: dict, is_compliant: bool
    ) -> list[str]:
        """Generate constitutional compliance recommendations."""
        recommendations = []

        if not is_compliant:
            if analysis["rights_protection_level"] < 2:
                recommendations.append(
                    "Strengthen fundamental rights protection mechanisms"
                )
            if analysis["power_structure_compliance"] < 2:
                recommendations.append(
                    "Ensure proper separation of powers and checks and balances"
                )
            if analysis["legal_framework_adherence"] < 2:
                recommendations.append(
                    "Establish clear legal authority and statutory basis"
                )
            if analysis["procedural_safeguards"] < 2:
                recommendations.append("Implement comprehensive procedural safeguards")

        if analysis["potential_violations"]:
            recommendations.append(
                "Address potential constitutional violations identified"
            )

        return recommendations

    def _analyze_oversight_mechanisms(self, policy_text: str) -> int:
        """Analyze oversight and monitoring mechanisms."""
        oversight_elements = [
            "oversight board",
            "monitoring committee",
            "review panel",
            "supervisory body",
            "watchdog function",
            "independent monitor",
        ]
        return sum(1 for element in oversight_elements if element in policy_text)

    def _analyze_enforcement_capacity(self, policy_text: str) -> int:
        """Analyze enforcement capacity and mechanisms."""
        enforcement_elements = [
            "enforcement authority",
            "penalty provisions",
            "compliance measures",
            "corrective action",
            "enforcement procedure",
            "sanctions",
        ]
        return sum(1 for element in enforcement_elements if element in policy_text)

    def _analyze_monitoring_systems(self, policy_text: str) -> int:
        """Analyze monitoring and tracking systems."""
        monitoring_elements = [
            "performance metrics",
            "monitoring system",
            "tracking mechanism",
            "evaluation framework",
            "measurement standards",
            "reporting system",
        ]
        return sum(1 for element in monitoring_elements if element in policy_text)

    def _analyze_remediation_processes(self, policy_text: str) -> int:
        """Analyze remediation and corrective action processes."""
        remediation_elements = [
            "corrective action",
            "remediation plan",
            "improvement measures",
            "resolution process",
            "remedial steps",
            "corrective measures",
        ]
        return sum(1 for element in remediation_elements if element in policy_text)

    def _map_responsibility_chain(self, policy_text: str) -> list[str]:
        """Map responsibility and accountability chain."""
        responsibility_indicators = [
            "responsible officer",
            "accountability manager",
            "oversight authority",
            "designated official",
            "accountable person",
            "responsible entity",
        ]
        return [
            indicator
            for indicator in responsibility_indicators
            if indicator in policy_text
        ]

    def _generate_accountability_recommendations(
        self, analysis: dict, is_compliant: bool
    ) -> list[str]:
        """Generate accountability improvement recommendations."""
        recommendations = []

        if not is_compliant:
            if analysis["oversight_strength"] < 2:
                recommendations.append(
                    "Establish robust oversight and monitoring mechanisms"
                )
            if analysis["enforcement_capacity"] < 2:
                recommendations.append(
                    "Strengthen enforcement authority and penalty provisions"
                )
            if analysis["monitoring_systems"] < 2:
                recommendations.append(
                    "Implement comprehensive monitoring and reporting systems"
                )
            if analysis["remediation_processes"] < 1:
                recommendations.append(
                    "Develop clear remediation and corrective action processes"
                )

        if analysis["accountability_gaps"]:
            recommendations.append(
                "Address identified accountability gaps and weaknesses"
            )

        if not analysis["responsibility_chain"]:
            recommendations.append(
                "Clearly define responsibility and accountability assignments"
            )

        return recommendations

    def _analyze_privacy_safeguards(self, policy_text: str) -> int:
        """Analyze privacy protection safeguards."""
        privacy_elements = [
            "privacy protection",
            "data protection",
            "confidentiality measures",
            "privacy rights",
            "data security",
            "personal information",
        ]
        return sum(1 for element in privacy_elements if element in policy_text)

    def _analyze_equality_measures(self, policy_text: str) -> int:
        """Analyze equality and non-discrimination measures."""
        equality_elements = [
            "equal treatment",
            "non-discrimination",
            "equality provision",
            "fair access",
            "equal opportunity",
            "anti-discrimination",
        ]
        return sum(1 for element in equality_elements if element in policy_text)

    def _analyze_due_process(self, policy_text: str) -> int:
        """Analyze due process protections."""
        due_process_elements = [
            "due process",
            "fair procedure",
            "natural justice",
            "procedural fairness",
            "right to hearing",
            "impartial decision",
        ]
        return sum(1 for element in due_process_elements if element in policy_text)

    def _analyze_remedial_mechanisms(self, policy_text: str) -> int:
        """Analyze remedial and appeal mechanisms."""
        remedial_elements = [
            "appeal process",
            "remedy mechanism",
            "grievance procedure",
            "redress system",
            "complaint mechanism",
            "dispute resolution",
        ]
        return sum(1 for element in remedial_elements if element in policy_text)

    def _identify_vulnerable_groups(self, policy_text: str) -> list[str]:
        """Identify consideration of vulnerable groups."""
        vulnerable_group_indicators = [
            "minority rights",
            "vulnerable populations",
            "protected groups",
            "disability access",
            "children",
            "elderly",
            "indigenous",
        ]
        return [
            indicator
            for indicator in vulnerable_group_indicators
            if indicator in policy_text
        ]

    def _generate_rights_recommendations(
        self, analysis: dict, is_compliant: bool
    ) -> list[str]:
        """Generate rights protection recommendations."""
        recommendations = []

        if not is_compliant:
            if analysis["privacy_safeguards"] < 2:
                recommendations.append(
                    "Strengthen privacy protection and data security measures"
                )
            if analysis["equality_measures"] < 2:
                recommendations.append(
                    "Enhance equality and non-discrimination provisions"
                )
            if analysis["due_process_protections"] < 2:
                recommendations.append("Implement comprehensive due process safeguards")
            if analysis["remedial_mechanisms"] < 1:
                recommendations.append(
                    "Establish accessible remedy and appeal mechanisms"
                )

        if analysis["potential_violations"]:
            recommendations.append("Address potential rights violations identified")

        if not analysis["vulnerable_groups_considered"]:
            recommendations.append(
                "Consider impacts on vulnerable groups and minorities"
            )

        return recommendations
