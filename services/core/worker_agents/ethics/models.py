"""
Data models for the Ethics Agent.

This module contains all Pydantic models used by the ethics agent
for analysis results, bias detection, and fairness evaluation.
"""

from typing import Any

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class EthicalAnalysisResult(BaseModel):
    """
    Result of ethical analysis performed by the ethics agent.

    Example:
        result = EthicalAnalysisResult(
            approved=True,
            risk_level="low",
            confidence=0.85,
            recommendations=["Monitor for bias in deployment"]
        )
    """

    approved: bool
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    confidence: float = Field(ge=0.0, le=1.0)
    bias_assessment: dict[str, Any] = Field(default_factory=dict)
    fairness_evaluation: dict[str, Any] = Field(default_factory=dict)
    harm_potential: dict[str, Any] = Field(default_factory=dict)
    stakeholder_impact: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    constitutional_compliance: dict[str, Any] = Field(default_factory=dict)
    analysis_metadata: dict[str, Any] = Field(default_factory=dict)


class BiasAssessment(BaseModel):
    """
    Bias assessment results.

    Example:
        assessment = BiasAssessment(
            demographic_parity=True,
            equalized_odds=False,
            bias_score=0.15
        )
    """

    demographic_parity: bool = False
    equalized_odds: bool = False
    calibration: bool = False
    individual_fairness: bool = False
    bias_score: float = Field(default=0.0, ge=0.0, le=1.0)
    affected_groups: list[str] = Field(default_factory=list)
    mitigation_strategies: list[str] = Field(default_factory=list)


class FairnessEvaluation(BaseModel):
    """
    Fairness evaluation metrics and results.

    Example:
        evaluation = FairnessEvaluation(
            fairness_score=0.78,
            meets_criteria=True,
            evaluation_method="statistical_parity"
        )
    """

    fairness_score: float = Field(ge=0.0, le=1.0)
    meets_criteria: bool
    evaluation_method: str
    metrics: dict[str, float] = Field(default_factory=dict)
    threshold_violations: list[str] = Field(default_factory=list)


class HarmAssessment(BaseModel):
    """
    Harm potential assessment.

    Example:
        harm = HarmAssessment(
            potential_level="low",
            harm_types=["privacy"],
            mitigation_required=False
        )
    """

    potential_level: str  # 'minimal', 'low', 'medium', 'high', 'severe'
    harm_types: list[str] = Field(default_factory=list)
    affected_populations: list[str] = Field(default_factory=list)
    mitigation_required: bool = False
    severity_score: float = Field(default=0.0, ge=0.0, le=1.0)


class StakeholderImpact(BaseModel):
    """
    Stakeholder impact analysis.

    Example:
        impact = StakeholderImpact(
            primary_stakeholders=["users", "developers"],
            impact_score=0.6,
            consultation_required=True
        )
    """

    primary_stakeholders: list[str] = Field(default_factory=list)
    secondary_stakeholders: list[str] = Field(default_factory=list)
    impact_score: float = Field(ge=0.0, le=1.0)
    consultation_required: bool = False
    impact_areas: dict[str, str] = Field(default_factory=dict)
