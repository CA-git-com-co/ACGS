#!/usr/bin/env python3
"""
ACGS Governance Maturity Assessment API

Web-based API for conducting governance maturity assessments
and generating improvement recommendations.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from governance_maturity_framework import (
    GovernanceDomain,
    GovernanceMaturityFramework,
)
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for API
class AssessmentRequest(BaseModel):
    organization_id: str = Field(..., description="Unique organization identifier")
    organization_name: str = Field(..., description="Organization name")
    assessor_name: str = Field(..., description="Name of person conducting assessment")
    responses: dict[str, int] = Field(
        ..., description="Assessment responses (1-5 scale)"
    )
    notes: str | None = Field(None, description="Additional assessment notes")


class AssessmentResponse(BaseModel):
    assessment_id: str
    organization_id: str
    overall_maturity_level: float
    maturity_level_name: str
    constitutional_compliance_score: float
    domain_scores: dict[str, float]
    recommendations: list[str]
    improvement_roadmap: list[dict[str, Any]]
    constitutional_hash: str


class MaturityIndicatorInfo(BaseModel):
    id: str
    name: str
    description: str
    domain: str
    criteria: dict[str, list[str]]
    weight: float


class DomainSummary(BaseModel):
    domain: str
    indicators: list[MaturityIndicatorInfo]
    description: str


# Initialize FastAPI app
app = FastAPI(
    title="ACGS Governance Maturity Assessment API",
    description="Constitutional governance maturity assessment and improvement framework",
    version="1.0.0",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize framework
framework = GovernanceMaturityFramework()


async def validate_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> bool:
    """Validate authentication token."""
    # Simplified token validation - implement proper validation in production
    return (
        credentials.credentials.startswith("acgs_")
        and len(credentials.credentials) > 20
    )


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "governance_maturity_assessment",
        "constitutional_hash": framework.constitutional_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/domains", response_model=list[DomainSummary])
async def get_assessment_domains():
    """Get all governance domains and their indicators."""
    domains = []

    for domain in GovernanceDomain:
        domain_indicators = [
            ind for ind in framework.indicators.values() if ind.domain == domain
        ]

        indicators_info = []
        for ind in domain_indicators:
            indicators_info.append(
                MaturityIndicatorInfo(
                    id=ind.id,
                    name=ind.name,
                    description=ind.description,
                    domain=ind.domain.value,
                    criteria={
                        "level_1": ind.level_1_criteria,
                        "level_2": ind.level_2_criteria,
                        "level_3": ind.level_3_criteria,
                        "level_4": ind.level_4_criteria,
                        "level_5": ind.level_5_criteria,
                    },
                    weight=ind.weight,
                )
            )

        domains.append(
            DomainSummary(
                domain=domain.value,
                indicators=indicators_info,
                description=f"Assessment indicators for {domain.value.replace('_', ' ')}",
            )
        )

    return domains


@app.get("/api/v1/indicators")
async def get_all_indicators():
    """Get all maturity indicators with detailed criteria."""
    indicators = {}

    for ind_id, ind in framework.indicators.items():
        indicators[ind_id] = {
            "id": ind.id,
            "name": ind.name,
            "description": ind.description,
            "domain": ind.domain.value,
            "criteria": {
                "1_initial": ind.level_1_criteria,
                "2_managed": ind.level_2_criteria,
                "3_defined": ind.level_3_criteria,
                "4_quantitatively_managed": ind.level_4_criteria,
                "5_optimizing": ind.level_5_criteria,
            },
            "weight": ind.weight,
            "constitutional_hash": ind.constitutional_hash,
        }

    return indicators


@app.post("/api/v1/assessments", response_model=AssessmentResponse)
async def conduct_assessment(
    request: AssessmentRequest,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """Conduct a governance maturity assessment."""
    if not await validate_token(credentials):
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    try:
        # Validate responses
        for indicator_id, score in request.responses.items():
            if indicator_id not in framework.indicators:
                raise HTTPException(
                    status_code=400, detail=f"Unknown indicator: {indicator_id}"
                )
            if not 1 <= score <= 5:
                raise HTTPException(
                    status_code=400,
                    detail=f"Score must be between 1-5, got {score} for {indicator_id}",
                )

        # Conduct assessment
        result = framework.conduct_assessment(
            request.organization_id, request.responses
        )

        # Generate assessment ID
        assessment_id = f"assess_{request.organization_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create response
        response = AssessmentResponse(
            assessment_id=assessment_id,
            organization_id=result.organization_id,
            overall_maturity_level=result.overall_maturity_level,
            maturity_level_name=framework._get_maturity_level_name(
                result.overall_maturity_level
            ),
            constitutional_compliance_score=result.constitutional_compliance_score,
            domain_scores={
                domain.value: score for domain, score in result.domain_scores.items()
            },
            recommendations=result.recommendations,
            improvement_roadmap=result.improvement_roadmap,
            constitutional_hash=result.constitutional_hash,
        )

        logger.info(
            f"Assessment completed for {request.organization_id}: {response.maturity_level_name}"
        )
        return response

    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {e!s}")


@app.get("/api/v1/assessments/{organization_id}/history")
async def get_assessment_history(
    organization_id: str, credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Get assessment history for an organization."""
    if not await validate_token(credentials):
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    # Filter assessments for the organization
    org_assessments = [
        {
            "assessment_date": result.assessment_date.isoformat(),
            "overall_maturity_level": result.overall_maturity_level,
            "maturity_level_name": framework._get_maturity_level_name(
                result.overall_maturity_level
            ),
            "constitutional_compliance_score": result.constitutional_compliance_score,
            "domain_scores": {
                domain.value: score for domain, score in result.domain_scores.items()
            },
        }
        for result in framework.assessment_history
        if result.organization_id == organization_id
    ]

    return {
        "organization_id": organization_id,
        "assessment_count": len(org_assessments),
        "assessments": org_assessments,
    }


