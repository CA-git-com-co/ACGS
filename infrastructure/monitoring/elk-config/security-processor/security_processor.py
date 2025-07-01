#!/usr/bin/env python3
"""
ACGS-1 Security Event Processor

Real-time security event analysis, threat detection, and automated response system.
Integrates with ELK stack for comprehensive security monitoring and SIEM capabilities.

Features:
- Real-time security event processing
- Threat intelligence integration
- Automated incident response
- Risk scoring and prioritization
- Integration with Prometheus metrics
- Webhook alerting for critical events
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import aiohttp
import structlog
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import uvicorn
from pydantic import BaseModel, Field

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
security_events_total = Counter(
    "acgs_security_events_total",
    "Total security events processed",
    ["event_type", "severity"],
)
threat_detections_total = Counter(
    "acgs_threat_detections_total", "Total threats detected", ["threat_type"]
)
response_time_histogram = Histogram(
    "acgs_security_processing_seconds", "Security event processing time"
)
active_threats_gauge = Gauge("acgs_active_threats", "Number of active threats")
risk_score_gauge = Gauge("acgs_current_risk_score", "Current system risk score")


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ThreatType(str, Enum):
    AUTHENTICATION_FAILURE = "authentication_failure"
    BRUTE_FORCE = "brute_force"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    GOVERNANCE_VIOLATION = "governance_violation"
    DATA_BREACH = "data_breach"
    MALWARE = "malware"
    INTRUSION = "intrusion"
    POLICY_VIOLATION = "policy_violation"


@dataclass
class SecurityEvent:
    timestamp: datetime
    event_type: str
    severity: SeverityLevel
    source_ip: Optional[str]
    user_id: Optional[str]
    description: str
    risk_score: int
    raw_data: Dict[str, Any]


@dataclass
class ThreatIntelligence:
    ip_address: str
    threat_type: ThreatType
    confidence: float
    last_seen: datetime
    source: str


class SecurityEventModel(BaseModel):
    timestamp: str
    event_type: str
    severity: str
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    description: str
    risk_score: int = Field(ge=0, le=100)
    metadata: Dict[str, Any] = {}


class SecurityProcessor:
    def __init__(self):
        self.es_client = None
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        self.active_threats: List[SecurityEvent] = []
        self.risk_threshold_critical = 80
        self.risk_threshold_high = 60
        self.risk_threshold_medium = 40

        # Configuration from environment
        self.elasticsearch_host = os.getenv(
            "ELASTICSEARCH_HOST", "elasticsearch-security:9200"
        )
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
        self.elasticsearch_password = os.getenv(
            "ELASTICSEARCH_PASSWORD", "acgs_security_2024"
        )
        self.prometheus_host = os.getenv("PROMETHEUS_HOST", "prometheus:9090")
        self.alert_webhook_url = os.getenv("ALERT_WEBHOOK_URL")

    async def initialize(self):
        """Initialize Elasticsearch connection and load threat intelligence"""
        try:
            self.es_client = AsyncElasticsearch(
                [f"http://{self.elasticsearch_host}"],
                basic_auth=(self.elasticsearch_username, self.elasticsearch_password),
                verify_certs=False,
            )

            # Test connection
            await self.es_client.ping()
            logger.info("Connected to Elasticsearch", host=self.elasticsearch_host)

            # Load threat intelligence
            await self.load_threat_intelligence()

            # Start background tasks
            asyncio.create_task(self.process_security_events())
            asyncio.create_task(self.update_threat_intelligence())
            asyncio.create_task(self.cleanup_old_threats())

        except Exception as e:
            logger.error("Failed to initialize SecurityProcessor", error=str(e))
            raise

    async def load_threat_intelligence(self):
        """Load threat intelligence from various sources"""
        try:
            # Load from Elasticsearch threat intelligence index
            query = {"query": {"match_all": {}}, "size": 10000}

            response = await self.es_client.search(
                index="acgs-threat-intelligence", body=query
            )

            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                threat = ThreatIntelligence(
                    ip_address=source["ip_address"],
                    threat_type=ThreatType(source["threat_type"]),
                    confidence=source["confidence"],
                    last_seen=datetime.fromisoformat(source["last_seen"]),
                    source=source["source"],
                )
                self.threat_intelligence[threat.ip_address] = threat

            logger.info(
                "Loaded threat intelligence", count=len(self.threat_intelligence)
            )

        except Exception as e:
            logger.warning("Failed to load threat intelligence", error=str(e))

    async def process_security_events(self):
        """Continuously process security events from Elasticsearch"""
        while True:
            try:
                # Query for recent security events
                query = {
                    "query": {
                        "bool": {
                            "must": [
                                {"range": {"@timestamp": {"gte": "now-1m"}}},
                                {
                                    "terms": {
                                        "tags": [
                                            "security_alert",
                                            "suspicious_activity",
                                            "failed_auth",
                                        ]
                                    }
                                },
                            ]
                        }
                    },
                    "sort": [{"@timestamp": {"order": "desc"}}],
                    "size": 100,
                }

                response = await self.es_client.search(
                    index="acgs-security-alerts-*", body=query
                )

                for hit in response["hits"]["hits"]:
                    await self.analyze_security_event(hit["_source"])

                await asyncio.sleep(10)  # Process every 10 seconds

            except Exception as e:
                logger.error("Error processing security events", error=str(e))
                await asyncio.sleep(30)

    async def analyze_security_event(self, event_data: Dict[str, Any]):
        """Analyze individual security event and determine threat level"""
        start_time = time.time()

        try:
            # Parse event
            event = SecurityEvent(
                timestamp=datetime.fromisoformat(
                    event_data.get("@timestamp", datetime.now().isoformat())
                ),
                event_type=event_data.get("event_type", "unknown"),
                severity=SeverityLevel(event_data.get("severity", "INFO")),
                source_ip=event_data.get("source_ip"),
                user_id=event_data.get("user_id"),
                description=event_data.get("description", ""),
                risk_score=event_data.get("risk_score", 0),
                raw_data=event_data,
            )

            # Update metrics
            security_events_total.labels(
                event_type=event.event_type, severity=event.severity.value
            ).inc()

            # Enhance with threat intelligence
            enhanced_event = await self.enhance_with_threat_intelligence(event)

            # Determine if this is a threat
            if await self.is_threat(enhanced_event):
                await self.handle_threat(enhanced_event)

            # Update risk score
            await self.update_system_risk_score()

            # Record processing time
            processing_time = time.time() - start_time
            response_time_histogram.observe(processing_time)

            logger.info(
                "Processed security event",
                event_type=event.event_type,
                severity=event.severity.value,
                risk_score=event.risk_score,
                processing_time=processing_time,
            )

        except Exception as e:
            logger.error(
                "Error analyzing security event", error=str(e), event_data=event_data
            )

    async def enhance_with_threat_intelligence(
        self, event: SecurityEvent
    ) -> SecurityEvent:
        """Enhance security event with threat intelligence data"""
        if event.source_ip and event.source_ip in self.threat_intelligence:
            threat_intel = self.threat_intelligence[event.source_ip]

            # Increase risk score based on threat intelligence
            event.risk_score = min(
                100, event.risk_score + int(threat_intel.confidence * 30)
            )

            # Update event description
            event.description += f" [THREAT INTEL: {threat_intel.threat_type.value}, confidence: {threat_intel.confidence:.2f}]"

            logger.info(
                "Enhanced event with threat intelligence",
                ip=event.source_ip,
                threat_type=threat_intel.threat_type.value,
                confidence=threat_intel.confidence,
            )

        return event

    async def is_threat(self, event: SecurityEvent) -> bool:
        """Determine if security event represents a threat"""
        # High risk score threshold
        if event.risk_score >= self.risk_threshold_high:
            return True

        # Critical severity events
        if event.severity == SeverityLevel.CRITICAL:
            return True

        # Multiple failed authentication attempts
        if event.event_type == "authentication_failure":
            recent_failures = await self.count_recent_failures(
                event.source_ip, event.user_id
            )
            if recent_failures >= 5:
                return True

        # Governance violations are always threats
        if event.event_type == "governance_violation":
            return True

        return False

    async def count_recent_failures(
        self, source_ip: Optional[str], user_id: Optional[str]
    ) -> int:
        """Count recent authentication failures for IP/user"""
        try:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"range": {"@timestamp": {"gte": "now-15m"}}},
                            {"term": {"event_type": "authentication_failure"}},
                        ]
                    }
                }
            }

            if source_ip:
                query["query"]["bool"]["must"].append(
                    {"term": {"source_ip": source_ip}}
                )
            if user_id:
                query["query"]["bool"]["must"].append({"term": {"user_id": user_id}})

            response = await self.es_client.count(
                index="acgs-security-alerts-*", body=query
            )

            return response["count"]

        except Exception as e:
            logger.error("Error counting recent failures", error=str(e))
            return 0

    async def handle_threat(self, event: SecurityEvent):
        """Handle detected threat with appropriate response"""
        try:
            # Add to active threats
            self.active_threats.append(event)

            # Update metrics
            threat_detections_total.labels(threat_type=event.event_type).inc()
            active_threats_gauge.set(len(self.active_threats))

            # Determine response based on severity and risk score
            if (
                event.severity == SeverityLevel.CRITICAL
                or event.risk_score >= self.risk_threshold_critical
            ):
                await self.critical_threat_response(event)
            elif (
                event.severity == SeverityLevel.HIGH
                or event.risk_score >= self.risk_threshold_high
            ):
                await self.high_threat_response(event)
            else:
                await self.medium_threat_response(event)

            # Log threat detection
            logger.warning(
                "Threat detected",
                event_type=event.event_type,
                severity=event.severity.value,
                risk_score=event.risk_score,
                source_ip=event.source_ip,
                user_id=event.user_id,
                description=event.description,
            )

            # Store threat in Elasticsearch
            await self.store_threat(event)

        except Exception as e:
            logger.error("Error handling threat", error=str(e), event=event)

    async def critical_threat_response(self, event: SecurityEvent):
        """Handle critical threats with immediate response"""
        # Send immediate alert
        await self.send_alert(event, "CRITICAL")

        # Block IP if applicable
        if event.source_ip:
            await self.block_ip(event.source_ip)

        # Disable user if applicable
        if event.user_id:
            await self.disable_user(event.user_id)

        # Trigger incident response
        await self.trigger_incident_response(event)

    async def high_threat_response(self, event: SecurityEvent):
        """Handle high-priority threats"""
        # Send alert
        await self.send_alert(event, "HIGH")

        # Increase monitoring for IP/user
        if event.source_ip:
            await self.increase_monitoring(event.source_ip, event.user_id)

    async def medium_threat_response(self, event: SecurityEvent):
        """Handle medium-priority threats"""
        # Log for investigation
        await self.log_for_investigation(event)

        # Update threat intelligence
        if event.source_ip:
            await self.update_threat_intel(event.source_ip, event.event_type)

    async def send_alert(self, event: SecurityEvent, priority: str):
        """Send alert via webhook or other notification system"""
        if not self.alert_webhook_url:
            return

        try:
            alert_data = {
                "timestamp": event.timestamp.isoformat(),
                "priority": priority,
                "event_type": event.event_type,
                "severity": event.severity.value,
                "risk_score": event.risk_score,
                "source_ip": event.source_ip,
                "user_id": event.user_id,
                "description": event.description,
                "system": "acgs-1",
                "environment": "production",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.alert_webhook_url,
                    json=alert_data,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        logger.info(
                            "Alert sent successfully",
                            priority=priority,
                            event_type=event.event_type,
                        )
                    else:
                        logger.error(
                            "Failed to send alert",
                            status=response.status,
                            priority=priority,
                        )

        except Exception as e:
            logger.error("Error sending alert", error=str(e), priority=priority)

    async def block_ip(self, ip_address: str):
        """Block IP address (placeholder for actual implementation)"""
        logger.info("Blocking IP address", ip=ip_address)
        # Implementation would integrate with firewall/security groups

    async def disable_user(self, user_id: str):
        """Disable user account (placeholder for actual implementation)"""
        logger.info("Disabling user account", user_id=user_id)
        # Implementation would integrate with authentication service

    async def trigger_incident_response(self, event: SecurityEvent):
        """Trigger incident response procedures"""
        logger.critical(
            "Triggering incident response",
            event_type=event.event_type,
            risk_score=event.risk_score,
        )
        # Implementation would integrate with incident management system

    async def increase_monitoring(self, ip_address: str, user_id: Optional[str]):
        """Increase monitoring for specific IP/user"""
        logger.info("Increasing monitoring", ip=ip_address, user_id=user_id)
        # Implementation would adjust monitoring thresholds

    async def log_for_investigation(self, event: SecurityEvent):
        """Log event for manual investigation"""
        investigation_data = {
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "severity": event.severity.value,
            "risk_score": event.risk_score,
            "source_ip": event.source_ip,
            "user_id": event.user_id,
            "description": event.description,
            "status": "pending_investigation",
            "assigned_to": None,
        }

        await self.es_client.index(index="acgs-investigations", body=investigation_data)

        logger.info("Logged for investigation", event_type=event.event_type)

    async def update_threat_intel(self, ip_address: str, threat_type: str):
        """Update threat intelligence with new information"""
        threat_data = {
            "ip_address": ip_address,
            "threat_type": threat_type,
            "confidence": 0.7,
            "last_seen": datetime.now().isoformat(),
            "source": "acgs-security-processor",
            "updated_at": datetime.now().isoformat(),
        }

        await self.es_client.index(
            index="acgs-threat-intelligence", id=ip_address, body=threat_data
        )

        # Update local cache
        self.threat_intelligence[ip_address] = ThreatIntelligence(
            ip_address=ip_address,
            threat_type=ThreatType(threat_type),
            confidence=0.7,
            last_seen=datetime.now(),
            source="acgs-security-processor",
        )

    async def store_threat(self, event: SecurityEvent):
        """Store threat information in Elasticsearch"""
        try:
            threat_data = {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "severity": event.severity.value,
                "risk_score": event.risk_score,
                "source_ip": event.source_ip,
                "user_id": event.user_id,
                "description": event.description,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "raw_data": event.raw_data,
            }

            await self.es_client.index(index="acgs-threats", body=threat_data)

        except Exception as e:
            logger.error("Error storing threat", error=str(e))

    async def update_system_risk_score(self):
        """Calculate and update overall system risk score"""
        try:
            # Calculate risk score based on active threats
            if not self.active_threats:
                risk_score = 0
            else:
                # Average risk score of active threats
                total_risk = sum(threat.risk_score for threat in self.active_threats)
                risk_score = min(100, total_risk / len(self.active_threats))

            risk_score_gauge.set(risk_score)

            # Store risk score in Elasticsearch
            risk_data = {
                "timestamp": datetime.now().isoformat(),
                "risk_score": risk_score,
                "active_threats_count": len(self.active_threats),
                "system": "acgs-1",
            }

            await self.es_client.index(index="acgs-risk-scores", body=risk_data)

        except Exception as e:
            logger.error("Error updating system risk score", error=str(e))

    async def update_threat_intelligence(self):
        """Periodically update threat intelligence from external sources"""
        while True:
            try:
                # Update every hour
                await asyncio.sleep(3600)

                # Reload threat intelligence
                await self.load_threat_intelligence()

                logger.info(
                    "Updated threat intelligence", count=len(self.threat_intelligence)
                )

            except Exception as e:
                logger.error("Error updating threat intelligence", error=str(e))
                await asyncio.sleep(300)  # Retry in 5 minutes

    async def cleanup_old_threats(self):
        """Clean up old threats from active list"""
        while True:
            try:
                # Clean up every 10 minutes
                await asyncio.sleep(600)

                # Remove threats older than 1 hour
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.active_threats = [
                    threat
                    for threat in self.active_threats
                    if threat.timestamp > cutoff_time
                ]

                active_threats_gauge.set(len(self.active_threats))

                logger.info(
                    "Cleaned up old threats", active_count=len(self.active_threats)
                )

            except Exception as e:
                logger.error("Error cleaning up threats", error=str(e))


# FastAPI application
app = FastAPI(
    title="ACGS-1 Security Event Processor",
    description="Real-time security monitoring and threat detection system",
    version="1.0.0",
)

# Global security processor instance
security_processor = SecurityProcessor()


@app.on_event("startup")
async def startup_event():
    """Initialize security processor on startup"""
    await security_processor.initialize()

    # Start Prometheus metrics server
    start_http_server(8081)
    logger.info("Security processor started", prometheus_port=8081)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Elasticsearch connection
        if security_processor.es_client:
            await security_processor.es_client.ping()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "active_threats": len(security_processor.active_threats),
            "threat_intelligence_count": len(security_processor.threat_intelligence),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """Get security metrics"""
    return {
        "active_threats": len(security_processor.active_threats),
        "threat_intelligence_count": len(security_processor.threat_intelligence),
        "risk_thresholds": {
            "critical": security_processor.risk_threshold_critical,
            "high": security_processor.risk_threshold_high,
            "medium": security_processor.risk_threshold_medium,
        },
    }


@app.get("/threats")
async def get_active_threats():
    """Get list of active threats"""
    threats = []
    for threat in security_processor.active_threats:
        threats.append(
            {
                "timestamp": threat.timestamp.isoformat(),
                "event_type": threat.event_type,
                "severity": threat.severity.value,
                "risk_score": threat.risk_score,
                "source_ip": threat.source_ip,
                "user_id": threat.user_id,
                "description": threat.description,
            }
        )

    return {"threats": threats, "count": len(threats)}


@app.post("/events")
async def process_security_event(
    event: SecurityEventModel, background_tasks: BackgroundTasks
):
    """Process a security event"""
    try:
        # Convert to internal format
        security_event = SecurityEvent(
            timestamp=datetime.fromisoformat(event.timestamp),
            event_type=event.event_type,
            severity=SeverityLevel(event.severity),
            source_ip=event.source_ip,
            user_id=event.user_id,
            description=event.description,
            risk_score=event.risk_score,
            raw_data=event.metadata,
        )

        # Process in background
        background_tasks.add_task(
            security_processor.analyze_security_event, security_event.raw_data
        )

        return {
            "status": "accepted",
            "event_id": f"{event.event_type}_{int(time.time())}",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid event data: {str(e)}")


@app.get("/threat-intelligence/{ip_address}")
async def get_threat_intelligence(ip_address: str):
    """Get threat intelligence for specific IP"""
    if ip_address in security_processor.threat_intelligence:
        threat = security_processor.threat_intelligence[ip_address]
        return {
            "ip_address": threat.ip_address,
            "threat_type": threat.threat_type.value,
            "confidence": threat.confidence,
            "last_seen": threat.last_seen.isoformat(),
            "source": threat.source,
        }
    else:
        raise HTTPException(
            status_code=404, detail="No threat intelligence found for IP"
        )


if __name__ == "__main__":
    uvicorn.run(
        "security_processor:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        access_log=True,
    )
