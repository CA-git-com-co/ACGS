# Phase 1: DGM Service Foundation - Detailed Specifications

## 1.1 Infrastructure Setup

### 1.1.1 Docker Environment Setup

**Objective**: Create secure, scalable Docker containers for DGM service with proper resource management and security constraints.

**Deliverables**:

- Production-ready Dockerfile with multi-stage builds
- Docker Compose configuration for local development
- Container security policies and resource limits
- Volume management for persistent data

**Technical Specifications**:

```dockerfile
# Dockerfile.dgm-service
FROM python:3.11-slim as base

# Security: Create non-root user
RUN useradd -m -u 1000 dgm && \
    apt-get update && apt-get install -y \
    build-essential git curl docker.io && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base as production
COPY --chown=dgm:dgm . .
USER dgm

# Resource limits
LABEL resource.cpu="4.0"
LABEL resource.memory="16G"
LABEL security.no-new-privileges="true"

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8007/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
```

**Acceptance Criteria**:

- [ ] Container builds successfully with security scanning passing
- [ ] Resource limits enforced (CPU: 4 cores, Memory: 16GB)
- [ ] Health checks respond within 10 seconds
- [ ] Non-root user execution verified
- [ ] Volume mounts for archive and logs functional

**Dependencies**: None
**Estimated Effort**: 1 week
**Risk Level**: Low

### 1.1.2 Kubernetes Deployment

**Objective**: Design production-ready Kubernetes manifests with auto-scaling, health checks, and service mesh integration.

**Deliverables**:

- Kubernetes Deployment manifests
- Service and Ingress configurations
- HorizontalPodAutoscaler setup
- NetworkPolicy for security

**Technical Specifications**:

```yaml
# k8s/dgm-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dgm-service
  namespace: acgs
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dgm-service
  template:
    metadata:
      labels:
        app: dgm-service
        version: v1.0.0
    spec:
      serviceAccountName: dgm-service
      containers:
        - name: dgm-service
          image: acgs/dgm-service:latest
          ports:
            - containerPort: 8007
          resources:
            requests:
              memory: '8Gi'
              cpu: '2000m'
            limits:
              memory: '16Gi'
              cpu: '4000m'
          livenessProbe:
            httpGet:
              path: /health
              port: 8007
            initialDelaySeconds: 60
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: 8007
            initialDelaySeconds: 30
            periodSeconds: 10
          env:
            - name: SERVICE_NAME
              value: 'dgm-service'
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: acgs-secrets
                  key: database-url
```

**Acceptance Criteria**:

- [ ] Deployment scales automatically based on CPU/memory usage
- [ ] Health checks prevent traffic to unhealthy pods
- [ ] Service mesh integration functional
- [ ] Network policies restrict unauthorized access
- [ ] Rolling updates complete without downtime

**Dependencies**: Kubernetes cluster, service mesh
**Estimated Effort**: 1.5 weeks
**Risk Level**: Medium

### 1.1.3 Storage Architecture

**Objective**: Implement persistent storage solution for DGM archive, logs, and temporary workspaces with backup and recovery.

**Deliverables**:

- Persistent Volume Claims for different data types
- Backup and recovery procedures
- Storage monitoring and alerting
- Data retention policies

**Technical Specifications**:

```yaml
# k8s/storage/dgm-archive-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dgm-archive-pvc
  namespace: acgs
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 2Ti
  storageClassName: fast-ssd
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dgm-workspace-pvc
  namespace: acgs
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Gi
  storageClassName: fast-ssd
```

**Storage Requirements**:

- **Archive Storage**: 2TB with daily incremental backups
- **Workspace Storage**: 500GB for temporary improvement workspaces
- **Log Storage**: 100GB with 30-day retention
- **Backup Storage**: 6TB for 3-month archive retention

**Acceptance Criteria**:

- [ ] All storage volumes provisioned and accessible
- [ ] Backup procedures tested and documented
- [ ] Storage monitoring alerts configured
- [ ] Data retention policies implemented
- [ ] Recovery procedures validated

