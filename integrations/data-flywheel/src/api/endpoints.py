# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.api.db import get_db
from src.api.job_service import cancel_job, delete_job, get_job_details
from src.api.models import FlywheelRun
from src.api.schemas import (
    FlywheelRunStatus,
    JobCancelResponse,
    JobDeleteResponse,
    JobDetailResponse,
    JobListItem,
    JobRequest,
    JobResponse,
    JobsListResponse,
)
from src.log_utils import setup_logging
from src.tasks.tasks import run_nim_workflow_dag

# ACGS-1 Constitutional Governance Integration
from src.constitutional.compliance_validator import ConstitutionalComplianceValidator
from src.constitutional.acgs_integration import ACGSServiceIntegration

logger = setup_logging("data_flywheel.api.endpoints")

router = APIRouter()

# Initialize ACGS-1 integration components
acgs_integration = ACGSServiceIntegration()
compliance_validator = ConstitutionalComplianceValidator()


# ACGS-1 Constitutional Governance Schemas
class ConstitutionalJobRequest(BaseModel):
    """Enhanced job request with constitutional governance requirements"""

    workload_id: str
    client_id: str = "acgs_governance"
    constitutional_requirements: Optional[Dict] = None
    governance_context: Optional[Dict] = None
    data_split_config: Optional[Dict] = None


class ConstitutionalComplianceResponse(BaseModel):
    """Constitutional compliance validation response"""

    job_id: str
    overall_compliance_score: float
    compliant: bool
    principle_scores: Dict[str, float]
    recommendations: List[str]
    validation_timestamp: str


class ACGSHealthResponse(BaseModel):
    """ACGS-1 services health status response"""

    overall_status: str
    services: Dict[str, bool]
    constitutional_validation_available: bool
    governance_workflows_operational: bool


@router.post("/jobs", response_model=JobResponse)
async def create_job(request: JobRequest) -> JobResponse:
    """
    Create a new job that runs the NIM workflow.
    """
    # create entry for current time, workload_id, and model_name
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"Request received at {current_time} for workload_id {request.workload_id} and client_id {request.client_id}"
    logger.info(entry)

    # Create FlywheelRun document
    flywheel_run = FlywheelRun(
        workload_id=request.workload_id,
        client_id=request.client_id,
        started_at=datetime.utcnow(),
        num_records=0,  # Will be updated when datasets are created
        nims=[],
        status=FlywheelRunStatus.PENDING,
    )

    # Save to MongoDB
    db = get_db()
    result = db.flywheel_runs.insert_one(flywheel_run.to_mongo())
    flywheel_run.id = str(result.inserted_id)

    # Call the NIM workflow task asynchronously. This will be executed
    # in the background.
    run_nim_workflow_dag.delay(
        workload_id=request.workload_id,
        flywheel_run_id=flywheel_run.id,
        client_id=request.client_id,
        data_split_config=(
            request.data_split_config.model_dump()
            if request.data_split_config
            else None
        ),
    )

    return JobResponse(
        id=flywheel_run.id, status="queued", message="NIM workflow started"
    )


@router.get("/jobs", response_model=JobsListResponse)
async def get_jobs() -> JobsListResponse:
    """
    Get a list of all active and recent jobs.
    """
    db = get_db()
    jobs: list[JobListItem] = []

    # Get all FlywheelRun documents
    for doc in db.flywheel_runs.find():
        flywheel_run = FlywheelRun.from_mongo(doc)
        job = JobListItem(
            id=str(flywheel_run.id),
            workload_id=flywheel_run.workload_id,
            client_id=flywheel_run.client_id,
            status=flywheel_run.status,
            started_at=flywheel_run.started_at,
            finished_at=flywheel_run.finished_at,
            datasets=flywheel_run.datasets,
            error=flywheel_run.error,
        )
        jobs.append(job)

    return JobsListResponse(jobs=jobs)


@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job(job_id: str) -> JobDetailResponse:
    """
    Get the status and result of a job, including detailed information about all tasks in the workflow.
    """
    return get_job_details(job_id)


