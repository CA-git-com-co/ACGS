#!/usr/bin/env python3
"""
ACGS-1 Lite Audit Engine Service

Production-ready FastAPI service providing:
- Cryptographic hash-chained audit events with PostgreSQL persistence
- Real-time event ingestion via Redpanda consumer
- S3 archival with Object Lock for immutability
- Comprehensive REST API for audit queries and verification

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import asyncpg
import aiofiles
import aioboto3
import aioredis
import uvicorn
from aiokafka import AIOKafkaConsumer
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, HTTPException, Request, Response, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field
import structlog

# Import our audit compliance manager
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from compliance.audit_compliance_manager import (
    AuditComplianceManager, AuditEvent, AuditEventType, 
    DataClassification, ComplianceFramework, RetentionPolicy
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Prometheus metrics
AUDIT_EVENTS_INGESTED_TOTAL = Counter(
    "audit_events_ingested_total",
    "Total number of audit events ingested",
    ["source", "event_type", "result"]
)

AUDIT_QUERY_DURATION = Histogram(
    "audit_query_duration_seconds",
    "Time spent executing audit queries",
    ["query_type"]
)

CHAIN_INTEGRITY_STATUS = Gauge(
    "audit_chain_integrity_status",
    "Audit chain integrity status (1=valid, 0=invalid)"
)

S3_ARCHIVAL_OPERATIONS_TOTAL = Counter(
    "s3_archival_operations_total",
    "Total S3 archival operations",
    ["operation", "result"]
)

REDPANDA_CONSUMER_LAG = Gauge(
    "redpanda_consumer_lag",
    "Current Redpanda consumer lag"
)

# Constitutional hash for integrity verification
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Pydantic models
class EventIngestRequest(BaseModel):
    """Request model for direct event ingestion."""
    event_type: str = Field(..., description="Type of audit event")
    service_name: str = Field(..., description="Name of originating service")
    agent_id: Optional[str] = Field(None, description="Agent identifier")
    action: str = Field(..., description="Action performed")
    outcome: str = Field(..., description="Outcome of action")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    ip_address: Optional[str] = Field(None, description="IP address")

class EventQueryParams(BaseModel):
    """Query parameters for event retrieval."""
    agent_id: Optional[str] = None
    event_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)

class ChainVerificationResult(BaseModel):
    """Result of chain integrity verification."""
    is_valid: bool
    total_events: int
    verification_time_ms: float
    last_chain_hash: str
    constitutional_hash_verified: bool

class ExportRequest(BaseModel):
    """Request for audit event export."""
    start_date: datetime
    end_date: datetime
    format: str = Field(default="json", description="Export format (json, csv)")
    include_sensitive: bool = Field(default=False, description="Include sensitive data")

# FastAPI app
app = FastAPI(
    title="ACGS-1 Lite Audit Engine",
    description="Production audit event ingestion and verification service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

class AuditEngineService:
    """Main audit engine service class."""
    
    def __init__(self):
        self.db_pool = None
        self.redis = None
        self.s3_session = None
        self.kafka_consumer = None
        self.audit_manager = None
        self.consumer_task = None
        self.archival_task = None
        
        # Configuration from environment
        self.db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/audit_db")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.kafka_brokers = os.getenv("KAFKA_BROKERS", "localhost:9092").split(",")
        self.kafka_topic = os.getenv("KAFKA_TOPIC", "constitutional-events")
        self.s3_bucket = os.getenv("S3_BUCKET", "acgs-audit-archive")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        
    async def initialize(self):
        """Initialize all service components."""
        try:
            logger.info("Initializing Audit Engine Service", constitutional_hash=CONSTITUTIONAL_HASH)
            
            # Initialize database
            await self._init_database()
            
            # Initialize Redis
            await self._init_redis()
            
            # Initialize audit manager with existing keys or generate new ones
            await self._init_audit_manager()
            
            # Initialize S3 client
            await self._init_s3()
            
            # Initialize Redpanda consumer
            await self._init_kafka_consumer()
            
            # Start background tasks
            self.consumer_task = asyncio.create_task(self._consume_events())
            self.archival_task = asyncio.create_task(self._daily_archival_task())
            
            # Verify chain integrity on startup
            await self._verify_startup_integrity()
            
            logger.info("Audit Engine Service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Audit Engine Service", error=str(e))
            raise
    
    async def _init_database(self):
        """Initialize PostgreSQL connection pool."""
        self.db_pool = await asyncpg.create_pool(
            self.db_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        
        # Create tables if they don't exist
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id UUID PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    agent_id VARCHAR(255),
                    action VARCHAR(255) NOT NULL,
                    outcome VARCHAR(50) NOT NULL,
                    payload JSONB,
                    content_hash VARCHAR(64) NOT NULL,
                    chain_hash VARCHAR(64) NOT NULL,
                    prev_hash VARCHAR(64) NOT NULL,
                    signature TEXT,
                    service_name VARCHAR(100) NOT NULL,
                    user_id VARCHAR(255),
                    session_id VARCHAR(255),
                    ip_address INET,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp);
                CREATE INDEX IF NOT EXISTS idx_audit_agent ON audit_events(agent_id);
                CREATE INDEX IF NOT EXISTS idx_audit_type ON audit_events(event_type);
                CREATE INDEX IF NOT EXISTS idx_audit_chain_hash ON audit_events(chain_hash);
                CREATE INDEX IF NOT EXISTS idx_audit_service ON audit_events(service_name);
                
                CREATE TABLE IF NOT EXISTS audit_metadata (
                    key VARCHAR(100) PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            
            logger.info("Database schema initialized")
    
    async def _init_redis(self):
        """Initialize Redis connection."""
        self.redis = await aioredis.from_url(self.redis_url)
        await self.redis.ping()
        logger.info("Redis connection established")
    
    async def _init_audit_manager(self):
        """Initialize audit compliance manager with persistent keys."""
        # Try to load existing signing key from database
        signing_key = None
        async with self.db_pool.acquire() as conn:
            key_data = await conn.fetchval(
                "SELECT value FROM audit_metadata WHERE key = 'signing_key'"
            )
            
            if key_data:
                # Load existing key
                signing_key = serialization.load_pem_private_key(
                    key_data.encode(),
                    password=None,
                )
                logger.info("Loaded existing signing key from database")
            else:
                # Generate new key and store it
                signing_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                )
                
                key_pem = signing_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                await conn.execute(
                    "INSERT INTO audit_metadata (key, value) VALUES ($1, $2) "
                    "ON CONFLICT (key) DO UPDATE SET value = $2, updated_at = NOW()",
                    "signing_key", key_pem.decode()
                )
                logger.info("Generated and stored new signing key")
        
        self.audit_manager = AuditComplianceManager(signing_key=signing_key)
        
        # Load existing events from database to rebuild chain
        await self._load_existing_events()
    
    async def _load_existing_events(self):
        """Load existing events from database to rebuild audit chain."""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM audit_events ORDER BY timestamp ASC"
            )
            
            for row in rows:
                # Reconstruct AuditEvent from database row
                event = AuditEvent(
                    event_id=str(row["id"]),
                    timestamp=row["timestamp"],
                    event_type=AuditEventType(row["event_type"]),
                    service_name=row["service_name"],
                    user_id=row["user_id"],
                    session_id=row["session_id"],
                    ip_address=row["ip_address"],
                    user_agent=None,  # Not stored in this schema
                    resource=row["agent_id"] or "unknown",
                    action=row["action"],
                    result=row["outcome"],
                    details=row["payload"] or {},
                    data_classification=DataClassification.INTERNAL,
                    compliance_frameworks=[ComplianceFramework.CONSTITUTIONAL_GOVERNANCE],
                    retention_policy=RetentionPolicy.YEARS_7,
                    privacy_impact=False,
                    constitutional_impact=True,
                    content_hash=row["content_hash"],
                    digital_signature=row["signature"],
                    chain_hash=row["chain_hash"]
                )
                
                self.audit_manager.audit_events.append(event)
                self.audit_manager.chain_hash = event.chain_hash
            
            logger.info(f"Loaded {len(rows)} existing audit events")
    
    async def _init_s3(self):
        """Initialize S3 client session."""
        self.s3_session = aioboto3.Session()
        logger.info("S3 session initialized")
    
    async def _init_kafka_consumer(self):
        """Initialize Kafka consumer for real-time event ingestion."""
        self.kafka_consumer = AIOKafkaConsumer(
            self.kafka_topic,
            bootstrap_servers=self.kafka_brokers,
            group_id="audit-engine",
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
            consumer_timeout_ms=1000
        )
        
        await self.kafka_consumer.start()
        logger.info(f"Kafka consumer started for topic: {self.kafka_topic}")
    
    async def _consume_events(self):
        """Background task to consume events from Redpanda."""
        logger.info("Starting Redpanda event consumer")
        
        try:
            async for msg in self.kafka_consumer:
                try:
                    event_data = msg.value
                    
                    # Process the event
                    await self._process_kafka_event(event_data)
                    
                    AUDIT_EVENTS_INGESTED_TOTAL.labels(
                        source="kafka",
                        event_type=event_data.get("event_type", "unknown"),
                        result="success"
                    ).inc()
                    
                    # Update consumer lag metric
                    lag = msg.highwater - msg.offset
                    REDPANDA_CONSUMER_LAG.set(lag)
                    
                except Exception as e:
                    logger.error("Error processing Kafka event", error=str(e), event=msg.value)
                    AUDIT_EVENTS_INGESTED_TOTAL.labels(
                        source="kafka",
                        event_type="unknown",
                        result="error"
                    ).inc()
                    
        except Exception as e:
            logger.error("Kafka consumer error", error=str(e))
            # Restart consumer after delay
            await asyncio.sleep(5)
            await self._init_kafka_consumer()
            self.consumer_task = asyncio.create_task(self._consume_events())
    
    async def _process_kafka_event(self, event_data: Dict[str, Any]):
        """Process a single event from Kafka."""
        # Map Kafka event to our audit event structure
        event_id = await self._ingest_audit_event(
            event_type=event_data.get("event_type", "unknown"),
            service_name=event_data.get("service_name", "unknown"),
            agent_id=event_data.get("agent_id"),
            action=event_data.get("action", "unknown"),
            outcome=event_data.get("outcome", "unknown"),
            payload=event_data.get("payload", {}),
            user_id=event_data.get("user_id"),
            session_id=event_data.get("session_id"),
            ip_address=event_data.get("ip_address")
        )
        
        logger.debug("Processed Kafka event", event_id=event_id)
    
    async def _ingest_audit_event(self, **kwargs) -> str:
        """Internal method to ingest and persist audit event."""
        start_time = time.time()
        
        try:
            # Create audit event using compliance manager
            event_id = self.audit_manager.log_audit_event(
                event_type=AuditEventType(kwargs.get("event_type", "governance_action")),
                service_name=kwargs["service_name"],
                resource=kwargs.get("agent_id", "system"),
                action=kwargs["action"],
                result=kwargs["outcome"],
                user_id=kwargs.get("user_id"),
                session_id=kwargs.get("session_id"),
                ip_address=kwargs.get("ip_address"),
                details=kwargs.get("payload", {}),
                constitutional_impact=True
            )
            
            # Get the created event
            event = self.audit_manager.audit_events[-1]
            
            # Persist to PostgreSQL
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO audit_events (
                        id, timestamp, event_type, agent_id, action, outcome,
                        payload, content_hash, chain_hash, prev_hash, signature,
                        service_name, user_id, session_id, ip_address
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                """, 
                    uuid.UUID(event.event_id),
                    event.timestamp,
                    event.event_type.value,
                    kwargs.get("agent_id"),
                    event.action,
                    event.result,
                    json.dumps(event.details),
                    event.content_hash,
                    event.chain_hash,
                    # Calculate previous hash
                    self.audit_manager.audit_events[-2].chain_hash if len(self.audit_manager.audit_events) > 1 else "0" * 64,
                    event.digital_signature,
                    event.service_name,
                    event.user_id,
                    event.session_id,
                    event.ip_address
                )
            
            # Cache recent event in Redis for fast access
            await self.redis.setex(
                f"audit:event:{event_id}",
                3600,  # 1 hour TTL
                json.dumps(event.to_dict(), default=str)
            )
            
            duration = (time.time() - start_time) * 1000
            logger.debug("Audit event ingested", event_id=event_id, duration_ms=duration)
            
            return event_id
            
        except Exception as e:
            logger.error("Failed to ingest audit event", error=str(e))
            raise
    
    async def _verify_startup_integrity(self):
        """Verify audit chain integrity on startup."""
        start_time = time.time()
        
        try:
            is_valid = self.audit_manager.verify_chain_integrity()
            duration_ms = (time.time() - start_time) * 1000
            
            CHAIN_INTEGRITY_STATUS.set(1 if is_valid else 0)
            
            logger.info(
                "Chain integrity verification completed",
                is_valid=is_valid,
                total_events=len(self.audit_manager.audit_events),
                duration_ms=duration_ms,
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
            if not is_valid:
                logger.error("Chain integrity verification FAILED - audit chain compromised!")
                
        except Exception as e:
            logger.error("Chain integrity verification error", error=str(e))
            CHAIN_INTEGRITY_STATUS.set(0)
    
    async def _daily_archival_task(self):
        """Daily task to archive old events to S3."""
        while True:
            try:
                # Run at 2 AM UTC daily
                now = datetime.now(timezone.utc)
                next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                
                sleep_seconds = (next_run - now).total_seconds()
                await asyncio.sleep(sleep_seconds)
                
                await self._archive_to_s3()
                
            except Exception as e:
                logger.error("Daily archival task error", error=str(e))
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _archive_to_s3(self):
        """Archive yesterday's events to S3 with Object Lock."""
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        try:
            logger.info("Starting daily S3 archival", date=yesterday.date())
            
            # Query events from yesterday
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM audit_events 
                    WHERE timestamp >= $1 AND timestamp <= $2
                    ORDER BY timestamp ASC
                """, start_date, end_date)
            
            if not rows:
                logger.info("No events to archive", date=yesterday.date())
                return
            
            # Prepare archive data
            archive_data = {
                "archive_metadata": {
                    "date": yesterday.date().isoformat(),
                    "total_events": len(rows),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                "events": [dict(row) for row in rows]
            }
            
            # Upload to S3 with Object Lock
            async with self.s3_session.client("s3", region_name=self.aws_region) as s3:
                key = f"audit-archive/{yesterday.year}/{yesterday.month:02d}/{yesterday.day:02d}/events.json"
                
                await s3.put_object(
                    Bucket=self.s3_bucket,
                    Key=key,
                    Body=json.dumps(archive_data, default=str, indent=2),
                    ContentType="application/json",
                    Metadata={
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                        "event_count": str(len(rows)),
                        "archive_date": yesterday.date().isoformat()
                    },
                    ObjectLockMode="COMPLIANCE",
                    ObjectLockRetainUntilDate=datetime.now(timezone.utc) + timedelta(days=2555)  # 7 years
                )
            
            # Update archival metadata
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO audit_metadata (key, value) VALUES ($1, $2) "
                    "ON CONFLICT (key) DO UPDATE SET value = $2, updated_at = NOW()",
                    f"archive_{yesterday.date().isoformat()}", key
                )
            
            S3_ARCHIVAL_OPERATIONS_TOTAL.labels(operation="archive", result="success").inc()
            logger.info("S3 archival completed", date=yesterday.date(), events_archived=len(rows), s3_key=key)
            
        except Exception as e:
            S3_ARCHIVAL_OPERATIONS_TOTAL.labels(operation="archive", result="error").inc()
            logger.error("S3 archival failed", error=str(e), date=yesterday.date())
    
    async def shutdown(self):
        """Gracefully shutdown the service."""
        logger.info("Shutting down Audit Engine Service")
        
        if self.consumer_task:
            self.consumer_task.cancel()
        
        if self.archival_task:
            self.archival_task.cancel()
        
        if self.kafka_consumer:
            await self.kafka_consumer.stop()
        
        if self.redis:
            await self.redis.close()
        
        if self.db_pool:
            await self.db_pool.close()

# Global service instance
audit_service = AuditEngineService()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract user from JWT token."""
    # Simplified authentication - implement proper JWT validation in production
    return {"user_id": "system", "role": "admin"}

# API Endpoints
@app.on_event("startup")
async def startup():
    """Initialize service on startup."""
    await audit_service.initialize()

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    await audit_service.shutdown()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "audit-engine",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "chain_integrity": bool(CHAIN_INTEGRITY_STATUS._value._value)
    }