**Dependencies**: Storage infrastructure
**Estimated Effort**: 1 week
**Risk Level**: Medium

### 1.1.4 Network Configuration

**Objective**: Configure secure internal networking for DGM service communication with ACGS core services.

**Deliverables**:

- Network policies for service-to-service communication
- Load balancer configuration
- SSL/TLS certificate management
- Network monitoring setup

**Technical Specifications**:

```yaml
# k8s/network/dgm-network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: dgm-service-policy
  namespace: acgs
spec:
  podSelector:
    matchLabels:
      app: dgm-service
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: acgs
      ports:
        - protocol: TCP
          port: 8007
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: acgs
      ports:
        - protocol: TCP
          port: 8000 # Auth Service
        - protocol: TCP
          port: 8001 # AC Service
        - protocol: TCP
          port: 8004 # GS Service
    - to: [] # Allow external API calls (LLM services)
      ports:
        - protocol: TCP
          port: 443
```

**Acceptance Criteria**:

- [ ] Network policies enforce security boundaries
- [ ] Load balancer distributes traffic evenly
- [ ] SSL/TLS certificates auto-renew
- [ ] Network latency <10ms between services
- [ ] Network monitoring captures all traffic

**Dependencies**: Network infrastructure, certificates
**Estimated Effort**: 1 week
**Risk Level**: Low

## 1.2 Database Architecture

### 1.2.1 Database Schema Design

**Objective**: Design comprehensive PostgreSQL schema optimized for DGM operations with proper indexing and relationships.

**Deliverables**:

- Complete database schema with all tables
- Entity relationship diagrams
- Index optimization strategy
- Data model documentation

**Technical Specifications**:

```sql
-- Core DGM Archive table
CREATE TABLE dgm_archive (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    archive_entry_id VARCHAR(255) UNIQUE NOT NULL,
    parent_entry_id VARCHAR(255) REFERENCES dgm_archive(archive_entry_id),
    generation_number INTEGER NOT NULL DEFAULT 0,
    service_name VARCHAR(100) NOT NULL,
    problem_statement TEXT NOT NULL,
    solution_patch TEXT,
    performance_metrics JSONB NOT NULL,
    accuracy_score DECIMAL(5,4) NOT NULL,
    constitutional_compliance_score DECIMAL(5,4) NOT NULL,
    evaluation_results JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    -- Performance indexes
    INDEX idx_dgm_archive_service_generation (service_name, generation_number),
    INDEX idx_dgm_archive_score_desc (accuracy_score DESC),
    INDEX idx_dgm_archive_compliance (constitutional_compliance_score DESC),
    INDEX idx_dgm_archive_created_desc (created_at DESC),
    INDEX idx_dgm_archive_parent (parent_entry_id),

    -- Constraints
    CONSTRAINT chk_accuracy_score CHECK (accuracy_score >= 0 AND accuracy_score <= 1),
    CONSTRAINT chk_compliance_score CHECK (constitutional_compliance_score >= 0 AND constitutional_compliance_score <= 1)
);

-- Improvements tracking table
CREATE TABLE dgm_improvements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    improvement_id VARCHAR(255) UNIQUE NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    problem_statement TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(50) NOT NULL DEFAULT 'queued',
    progress INTEGER DEFAULT 0,
    max_improvement_time INTEGER DEFAULT 1800,
    constitutional_constraints JSONB,
    performance_metrics JSONB NOT NULL,
    results JSONB,
    archive_entry_id VARCHAR(255) REFERENCES dgm_archive(archive_entry_id),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    -- Indexes for operational queries
    INDEX idx_dgm_improvements_status_priority (status, priority),
    INDEX idx_dgm_improvements_service_created (service_name, created_at DESC),
    INDEX idx_dgm_improvements_active (status) WHERE status IN ('queued', 'running'),

    -- Constraints
    CONSTRAINT chk_progress CHECK (progress >= 0 AND progress <= 100),
    CONSTRAINT chk_priority CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT chk_status CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled'))
);
```

**Acceptance Criteria**:

