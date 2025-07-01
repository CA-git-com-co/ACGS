#!/usr/bin/env python3
"""
ACGS Governance Maturity Framework

A comprehensive framework for measuring and improving governance maturity
across organizations implementing constitutional AI governance systems.

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MaturityLevel(Enum):
    """Governance maturity levels based on capability maturity model."""

    INITIAL = 1  # Ad-hoc, chaotic processes
    MANAGED = 2  # Basic processes established
    DEFINED = 3  # Standardized processes
    QUANTITATIVELY_MANAGED = 4  # Measured and controlled
    OPTIMIZING = 5  # Continuous improvement


class GovernanceDomain(Enum):
    """Key domains of governance maturity assessment."""

    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    POLICY_MANAGEMENT = "policy_management"
    DECISION_TRANSPARENCY = "decision_transparency"
    STAKEHOLDER_ENGAGEMENT = "stakeholder_engagement"
    RISK_MANAGEMENT = "risk_management"
    AUDIT_AND_MONITORING = "audit_and_monitoring"
    CHANGE_MANAGEMENT = "change_management"
    TRAINING_AND_COMPETENCY = "training_and_competency"
    TECHNOLOGY_GOVERNANCE = "technology_governance"
    PERFORMANCE_MEASUREMENT = "performance_measurement"


@dataclass
class MaturityIndicator:
    """Individual maturity indicator within a domain."""

    id: str
    name: str
    description: str
    domain: GovernanceDomain
    level_1_criteria: List[str]  # Initial
    level_2_criteria: List[str]  # Managed
    level_3_criteria: List[str]  # Defined
    level_4_criteria: List[str]  # Quantitatively Managed
    level_5_criteria: List[str]  # Optimizing
    weight: float = 1.0
    constitutional_hash: str = "cdd01ef066bc6cf2"


@dataclass
class AssessmentResult:
    """Result of a maturity assessment."""

    organization_id: str
    assessment_date: datetime
    overall_maturity_level: float
    domain_scores: Dict[GovernanceDomain, float]
    indicator_scores: Dict[str, int]
    recommendations: List[str]
    improvement_roadmap: List[Dict[str, Any]]
    constitutional_compliance_score: float
    constitutional_hash: str = "cdd01ef066bc6cf2"


class GovernanceMaturityFramework:
    """Main framework for governance maturity assessment and improvement."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.indicators = self._initialize_indicators()
        self.assessment_history: List[AssessmentResult] = []

    def _initialize_indicators(self) -> Dict[str, MaturityIndicator]:
        """Initialize the maturity indicators for all domains."""
        indicators = {}

        # Constitutional Compliance Indicators
        indicators["const_policy_adherence"] = MaturityIndicator(
            id="const_policy_adherence",
            name="Constitutional Policy Adherence",
            description="Adherence to constitutional principles in policy development",
            domain=GovernanceDomain.CONSTITUTIONAL_COMPLIANCE,
            level_1_criteria=["Basic awareness of constitutional principles"],
            level_2_criteria=[
                "Documented constitutional policies",
                "Basic compliance checks",
            ],
            level_3_criteria=[
                "Standardized constitutional review process",
                "Regular compliance audits",
            ],
            level_4_criteria=[
                "Quantitative compliance metrics",
                "Automated compliance monitoring",
            ],
            level_5_criteria=[
                "Continuous constitutional optimization",
                "Predictive compliance analytics",
            ],
        )

        indicators["const_decision_validation"] = MaturityIndicator(
            id="const_decision_validation",
            name="Constitutional Decision Validation",
            description="Validation of decisions against constitutional requirements",
            domain=GovernanceDomain.CONSTITUTIONAL_COMPLIANCE,
            level_1_criteria=["Ad-hoc decision validation"],
            level_2_criteria=["Basic decision review process"],
            level_3_criteria=[
                "Standardized validation framework",
                "Constitutional AI integration",
            ],
            level_4_criteria=[
                "Quantitative validation metrics",
                "Real-time validation",
            ],
            level_5_criteria=[
                "Predictive decision analysis",
                "Continuous validation improvement",
            ],
        )

        # Policy Management Indicators
        indicators["policy_lifecycle"] = MaturityIndicator(
            id="policy_lifecycle",
            name="Policy Lifecycle Management",
            description="Management of policy creation, update, and retirement",
            domain=GovernanceDomain.POLICY_MANAGEMENT,
            level_1_criteria=["Basic policy documentation"],
            level_2_criteria=["Defined policy creation process", "Version control"],
            level_3_criteria=["Standardized lifecycle management", "Impact assessment"],
            level_4_criteria=[
                "Quantitative policy effectiveness metrics",
                "Automated lifecycle",
            ],
            level_5_criteria=[
                "Continuous policy optimization",
                "AI-driven policy evolution",
            ],
        )

        # Decision Transparency Indicators
        indicators["decision_transparency"] = MaturityIndicator(
            id="decision_transparency",
            name="Decision Process Transparency",
            description="Transparency in governance decision-making processes",
            domain=GovernanceDomain.DECISION_TRANSPARENCY,
            level_1_criteria=["Basic decision documentation"],
            level_2_criteria=[
                "Structured decision records",
                "Stakeholder notification",
            ],
            level_3_criteria=[
                "Standardized transparency framework",
                "Public decision logs",
            ],
            level_4_criteria=[
                "Quantitative transparency metrics",
                "Real-time decision tracking",
            ],
            level_5_criteria=[
                "Predictive transparency analytics",
                "Continuous improvement",
            ],
        )

        # Stakeholder Engagement Indicators
        indicators["stakeholder_participation"] = MaturityIndicator(
            id="stakeholder_participation",
            name="Stakeholder Participation",
            description="Engagement of stakeholders in governance processes",
            domain=GovernanceDomain.STAKEHOLDER_ENGAGEMENT,
            level_1_criteria=["Ad-hoc stakeholder consultation"],
            level_2_criteria=["Defined stakeholder groups", "Regular consultation"],
            level_3_criteria=[
                "Standardized engagement framework",
                "Feedback integration",
            ],
            level_4_criteria=[
                "Quantitative engagement metrics",
                "Automated feedback analysis",
            ],
            level_5_criteria=[
                "Predictive engagement optimization",
                "Continuous improvement",
            ],
        )

        # Risk Management Indicators
        indicators["governance_risk_mgmt"] = MaturityIndicator(
            id="governance_risk_mgmt",
            name="Governance Risk Management",
            description="Management of governance-related risks",
            domain=GovernanceDomain.RISK_MANAGEMENT,
            level_1_criteria=["Basic risk awareness"],
            level_2_criteria=["Risk identification process", "Basic mitigation"],
            level_3_criteria=["Standardized risk framework", "Regular risk assessment"],
            level_4_criteria=["Quantitative risk metrics", "Automated risk monitoring"],
            level_5_criteria=[
                "Predictive risk analytics",
                "Continuous risk optimization",
            ],
        )

        # Audit and Monitoring Indicators
        indicators["audit_effectiveness"] = MaturityIndicator(
            id="audit_effectiveness",
            name="Audit and Monitoring Effectiveness",
            description="Effectiveness of governance audit and monitoring systems",
            domain=GovernanceDomain.AUDIT_AND_MONITORING,
            level_1_criteria=["Basic audit activities"],
            level_2_criteria=["Defined audit process", "Regular monitoring"],
            level_3_criteria=["Standardized audit framework", "Continuous monitoring"],
            level_4_criteria=["Quantitative audit metrics", "Real-time monitoring"],
            level_5_criteria=["Predictive audit analytics", "Continuous improvement"],
        )

        # Technology Governance Indicators
        indicators["tech_governance"] = MaturityIndicator(
            id="tech_governance",
            name="Technology Governance",
            description="Governance of technology systems and AI components",
            domain=GovernanceDomain.TECHNOLOGY_GOVERNANCE,
            level_1_criteria=["Basic technology oversight"],
            level_2_criteria=["Defined tech governance process", "Basic AI oversight"],
            level_3_criteria=[
                "Standardized tech governance",
                "Constitutional AI integration",
            ],
            level_4_criteria=["Quantitative tech metrics", "Automated governance"],
            level_5_criteria=["Predictive tech governance", "Continuous optimization"],
        )

        return indicators

    def conduct_assessment(
        self, organization_id: str, responses: Dict[str, int]
    ) -> AssessmentResult:
        """Conduct a comprehensive governance maturity assessment."""
        logger.info(
            f"Conducting maturity assessment for organization: {organization_id}"
        )

        # Calculate domain scores
        domain_scores = {}
        for domain in GovernanceDomain:
            domain_indicators = [
                ind for ind in self.indicators.values() if ind.domain == domain
            ]
            if domain_indicators:
                domain_score = sum(
                    responses.get(ind.id, 1) * ind.weight for ind in domain_indicators
                ) / sum(ind.weight for ind in domain_indicators)
                domain_scores[domain] = domain_score

        # Calculate overall maturity level
        overall_score = sum(domain_scores.values()) / len(domain_scores)

        # Calculate constitutional compliance score
        const_indicators = [
            ind
            for ind in self.indicators.values()
            if ind.domain == GovernanceDomain.CONSTITUTIONAL_COMPLIANCE
        ]
        const_score = (
            sum(responses.get(ind.id, 1) * ind.weight for ind in const_indicators)
            / sum(ind.weight for ind in const_indicators)
            if const_indicators
            else 0
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(domain_scores, responses)

        # Create improvement roadmap
        roadmap = self._create_improvement_roadmap(domain_scores, responses)

        # Create assessment result
        result = AssessmentResult(
            organization_id=organization_id,
            assessment_date=datetime.now(timezone.utc),
            overall_maturity_level=overall_score,
            domain_scores=domain_scores,
            indicator_scores=responses,
            recommendations=recommendations,
            improvement_roadmap=roadmap,
            constitutional_compliance_score=const_score / 5.0,  # Normalize to 0-1
        )

        self.assessment_history.append(result)
        return result

    def _generate_recommendations(
        self, domain_scores: Dict[GovernanceDomain, float], responses: Dict[str, int]
    ) -> List[str]:
        """Generate improvement recommendations based on assessment results."""
        recommendations = []

        # Identify lowest scoring domains
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1])

        for domain, score in sorted_domains[:3]:  # Focus on top 3 improvement areas
            if score < 3.0:  # Below "Defined" level
                if domain == GovernanceDomain.CONSTITUTIONAL_COMPLIANCE:
                    recommendations.append(
                        "Implement comprehensive constitutional compliance framework with "
                        "automated validation and monitoring capabilities"
                    )
                elif domain == GovernanceDomain.POLICY_MANAGEMENT:
                    recommendations.append(
                        "Establish standardized policy lifecycle management with "
                        "version control and impact assessment"
                    )
                elif domain == GovernanceDomain.DECISION_TRANSPARENCY:
                    recommendations.append(
                        "Develop transparent decision-making framework with "
                        "public audit trails and stakeholder visibility"
                    )
                elif domain == GovernanceDomain.STAKEHOLDER_ENGAGEMENT:
                    recommendations.append(
                        "Create structured stakeholder engagement program with "
                        "regular consultation and feedback integration"
                    )
                elif domain == GovernanceDomain.TECHNOLOGY_GOVERNANCE:
                    recommendations.append(
                        "Implement comprehensive technology governance framework "
                        "with constitutional AI integration"
                    )

        return recommendations

    def _create_improvement_roadmap(
        self, domain_scores: Dict[GovernanceDomain, float], responses: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """Create a prioritized improvement roadmap."""
        roadmap = []

        # Phase 1: Foundation (0-6 months) - Address critical gaps
        phase1_items = []
        for domain, score in domain_scores.items():
            if score < 2.0:  # Below "Managed" level
                phase1_items.append(
                    {
                        "domain": domain.value,
                        "priority": "Critical",
                        "timeline": "0-6 months",
                        "effort": "High",
                        "description": f"Establish basic {domain.value.replace('_', ' ')} processes",
                    }
                )

        # Phase 2: Standardization (6-18 months) - Standardize processes
        phase2_items = []
        for domain, score in domain_scores.items():
            if 2.0 <= score < 3.0:  # "Managed" but not "Defined"
                phase2_items.append(
                    {
                        "domain": domain.value,
                        "priority": "High",
                        "timeline": "6-18 months",
                        "effort": "Medium",
                        "description": f"Standardize {domain.value.replace('_', ' ')} framework",
                    }
                )

        # Phase 3: Optimization (18+ months) - Advanced capabilities
        phase3_items = []
        for domain, score in domain_scores.items():
            if score >= 3.0:  # "Defined" or higher
                phase3_items.append(
                    {
                        "domain": domain.value,
                        "priority": "Medium",
                        "timeline": "18+ months",
                        "effort": "Low-Medium",
                        "description": f"Optimize {domain.value.replace('_', ' ')} with advanced analytics",
                    }
                )

        roadmap.extend(phase1_items)
        roadmap.extend(phase2_items)
        roadmap.extend(phase3_items)

        return roadmap

    def generate_assessment_report(self, result: AssessmentResult) -> Dict[str, Any]:
        """Generate a comprehensive assessment report."""
        return {
            "executive_summary": {
                "organization_id": result.organization_id,
                "assessment_date": result.assessment_date.isoformat(),
                "overall_maturity_level": result.overall_maturity_level,
                "maturity_level_name": self._get_maturity_level_name(
                    result.overall_maturity_level
                ),
                "constitutional_compliance_score": result.constitutional_compliance_score,
                "constitutional_hash": result.constitutional_hash,
            },
            "domain_analysis": {
                domain.value: {
                    "score": score,
                    "level": self._get_maturity_level_name(score),
                    "status": self._get_domain_status(score),
                }
                for domain, score in result.domain_scores.items()
            },
            "key_findings": {
                "strengths": self._identify_strengths(result.domain_scores),
                "improvement_areas": self._identify_improvement_areas(
                    result.domain_scores
                ),
                "critical_gaps": self._identify_critical_gaps(result.domain_scores),
            },
            "recommendations": result.recommendations,
            "improvement_roadmap": result.improvement_roadmap,
            "next_steps": self._generate_next_steps(result),
        }

    def _get_maturity_level_name(self, score: float) -> str:
        """Get the maturity level name for a given score."""
        if score < 1.5:
            return "Initial"
        elif score < 2.5:
            return "Managed"
        elif score < 3.5:
            return "Defined"
        elif score < 4.5:
            return "Quantitatively Managed"
        else:
            return "Optimizing"

    def _get_domain_status(self, score: float) -> str:
        """Get the status description for a domain score."""
        if score < 2.0:
            return "Needs Immediate Attention"
        elif score < 3.0:
            return "Requires Improvement"
        elif score < 4.0:
            return "Good"
        else:
            return "Excellent"

    def _identify_strengths(
        self, domain_scores: Dict[GovernanceDomain, float]
    ) -> List[str]:
        """Identify organizational strengths."""
        strengths = []
        for domain, score in domain_scores.items():
            if score >= 4.0:
                strengths.append(
                    f"Strong {domain.value.replace('_', ' ')} capabilities"
                )
        return strengths

    def _identify_improvement_areas(
        self, domain_scores: Dict[GovernanceDomain, float]
    ) -> List[str]:
        """Identify areas for improvement."""
        areas = []
        for domain, score in domain_scores.items():
            if 2.0 <= score < 3.5:
                areas.append(
                    f"{domain.value.replace('_', ' ').title()} standardization needed"
                )
        return areas

    def _identify_critical_gaps(
        self, domain_scores: Dict[GovernanceDomain, float]
    ) -> List[str]:
        """Identify critical gaps requiring immediate attention."""
        gaps = []
        for domain, score in domain_scores.items():
            if score < 2.0:
                gaps.append(f"Critical gap in {domain.value.replace('_', ' ')}")
        return gaps

    def _generate_next_steps(self, result: AssessmentResult) -> List[str]:
        """Generate immediate next steps."""
        next_steps = []

        # Always include constitutional compliance as first step
        if result.constitutional_compliance_score < 0.8:
            next_steps.append(
                "Prioritize constitutional compliance framework implementation"
            )

        # Add top 3 improvement areas
        sorted_domains = sorted(result.domain_scores.items(), key=lambda x: x[1])
        for domain, score in sorted_domains[:3]:
            if score < 3.0:
                next_steps.append(
                    f"Develop {domain.value.replace('_', ' ')} improvement plan"
                )

        # Add assessment follow-up
        next_steps.append("Schedule follow-up assessment in 6 months")

        return next_steps

    def save_assessment(self, result: AssessmentResult, filepath: str):
        """Save assessment result to file."""
        report = self.generate_assessment_report(result)
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Assessment saved to {filepath}")

    def load_assessment(self, filepath: str) -> Dict[str, Any]:
        """Load assessment result from file."""
        with open(filepath, "r") as f:
            return json.load(f)


def main():
    """Example usage of the Governance Maturity Framework."""
    framework = GovernanceMaturityFramework()

    # Example assessment responses (1-5 scale)
    sample_responses = {
        "const_policy_adherence": 3,
        "const_decision_validation": 2,
        "policy_lifecycle": 3,
        "decision_transparency": 2,
        "stakeholder_participation": 2,
        "governance_risk_mgmt": 3,
        "audit_effectiveness": 3,
        "tech_governance": 4,
    }

    # Conduct assessment
    result = framework.conduct_assessment("sample_org_001", sample_responses)

    # Generate and display report
    report = framework.generate_assessment_report(result)
    print(json.dumps(report, indent=2, default=str))

    # Save assessment
    framework.save_assessment(result, "sample_assessment.json")


if __name__ == "__main__":
    main()
