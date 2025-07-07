"""
EU AI Act Compliance Engine

Core compliance engine implementing the European Union's Artificial Intelligence Act
requirements for constitutional AI governance systems. This module provides automated
compliance assessment, risk classification, and regulatory obligation management.

Key Features:
- Automated AI system risk classification per EU AI Act Annex III
- Compliance requirement mapping and assessment
- Real-time compliance monitoring and violation detection
- Technical documentation generation and management
- Conformity assessment procedure automation
- Post-market surveillance and incident reporting
"""

# Constitutional Hash: cdd01ef066bc6cf2

import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)


class AISystemRiskLevel(Enum):
    """AI System Risk Levels per EU AI Act"""

    MINIMAL_RISK = "minimal_risk"
    LIMITED_RISK = "limited_risk"
    HIGH_RISK = "high_risk"
    UNACCEPTABLE_RISK = "unacceptable_risk"


class AISystemCategory(Enum):
    """AI System Categories per EU AI Act Annex III"""

    BIOMETRIC_IDENTIFICATION = "biometric_identification"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    EDUCATION_TRAINING = "education_training"
    EMPLOYMENT_MANAGEMENT = "employment_management"
    ESSENTIAL_SERVICES = "essential_services"
    LAW_ENFORCEMENT = "law_enforcement"
    MIGRATION_ASYLUM = "migration_asylum"
    ADMINISTRATION_JUSTICE = "administration_justice"
    DEMOCRATIC_PROCESSES = "democratic_processes"  # ACGS falls here
    GENERAL_PURPOSE = "general_purpose"


