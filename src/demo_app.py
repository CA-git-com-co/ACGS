#!/usr/bin/env python3
"""
ACGS-1 Data Flywheel Integration Demo API
A minimal working demonstration of the constitutional governance integration
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ACGS-1 Data Flywheel Integration Demo",
    description="Constitutional Governance AI Model Optimization Demo",
    version="1.0.0",
)

# Configuration
ACGS_BASE_URL = os.getenv("ACGS_BASE_URL", "http://localhost")
CONSTITUTIONAL_COMPLIANCE_THRESHOLD = float(
    os.getenv("CONSTITUTIONAL_COMPLIANCE_THRESHOLD", "0.95")
)

# ACGS-1 service endpoints
ACGS_SERVICES = {
    "auth_service": f"{ACGS_BASE_URL}:8000",
    "ac_service": f"{ACGS_BASE_URL}:8001",
    "integrity_service": f"{ACGS_BASE_URL}:8002",
    "fv_service": f"{ACGS_BASE_URL}:8003",
    "gs_service": f"{ACGS_BASE_URL}:8004",
    "pgc_service": f"{ACGS_BASE_URL}:8005",
    "ec_service": f"{ACGS_BASE_URL}:8006",
}

# Constitutional principles
CONSTITUTIONAL_PRINCIPLES = [
    "democratic_participation",
    "transparency",
    "accountability",
    "rule_of_law",
    "human_rights",
    "sustainability",
    "public_welfare",
    "equity",
    "privacy_protection",
    "due_process",
]


# Pydantic models
class ConstitutionalJobRequest(BaseModel):
    workload_id: str
    client_id: str = "acgs_governance"
    constitutional_requirements: Optional[Dict] = None
    governance_context: Optional[Dict] = None


class ConstitutionalComplianceResponse(BaseModel):
    job_id: str
    overall_compliance_score: float
    compliant: bool
    principle_scores: Dict[str, float]
    recommendations: List[str]
    validation_timestamp: str


class ACGSHealthResponse(BaseModel):
    overall_status: str
    services: Dict[str, bool]
    constitutional_validation_available: bool
    governance_workflows_operational: bool


class JobResponse(BaseModel):
    id: str
    status: str
    message: str


# Helper functions
async def check_acgs_service_health() -> Dict[str, bool]:
    """Check health of all ACGS-1 services"""
    health_status = {}

    async with httpx.AsyncClient() as client:
        for service_name, service_url in ACGS_SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                health_status[service_name] = response.status_code == 200
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                health_status[service_name] = False

    return health_status


async def validate_constitutional_compliance(
    model_output: str, expected_output: str, governance_context: Dict, workload_id: str
) -> Dict:
    """Simulate constitutional compliance validation"""

    # Simple heuristic-based validation for demo
    compliance_scores = {}

    for principle in CONSTITUTIONAL_PRINCIPLES:
        # Basic keyword matching for demo purposes
        score = 0.8  # Base score

        if principle == "transparency":
            if any(
                word in model_output.lower()
                for word in ["explain", "clear", "transparent", "open"]
            ):
                score += 0.15
        elif principle == "accountability":
            if any(
                word in model_output.lower()
                for word in ["responsible", "accountable", "oversight"]
            ):
                score += 0.15
        elif principle == "democratic_participation":
            if any(
                word in model_output.lower()
                for word in ["democratic", "participation", "inclusive", "citizen"]
            ):
                score += 0.15
        elif principle == "human_rights":
            if any(
                word in model_output.lower()
                for word in ["rights", "dignity", "equality", "fairness"]
            ):
                score += 0.15

        compliance_scores[principle] = min(score, 1.0)

    overall_score = sum(compliance_scores.values()) / len(compliance_scores)

    return {
        "overall_score": overall_score,
        "compliant": overall_score >= CONSTITUTIONAL_COMPLIANCE_THRESHOLD,
        "principle_scores": compliance_scores,
        "recommendations": (
            ["Enhance transparency language"] if overall_score < 0.9 else []
        ),
        "timestamp": datetime.utcnow().isoformat(),
    }


# API Endpoints
@app.get("/health")
async def health_check():
    """Enhanced health check including ACGS-1 integration status"""
    acgs_health = await check_acgs_service_health()

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "acgs_data_flywheel_demo",
        "acgs_integration": {
            "services": acgs_health,
            "integration_status": (
                "operational" if any(acgs_health.values()) else "degraded"
            ),
        },
    }


@app.get("/constitutional/health", response_model=ACGSHealthResponse)
async def get_acgs_health():
    """Get health status of ACGS-1 constitutional governance services"""
    health_status = await check_acgs_service_health()

    # Determine overall status
    all_healthy = all(health_status.values())
    critical_services = ["ac_service", "fv_service", "gs_service", "pgc_service"]
    critical_healthy = all(
        health_status.get(service, False) for service in critical_services
    )

    if all_healthy:
        overall_status = "healthy"
    elif critical_healthy:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    return ACGSHealthResponse(
        overall_status=overall_status,
        services=health_status,
        constitutional_validation_available=health_status.get("ac_service", False),
        governance_workflows_operational=critical_healthy,
    )


@app.get("/constitutional/workloads")
async def get_governance_workloads():
    """Get available governance workloads and their service mappings"""
    return {
        "workload_mapping": {
            "policy_synthesis": "gs_service",
            "formal_verification": "fv_service",
            "constitutional_analysis": "ac_service",
            "integrity_validation": "integrity_service",
            "policy_governance": "pgc_service",
            "evolutionary_computation": "ec_service",
        },
        "optimization_targets": {
            "cost_reduction": 0.80,
            "response_time": 500,
            "accuracy_threshold": 0.95,
            "constitutional_compliance": 0.98,
        },
        "evaluation_criteria": {
            "constitutional_adherence": 0.4,
            "performance_accuracy": 0.3,
            "cost_efficiency": 0.2,
            "response_time": 0.1,
        },
        "available_workloads": [
            "policy_synthesis",
            "formal_verification",
            "constitutional_analysis",
            "integrity_validation",
            "policy_governance",
            "evolutionary_computation",
        ],
    }


@app.post("/constitutional/jobs", response_model=JobResponse)
async def create_constitutional_job(request: ConstitutionalJobRequest):
    """Create a new constitutional governance optimization job"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(
        f"Constitutional job request received at {current_time} for workload_id {request.workload_id}"
    )

    # Validate ACGS-1 service health
    health_status = await check_acgs_service_health()
    unhealthy_services = [
        name for name, healthy in health_status.items() if not healthy
    ]

    if unhealthy_services:
        logger.warning(f"Some ACGS-1 services are unhealthy: {unhealthy_services}")

    # Generate a demo job ID
    job_id = f"demo_job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    return JobResponse(
        id=job_id,
        status="queued",
        message="Constitutional governance optimization workflow started (demo mode)",
    )


