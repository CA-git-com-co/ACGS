# ACGS-1 Lite Audit Engine Service

Production-ready audit event ingestion and verification service with cryptographic integrity guarantees.

## Features

- **High-Performance Ingestion**: 1000+ events/second with sub-100ms API response times
- **Cryptographic Integrity**: SHA-256 hash chaining with RSA digital signatures
- **Real-time Streaming**: Redpanda/Kafka consumer for continuous event ingestion
- **Persistent Storage**: PostgreSQL with optimized indexes for fast queries
- **Immutable Archival**: S3 Object Lock for regulatory compliance
- **Constitutional Verification**: Built-in constitutional hash validation (`cdd01ef066bc6cf2`)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Services      │    │  Audit Engine   │    │   Storage       │
│                 │    │                 │    │                 │
│ Policy Engine   │────┤ FastAPI Service │────┤ PostgreSQL      │
│ Sandbox Ctrl    │    │ Port 8003       │    │ (Events)        │
│ Evolution Mgr   │    │                 │    │                 │
└─────────────────┘    │ Redpanda        │    │ Redis           │
                       │ Consumer        │    │ (Cache)         │
                       │                 │    │                 │
                       │ S3 Archival     │────┤ S3 Bucket       │
                       │ (Daily)         │    │ (Archive)       │
                       └─────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- AWS credentials (for S3 archival)
- 8GB+ RAM recommended

### Deployment

```bash
# Clone and navigate to service
cd /home/ubuntu/ACGS/services/core/audit-engine

# Set AWS credentials (optional, for S3 archival)
export AWS_ACCESS_KEY_ID=your_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_key

# Deploy all services
./deploy.sh
```

### Verification

```bash
# Health check
curl http://localhost:8003/health

# Verify constitutional hash
curl http://localhost:8003/api/v1/audit/verify

# Test event ingestion
curl -X POST http://localhost:8003/api/v1/audit/events \
  -H 'Content-Type: application/json' \
  -d '{
    "event_type": "policy_enforcement",
    "service_name": "policy_engine", 
    "action": "evaluate_request",
    "outcome": "allowed",
    "payload": {"confidence": 0.95}
  }'
```

## API Reference

### Authentication

All endpoints require Bearer token authentication:
```bash
curl -H "Authorization: Bearer your_token" http://localhost:8003/api/v1/audit/events
```

### Core Endpoints

#### `POST /api/v1/audit/events`
Ingest new audit event.

**Request Body:**
```json
{
  "event_type": "string",           // Required: Event type
  "service_name": "string",         // Required: Originating service
  "agent_id": "string",            // Optional: Agent identifier  
  "action": "string",              // Required: Action performed
  "outcome": "string",             // Required: Outcome (success/failure/error)
  "payload": {},                   // Optional: Event-specific data
  "user_id": "string",             // Optional: User identifier
  "session_id": "string",          // Optional: Session identifier
  "ip_address": "string"           // Optional: Client IP address
}
```

**Response:**
```json
{
  "success": true,
  "event_id": "uuid",
  "processing_time_ms": 12.34
}
```

#### `GET /api/v1/audit/events`
Query audit events with filters.