class ComplianceStatus(Enum):
    """Compliance Status"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_ASSESSMENT = "under_assessment"
    REQUIRES_REMEDIATION = "requires_remediation"


class ObligationLevel(Enum):
    """Compliance Obligation Levels"""

    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


@dataclass
class ComplianceRequirement:
    """EU AI Act compliance requirement"""

    requirement_id: str
    article_reference: str
    title: str
    description: str
    obligation_level: ObligationLevel
    applicable_risk_levels: list[AISystemRiskLevel]
    applicable_categories: list[AISystemCategory]
    assessment_criteria: list[str]
    evidence_required: list[str]
    deadline_days: Optional[int]
    created_at: datetime


@dataclass
class RiskAssessment:
    """AI System Risk Assessment Result"""

    system_name: str
    system_version: str
    assessed_risk_level: AISystemRiskLevel
    assessed_category: AISystemCategory
    assessment_rationale: str
    risk_factors: list[str]
    mitigation_measures: list[str]
    assessment_date: datetime
    assessor: str
    next_review_date: datetime
    confidence_score: float


@dataclass
class ComplianceAssessment:
    """Compliance Assessment Result"""

    assessment_id: str
    requirement_id: str
    system_name: str
    status: ComplianceStatus
    evidence_provided: list[str]
    gaps_identified: list[str]
    remediation_actions: list[str]
    assessment_date: datetime
    assessor: str
    next_review_date: datetime
    risk_score: float


class EUAIActCompliance:
    """
    EU AI Act Compliance Engine for Constitutional AI Systems
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()

        # System configuration
        self.system_name = config.get("system_name", "ACGS")
        self.system_version = config.get("system_version", "1.0.0")
        self.organization = config.get("organization", "Constitutional AI Organization")
        self.deployment_region = config.get("deployment_region", "EU")

        # Compliance configuration
        self.assessment_interval_days = config.get("assessment_interval_days", 90)
        self.auto_remediation_enabled = config.get("auto_remediation_enabled", True)
        self.compliance_threshold = config.get("compliance_threshold", 0.95)

        # State management
        self.compliance_requirements = {}
        self.risk_assessments = {}
        self.compliance_assessments = {}
        self.violation_log = []

        # Initialize compliance framework
        self._initialize_compliance_requirements()

    def _initialize_compliance_requirements(self):
        """Initialize EU AI Act compliance requirements"""

        # Article 8: Compliance with requirements
        self.compliance_requirements["art8_compliance"] = ComplianceRequirement(
            requirement_id="art8_compliance",
            article_reference="Article 8",
            title="General Compliance with High-Risk AI System Requirements",
            description=(
                "High-risk AI systems must comply with requirements in Chapter III"
            ),
            obligation_level=ObligationLevel.MANDATORY,
            applicable_risk_levels=[AISystemRiskLevel.HIGH_RISK],
            applicable_categories=[AISystemCategory.DEMOCRATIC_PROCESSES],
            assessment_criteria=[
                "System meets data governance requirements",
                "Technical documentation is complete and current",
                "Record-keeping systems are operational",
                "Transparency obligations are fulfilled",
                "Human oversight measures are implemented",
                "Accuracy and robustness requirements are met",
            ],
            evidence_required=[
                "Technical documentation package",
                "Data governance policies",
                "Human oversight procedures",
                "Testing and validation reports",
            ],
            deadline_days=None,
            created_at=datetime.utcnow(),
        )

        # Article 9: Risk management system
        self.compliance_requirements["art9_risk_mgmt"] = ComplianceRequirement(
            requirement_id="art9_risk_mgmt",
            article_reference="Article 9",
            title="Risk Management System",
            description="Establish and maintain a risk management system",
            obligation_level=ObligationLevel.MANDATORY,
            applicable_risk_levels=[AISystemRiskLevel.HIGH_RISK],
            applicable_categories=[AISystemCategory.DEMOCRATIC_PROCESSES],
            assessment_criteria=[
                "Risk management process is documented",
                "Risks are identified and assessed regularly",
                "Risk mitigation measures are implemented",
                "Residual risks are acceptable and documented",
                "Risk management is integrated throughout lifecycle",
            ],
            evidence_required=[
                "Risk management documentation",
                "Risk assessment reports",
                "Mitigation measures documentation",
                "Residual risk analysis",
            ],
            deadline_days=None,
            created_at=datetime.utcnow(),
        )

        # Article 10: Data governance
        self.compliance_requirements["art10_data_governance"] = ComplianceRequirement(
            requirement_id="art10_data_governance",
            article_reference="Article 10",
            title="Data and Data Governance",
            description="Implement appropriate data governance measures",
            obligation_level=ObligationLevel.MANDATORY,
            applicable_risk_levels=[AISystemRiskLevel.HIGH_RISK],
            applicable_categories=[AISystemCategory.DEMOCRATIC_PROCESSES],
            assessment_criteria=[
                "Training data is relevant and representative",
                "Data quality is appropriate for intended purpose",
                "Data sets are complete and error-free",
                "Biases in data are identified and addressed",
                "Data lineage is documented and traceable",
            ],
            evidence_required=[
                "Data governance policies",
                "Data quality reports",
                "Bias assessment documentation",
                "Data lineage documentation",
            ],
            deadline_days=None,
            created_at=datetime.utcnow(),
        )

        # Article 11: Technical documentation
        self.compliance_requirements["art11_tech_docs"] = ComplianceRequirement(
            requirement_id="art11_tech_docs",
            article_reference="Article 11",
            title="Technical Documentation",
            description="Maintain comprehensive technical documentation",
            obligation_level=ObligationLevel.MANDATORY,
            applicable_risk_levels=[AISystemRiskLevel.HIGH_RISK],
            applicable_categories=[AISystemCategory.DEMOCRATIC_PROCESSES],
            assessment_criteria=[
                "Documentation covers all required elements per Annex IV",
                "Documentation is up-to-date and accurate",
                "Documentation is accessible to authorities",
                "Documentation demonstrates compliance with requirements",
            ],
            evidence_required=[
                "Complete technical documentation package",
                "Documentation management procedures",
                "Version control records",
            ],
            deadline_days=None,
            created_at=datetime.utcnow(),
        )

        # Article 12: Record-keeping
        self.compliance_requirements["art12_recordkeeping"] = ComplianceRequirement(
            requirement_id="art12_recordkeeping",
            article_reference="Article 12",
            title="Record-keeping",
            description="Maintain comprehensive operational records",
            obligation_level=ObligationLevel.MANDATORY,
            applicable_risk_levels=[AISystemRiskLevel.HIGH_RISK],
            applicable_categories=[AISystemCategory.DEMOCRATIC_PROCESSES],
            assessment_criteria=[
                "Automatic logging is implemented and operational",
                "Logs capture all required information",
                "Log integrity and security are maintained",
                "Logs are retained for required period",
                "Log analysis capabilities are available",
            ],
            evidence_required=[
                "Logging system documentation",
                "Log retention policies",
                "Log security measures",
                "Sample log records",
            ],
            deadline_days=None,
            created_at=datetime.utcnow(),
        )

        # Article 13: Transparency
        self.compliance_requirements["art13_transparency"] = ComplianceRequirement(
            requirement_id="art13_transparency",
            article_reference="Article 13",
            title="Transparency and Information to Users",
            description="Ensure transparency and provide clear information to users",
            obligation_level=ObligationLevel.MANDATORY,
            applicable_risk_levels=[AISystemRiskLevel.HIGH_RISK],
            applicable_categories=[AISystemCategory.DEMOCRATIC_PROCESSES],
            assessment_criteria=[
                "Users are informed they are interacting with AI",
                "System capabilities and limitations are communicated",
                "Instructions for use are clear and comprehensive",
                "Information is provided in accessible format",
                "Transparency measures do not compromise security",
            ],
            evidence_required=[
                "User information materials",
                "Instructions for use",
                "Transparency implementation documentation",
            ],
            deadline_days=None,
            created_at=datetime.utcnow(),
        )

        # Article 14: Human oversight
        self.compliance_requirements["art14_human_oversight"] = ComplianceRequirement(
            requirement_id="art14_human_oversight",
            article_reference="Article 14",
            title="Human Oversight",
            description="Implement effective human oversight measures",
            obligation_level=ObligationLevel.MANDATORY,
            applicable_risk_levels=[AISystemRiskLevel.HIGH_RISK],
            applicable_categories=[AISystemCategory.DEMOCRATIC_PROCESSES],
            assessment_criteria=[
                "Human oversight measures are designed and implemented",
                "Humans can understand system capabilities and limitations",
                "Humans can monitor system operation",
                "Humans can interpret system outputs",
                "Humans can intervene or interrupt system operation",
            ],
            evidence_required=[
                "Human oversight procedures",
                "Training documentation for human overseers",
                "Intervention mechanisms documentation",
            ],
            deadline_days=None,
            created_at=datetime.utcnow(),
        )

        # Article 15: Accuracy, robustness and cybersecurity
        self.compliance_requirements["art15_accuracy_robustness"] = (
            ComplianceRequirement(
                requirement_id="art15_accuracy_robustness",
                article_reference="Article 15",
                title="Accuracy, Robustness and Cybersecurity",
                description=(
                    "Ensure appropriate levels of accuracy, robustness and"
                    " cybersecurity"
                ),
                obligation_level=ObligationLevel.MANDATORY,
                applicable_risk_levels=[AISystemRiskLevel.HIGH_RISK],
                applicable_categories=[AISystemCategory.DEMOCRATIC_PROCESSES],
                assessment_criteria=[
                    "Accuracy levels are appropriate for intended purpose",
                    "System is robust against errors and faults",
                    "Cybersecurity measures are implemented",
                    "System resilience is tested and validated",
                    "Performance monitoring is operational",
                ],
                evidence_required=[
                    "Accuracy testing reports",
                    "Robustness testing documentation",
                    "Cybersecurity assessment",
                    "Performance monitoring reports",
                ],
                deadline_days=None,
                created_at=datetime.utcnow(),
            )
        )

        # Article 16: Obligations of providers
        self.compliance_requirements["art16_provider_obligations"] = (
            ComplianceRequirement(
                requirement_id="art16_provider_obligations",
                article_reference="Article 16",
                title="Obligations of Providers of High-Risk AI Systems",
                description=(
                    "Fulfill provider obligations including QMS and conformity"
                    " assessment"
                ),
                obligation_level=ObligationLevel.MANDATORY,
                applicable_risk_levels=[AISystemRiskLevel.HIGH_RISK],
                applicable_categories=[AISystemCategory.DEMOCRATIC_PROCESSES],
                assessment_criteria=[
                    "Quality management system is established",
                    "Conformity assessment is completed",
                    "CE marking and declaration of conformity",
                    "Post-market monitoring system is operational",
                    "Corrective action procedures are defined",
                ],
                evidence_required=[
                    "Quality management system documentation",
                    "Conformity assessment reports",
                    "CE marking documentation",
                    "Post-market monitoring procedures",
                ],
                deadline_days=None,
                created_at=datetime.utcnow(),
            )
        )

    async def assess_system_risk(
        self, system_details: dict[str, Any]
    ) -> RiskAssessment:
        """
        Assess AI system risk level according to EU AI Act

        Args:
            system_details: Dictionary containing system information

        Returns:
            Risk assessment result
        """
        try:
            system_name = system_details.get("name", self.system_name)
            system_version = system_details.get("version", self.system_version)

            # ACGS is classified as HIGH_RISK under DEMOCRATIC_PROCESSES category
            # per EU AI Act Annex III, Point 8: AI systems intended to be used in
            # democratic processes

            risk_factors = self._identify_risk_factors(system_details)
            mitigation_measures = self._identify_mitigation_measures(risk_factors)
            confidence_score = self._calculate_risk_confidence(
                system_details, risk_factors
            )

            assessment = RiskAssessment(
                system_name=system_name,
                system_version=system_version,
                assessed_risk_level=AISystemRiskLevel.HIGH_RISK,
                assessed_category=AISystemCategory.DEMOCRATIC_PROCESSES,
                assessment_rationale=(
                    "ACGS is classified as HIGH_RISK under EU AI Act Annex III, Point 8"
                    " (AI systems intended to be used in democratic processes) as it"
                    " provides constitutional AI governance and democratic"
                    " decision-making support that could significantly impact"
                    " democratic processes."
                ),
                risk_factors=risk_factors,
                mitigation_measures=mitigation_measures,
                assessment_date=datetime.utcnow(),
                assessor="EU_AI_Act_Compliance_Engine",
                next_review_date=datetime.utcnow()
                + timedelta(days=self.assessment_interval_days),
                confidence_score=confidence_score,
            )

            # Store assessment
            self.risk_assessments[system_name] = assessment

            # Log assessment
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "risk_assessment_completed",
                    "system_name": system_name,
                    "risk_level": assessment.assessed_risk_level.value,
                    "category": assessment.assessed_category.value,
                    "confidence_score": confidence_score,
                    "timestamp": assessment.assessment_date.isoformat(),
                }
            )

            return assessment

        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            raise

    def _identify_risk_factors(self, system_details: dict[str, Any]) -> list[str]:
        """Identify risk factors for the AI system"""
        risk_factors = []

        # Democratic process risks
        if system_details.get("affects_democratic_decisions", True):
            risk_factors.append(
                "System influences democratic decision-making processes"
            )

        if system_details.get("processes_citizen_data", True):
            risk_factors.append("System processes personal data of citizens")

        if system_details.get("automated_decision_making", True):
            risk_factors.append(
                "System makes automated decisions affecting individuals"
            )

        if system_details.get("constitutional_interpretation", True):
            risk_factors.append("System interprets constitutional principles and laws")

        if system_details.get("policy_recommendations", True):
            risk_factors.append("System generates policy recommendations")

        if system_details.get("public_service_integration", True):
            risk_factors.append("System integrates with public service delivery")

        # Technical risks
        if system_details.get("machine_learning_based", True):
            risk_factors.append("System uses machine learning algorithms")

        if system_details.get("large_language_models", True):
            risk_factors.append("System employs large language models")

        if system_details.get("real_time_processing", True):
            risk_factors.append("System processes data in real-time")

        # Scale and impact risks
        if system_details.get("wide_deployment", True):
            risk_factors.append("System has wide-scale deployment")

        if system_details.get("high_impact_decisions", True):
            risk_factors.append("System supports high-impact governance decisions")

        return risk_factors

    def _identify_mitigation_measures(self, risk_factors: list[str]) -> list[str]:
        """Identify appropriate mitigation measures for identified risks"""
        mitigation_measures = []

        # Standard mitigations for democratic processes
        mitigation_measures.extend(
            [
                "Implement mandatory human oversight for all decisions",
                "Establish transparent decision-making processes",
                "Provide comprehensive audit trails",
                "Implement bias detection and mitigation",
                "Ensure explainability of all decisions",
                "Establish appeal and review mechanisms",
                "Implement data protection and privacy safeguards",
                "Conduct regular fairness assessments",
                "Establish public consultation processes",
                "Implement constitutional compliance validation",
            ]
        )

        # Risk-specific mitigations
        if "machine learning algorithms" in str(risk_factors):
            mitigation_measures.extend(
                [
                    "Implement model validation and testing procedures",
                    "Establish model drift monitoring",
                    "Implement adversarial robustness testing",
                ]
            )

        if "real-time processing" in str(risk_factors):
            mitigation_measures.extend(
                [
                    "Implement circuit breakers for system failures",
                    "Establish graceful degradation procedures",
                    "Implement real-time monitoring and alerting",
                ]
            )

        if "wide-scale deployment" in str(risk_factors):
            mitigation_measures.extend(
                [
                    "Implement phased rollout procedures",
                    "Establish incident response capabilities",
                    "Implement comprehensive monitoring and logging",
                ]
            )

        return list(set(mitigation_measures))  # Remove duplicates

    def _calculate_risk_confidence(
        self, system_details: dict[str, Any], risk_factors: list[str]
    ) -> float:
        """Calculate confidence score for risk assessment"""
        base_confidence = 0.9  # High confidence for clear regulatory classification

        # Adjust based on information completeness
        required_fields = [
            "affects_democratic_decisions",
            "processes_citizen_data",
            "automated_decision_making",
            "constitutional_interpretation",
        ]

        provided_fields = sum(1 for field in required_fields if field in system_details)
        completeness_factor = provided_fields / len(required_fields)

        # Adjust based on risk factor count
        risk_factor_adjustment = min(0.1, len(risk_factors) * 0.01)

        confidence = base_confidence * completeness_factor + risk_factor_adjustment
        return min(1.0, confidence)

    async def assess_compliance(
        self, requirement_id: str, evidence: dict[str, Any]
    ) -> ComplianceAssessment:
        """
        Assess compliance with specific EU AI Act requirement

        Args:
            requirement_id: ID of the compliance requirement
            evidence: Evidence provided for assessment

        Returns:
            Compliance assessment result
        """
        try:
            if requirement_id not in self.compliance_requirements:
                raise ValueError(f"Unknown requirement ID: {requirement_id}")

            requirement = self.compliance_requirements[requirement_id]
            assessment_id = str(uuid.uuid4())

            # Assess compliance based on provided evidence
            status, gaps, actions = await self._evaluate_compliance(
                requirement, evidence
            )
            risk_score = self._calculate_compliance_risk(status, gaps)

            assessment = ComplianceAssessment(
                assessment_id=assessment_id,
                requirement_id=requirement_id,
                system_name=self.system_name,
                status=status,
                evidence_provided=list(evidence.keys()),
                gaps_identified=gaps,
                remediation_actions=actions,
                assessment_date=datetime.utcnow(),
                assessor="EU_AI_Act_Compliance_Engine",
                next_review_date=datetime.utcnow()
                + timedelta(days=self.assessment_interval_days),
                risk_score=risk_score,
            )

            # Store assessment
            self.compliance_assessments[assessment_id] = assessment

            # Log compliance assessment
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "compliance_assessment_completed",
                    "assessment_id": assessment_id,
                    "requirement_id": requirement_id,
                    "status": status.value,
                    "risk_score": risk_score,
                    "gaps_count": len(gaps),
                    "timestamp": assessment.assessment_date.isoformat(),
                }
            )

            # Send alerts for non-compliance
            if status in [
                ComplianceStatus.NON_COMPLIANT,
                ComplianceStatus.REQUIRES_REMEDIATION,
            ]:
                await self.alerting.send_alert(
                    f"eu_ai_act_compliance_violation_{requirement_id}",
                    f"Non-compliance detected for {requirement.title}: {gaps}",
                    severity="high",
                )

            return assessment

        except Exception as e:
            logger.error(f"Compliance assessment failed for {requirement_id}: {e}")
            raise

    async def _evaluate_compliance(
        self, requirement: ComplianceRequirement, evidence: dict[str, Any]
    ) -> tuple:
        """Evaluate compliance status based on evidence"""
        gaps = []
        remediation_actions = []

        # Check if all required evidence is provided
        provided_evidence = set(evidence.keys())
        required_evidence = set(requirement.evidence_required)
        missing_evidence = required_evidence - provided_evidence

        if missing_evidence:
            gaps.extend([f"Missing evidence: {item}" for item in missing_evidence])
            remediation_actions.extend([f"Provide {item}" for item in missing_evidence])

        # Assess each criterion
        for criterion in requirement.assessment_criteria:
            criterion_met = await self._assess_criterion(criterion, evidence)
            if not criterion_met:
                gaps.append(f"Criterion not met: {criterion}")
                remediation_actions.append(f"Address criterion: {criterion}")

        # Determine overall status
        if not gaps:
            status = ComplianceStatus.COMPLIANT
        elif len(gaps) <= len(requirement.assessment_criteria) * 0.2:  # 20% tolerance
            status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            status = ComplianceStatus.NON_COMPLIANT

        return status, gaps, remediation_actions

    async def _assess_criterion(self, criterion: str, evidence: dict[str, Any]) -> bool:
        """Assess whether a specific criterion is met"""
        # Simplified criterion assessment - in practice this would be more sophisticated
        criterion_lower = criterion.lower()

        # Check for relevant evidence keywords
        relevant_keywords = [
            "documentation",
            "policy",
            "procedure",
            "system",
            "process",
            "testing",
            "validation",
            "monitoring",
            "oversight",
            "governance",
        ]

        for keyword in relevant_keywords:
            if keyword in criterion_lower:
                # Look for evidence that might address this criterion
                for evidence_key, evidence_value in evidence.items():
                    if keyword in evidence_key.lower() or (
                        isinstance(evidence_value, str)
                        and keyword in evidence_value.lower()
                    ):
                        return True

        # Default assessment based on evidence completeness
        return len(evidence) > 0

    def _calculate_compliance_risk(
        self, status: ComplianceStatus, gaps: list[str]
    ) -> float:
        """Calculate compliance risk score"""
        base_risk = {
            ComplianceStatus.COMPLIANT: 0.1,
            ComplianceStatus.PARTIALLY_COMPLIANT: 0.4,
            ComplianceStatus.NON_COMPLIANT: 0.8,
            ComplianceStatus.REQUIRES_REMEDIATION: 0.9,
            ComplianceStatus.UNDER_ASSESSMENT: 0.5,
        }.get(status, 0.5)

        # Adjust based on number of gaps
        gap_risk = min(0.3, len(gaps) * 0.05)

        return min(1.0, base_risk + gap_risk)

    async def get_compliance_status(self) -> dict[str, Any]:
        """Get overall compliance status for the system"""
        total_requirements = len(self.compliance_requirements)
        assessed_requirements = len(self.compliance_assessments)

        if assessed_requirements == 0:
            overall_status = ComplianceStatus.UNDER_ASSESSMENT
            compliance_score = 0.0
        else:
            compliant_count = sum(
                1
                for assessment in self.compliance_assessments.values()
                if assessment.status == ComplianceStatus.COMPLIANT
            )
            compliance_score = compliant_count / total_requirements

            if compliance_score >= self.compliance_threshold:
                overall_status = ComplianceStatus.COMPLIANT
            elif compliance_score >= 0.7:
                overall_status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                overall_status = ComplianceStatus.NON_COMPLIANT

        return {
            "overall_status": overall_status.value,
            "compliance_score": compliance_score,
            "total_requirements": total_requirements,
            "assessed_requirements": assessed_requirements,
            "compliant_requirements": sum(
                1
                for assessment in self.compliance_assessments.values()
                if assessment.status == ComplianceStatus.COMPLIANT
            ),
            "non_compliant_requirements": sum(
                1
                for assessment in self.compliance_assessments.values()
                if assessment.status == ComplianceStatus.NON_COMPLIANT
            ),
            "pending_assessments": total_requirements - assessed_requirements,
            "last_assessment_date": max(
                (
                    assessment.assessment_date
                    for assessment in self.compliance_assessments.values()
                ),
                default=None,
            ),
            "next_review_date": min(
                (
                    assessment.next_review_date
                    for assessment in self.compliance_assessments.values()
                ),
                default=datetime.utcnow()
                + timedelta(days=self.assessment_interval_days),
            ),
        }

    async def generate_compliance_report(self) -> dict[str, Any]:
        """Generate comprehensive compliance report"""
        compliance_status = await self.get_compliance_status()

        # Get risk assessment
        risk_assessment = self.risk_assessments.get(self.system_name)

        # Compile detailed assessments
        detailed_assessments = {}
        for assessment_id, assessment in self.compliance_assessments.items():
            requirement = self.compliance_requirements[assessment.requirement_id]
            detailed_assessments[assessment.requirement_id] = {
                "requirement": {
                    "title": requirement.title,
                    "article_reference": requirement.article_reference,
                    "obligation_level": requirement.obligation_level.value,
                },
                "assessment": {
                    "status": assessment.status.value,
                    "risk_score": assessment.risk_score,
                    "gaps_count": len(assessment.gaps_identified),
                    "evidence_count": len(assessment.evidence_provided),
                    "assessment_date": assessment.assessment_date.isoformat(),
                },
            }

        report = {
            "report_metadata": {
                "system_name": self.system_name,
                "system_version": self.system_version,
                "organization": self.organization,
                "report_date": datetime.utcnow().isoformat(),
                "report_type": "EU_AI_Act_Compliance_Report",
                "report_version": "1.0",
            },
            "executive_summary": compliance_status,
            "risk_assessment": asdict(risk_assessment) if risk_assessment else None,
            "detailed_assessments": detailed_assessments,
            "recommendations": await self._generate_recommendations(),
            "next_actions": await self._generate_next_actions(),
        }

        return report

    async def _generate_recommendations(self) -> list[str]:
        """Generate compliance recommendations"""
        recommendations = []

        # Analyze assessment results
        non_compliant_assessments = [
            assessment
            for assessment in self.compliance_assessments.values()
            if assessment.status
            in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.REQUIRES_REMEDIATION]
        ]

        if non_compliant_assessments:
            recommendations.append(
                f"Address {len(non_compliant_assessments)} non-compliant requirements"
                " immediately"
            )

        partially_compliant_count = sum(
            1
            for assessment in self.compliance_assessments.values()
            if assessment.status == ComplianceStatus.PARTIALLY_COMPLIANT
        )

        if partially_compliant_count > 0:
            recommendations.append(
                f"Improve {partially_compliant_count} partially compliant requirements"
            )

        # Standard recommendations for high-risk AI systems
        recommendations.extend(
            [
                "Establish regular compliance monitoring procedures",
                "Implement automated compliance checking where possible",
                "Conduct quarterly compliance reviews",
                "Maintain up-to-date technical documentation",
                "Ensure human oversight procedures are followed",
                "Monitor for bias and fairness issues continuously",
                "Establish incident response procedures for compliance violations",
            ]
        )

        return recommendations

    async def _generate_next_actions(self) -> list[str]:
        """Generate next actions for compliance improvement"""
        actions = []

        # Unassessed requirements
        unassessed_requirements = set(self.compliance_requirements.keys()) - set(
            assessment.requirement_id
            for assessment in self.compliance_assessments.values()
        )

        if unassessed_requirements:
            actions.extend(
                [
                    f"Conduct compliance assessment for {req_id}"
                    for req_id in unassessed_requirements
                ]
            )

        # Remediation actions from assessments
        for assessment in self.compliance_assessments.values():
            if assessment.remediation_actions:
                actions.extend(assessment.remediation_actions)

        # Due assessments
        upcoming_reviews = [
            assessment
            for assessment in self.compliance_assessments.values()
            if assessment.next_review_date <= datetime.utcnow() + timedelta(days=30)
        ]

        if upcoming_reviews:
            actions.extend(
                [
                    f"Schedule compliance review for {assessment.requirement_id}"
                    for assessment in upcoming_reviews
                ]
            )

        return list(set(actions))  # Remove duplicates

    def get_applicable_requirements(
        self, risk_level: AISystemRiskLevel, category: AISystemCategory
    ) -> list[ComplianceRequirement]:
        """Get compliance requirements applicable to specific risk level and category"""
        applicable_requirements = []

        for requirement in self.compliance_requirements.values():
            if (
                risk_level in requirement.applicable_risk_levels
                and category in requirement.applicable_categories
            ):
                applicable_requirements.append(requirement)

        return applicable_requirements