@app.post("/constitutional/validate")
async def validate_constitutional_compliance_endpoint(
    model_output: str, expected_output: str, governance_context: Dict, workload_id: str
):
    """Manually validate constitutional compliance for model outputs"""
    try:
        compliance_results = await validate_constitutional_compliance(
            model_output=model_output,
            expected_output=expected_output,
            governance_context=governance_context,
            workload_id=workload_id,
        )

        return {
            "validation_results": [
                {
                    "principle": principle,
                    "score": score,
                    "level": (
                        "high" if score > 0.9 else "medium" if score > 0.7 else "low"
                    ),
                    "explanation": f"Compliance assessment for {principle}",
                    "recommendations": (
                        ["Enhance constitutional language"] if score < 0.9 else []
                    ),
                }
                for principle, score in compliance_results["principle_scores"].items()
            ],
            "summary": {
                "overall_score": compliance_results["overall_score"],
                "compliant": compliance_results["compliant"],
                "threshold": CONSTITUTIONAL_COMPLIANCE_THRESHOLD,
                "total_principles_evaluated": len(CONSTITUTIONAL_PRINCIPLES),
                "summary": f"Constitutional compliance: {compliance_results['overall_score']:.1%}",
            },
            "timestamp": compliance_results["timestamp"],
        }

    except Exception as e:
        logger.error(f"Constitutional validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.post("/constitutional/traffic/collect")
async def collect_governance_traffic(
    hours: int = 24, workload_filter: Optional[List[str]] = None
):
    """Manually trigger collection of governance traffic from ACGS-1 services"""
    try:
        # Simulate traffic collection for demo
        collected_logs = 42  # Demo value

        return {
            "status": "success",
            "collected_logs": collected_logs,
            "time_range_hours": hours,
            "workload_filter": workload_filter,
            "message": f"Collected {collected_logs} governance traffic logs (demo mode)",
        }

    except Exception as e:
        logger.error(f"Failed to collect governance traffic: {e}")
        raise HTTPException(
            status_code=500, detail=f"Traffic collection failed: {str(e)}"
        )


if __name__ == "__main__":
    logger.info("Starting ACGS-1 Data Flywheel Integration Demo API...")
    uvicorn.run(
        "demo_app:app", host="0.0.0.0", port=8010, reload=True, log_level="info"
    )
