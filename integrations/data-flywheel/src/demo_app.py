#!/usr/bin/env python3
"""
ACGS-1 Data Flywheel Integration Demo API
A minimal working demonstration of the constitutional governance integration
"""

import logging
import os
from datetime import datetime

import httpx
import uvicorn
from fastapi import FastAPI
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
    constitutional_requirements: dict | None = None
    governance_context: dict | None = None


class JobResponse(BaseModel):
    id: str
    status: str
    message: str


class ACGSHealthResponse(BaseModel):
    overall_status: str
    services: dict[str, bool]
    constitutional_validation_available: bool
    governance_workflows_operational: bool


# Helper functions
async def check_acgs_service_health() -> dict[str, bool]:
    """Check health of all ACGS-1 services"""
    health_status = {}

    # Use secure SSL verification for all connections
    async with httpx.AsyncClient(verify=True) as client:
        for service_name, service_url in ACGS_SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                health_status[service_name] = response.status_code == 200
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                health_status[service_name] = False

    return health_status


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


if __name__ == "__main__":
    logger.info("Starting ACGS-1 Data Flywheel Integration Demo API...")
    uvicorn.run(
        "demo_app:app", host="0.0.0.0", port=8010, reload=True, log_level="info"
    )