- [ ] All tables created with proper constraints
- [ ] Indexes optimize common query patterns
- [ ] Foreign key relationships maintain data integrity
- [ ] Schema supports concurrent access patterns
- [ ] Documentation covers all entities and relationships

**Dependencies**: PostgreSQL 15+ instance
**Estimated Effort**: 1.5 weeks
**Risk Level**: Low

### 1.2.2 Migration Scripts

**Objective**: Create robust database migration system with rollback capabilities and data integrity validation.

**Deliverables**:

- Migration script framework
- Version control for schema changes
- Rollback procedures for each migration
- Data integrity validation scripts

**Technical Specifications**:

```python
# migrations/001_create_dgm_tables.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    """Create initial DGM tables."""

    # Create dgm_archive table
    op.create_table(
        'dgm_archive',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('archive_entry_id', sa.String(255), nullable=False, unique=True),
        sa.Column('parent_entry_id', sa.String(255), nullable=True),
        sa.Column('generation_number', sa.Integer, nullable=False, default=0),
        sa.Column('service_name', sa.String(100), nullable=False),
        sa.Column('problem_statement', sa.Text, nullable=False),
        sa.Column('solution_patch', sa.Text, nullable=True),
        sa.Column('performance_metrics', postgresql.JSONB, nullable=False),
        sa.Column('accuracy_score', sa.Numeric(5, 4), nullable=False),
        sa.Column('constitutional_compliance_score', sa.Numeric(5, 4), nullable=False),
        sa.Column('evaluation_results', postgresql.JSONB, nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='active'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Create indexes
    op.create_index('idx_dgm_archive_service_generation', 'dgm_archive', ['service_name', 'generation_number'])
    op.create_index('idx_dgm_archive_score_desc', 'dgm_archive', [sa.desc('accuracy_score')])

    # Add constraints
    op.create_check_constraint(
        'chk_accuracy_score',
        'dgm_archive',
        'accuracy_score >= 0 AND accuracy_score <= 1'
    )

def downgrade():
    """Rollback DGM tables creation."""
    op.drop_table('dgm_archive')
```

**Acceptance Criteria**:

- [ ] Migration framework supports forward and backward migrations
- [ ] All migrations include comprehensive rollback procedures
- [ ] Data integrity checks validate migration success
- [ ] Migration history tracked and auditable
- [ ] Zero-downtime migration capability for production

**Dependencies**: Database schema design
**Estimated Effort**: 1 week
**Risk Level**: Medium

### 1.2.3 Redis Cache Implementation

**Objective**: Implement high-performance Redis caching strategy for real-time metrics, archive entries, and session data.

**Deliverables**:

- Redis configuration and deployment
- Caching layer implementation
- Cache invalidation strategies
- Performance monitoring for cache hit rates

**Technical Specifications**:

```python
# app/core/redis_cache.py
import redis.asyncio as redis
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib

class DGMRedisCache:
    """High-performance Redis cache for DGM operations."""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour

    # Performance metrics caching
    async def store_performance_metrics(self, service_name: str, metrics: Dict[str, Any]):
        """Store real-time performance metrics with automatic expiration."""
        key = f"dgm:metrics:{service_name}:current"

        # Store with 5-minute TTL for real-time monitoring
        await self.redis.setex(
            key,
            300,
            json.dumps({
                **metrics,
                "timestamp": datetime.utcnow().isoformat(),
                "cache_key": key
            })
        )

        # Add to time-series for trend analysis (24-hour retention)
        ts_key = f"dgm:metrics:{service_name}:timeseries"
        score = datetime.utcnow().timestamp()
        await self.redis.zadd(ts_key, {json.dumps(metrics): score})

        # Cleanup old entries (keep last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        await self.redis.zremrangebyscore(ts_key, 0, cutoff.timestamp())

    # Archive entry caching with intelligent prefetching
    async def cache_archive_entry(self, entry_id: str, entry_data: Dict[str, Any]):
        """Cache frequently accessed archive entries with metadata."""
        key = f"dgm:archive:{entry_id}"

        # Add metadata for cache management
        cache_data = {
            **entry_data,
            "cached_at": datetime.utcnow().isoformat(),
            "access_count": await self._increment_access_count(entry_id)
        }

        # Use longer TTL for high-value archive entries
        ttl = self._calculate_cache_ttl(cache_data)
        await self.redis.setex(key, ttl, json.dumps(cache_data))

        # Update access patterns for intelligent prefetching
        await self._update_access_patterns(entry_id)

    async def _calculate_cache_ttl(self, entry_data: Dict[str, Any]) -> int:
        """Calculate optimal TTL based on entry characteristics."""
        base_ttl = 3600  # 1 hour

        # Extend TTL for high-performing entries
        accuracy_score = entry_data.get("accuracy_score", 0)
        compliance_score = entry_data.get("constitutional_compliance_score", 0)

        if accuracy_score > 0.8 and compliance_score > 0.9:
            return base_ttl * 4  # 4 hours for high-quality entries
        elif accuracy_score > 0.6:
            return base_ttl * 2  # 2 hours for good entries
        else:
            return base_ttl  # 1 hour for standard entries
```