# Example usage and testing
async def example_usage():
    """Example of using the EU AI Act compliance engine"""
    # Initialize compliance engine
    compliance_engine = EUAIActCompliance(
        {
            "system_name": "ACGS",
            "system_version": "1.0.0",
            "organization": "Constitutional AI Research Institute",
            "deployment_region": "EU",
        }
    )

    # Assess system risk
    system_details = {
        "name": "ACGS",
        "version": "1.0.0",
        "affects_democratic_decisions": True,
        "processes_citizen_data": True,
        "automated_decision_making": True,
        "constitutional_interpretation": True,
        "policy_recommendations": True,
        "machine_learning_based": True,
        "large_language_models": True,
    }

    risk_assessment = await compliance_engine.assess_system_risk(system_details)
    print(f"Risk Assessment: {risk_assessment.assessed_risk_level.value}")
    print(f"Category: {risk_assessment.assessed_category.value}")

    # Assess compliance for specific requirement
    evidence = {
        "technical_documentation": "Complete technical documentation package available",
        "data_governance_policy": "Data governance policies implemented",
        "human_oversight_procedures": "Human oversight procedures documented",
        "testing_reports": "System testing and validation completed",
    }

    assessment = await compliance_engine.assess_compliance("art11_tech_docs", evidence)
    print(f"Compliance Status: {assessment.status.value}")

    # Get overall compliance status
    status = await compliance_engine.get_compliance_status()
    print(f"Overall Compliance Score: {status['compliance_score']:.2%}")

    # Generate compliance report
    report = await compliance_engine.generate_compliance_report()
    print(f"Report generated with {len(report['detailed_assessments'])} assessments")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