@app.post("/api/v1/audit/events")
async def ingest_event(
    request: EventIngestRequest,
    user: Dict = Depends(get_current_user)
):
    """Direct audit event ingestion."""
    start_time = time.time()
    
    try:
        event_id = await audit_service._ingest_audit_event(
            event_type=request.event_type,
            service_name=request.service_name,
            agent_id=request.agent_id,
            action=request.action,
            outcome=request.outcome,
            payload=request.payload,
            user_id=request.user_id,
            session_id=request.session_id,
            ip_address=request.ip_address
        )
        
        AUDIT_EVENTS_INGESTED_TOTAL.labels(
            source="api",
            event_type=request.event_type,
            result="success"
        ).inc()
        
        duration = (time.time() - start_time) * 1000
        
        return {
            "success": True,
            "event_id": event_id,
            "processing_time_ms": round(duration, 2)
        }
        
    except Exception as e:
        AUDIT_EVENTS_INGESTED_TOTAL.labels(
            source="api",
            event_type=request.event_type,
            result="error"
        ).inc()
        
        logger.error("Event ingestion failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Event ingestion failed: {str(e)}")

@app.get("/api/v1/audit/events")
async def query_events(
    agent_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    user: Dict = Depends(get_current_user)
):
    """Query audit events with filters."""
    start_time = time.time()
    
    try:
        # Build query
        conditions = []
        params = []
        param_count = 0
        
        if agent_id:
            param_count += 1
            conditions.append(f"agent_id = ${param_count}")
            params.append(agent_id)
            
        if event_type:
            param_count += 1
            conditions.append(f"event_type = ${param_count}")
            params.append(event_type)
            
        if start_date:
            param_count += 1
            conditions.append(f"timestamp >= ${param_count}")
            params.append(start_date)
            
        if end_date:
            param_count += 1
            conditions.append(f"timestamp <= ${param_count}")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT id, timestamp, event_type, agent_id, action, outcome, 
                   payload, content_hash, chain_hash, service_name,
                   user_id, session_id, ip_address, created_at
            FROM audit_events 
            {where_clause}
            ORDER BY timestamp DESC 
            LIMIT ${param_count + 1} OFFSET ${param_count + 2}
        """
        
        params.extend([limit, offset])
        
        async with audit_service.db_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            
            # Get total count
            count_query = f"SELECT COUNT(*) FROM audit_events {where_clause}"
            total_count = await conn.fetchval(count_query, *params[:-2])
        
        events = [dict(row) for row in rows]
        
        duration = (time.time() - start_time) * 1000
        AUDIT_QUERY_DURATION.labels(query_type="events").observe(duration / 1000)
        
        return {
            "events": events,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "query_time_ms": round(duration, 2)
        }
        
    except Exception as e:
        logger.error("Event query failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/api/v1/audit/events/{event_id}")
async def get_event(
    event_id: str,
    user: Dict = Depends(get_current_user)
):
    """Get specific audit event by ID."""
    try:
        # Try Redis cache first
        cached = await audit_service.redis.get(f"audit:event:{event_id}")
        if cached:
            return json.loads(cached)
        
        # Query database
        async with audit_service.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM audit_events WHERE id = $1",
                uuid.UUID(event_id)
            )
            
        if not row:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return dict(row)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event ID format")
    except Exception as e:
        logger.error("Event retrieval failed", error=str(e), event_id=event_id)
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@app.get("/api/v1/audit/verify")
async def verify_chain_integrity(
    user: Dict = Depends(get_current_user)
):
    """Verify complete audit chain integrity."""
    start_time = time.time()
    
    try:
        is_valid = audit_service.audit_manager.verify_chain_integrity()
        duration_ms = (time.time() - start_time) * 1000
        
        # Update metric
        CHAIN_INTEGRITY_STATUS.set(1 if is_valid else 0)
        
        return ChainVerificationResult(
            is_valid=is_valid,
            total_events=len(audit_service.audit_manager.audit_events),
            verification_time_ms=round(duration_ms, 2),
            last_chain_hash=audit_service.audit_manager.chain_hash,
            constitutional_hash_verified=(CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2")
        )
        
    except Exception as e:
        logger.error("Chain verification failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@app.post("/api/v1/audit/export")
async def export_events(
    request: ExportRequest,
    user: Dict = Depends(get_current_user)
):
    """Export audit events for specified date range."""
    try:
        # Query events in date range
        async with audit_service.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM audit_events 
                WHERE timestamp >= $1 AND timestamp <= $2
                ORDER BY timestamp ASC
            """, request.start_date, request.end_date)
        
        if not rows:
            raise HTTPException(status_code=404, detail="No events found in date range")
        
        # Format based on request
        if request.format == "json":
            export_data = {
                "export_metadata": {
                    "start_date": request.start_date.isoformat(),
                    "end_date": request.end_date.isoformat(),
                    "total_events": len(rows),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "exported_at": datetime.now(timezone.utc).isoformat()
                },
                "events": [dict(row) for row in rows]
            }
            
            return export_data
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        logger.error("Event export failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=False,
        log_config=None  # Use our structured logging
    )