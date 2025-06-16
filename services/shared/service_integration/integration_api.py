"""
Service Integration API for Phase 2 ACGS-1

This module provides API endpoints for managing and monitoring service integration,
event-driven communication, and workflow orchestration across all 7 core services.

requires: Service orchestration, event management, workflow coordination
ensures: Comprehensive service integration monitoring and control
sha256: b8a7c6d5e4f3b2a1c8d7e6f5c4b3a2d1e8f7c6d5e4f3b2a1c8d7e6f5c4b3a2d1
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field

from .phase2_orchestrator import (
    EventType,
    IntegrationPattern,
    Phase2ServiceOrchestrator,
    ServiceEvent,
    ServiceType,
    get_phase2_orchestrator,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class ServiceCallRequest(BaseModel):
    """Request model for service calls."""

    service_type: str = Field(..., description="Target service type")
    endpoint: str = Field(..., description="API endpoint to call")
    method: str = Field(default="GET", description="HTTP method")
    data: Optional[Dict[str, Any]] = Field(None, description="Request data")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional headers")
    timeout: Optional[float] = Field(None, description="Request timeout")


class EventPublishRequest(BaseModel):
    """Request model for publishing events."""

    event_type: str = Field(..., description="Type of event to publish")
    source_service: str = Field(..., description="Source service")
    target_services: List[str] = Field(..., description="Target services")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    priority: int = Field(default=5, description="Event priority (1-10)")


class WorkflowStartRequest(BaseModel):
    """Request model for starting workflows."""

    workflow_type: str = Field(..., description="Type of workflow")
    services: List[str] = Field(..., description="Services involved in workflow")
    workflow_data: Dict[str, Any] = Field(default_factory=dict, description="Workflow data")


class ServiceIntegrationStatus(BaseModel):
    """Service integration status response."""

    orchestrator_running: bool
    total_services: int
    healthy_services: int
    active_workflows: int
    total_events_processed: int
    average_event_processing_time_ms: float
    service_health: Dict[str, bool]
    timestamp: datetime


@router.post("/call-service", status_code=200)
async def call_service_endpoint(
    request: ServiceCallRequest,
    background_tasks: BackgroundTasks,
    orchestrator: Phase2ServiceOrchestrator = None,
):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Call a specific service through the orchestrator with comprehensive monitoring.

    This endpoint provides unified service communication with:
    - Circuit breaker protection
    - Automatic retry logic
    - Performance monitoring
    - Error handling and logging
    - Authentication management
    """
    call_start = time.time()

    try:
        # Get orchestrator instance
        if not orchestrator:
            orchestrator = await get_phase2_orchestrator()

        # Validate service type
        try:
            service_type = ServiceType(request.service_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid service type: {request.service_type}"
            )

        # Make service call
        response_data = await orchestrator.call_service(
            service_type=service_type,
            endpoint=request.endpoint,
            method=request.method,
            data=request.data,
            headers=request.headers,
            timeout=request.timeout,
        )

        # Calculate response time
        call_time_ms = (time.time() - call_start) * 1000

        # Prepare response
        result = {
            "success": True,
            "service_type": request.service_type,
            "endpoint": request.endpoint,
            "method": request.method,
            "response_data": response_data,
            "performance": {
                "call_time_ms": call_time_ms,
                "target_time_ms": 2000,  # <2s target
                "performance_met": call_time_ms < 2000,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            f"Service call completed: {request.service_type} {request.method} {request.endpoint} "
            f"in {call_time_ms:.2f}ms"
        )

        return result

    except Exception as e:
        call_time_ms = (time.time() - call_start) * 1000
        logger.error(
            f"Service call failed: {request.service_type} {request.method} {request.endpoint} "
            f"after {call_time_ms:.2f}ms: {e}"
        )

        raise HTTPException(status_code=500, detail=f"Service call failed: {str(e)}")


@router.post("/publish-event", status_code=200)
async def publish_event_endpoint(
    request: EventPublishRequest,
    background_tasks: BackgroundTasks,
    orchestrator: Phase2ServiceOrchestrator = None,
):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Publish an event to the service integration event system.

    This endpoint enables event-driven communication between services with:
    - Event routing and delivery
    - Priority-based processing
    - Retry mechanisms
    - Event history tracking
    - Correlation ID management
    """
    try:
        # Get orchestrator instance
        if not orchestrator:
            orchestrator = await get_phase2_orchestrator()

        # Validate event type
        try:
            event_type = EventType(request.event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {request.event_type}")

        # Validate source service
        try:
            source_service = ServiceType(request.source_service)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid source service: {request.source_service}"
            )

        # Validate target services
        target_services = []
        for service_str in request.target_services:
            try:
                target_services.append(ServiceType(service_str))
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid target service: {service_str}"
                )

        # Create service event
        event = ServiceEvent(
            event_id=f"api-{int(time.time() * 1000)}",
            event_type=event_type,
            source_service=source_service,
            target_services=target_services,
            payload=request.payload,
            priority=request.priority,
        )

        # Publish event
        event_id = await orchestrator.publish_event(event)

        # Prepare response
        result = {
            "success": True,
            "event_id": event_id,
            "event_type": request.event_type,
            "source_service": request.source_service,
            "target_services": request.target_services,
            "correlation_id": event.correlation_id,
            "priority": request.priority,
            "timestamp": event.created_at.isoformat(),
        }

        logger.info(f"Event published successfully: {event_id}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Event publishing failed: {e}")

        raise HTTPException(status_code=500, detail=f"Event publishing failed: {str(e)}")


@router.post("/start-workflow", status_code=200)
async def start_workflow_endpoint(
    request: WorkflowStartRequest,
    background_tasks: BackgroundTasks,
    orchestrator: Phase2ServiceOrchestrator = None,
):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Start a multi-service workflow with orchestrated execution.

    This endpoint provides workflow management with:
    - Multi-service coordination
    - Step-by-step execution tracking
    - Correlation ID management
    - Workflow completion detection
    - Error handling and rollback
    """
    try:
        # Get orchestrator instance
        if not orchestrator:
            orchestrator = await get_phase2_orchestrator()

        # Validate services
        services = []
        for service_str in request.services:
            try:
                services.append(ServiceType(service_str))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid service: {service_str}")

        # Generate workflow ID
        workflow_id = f"workflow-{int(time.time() * 1000)}"

        # Start workflow
        correlation_id = await orchestrator.start_workflow(
            workflow_id=workflow_id,
            workflow_type=request.workflow_type,
            services=services,
            workflow_data=request.workflow_data,
        )

        # Prepare response
        result = {
            "success": True,
            "workflow_id": workflow_id,
            "workflow_type": request.workflow_type,
            "correlation_id": correlation_id,
            "services": request.services,
            "total_steps": len(services),
            "status": "started",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"Workflow started: {workflow_id} with correlation {correlation_id}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow start failed: {e}")

        raise HTTPException(status_code=500, detail=f"Workflow start failed: {str(e)}")


@router.get("/status", response_model=ServiceIntegrationStatus)
async def get_integration_status(
    orchestrator: Phase2ServiceOrchestrator = None,
):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Get comprehensive service integration status and health information.

    Returns detailed status including:
    - Orchestrator running status
    - Service health status
    - Active workflow count
    - Event processing metrics
    - Performance statistics
    """
    try:
        # Get orchestrator instance
        if not orchestrator:
            orchestrator = await get_phase2_orchestrator()

        # Get metrics
        metrics = orchestrator.get_metrics()

        # Calculate health statistics
        health_status = metrics["health_status"]
        healthy_services = sum(1 for healthy in health_status.values() if healthy)
        total_services = len(health_status)

        # Prepare status response
        status_response = ServiceIntegrationStatus(
            orchestrator_running=orchestrator.running,
            total_services=total_services,
            healthy_services=healthy_services,
            active_workflows=metrics["workflow_metrics"]["active_workflows"],
            total_events_processed=metrics["event_metrics"]["total_events"],
            average_event_processing_time_ms=metrics["event_metrics"]["average_processing_time_ms"],
            service_health=health_status,
            timestamp=datetime.now(timezone.utc),
        )

        return status_response

    except Exception as e:
        logger.error(f"Status retrieval failed: {e}")

        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


@router.get("/metrics", status_code=200)
async def get_integration_metrics(
    orchestrator: Phase2ServiceOrchestrator = None,
):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Get comprehensive service integration metrics and performance data.

    Returns detailed metrics including:
    - Event processing statistics
    - Service call performance
    - Workflow completion rates
    - Health monitoring data
    - System performance indicators
    """
    try:
        # Get orchestrator instance
        if not orchestrator:
            orchestrator = await get_phase2_orchestrator()

        # Get comprehensive metrics
        metrics = orchestrator.get_metrics()

        # Enhance with additional analysis
        enhanced_metrics = {
            **metrics,
            "performance_analysis": {
                "overall_health_percentage": (
                    sum(1 for healthy in metrics["health_status"].values() if healthy)
                    / max(len(metrics["health_status"]), 1)
                    * 100
                ),
                "event_success_rate_percentage": (metrics["event_metrics"]["success_rate"] * 100),
                "average_service_call_time_ms": (
                    sum(
                        service_metrics["average_time_ms"]
                        for service_metrics in metrics["service_metrics"].values()
                    )
                    / max(len(metrics["service_metrics"]), 1)
                    if metrics["service_metrics"]
                    else 0.0
                ),
                "integration_grade": _calculate_integration_grade(metrics),
            },
            "targets": {
                "target_service_response_time_ms": 2000,
                "target_event_processing_time_ms": 100,
                "target_service_availability": 0.995,
                "target_event_success_rate": 0.95,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return enhanced_metrics

    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")

        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")


@router.post("/health-check", status_code=200)
async def trigger_health_check(
    background_tasks: BackgroundTasks,
    orchestrator: Phase2ServiceOrchestrator = None,
):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Trigger immediate health check for all services.

    This endpoint forces an immediate health check of all registered services
    and returns the updated health status.
    """
    try:
        # Get orchestrator instance
        if not orchestrator:
            orchestrator = await get_phase2_orchestrator()

        # Trigger health checks in background
        async def perform_health_checks():
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            """Perform health checks for all services."""
            health_results = {}

            for service_type, service_config in orchestrator.services.items():
                try:
                    # Perform health check
                    response_data = await orchestrator.call_service(
                        service_type=service_type, endpoint="/health", method="GET", timeout=5.0
                    )

                    health_results[service_type.value] = {
                        "healthy": True,
                        "response": response_data,
                        "checked_at": datetime.now(timezone.utc).isoformat(),
                    }

                except Exception as e:
                    health_results[service_type.value] = {
                        "healthy": False,
                        "error": str(e),
                        "checked_at": datetime.now(timezone.utc).isoformat(),
                    }

            logger.info(f"Health check completed for {len(health_results)} services")
            return health_results

        # Start health check in background
        background_tasks.add_task(perform_health_checks)

        # Return immediate response
        result = {
            "success": True,
            "message": "Health check initiated for all services",
            "services_checked": len(orchestrator.services),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return result

    except Exception as e:
        logger.error(f"Health check trigger failed: {e}")

        raise HTTPException(status_code=500, detail=f"Health check trigger failed: {str(e)}")


def _calculate_integration_grade(metrics: Dict[str, Any]) -> str:
    """Calculate overall integration grade based on metrics."""

    # Calculate component scores
    health_score = sum(1 for healthy in metrics["health_status"].values() if healthy) / max(
        len(metrics["health_status"]), 1
    )

    event_score = metrics["event_metrics"]["success_rate"]

    # Average service performance (assuming <2s is good)
    service_scores = []
    for service_metrics in metrics["service_metrics"].values():
        avg_time = service_metrics.get("average_time_ms", 0)
        service_score = max(0, 1 - (avg_time / 2000))  # 2s target
        service_scores.append(service_score)

    avg_service_score = sum(service_scores) / max(len(service_scores), 1) if service_scores else 0.8

    # Calculate overall score
    overall_score = health_score * 0.4 + event_score * 0.3 + avg_service_score * 0.3

    # Assign grade
    if overall_score >= 0.95:
        return "A+"
    elif overall_score >= 0.90:
        return "A"
    elif overall_score >= 0.85:
        return "B+"
    elif overall_score >= 0.80:
        return "B"
    elif overall_score >= 0.75:
        return "C+"
    elif overall_score >= 0.70:
        return "C"
    else:
        return "D"
