# Audit Engine Service Implementation Prompt

## Context
You are implementing the Audit Engine microservice for ACGS-1 Lite. The core cryptographic hash chaining logic exists in `AuditComplianceManager`, but needs to be wrapped in a production-ready FastAPI service with persistent storage, Redpanda integration, and comprehensive API endpoints.

## Requirements

### Core Functionality
1. **Persistent Storage**: Implement PostgreSQL backend for audit events with the following schema:
   ```sql
   CREATE TABLE audit_events (
     id UUID PRIMARY KEY,
     timestamp TIMESTAMPTZ NOT NULL,
     event_type VARCHAR(50) NOT NULL,
     agent_id VARCHAR(255),
     action VARCHAR(255),
     outcome VARCHAR(50),
     payload JSONB,
     content_hash VARCHAR(64) NOT NULL,
     chain_hash VARCHAR(64) NOT NULL,
     prev_hash VARCHAR(64) NOT NULL,
     signature TEXT,
     created_at TIMESTAMPTZ DEFAULT NOW()
   );
   CREATE INDEX idx_audit_timestamp ON audit_events(timestamp);
   CREATE INDEX idx_audit_agent ON audit_events(agent_id);
   CREATE INDEX idx_audit_type ON audit_events(event_type);
   ```

2. **Redpanda Consumer**: Subscribe to `constitutional-events-kafka:9092` topic and process events:
   - Use `confluent_kafka` or `aiokafka` for async consumption
   - Implement at-least-once delivery with offset management
   - Handle backpressure and retries

3. **REST API**: FastAPI service on port 8003 with endpoints:
   - `POST /api/v1/audit/events` - Direct event ingestion
   - `GET /api/v1/audit/events` - Query with filters (agent_id, type, date range)
   - `GET /api/v1/audit/events/{id}` - Get specific event
   - `GET /api/v1/audit/verify` - Verify chain integrity
   - `GET /api/v1/audit/export` - Export events for date range

4. **S3 Integration**: Implement daily archival to S3 with Object Lock:
   ```python
   async def archive_to_s3():
       # Export yesterday's events to JSON
       # Upload to S3 with Object Lock retention
       # Update archive metadata
   ```

5. **Cryptographic Features**:
   - Use existing `AuditComplianceManager` for hash chaining
   - Implement field-level encryption for sensitive payload data
   - Add RSA/Ed25519 signing for each event

### Performance Requirements
- Handle 1000+ events/second ingestion rate
- Query response time <100ms for indexed fields
- Chain verification <5 seconds for 1M events

### Security Requirements
- JWT authentication for API endpoints
- Role-based access (admin: all, auditor: read-only)
- Encrypted storage for sensitive fields
- TLS for all communications

## Implementation Steps

1. **Service Skeleton**:
   ```python
   # services/core/audit-engine/main.py
   from fastapi import FastAPI, Depends, HTTPException
   from services.shared.compliance.audit_compliance_manager import AuditComplianceManager
   
   app = FastAPI(title="ACGS-1 Lite Audit Engine")
   audit_manager = AuditComplianceManager()
   
   @app.on_event("startup")
   async def startup():
       # Initialize DB connection
       # Start Redpanda consumer
       # Load signing keys
       # Verify chain integrity
   ```

2. **Database Integration**:
   - Use SQLAlchemy async with PostgreSQL
   - Implement connection pooling
   - Add retry logic for transient failures

3. **Monitoring & Alerts**:
   - Prometheus metrics: events_processed_total, chain_integrity_status
   - Alert on chain verification failures
   - Dashboard for event volume and latency

## Testing Requirements
- Unit tests for hash chain verification
- Integration tests with mock Redpanda
- Load test to verify 1000 events/second
- Security tests for authentication and encryption

## Success Criteria
- [ ] All API endpoints return correct data
- [ ] Chain integrity maintained under load
- [ ] S3 archival runs daily without failures
- [ ] Performance metrics meet requirements
- [ ] Security scan shows no vulnerabilities