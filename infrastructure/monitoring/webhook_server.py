#!/usr/bin/env python3
"""
ACGS-1 Intelligent Alerting Webhook Server
Receives alerts from Prometheus Alertmanager and triggers intelligent responses
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from intelligent_alerting import IntelligentAlertManager, AlertSeverity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ACGS-1 Intelligent Alerting Webhook Server",
    description="Webhook server for intelligent alert processing and automated remediation",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Global alert manager instance
alert_manager: IntelligentAlertManager = None


async def get_alert_manager() -> IntelligentAlertManager:
    """Get or initialize alert manager"""
    global alert_manager
    if alert_manager is None:
        alert_manager = IntelligentAlertManager()
    return alert_manager


def verify_webhook_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify webhook authentication token"""
    expected_token = "acgs-webhook-secret-2024"
    if credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return credentials


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global alert_manager
    alert_manager = IntelligentAlertManager()
    logger.info("Intelligent Alerting Webhook Server started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Intelligent Alerting Webhook Server shutting down")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "acgs-intelligent-alerting-webhook"
    }


@app.post("/webhook/prometheus-alerts")
async def receive_prometheus_alerts(
    request: Request,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(verify_webhook_token)
):
    """Receive alerts from Prometheus Alertmanager"""
    try:
        payload = await request.json()
        manager = await get_alert_manager()
        
        # Process alerts in background
        background_tasks.add_task(process_prometheus_alerts, payload, manager)
        
        return {"status": "received", "alerts_count": len(payload.get("alerts", []))}
    
    except Exception as e:
        logger.error(f"Error processing Prometheus alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/critical-alerts")
async def receive_critical_alerts(
    request: Request,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(verify_webhook_token)
):
    """Receive critical alerts with immediate processing"""
    try:
        payload = await request.json()
        manager = await get_alert_manager()
        
        # Process critical alerts immediately
        await process_prometheus_alerts(payload, manager, priority="critical")
        
        return {"status": "processed", "priority": "critical"}
    
    except Exception as e:
        logger.error(f"Error processing critical alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/governance-alerts")
async def receive_governance_alerts(
    request: Request,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(verify_webhook_token)
):
    """Receive constitutional governance alerts"""
    try:
        payload = await request.json()
        manager = await get_alert_manager()
        
        # Add governance-specific processing
        background_tasks.add_task(
            process_governance_alerts, payload, manager
        )
        
        return {"status": "received", "type": "governance"}
    
    except Exception as e:
        logger.error(f"Error processing governance alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/security-alerts")
async def receive_security_alerts(
    request: Request,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(verify_webhook_token)
):
    """Receive security alerts with immediate escalation"""
    try:
        payload = await request.json()
        manager = await get_alert_manager()
        
        # Process security alerts with high priority
        await process_security_alerts(payload, manager)
        
        return {"status": "processed", "type": "security", "escalated": True}
    
    except Exception as e:
        logger.error(f"Error processing security alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts/active")
async def get_active_alerts():
    """Get all active alerts"""
    manager = await get_alert_manager()
    active_alerts = await manager.get_active_alerts()
    
    return {
        "active_alerts": [
            {
                "id": alert.id,
                "name": alert.name,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "message": alert.message,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "remediation_attempted": alert.remediation_attempted,
                "remediation_success": alert.remediation_success,
                "escalation_level": alert.escalation_level
            }
            for alert in active_alerts
        ],
        "count": len(active_alerts)
    }


@app.get("/alerts/history")
async def get_alert_history(hours: int = 24):
    """Get alert history"""
    manager = await get_alert_manager()
    history = await manager.get_alert_history(hours=hours)
    
    return {
        "alert_history": [
            {
                "id": alert.id,
                "name": alert.name,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "timestamp": alert.timestamp.isoformat(),
                "resolution_time": alert.resolution_time.isoformat() if alert.resolution_time else None
            }
            for alert in history
        ],
        "count": len(history),
        "hours": hours
    }