@app.get("/api/v1/reports/{organization_id}/latest")
async def get_latest_report(
    organization_id: str, credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Get the latest comprehensive assessment report for an organization."""
    if not await validate_token(credentials):
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    # Find latest assessment
    org_assessments = [
        result
        for result in framework.assessment_history
        if result.organization_id == organization_id
    ]

    if not org_assessments:
        raise HTTPException(
            status_code=404, detail="No assessments found for organization"
        )

    latest_assessment = max(org_assessments, key=lambda x: x.assessment_date)
    report = framework.generate_assessment_report(latest_assessment)

    return report


@app.get("/api/v1/benchmarks")
async def get_industry_benchmarks():
    """Get industry benchmarks for governance maturity."""
    # Simulated industry benchmarks - in production, calculate from real data
    return {
        "industry_averages": {
            "overall_maturity": 2.8,
            "constitutional_compliance": 0.72,
            "domains": {
                "constitutional_compliance": 2.9,
                "policy_management": 2.7,
                "decision_transparency": 2.6,
                "stakeholder_engagement": 2.5,
                "risk_management": 3.0,
                "audit_and_monitoring": 2.8,
                "change_management": 2.4,
                "training_and_competency": 2.3,
                "technology_governance": 3.2,
                "performance_measurement": 2.7,
            },
        },
        "top_quartile": {
            "overall_maturity": 4.2,
            "constitutional_compliance": 0.92,
            "domains": {
                "constitutional_compliance": 4.3,
                "policy_management": 4.1,
                "decision_transparency": 4.0,
                "stakeholder_engagement": 3.9,
                "risk_management": 4.4,
                "audit_and_monitoring": 4.2,
                "change_management": 3.8,
                "training_and_competency": 3.7,
                "technology_governance": 4.6,
                "performance_measurement": 4.1,
            },
        },
        "constitutional_hash": framework.constitutional_hash,
    }


@app.post("/api/v1/recommendations/generate")
async def generate_custom_recommendations(
    request: dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """Generate custom improvement recommendations based on specific criteria."""
    if not await validate_token(credentials):
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    organization_id = request.get("organization_id")
    focus_areas = request.get("focus_areas", [])
    timeline = request.get("timeline", "12_months")
    budget_level = request.get("budget_level", "medium")

    # Generate customized recommendations
    recommendations = {
        "organization_id": organization_id,
        "focus_areas": focus_areas,
        "timeline": timeline,
        "budget_level": budget_level,
        "recommendations": [],
        "implementation_plan": [],
        "constitutional_hash": framework.constitutional_hash,
    }

    # Add focus area specific recommendations
    for area in focus_areas:
        if area == "constitutional_compliance":
            recommendations["recommendations"].append(
                {
                    "area": "Constitutional Compliance",
                    "priority": "Critical",
                    "description": "Implement comprehensive constitutional AI validation framework",
                    "effort": "High",
                    "timeline": "3-6 months",
                    "expected_impact": "Significant improvement in constitutional compliance score",
                }
            )
        elif area == "stakeholder_engagement":
            recommendations["recommendations"].append(
                {
                    "area": "Stakeholder Engagement",
                    "priority": "High",
                    "description": "Establish structured stakeholder consultation framework",
                    "effort": "Medium",
                    "timeline": "2-4 months",
                    "expected_impact": "Enhanced democratic legitimacy and transparency",
                }
            )

    return recommendations


async def start_server(host: str = "0.0.0.0", port: int = 8030):
    """Start the assessment API server."""
    logger.info(f"🚀 Starting Governance Maturity Assessment API on {host}:{port}")
    logger.info(f"📜 Constitutional Hash: {framework.constitutional_hash}")

    config = uvicorn.Config(app=app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    """Main function to run the assessment API."""
    try:
        await start_server()
    except Exception as e:
        logger.error(f"❌ Assessment API failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
