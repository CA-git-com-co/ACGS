"""
Observability API endpoints for ACGS-1 Self-Evolving AI Architecture Foundation.

This module provides REST API endpoints for observability management, including
metrics collection, tracing, alerting, and monitoring capabilities.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...core.observability_framework import (
    AlertLevel,
    MetricType,
    ObservabilityFramework,
)
from ...dependencies import get_observability_framework

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class MetricRecordRequest(BaseModel):
    """Request model for recording metrics."""

    metric_name: str = Field(..., description="Name of the metric")
    value: float = Field(..., description="Metric value")
    metric_type: str = Field(
        default="gauge",
        description="Type of metric (counter, gauge, histogram, summary)",
    )
    unit: str = Field(default="", description="Unit of measurement")
    labels: dict[str, str] = Field(default_factory=dict, description="Metric labels")


class SpanStartRequest(BaseModel):
    """Request model for starting a trace span."""

    operation_name: str = Field(..., description="Name of the operation being traced")
    tags: dict[str, str] = Field(default_factory=dict, description="Span tags")


class SpanFinishRequest(BaseModel):
    """Request model for finishing a trace span."""

    status: str = Field(default="ok", description="Span status (ok, error, timeout)")
    logs: list[dict[str, Any]] = Field(
        default_factory=list, description="Span log entries"
    )


class AlertTriggerRequest(BaseModel):
    """Request model for triggering alerts."""

    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    alert_level: str = Field(
        default="warning", description="Alert level (info, warning, error, critical)"
    )
    source: str = Field(default="api", description="Source of the alert")
    metric_name: str | None = Field(None, description="Related metric name")
    threshold_value: float | None = Field(
        None, description="Threshold that was exceeded"
    )
    current_value: float | None = Field(None, description="Current metric value")


class ObservabilityResponse(BaseModel):
    """Response model for observability operations."""

    success: bool
    message: str
    data: dict[str, Any] | None = None


# API Endpoints
@router.post("/metrics/record", response_model=ObservabilityResponse)
async def record_metric(
    request: MetricRecordRequest,
    observability_framework: ObservabilityFramework = Depends(
        get_observability_framework
    ),
):
    """
    Record a performance metric.

    This endpoint allows recording of custom metrics for monitoring and
    alerting purposes. Metrics are automatically integrated with the
    OpenTelemetry framework when available.
    """
    try:
        await observability_framework.record_metric(
            metric_name=request.metric_name,
            value=request.value,
            metric_type=MetricType(request.metric_type),
            unit=request.unit,
            labels=request.labels,
        )

        return ObservabilityResponse(
            success=True,
            message="Metric recorded successfully",
            data={
                "metric_name": request.metric_name,
                "value": request.value,
                "metric_type": request.metric_type,
                "unit": request.unit,
                "labels": request.labels,
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Metric recording failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/tracing/start-span", response_model=ObservabilityResponse)
async def start_span(
    request: SpanStartRequest,
    observability_framework: ObservabilityFramework = Depends(
        get_observability_framework
    ),
):
    """
    Start a new trace span.

    This endpoint starts a new distributed trace span for tracking
    operations across the self-evolving AI architecture.
    """
    try:
        span_id = await observability_framework.start_span(
            operation_name=request.operation_name, tags=request.tags
        )

        return ObservabilityResponse(
            success=True,
            message="Span started successfully",
            data={
                "span_id": span_id,
                "operation_name": request.operation_name,
                "tags": request.tags,
            },
        )

    except Exception as e:
        logger.error(f"Span start failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/tracing/finish-span/{span_id}", response_model=ObservabilityResponse)
async def finish_span(
    span_id: str,
    request: SpanFinishRequest,
    observability_framework: ObservabilityFramework = Depends(
        get_observability_framework
    ),
):
    """
    Finish a trace span.

    This endpoint finishes an active trace span, recording its completion
    time and final status for distributed tracing analysis.
    """
    try:
        await observability_framework.finish_span(
            span_id=span_id, status=request.status, logs=request.logs
        )

        return ObservabilityResponse(
            success=True,
            message="Span finished successfully",
            data={
                "span_id": span_id,
                "status": request.status,
                "logs_count": len(request.logs),
            },
        )

    except Exception as e:
        logger.error(f"Span finish failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/alerts/trigger", response_model=ObservabilityResponse)
async def trigger_alert(
    request: AlertTriggerRequest,
    observability_framework: ObservabilityFramework = Depends(
        get_observability_framework
    ),
):
    """
    Trigger a custom alert.

    This endpoint allows triggering of custom alerts for monitoring
    and notification purposes. Alerts are integrated with the overall
    alerting framework.
    """
    try:
        alert_id = await observability_framework.trigger_alert(
            title=request.title,
            description=request.description,
            alert_level=AlertLevel(request.alert_level),
            source=request.source,
            metric_name=request.metric_name,
            threshold_value=request.threshold_value,
            current_value=request.current_value,
        )

        return ObservabilityResponse(
            success=True,
            message="Alert triggered successfully",
            data={
                "alert_id": alert_id,
                "title": request.title,
                "alert_level": request.alert_level,
                "source": request.source,
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Alert trigger failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/alerts/{alert_id}/resolve", response_model=ObservabilityResponse)
async def resolve_alert(
    alert_id: str,
    observability_framework: ObservabilityFramework = Depends(
        get_observability_framework
    ),
):
    """
    Resolve an active alert.

    This endpoint resolves an active alert, marking it as resolved
    and removing it from the active alerts list.
    """
    try:
        await observability_framework.resolve_alert(alert_id)

        return ObservabilityResponse(
            success=True,
            message="Alert resolved successfully",
            data={
                "alert_id": alert_id,
                "status": "resolved",
            },
        )

    except Exception as e:
        logger.error(f"Alert resolution failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/metrics")
async def get_metrics(
    observability_framework: ObservabilityFramework = Depends(
        get_observability_framework
    ),
):
    """
    Get current metrics buffer.

    This endpoint returns the current metrics buffer with recent
    performance metrics collected by the observability framework.
    """
    try:
        metrics_data = []

        for metric in observability_framework.metrics_buffer[-100:]:  # Last 100 metrics
            metrics_data.append(
                {
                    "metric_name": metric.metric_name,
                    "metric_type": metric.metric_type.value,
                    "value": metric.value,
                    "unit": metric.unit,
                    "labels": metric.labels,
                    "timestamp": metric.timestamp.isoformat(),
                    "metadata": metric.metadata,
                }
            )

        return {
            "success": True,
            "message": f"Retrieved {len(metrics_data)} metrics",
            "data": {
                "metrics": metrics_data,
                "total_count": len(metrics_data),
                "buffer_size": len(observability_framework.metrics_buffer),
            },
        }

    except Exception as e:
        logger.error(f"Get metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/traces")
async def get_active_traces(
    observability_framework: ObservabilityFramework = Depends(
        get_observability_framework
    ),
):
    """
    Get active trace spans.

    This endpoint returns information about currently active trace spans
    for monitoring distributed operations.
    """
    try:
        active_spans = []

        for span_id, span in observability_framework.active_spans.items():
            active_spans.append(
                {
                    "span_id": span_id,
                    "trace_id": span.trace_id,
                    "operation_name": span.operation_name,
                    "start_time": span.start_time.isoformat(),
                    "status": span.status,
                    "tags": span.tags,
                    "logs_count": len(span.logs),
                }
            )

        return {
            "success": True,
            "message": f"Retrieved {len(active_spans)} active spans",
            "data": {
                "active_spans": active_spans,
                "total_count": len(active_spans),
            },
        }

    except Exception as e:
        logger.error(f"Get active traces failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/alerts")
async def get_active_alerts(
    observability_framework: ObservabilityFramework = Depends(
        get_observability_framework
    ),
):
    """
    Get active alerts.

    This endpoint returns information about all currently active alerts
    in the observability framework.
    """
    try:
        active_alerts = []

        for alert_id, alert in observability_framework.active_alerts.items():
            active_alerts.append(
                {
                    "alert_id": alert_id,
                    "alert_level": alert.alert_level.value,
                    "title": alert.title,
                    "description": alert.description,
                    "source": alert.source,
                    "metric_name": alert.metric_name,
                    "threshold_value": alert.threshold_value,
                    "current_value": alert.current_value,
                    "triggered_at": alert.triggered_at.isoformat(),
                    "metadata": alert.metadata,
                }
            )

        return {
            "success": True,
            "message": f"Retrieved {len(active_alerts)} active alerts",
            "data": {
                "active_alerts": active_alerts,
                "total_count": len(active_alerts),
                "alert_levels": {
                    "critical": len(
                        [a for a in active_alerts if a["alert_level"] == "critical"]
                    ),
                    "error": len(
                        [a for a in active_alerts if a["alert_level"] == "error"]
                    ),
                    "warning": len(
                        [a for a in active_alerts if a["alert_level"] == "warning"]
                    ),
                    "info": len(
                        [a for a in active_alerts if a["alert_level"] == "info"]
                    ),
                },
            },
        }

    except Exception as e:
        logger.error(f"Get active alerts failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status")
async def get_observability_status(
    observability_framework: ObservabilityFramework = Depends(
        get_observability_framework
    ),
):
    """
    Get observability framework status.

    This endpoint provides comprehensive status information about the
    observability framework, including OpenTelemetry integration status.
    """
    try:
        status = await observability_framework.get_observability_status()

        return {
            "success": True,
            "message": "Observability status retrieved successfully",
            "data": status,
        }

    except Exception as e:
        logger.error(f"Get observability status failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def observability_health_check(
    observability_framework: ObservabilityFramework = Depends(
        get_observability_framework
    ),
):
    """
    Health check for the observability framework.

    This endpoint provides health status information for the observability
    framework, including OpenTelemetry components and monitoring capabilities.
    """
    try:
        health_status = await observability_framework.health_check()

        if health_status.get("healthy", False):
            return {
                "status": "healthy",
                "message": "Observability framework is operational",
                "data": health_status,
            }
        return {
            "status": "unhealthy",
            "message": "Observability framework has issues",
            "data": health_status,
        }

    except Exception as e:
        logger.error(f"Observability health check failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