@app.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, acknowledged_by: str = "webhook"):
    """Acknowledge an alert"""
    manager = await get_alert_manager()
    success = await manager.acknowledge_alert(alert_id, acknowledged_by)
    
    if success:
        return {"status": "acknowledged", "alert_id": alert_id}
    else:
        raise HTTPException(status_code=404, detail="Alert not found")


@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolution_reason: str = "Manual resolution"):
    """Manually resolve an alert"""
    manager = await get_alert_manager()
    await manager._resolve_alert(alert_id, resolution_reason)
    
    return {"status": "resolved", "alert_id": alert_id, "reason": resolution_reason}


async def process_prometheus_alerts(payload: Dict[str, Any], manager: IntelligentAlertManager, priority: str = "normal"):
    """Process alerts from Prometheus Alertmanager"""
    alerts = payload.get("alerts", [])
    
    for alert_data in alerts:
        try:
            # Extract alert information
            labels = alert_data.get("labels", {})
            annotations = alert_data.get("annotations", {})
            status = alert_data.get("status", "firing")
            
            # Skip resolved alerts for now (could be enhanced later)
            if status == "resolved":
                continue
            
            # Map Prometheus severity to our AlertSeverity
            severity_map = {
                "critical": AlertSeverity.CRITICAL,
                "high": AlertSeverity.HIGH,
                "warning": AlertSeverity.MEDIUM,
                "info": AlertSeverity.INFO
            }
            
            severity = severity_map.get(
                labels.get("severity", "medium").lower(),
                AlertSeverity.MEDIUM
            )
            
            # Create alert
            alert = await manager.create_alert(
                name=labels.get("alertname", "Unknown Alert"),
                severity=severity,
                message=annotations.get("summary", "No summary provided"),
                source="prometheus",
                labels=labels,
                annotations=annotations
            )
            
            logger.info(f"Processed Prometheus alert: {alert.id} - {alert.name}")
            
        except Exception as e:
            logger.error(f"Error processing individual alert: {e}")


async def process_governance_alerts(payload: Dict[str, Any], manager: IntelligentAlertManager):
    """Process constitutional governance specific alerts"""
    alerts = payload.get("alerts", [])
    
    for alert_data in alerts:
        try:
            labels = alert_data.get("labels", {})
            annotations = alert_data.get("annotations", {})
            
            # Add governance-specific context
            labels["component"] = "constitutional_governance"
            labels["constitutional_hash"] = labels.get("constitutional_hash", "cdd01ef066bc6cf2")
            
            # Governance alerts are typically critical
            alert = await manager.create_alert(
                name=f"Governance: {labels.get('alertname', 'Unknown')}",
                severity=AlertSeverity.CRITICAL,
                message=annotations.get("summary", "Constitutional governance issue detected"),
                source="governance_system",
                labels=labels,
                annotations=annotations
            )
            
            logger.warning(f"Processed governance alert: {alert.id}")
            
        except Exception as e:
            logger.error(f"Error processing governance alert: {e}")


async def process_security_alerts(payload: Dict[str, Any], manager: IntelligentAlertManager):
    """Process security alerts with immediate escalation"""
    alerts = payload.get("alerts", [])
    
    for alert_data in alerts:
        try:
            labels = alert_data.get("labels", {})
            annotations = alert_data.get("annotations", {})
            
            # Security alerts are always critical
            labels["category"] = "security"
            
            alert = await manager.create_alert(
                name=f"SECURITY: {labels.get('alertname', 'Unknown')}",
                severity=AlertSeverity.CRITICAL,
                message=annotations.get("summary", "Security incident detected"),
                source="security_system",
                labels=labels,
                annotations=annotations
            )
            
            # Immediate escalation for security alerts
            await manager._escalate_alert(alert)
            
            logger.critical(f"Processed security alert with escalation: {alert.id}")
            
        except Exception as e:
            logger.error(f"Error processing security alert: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "webhook_server:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=False
    )