**Query Parameters:**
- `agent_id`: Filter by agent ID
- `event_type`: Filter by event type
- `start_date`: ISO timestamp for range start
- `end_date`: ISO timestamp for range end  
- `limit`: Max results (default: 100, max: 1000)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "events": [...],
  "total_count": 1234,
  "limit": 100,
  "offset": 0,
  "query_time_ms": 45.67
}
```

#### `GET /api/v1/audit/events/{event_id}`
Retrieve specific event by ID.

#### `GET /api/v1/audit/verify`
Verify complete audit chain integrity.

**Response:**
```json
{
  "is_valid": true,
  "total_events": 12345,
  "verification_time_ms": 234.56,
  "last_chain_hash": "abc123...",
  "constitutional_hash_verified": true
}
```

#### `POST /api/v1/audit/export`
Export events for date range.

**Request Body:**
```json
{
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-31T23:59:59Z",
  "format": "json",                    // json or csv
  "include_sensitive": false
}
```

### Monitoring Endpoints

#### `GET /health`
Service health check.

#### `GET /metrics`
Prometheus metrics endpoint.

**Key Metrics:**
- `audit_events_ingested_total`: Total events ingested by source/type/result
- `audit_query_duration_seconds`: Query execution time histogram
- `audit_chain_integrity_status`: Chain integrity status (1=valid, 0=invalid)
- `s3_archival_operations_total`: S3 operations by type/result
- `redpanda_consumer_lag`: Current consumer lag

## Performance Specifications

### Ingestion Performance
- **Target**: 1000+ events/second
- **API Response**: <100ms P99 latency
- **Batch Processing**: Supports concurrent ingestion

### Query Performance  
- **Indexed Queries**: <100ms response time
- **Complex Queries**: <500ms response time
- **Chain Verification**: <5 seconds for 1M events

### Resource Usage
- **Memory**: 2GB baseline + 1KB per cached event
- **CPU**: 2 cores for 1000 events/second
- **Storage**: ~1KB per event in PostgreSQL

## Database Schema

### audit_events Table
```sql
CREATE TABLE audit_events (
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

-- Optimized indexes
CREATE INDEX idx_audit_timestamp ON audit_events(timestamp);
CREATE INDEX idx_audit_agent ON audit_events(agent_id);
CREATE INDEX idx_audit_type ON audit_events(event_type);
CREATE INDEX idx_audit_chain_hash ON audit_events(chain_hash);
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:password@localhost:5432/audit_db` | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection |
| `KAFKA_BROKERS` | `localhost:9092` | Redpanda/Kafka brokers |
| `KAFKA_TOPIC` | `constitutional-events` | Topic to consume |
| `S3_BUCKET` | `acgs-audit-archive` | S3 bucket for archival |
| `AWS_REGION` | `us-east-1` | AWS region |

### Security Configuration

- **JWT Authentication**: Configure token validation
- **TLS**: Enable TLS for production deployment
- **Network Security**: Restrict access to internal networks
- **S3 Object Lock**: 7-year retention for compliance

## Testing

### Unit Tests
```bash
# Install test dependencies
pip install -r requirements.txt

# Run test suite
pytest tests/ -v

# Run performance benchmarks
python tests/test_audit_engine.py
```

### Load Testing
```bash
# Test ingestion performance
python -c "
import asyncio
from tests.test_audit_engine import run_performance_benchmarks
asyncio.run(run_performance_benchmarks())
"
```

### Integration Testing
```bash
# Test with live services
docker-compose exec audit-engine python tests/test_audit_engine.py
```

## Troubleshooting

### Common Issues

**1. High Memory Usage**
- Reduce Redis cache TTL
- Implement event pagination
- Add database connection pooling limits

**2. Slow Query Performance**
- Verify indexes are present: `EXPLAIN ANALYZE SELECT ...`
- Consider partitioning by timestamp
- Add composite indexes for common query patterns

**3. Chain Integrity Failures**
- Check for concurrent modifications
- Verify database transaction isolation
- Restart service to reload chain state

**4. S3 Archival Failures**
- Verify AWS credentials and permissions
- Check S3 bucket policy and Object Lock configuration
- Monitor archival logs: `docker-compose logs audit-engine | grep archival`

### Monitoring

**Key Alerts:**
- Chain integrity status drops to 0
- Event ingestion rate falls below 500/second
- Query response time exceeds 200ms
- S3 archival failures

**Log Analysis:**
```bash
# View real-time logs
docker-compose logs -f audit-engine

# Filter for errors
docker-compose logs audit-engine | grep ERROR

# Monitor performance
docker-compose logs audit-engine | grep "processing_time_ms\|query_time_ms"
```

## Architecture Decisions

### Why Redpanda over Kafka?
- Simpler deployment (no Zookeeper)
- Better performance for small clusters  
- Kafka-compatible API

### Why PostgreSQL over MongoDB?
- ACID compliance for audit trails
- Better query performance for time-series data
- Mature ecosystem and tooling

### Why RSA over ECDSA?
- Wider compatibility
- Well-established security properties
- Simpler key management

## Contributing

1. Follow the existing code structure
2. Add tests for new functionality  
3. Update this README for significant changes
4. Ensure constitutional hash verification passes

## Constitutional Compliance

This service implements constitutional governance principles:

- **Immutable Audit Trails**: Cryptographic hash chaining prevents tampering
- **Transparency**: All events are logged with full context
- **Accountability**: Digital signatures provide non-repudiation
- **Integrity**: Chain verification ensures data consistency

Constitutional Hash: `cdd01ef066bc6cf2`