**Cache Strategy**:

- **Hot Data**: Performance metrics (5-minute TTL)
- **Warm Data**: Archive entries (1-4 hour TTL based on quality)
- **Cold Data**: Historical metrics (24-hour retention)
- **Session Data**: User sessions and tokens (configurable TTL)

**Acceptance Criteria**:

- [ ] Cache hit rate >80% for frequently accessed data
- [ ] Cache invalidation maintains data consistency
- [ ] Performance metrics show <10ms cache response time
- [ ] Memory usage optimized with intelligent eviction
- [ ] Cache monitoring and alerting functional

**Dependencies**: Redis 7+ cluster
**Estimated Effort**: 1.5 weeks
**Risk Level**: Low

### 1.2.4 Database Performance Optimization

**Objective**: Optimize database performance for DGM workloads with advanced indexing, partitioning, and query optimization.

**Deliverables**:

- Performance-optimized indexes
- Table partitioning strategy
- Query optimization guidelines
- Database monitoring and tuning

**Technical Specifications**:

```sql
-- Advanced indexing strategy
CREATE INDEX CONCURRENTLY idx_dgm_archive_composite_perf
ON dgm_archive (service_name, accuracy_score DESC, created_at DESC)
WHERE status = 'active';

-- Partial index for active improvements
CREATE INDEX CONCURRENTLY idx_dgm_improvements_active_priority
ON dgm_improvements (priority, created_at DESC)
WHERE status IN ('queued', 'running');

-- GIN index for JSONB performance metrics queries
CREATE INDEX CONCURRENTLY idx_dgm_archive_metrics_gin
ON dgm_archive USING GIN (performance_metrics);

-- Partitioning for performance metrics table
CREATE TABLE dgm_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    measurement_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    archive_entry_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (measurement_timestamp);

-- Create monthly partitions
CREATE TABLE dgm_performance_metrics_2024_01 PARTITION OF dgm_performance_metrics
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Automated partition management
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name text, start_date date)
RETURNS void AS $$
DECLARE
    partition_name text;
    end_date date;
BEGIN
    partition_name := table_name || '_' || to_char(start_date, 'YYYY_MM');
    end_date := start_date + interval '1 month';

    EXECUTE format('CREATE TABLE %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
                   partition_name, table_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;
```

**Performance Targets**:

- **Query Response Time**: <100ms for 95% of queries
- **Concurrent Connections**: Support 500+ concurrent connections
- **Throughput**: 10,000+ transactions per second
- **Index Efficiency**: >95% index usage for complex queries

**Acceptance Criteria**:

- [ ] All performance targets met under load testing
- [ ] Automated partition management functional
- [ ] Query execution plans optimized
- [ ] Database monitoring shows consistent performance
- [ ] Backup and recovery procedures validated

**Dependencies**: Database schema, Redis cache
**Estimated Effort**: 2 weeks
**Risk Level**: Medium
