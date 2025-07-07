"""
ACGS Centralized Audit Aggregation Service
Collects, correlates, and provides unified access to audit events across all ACGS services.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ACGS Standardized Error Handling
try:
    import sys
    from pathlib import Path
    shared_middleware_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "middleware"
    sys.path.insert(0, str(shared_middleware_path))
    
    from error_handling import (
        setup_error_handlers,
        ErrorHandlingMiddleware,
        ACGSException,
        ConstitutionalComplianceError,
        SecurityValidationError,
        AuthenticationError,
        ValidationError,
        log_error_with_context,
        ErrorContext
    )
    ACGS_ERROR_HANDLING_AVAILABLE = True
    print(f"✅ ACGS Error handling loaded for {service_name}")
except ImportError as e:
    print(f"⚠️ ACGS Error handling not available for {service_name}: {e}")
    ACGS_ERROR_HANDLING_AVAILABLE = False


# ACGS Security Middleware Integration
try:
    import sys
    from pathlib import Path
    shared_security_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "security"
    sys.path.insert(0, str(shared_security_path))
    
    from middleware_integration import (
        apply_acgs_security_middleware,
        setup_security_monitoring,
        get_security_headers,
        SecurityLevel,
        validate_request_body,
        create_secure_endpoint_decorator
    )
    ACGS_SECURITY_AVAILABLE = True
    print(f"✅ ACGS Security middleware loaded for {service_name}")
except ImportError as e:
    print(f"⚠️ ACGS Security middleware not available for {service_name}: {e}")
    ACGS_SECURITY_AVAILABLE = False


# Import shared components
try:
    from services.shared.audit.compliance_audit_logger import (
        AuditEventType, AuditSeverity, ComplianceStandard, AuditEvent,
        get_audit_logger, log_constitutional_compliance_event
    )
    from services.shared.cache.tenant_isolated_redis import get_tenant_redis
    from services.shared.middleware.tenant_middleware import get_tenant_context
    from services.shared.database import get_async_db
except ImportError:
    # Fallback for standalone deployment
    pass

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
SERVICE_NAME = "audit-aggregator"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(


# Apply ACGS Error Handling
if ACGS_ERROR_HANDLING_AVAILABLE:
    import os
    development_mode = os.getenv("ENVIRONMENT", "development") != "production"
    setup_error_handlers(app, "audit_aggregator", include_traceback=development_mode)

# Apply ACGS Security Middleware
if ACGS_SECURITY_AVAILABLE:
    environment = os.getenv("ENVIRONMENT", "development")
    apply_acgs_security_middleware(app, "audit_aggregator", environment)
    setup_security_monitoring(app, "audit_aggregator")

    title="ACGS Audit Aggregation Service",
    description="Centralized audit event collection and analysis for ACGS",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AuditEventRequest(BaseModel):
    """Request model for audit event submission."""
    event_type: str
    service_name: str
    action: str
    outcome: str = "success"
    severity: str = "low"
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    compliance_tags: List[str] = Field(default_factory=list)

class AuditEventResponse(BaseModel):
    """Response model for audit events."""
    event_id: str
    timestamp: str
    event_type: str
    service_name: str
    action: str
    outcome: str
    severity: str
    constitutional_hash: str
    correlation_id: Optional[str] = None

class AuditQueryRequest(BaseModel):
    """Request model for audit event queries."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[str]] = None
    service_names: Optional[List[str]] = None
    tenant_ids: Optional[List[str]] = None
    user_ids: Optional[List[str]] = None
    severity_levels: Optional[List[str]] = None
    compliance_tags: Optional[List[str]] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)

class AuditQueryResponse(BaseModel):
    """Response model for audit queries."""
    events: List[Dict[str, Any]]
    total_count: int
    query_time_ms: float
    constitutional_hash: str