@router.delete("/jobs/{job_id}", response_model=JobDeleteResponse)
async def delete_job_endpoint(job_id: str) -> JobDeleteResponse:
    """
    Delete a job and all its associated resources from the database.
    This is an asynchronous operation - the endpoint returns immediately while
    the deletion continues in the background.

    If the job is still running, it must be cancelled first.
    """
    return delete_job(job_id)


@router.post("/jobs/{job_id}/cancel", response_model=JobCancelResponse)
async def cancel_job_endpoint(job_id: str) -> JobCancelResponse:
    """
    Cancel a running job.
    This will stop the job execution and mark it as cancelled.

    The job must be in a running state to be cancelled.
    Already finished jobs cannot be cancelled.
    """
    return cancel_job(job_id)


# ACGS-1 Constitutional Governance Endpoints


@router.post("/constitutional/jobs", response_model=JobResponse)
async def create_constitutional_job(request: ConstitutionalJobRequest) -> JobResponse:
    """
    Create a new constitutional governance optimization job.
    This endpoint integrates with ACGS-1 services to ensure constitutional compliance.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"Constitutional job request received at {current_time} for workload_id {request.workload_id}"
    logger.info(entry)

    # Validate ACGS-1 service health before proceeding
    health_status = await acgs_integration.validate_service_health()
    unhealthy_services = [
        name for name, healthy in health_status.items() if not healthy
    ]

    if unhealthy_services:
        logger.warning(f"Some ACGS-1 services are unhealthy: {unhealthy_services}")
        # Continue with warning but don't fail

    # Get constitutional context for the workload
    constitutional_context = await acgs_integration.get_constitutional_context(
        request.workload_id
    )

    # Create enhanced FlywheelRun document with constitutional requirements
    flywheel_run = FlywheelRun(
        workload_id=request.workload_id,
        client_id=request.client_id,
        started_at=datetime.utcnow(),
        num_records=0,
        nims=[],
        status=FlywheelRunStatus.PENDING,
        # Add constitutional governance metadata
        metadata={
            "constitutional_requirements": request.constitutional_requirements or {},
            "governance_context": request.governance_context or {},
            "constitutional_context": constitutional_context,
            "acgs_service_health": health_status,
        },
    )

    # Save to MongoDB
    db = get_db()
    result = db.flywheel_runs.insert_one(flywheel_run.to_mongo())
    flywheel_run.id = str(result.inserted_id)

    # Call the enhanced NIM workflow task with constitutional validation
    run_nim_workflow_dag.delay(
        workload_id=request.workload_id,
        flywheel_run_id=flywheel_run.id,
        client_id=request.client_id,
        data_split_config=request.data_split_config,
        constitutional_requirements=request.constitutional_requirements,
        governance_context=request.governance_context,
    )

    return JobResponse(
        id=flywheel_run.id,
        status="queued",
        message="Constitutional governance optimization workflow started",
    )


@router.get(
    "/constitutional/compliance/{job_id}",
    response_model=ConstitutionalComplianceResponse,
)
async def get_constitutional_compliance(
    job_id: str,
) -> ConstitutionalComplianceResponse:
    """
    Get constitutional compliance validation results for a specific job.
    """
    db = get_db()
    flywheel_run_doc = db.flywheel_runs.find_one({"_id": job_id})

    if not flywheel_run_doc:
        raise HTTPException(status_code=404, detail="Job not found")

    flywheel_run = FlywheelRun.from_mongo(flywheel_run_doc)

    # Extract constitutional compliance results from metadata
    metadata = flywheel_run.metadata or {}
    compliance_results = metadata.get("constitutional_compliance", {})

    if not compliance_results:
        raise HTTPException(
            status_code=404,
            detail="Constitutional compliance results not available yet",
        )

    return ConstitutionalComplianceResponse(
        job_id=job_id,
        overall_compliance_score=compliance_results.get("overall_score", 0.0),
        compliant=compliance_results.get("compliant", False),
        principle_scores=compliance_results.get("principle_scores", {}),
        recommendations=compliance_results.get("recommendations", []),
        validation_timestamp=compliance_results.get("timestamp", ""),
    )


@router.get("/constitutional/health", response_model=ACGSHealthResponse)
async def get_acgs_health() -> ACGSHealthResponse:
    """
    Get health status of ACGS-1 constitutional governance services.
    """
    health_status = await acgs_integration.validate_service_health()

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


@router.get("/constitutional/workloads")
async def get_governance_workloads():
    """
    Get available governance workloads and their service mappings.
    """
    workload_mapping = acgs_integration.get_workload_service_mapping()
    optimization_targets = acgs_integration.get_optimization_targets()
    evaluation_criteria = acgs_integration.get_evaluation_criteria()

    return {
        "workload_mapping": workload_mapping,
        "optimization_targets": optimization_targets,
        "evaluation_criteria": evaluation_criteria,
        "available_workloads": list(workload_mapping.keys()),
    }


@router.post("/constitutional/traffic/collect")
async def collect_governance_traffic(
    hours: int = Query(24, description="Hours of traffic to collect"),
    workload_filter: Optional[List[str]] = Query(
        None, description="Filter by workload IDs"
    ),
):
    """
    Manually trigger collection of governance traffic from ACGS-1 services.
    """
    from datetime import timedelta

    try:
        traffic_logs = await acgs_integration.collect_governance_traffic(
            time_range=timedelta(hours=hours), workload_filter=workload_filter
        )

        return {
            "status": "success",
            "collected_logs": len(traffic_logs),
            "time_range_hours": hours,
            "workload_filter": workload_filter,
            "message": f"Collected {len(traffic_logs)} governance traffic logs",
        }

    except Exception as e:
        logger.error(f"Failed to collect governance traffic: {e}")
        raise HTTPException(
            status_code=500, detail=f"Traffic collection failed: {str(e)}"
        )


@router.get("/constitutional/metrics/{job_id}")
async def get_constitutional_metrics(job_id: str):
    """
    Get detailed constitutional governance metrics for a specific job.
    """
    db = get_db()
    flywheel_run_doc = db.flywheel_runs.find_one({"_id": job_id})

    if not flywheel_run_doc:
        raise HTTPException(status_code=404, detail="Job not found")

    flywheel_run = FlywheelRun.from_mongo(flywheel_run_doc)
    metadata = flywheel_run.metadata or {}

    return {
        "job_id": job_id,
        "workload_id": flywheel_run.workload_id,
        "constitutional_compliance": metadata.get("constitutional_compliance", {}),
        "governance_metrics": metadata.get("governance_metrics", {}),
        "optimization_results": metadata.get("optimization_results", {}),
        "performance_comparison": metadata.get("performance_comparison", {}),
        "cost_analysis": metadata.get("cost_analysis", {}),
    }


@router.post("/constitutional/validate")
async def validate_constitutional_compliance(
    model_output: str, expected_output: str, governance_context: Dict, workload_id: str
):
    """
    Manually validate constitutional compliance for model outputs.
    """
    try:
        compliance_results = await compliance_validator.validate_model_output(
            model_output=model_output,
            expected_output=expected_output,
            governance_context=governance_context,
            workload_id=workload_id,
        )

        compliance_summary = compliance_validator.get_compliance_summary(
            compliance_results
        )

        return {
            "validation_results": [
                {
                    "principle": result.principle.value,
                    "score": result.score,
                    "level": result.level.value,
                    "explanation": result.explanation,
                    "recommendations": result.recommendations,
                }
                for result in compliance_results
            ],
            "summary": compliance_summary,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Constitutional validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Enhanced health check including ACGS-1 integration status.
    """
    # Check basic Data Flywheel health
    basic_health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "acgs_data_flywheel",
    }

    # Check ACGS-1 integration health
    try:
        acgs_health = await acgs_integration.validate_service_health()
        constitutional_validator_health = (
            await compliance_validator.check_acgs_service_health()
        )

        basic_health["acgs_integration"] = {
            "services": acgs_health,
            "constitutional_validator": constitutional_validator_health,
            "integration_status": (
                "operational" if any(acgs_health.values()) else "degraded"
            ),
        }

    except Exception as e:
        logger.error(f"ACGS-1 health check failed: {e}")
        basic_health["acgs_integration"] = {"status": "error", "error": str(e)}

    return basic_health