class ComplianceMetricsResponse(BaseModel):
    """Response model for compliance metrics."""
    constitutional_compliance_score: float
    total_events_24h: int
    violations_24h: int
    critical_alerts_24h: int
    service_compliance_scores: Dict[str, float]
    constitutional_hash: str
    last_updated: str

# Global state
audit_redis = None
aggregation_stats = {
    "events_processed": 0,
    "correlations_found": 0,
    "compliance_violations": 0,
    "service_startup_time": datetime.now(timezone.utc)
}

@app.on_event("startup")
async def startup_event():
    """Initialize the audit aggregation service."""
    global audit_redis
    
    try:
        # Initialize Redis connection
        audit_redis = await get_tenant_redis()
        
        # Log service startup
        audit_logger = get_audit_logger(SERVICE_NAME)
        await audit_logger.log_event(
            event_type=AuditEventType.SERVICE_START,
            action="audit_aggregator_startup",
            outcome="success",
            severity=AuditSeverity.LOW,
            details={
                "service_name": SERVICE_NAME,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "startup_time": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Start background aggregation task
        asyncio.create_task(background_aggregation_task())
        
        logger.info(f"Audit Aggregation Service started with constitutional hash: {CONSTITUTIONAL_HASH}")
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Failed to start audit aggregation service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on service shutdown."""
    try:
        # Log service shutdown
        audit_logger = get_audit_logger(SERVICE_NAME)
        await audit_logger.log_event(
            event_type=AuditEventType.SERVICE_STOP,
            action="audit_aggregator_shutdown",
            outcome="success",
            severity=AuditSeverity.LOW,
            details={
                "service_name": SERVICE_NAME,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "uptime_seconds": (datetime.now(timezone.utc) - aggregation_stats["service_startup_time"]).total_seconds()
            }
        )
        
        # Close Redis connection
        if audit_redis:
            await audit_redis.close()
            
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Error during shutdown: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test Redis connectivity
        redis_healthy = False
        if audit_redis:
            health_status = await audit_redis.health_check()
            redis_healthy = health_status.get("status") == "healthy"
        
        uptime = (datetime.now(timezone.utc) - aggregation_stats["service_startup_time"]).total_seconds()
        
        return {
            "status": "healthy" if redis_healthy else "degraded",
            "service": SERVICE_NAME,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "uptime_seconds": uptime,
            "events_processed": aggregation_stats["events_processed"],
            "redis_healthy": redis_healthy,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/api/v1/audit/events", response_model=AuditEventResponse)
async def submit_audit_event(
    event_request: AuditEventRequest,
    background_tasks: BackgroundTasks
):
    """Submit an audit event for aggregation and storage."""
    try:
        # Generate event ID and timestamp
        event_id = f"audit_{int(time.time())}_{event_request.service_name}"
        timestamp = datetime.now(timezone.utc)
        
        # Create audit event
        audit_event = {
            "event_id": event_id,
            "timestamp": timestamp.isoformat(),
            "event_type": event_request.event_type,
            "service_name": event_request.service_name,
            "action": event_request.action,
            "outcome": event_request.outcome,
            "severity": event_request.severity,
            "user_id": event_request.user_id,
            "tenant_id": event_request.tenant_id,
            "session_id": event_request.session_id,
            "ip_address": event_request.ip_address,
            "user_agent": event_request.user_agent,
            "resource": event_request.resource,
            "details": {
                **event_request.details,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "aggregator_processed": True
            },
            "compliance_tags": event_request.compliance_tags,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        # Store in Redis with TTL (7 days)
        if audit_redis:
            await audit_redis.set(
                tenant_id="system",
                key=f"audit_event:{event_id}",
                value=audit_event,
                ttl=604800  # 7 days
            )
            
            # Add to time-based index for efficient querying
            date_key = timestamp.strftime("%Y-%m-%d")
            await audit_redis.set(
                tenant_id="system",
                key=f"audit_index:{date_key}:{event_id}",
                value={"event_id": event_id, "timestamp": timestamp.isoformat()},
                ttl=604800
            )
        
        # Schedule background processing
        background_tasks.add_task(process_audit_event_background, audit_event)
        
        # Update statistics
        aggregation_stats["events_processed"] += 1
        
        # Determine correlation ID if this is part of a pattern
        correlation_id = await detect_event_correlation(audit_event)
        
        return AuditEventResponse(
            event_id=event_id,
            timestamp=timestamp.isoformat(),
            event_type=event_request.event_type,
            service_name=event_request.service_name,
            action=event_request.action,
            outcome=event_request.outcome,
            severity=event_request.severity,
            constitutional_hash=CONSTITUTIONAL_HASH,
            correlation_id=correlation_id
        )
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Failed to submit audit event: {e}")
        raise ACGSException(status_code=500, error_code="INTERNAL_ERROR", detail="Failed to process audit event")

@app.post("/api/v1/audit/query", response_model=AuditQueryResponse)
async def query_audit_events(query_request: AuditQueryRequest):
    """Query audit events with filtering and pagination."""
    start_time = time.time()
    
    try:
        # Default time range to last 24 hours if not specified
        if not query_request.start_time:
            query_request.start_time = datetime.now(timezone.utc) - timedelta(days=1)
        if not query_request.end_time:
            query_request.end_time = datetime.now(timezone.utc)
        
        events = []
        total_count = 0
        
        if audit_redis:
            # Query events from Redis time-based indices
            events, total_count = await query_events_from_redis(query_request)
        
        query_time_ms = (time.time() - start_time) * 1000
        
        return AuditQueryResponse(
            events=events,
            total_count=total_count,
            query_time_ms=query_time_ms,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Failed to query audit events: {e}")
        raise ACGSException(status_code=500, error_code="INTERNAL_ERROR", detail="Failed to query audit events")

@app.get("/api/v1/audit/compliance-metrics", response_model=ComplianceMetricsResponse)
async def get_compliance_metrics():
    """Get real-time constitutional compliance metrics."""
    try:
        # Calculate compliance metrics
        compliance_score = await calculate_constitutional_compliance_score()
        service_scores = await calculate_service_compliance_scores()
        
        # Get 24-hour statistics
        stats_24h = await get_24h_audit_statistics()
        
        return ComplianceMetricsResponse(
            constitutional_compliance_score=compliance_score,
            total_events_24h=stats_24h["total_events"],
            violations_24h=stats_24h["violations"],
            critical_alerts_24h=stats_24h["critical_alerts"],
            service_compliance_scores=service_scores,
            constitutional_hash=CONSTITUTIONAL_HASH,
            last_updated=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Failed to get compliance metrics: {e}")
        raise ACGSException(status_code=500, error_code="INTERNAL_ERROR", detail="Failed to get compliance metrics")

@app.get("/api/v1/audit/correlations/{event_id}")
async def get_event_correlations(event_id: str):
    """Get correlated events for a specific audit event."""
    try:
        if not audit_redis:
            raise HTTPException(status_code=503, detail="Redis unavailable")
        
        # Get the base event
        base_event = await audit_redis.get("system", f"audit_event:{event_id}")
        if not base_event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Find correlated events
        correlations = await find_correlated_events(base_event, event_id)
        
        return {
            "event_id": event_id,
            "correlations": correlations,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Failed to get event correlations: {e}")
        raise ACGSException(status_code=500, error_code="INTERNAL_ERROR", detail="Failed to get correlations")

@app.get("/api/v1/audit/stats")
async def get_aggregation_statistics():
    """Get audit aggregation service statistics."""
    uptime = (datetime.now(timezone.utc) - aggregation_stats["service_startup_time"]).total_seconds()
    
    return {
        "service_name": SERVICE_NAME,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "uptime_seconds": uptime,
        "events_processed": aggregation_stats["events_processed"],
        "correlations_found": aggregation_stats["correlations_found"],
        "compliance_violations": aggregation_stats["compliance_violations"],
        "startup_time": aggregation_stats["service_startup_time"].isoformat()
    }

# Background processing functions

async def process_audit_event_background(audit_event: Dict[str, Any]):
    """Process audit event in background for correlation and analysis."""
    try:
        # Check for constitutional compliance violations
        await check_constitutional_compliance(audit_event)
        
        # Perform event correlation analysis
        correlations = await analyze_event_correlations(audit_event)
        if correlations:
            aggregation_stats["correlations_found"] += len(correlations)
        
        # Update real-time metrics
        await update_real_time_metrics(audit_event)
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Background processing failed for event {audit_event.get('event_id')}: {e}")

async def background_aggregation_task():
    """Background task for periodic aggregation and cleanup."""
    while True:
        try:
            # Perform periodic cleanup of old events
            await cleanup_old_events()
            
            # Update aggregated statistics
            await update_aggregated_statistics()
            
            # Sleep for 5 minutes
            await asyncio.sleep(300)
            
        except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
            logger.error(f"Background aggregation task error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

async def detect_event_correlation(audit_event: Dict[str, Any]) -> Optional[str]:
    """Detect if this event correlates with recent events."""
    try:
        # Simple correlation based on service, user, and time proximity
        correlation_window = 300  # 5 minutes
        current_time = datetime.fromisoformat(audit_event["timestamp"].replace('Z', '+00:00'))
        
        # Look for related events in the correlation window
        # This is a simplified implementation - in practice, would use ML
        correlation_key = f"{audit_event.get('service_name')}_{audit_event.get('user_id')}_{audit_event.get('event_type')}"
        
        return f"corr_{hash(correlation_key) % 10000}"
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Correlation detection failed: {e}")
        return None

async def query_events_from_redis(query_request: AuditQueryRequest) -> tuple[List[Dict[str, Any]], int]:
    """Query events from Redis with filtering."""
    events = []
    total_count = 0
    
    try:
        # Generate date range for querying
        current_date = query_request.start_time.date()
        end_date = query_request.end_time.date()
        
        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            
            # Get all event IDs for this date
            pattern = f"audit_index:{date_key}:*"
            event_keys = await audit_redis.keys("system", pattern)
            
            for key in event_keys:
                # Get event data
                event_data = await audit_redis.get("system", f"audit_event:{key.split(':')[-1]}")
                if event_data and matches_query_filters(event_data, query_request):
                    events.append(event_data)
                    total_count += 1
            
            current_date += timedelta(days=1)
        
        # Apply pagination
        events = events[query_request.offset:query_request.offset + query_request.limit]
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Redis query failed: {e}")
    
    return events, total_count

def matches_query_filters(event_data: Dict[str, Any], query_request: AuditQueryRequest) -> bool:
    """Check if event matches query filters."""
    # Event type filter
    if query_request.event_types and event_data.get("event_type") not in query_request.event_types:
        return False
    
    # Service name filter
    if query_request.service_names and event_data.get("service_name") not in query_request.service_names:
        return False
    
    # Tenant ID filter
    if query_request.tenant_ids and event_data.get("tenant_id") not in query_request.tenant_ids:
        return False
    
    # User ID filter
    if query_request.user_ids and event_data.get("user_id") not in query_request.user_ids:
        return False
    
    # Severity filter
    if query_request.severity_levels and event_data.get("severity") not in query_request.severity_levels:
        return False
    
    return True

async def calculate_constitutional_compliance_score() -> float:
    """Calculate overall constitutional compliance score."""
    try:
        # Get compliance events from last 24 hours
        compliance_events = []
        violations = 0
        total_events = 0
        
        # Query constitutional compliance events
        if audit_redis:
            # This is a simplified calculation - in practice would be more sophisticated
            pattern = "audit_event:*"
            event_keys = await audit_redis.keys("system", pattern)
            
            for key in event_keys[-100:]:  # Last 100 events for calculation
                event_data = await audit_redis.get("system", key)
                if event_data and "constitutional" in event_data.get("event_type", "").lower():
                    total_events += 1
                    if event_data.get("outcome") in ["violation", "critical_violation"]:
                        violations += 1
        
        # Calculate score (0.0 to 1.0)
        if total_events == 0:
            return 1.0  # Perfect score if no events
        
        compliance_rate = 1.0 - (violations / total_events)
        return max(0.0, min(1.0, compliance_rate))
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Failed to calculate compliance score: {e}")
        return 0.5  # Default to neutral score on error

async def calculate_service_compliance_scores() -> Dict[str, float]:
    """Calculate compliance scores per service."""
    service_scores = {}
    
    try:
        # This would calculate per-service compliance in a real implementation
        # For now, return mock data
        acgs_services = [
            "constitutional-ai", "integrity-service", "api-gateway",
            "multi-agent-coordinator", "worker-agents", "blackboard-service",
            "governance-synthesis", "authentication-service", "audit-aggregator"
        ]
        
        for service in acgs_services:
            # Mock calculation - in practice would analyze actual events
            service_scores[service] = 0.95 + (hash(service) % 10) * 0.005
    
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Failed to calculate service scores: {e}")
    
    return service_scores

async def get_24h_audit_statistics() -> Dict[str, int]:
    """Get 24-hour audit statistics."""
    try:
        # Query last 24 hours of events
        total_events = 0
        violations = 0
        critical_alerts = 0
        
        # This would query actual events in a real implementation
        # For now, return mock statistics based on aggregation_stats
        total_events = min(aggregation_stats["events_processed"], 10000)
        violations = aggregation_stats["compliance_violations"]
        critical_alerts = violations // 10  # Assume 10% of violations are critical
        
        return {
            "total_events": total_events,
            "violations": violations,
            "critical_alerts": critical_alerts
        }
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Failed to get 24h statistics: {e}")
        return {"total_events": 0, "violations": 0, "critical_alerts": 0}

async def check_constitutional_compliance(audit_event: Dict[str, Any]):
    """Check event for constitutional compliance violations."""
    try:
        # Check constitutional hash
        event_hash = audit_event.get("constitutional_hash")
        if event_hash != CONSTITUTIONAL_HASH:
            aggregation_stats["compliance_violations"] += 1
            
            # Log compliance violation
            await log_constitutional_compliance_event(
                event_type=AuditEventType.CONSTITUTIONAL_HASH_MISMATCH,
                action="hash_verification_failed",
                compliance_score=0.0,
                hash_verified=False,
                violations=["constitutional_hash_mismatch"],
                service_name=audit_event.get("service_name"),
                details={
                    "expected_hash": CONSTITUTIONAL_HASH,
                    "received_hash": event_hash,
                    "original_event_id": audit_event.get("event_id")
                }
            )
        
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Constitutional compliance check failed: {e}")

async def analyze_event_correlations(audit_event: Dict[str, Any]) -> List[str]:
    """Analyze event for correlations with other events."""
    # Simplified correlation analysis
    return []

async def find_correlated_events(base_event: Dict[str, Any], event_id: str) -> List[Dict[str, Any]]:
    """Find events correlated with the base event."""
    # Simplified correlation finding
    return []

async def update_real_time_metrics(audit_event: Dict[str, Any]):
    """Update real-time metrics based on event."""
    # Update counters, rates, etc.
    pass

async def cleanup_old_events():
    """Clean up old audit events from Redis."""
    try:
        # Clean up events older than 7 days
        if audit_redis:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
            # Implementation would clean up old date indices
            pass
    except Exception as e:
        # TODO: Consider using ACGS error handling: log_error_with_context()
        logger.error(f"Cleanup failed: {e}")

async def update_aggregated_statistics():
    """Update aggregated statistics."""
    # Update periodic statistics
    pass

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8015,
        reload=True,
        log_level="info"
    )