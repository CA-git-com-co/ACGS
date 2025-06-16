# ACGS-1 Production Technical Documentation

**Version**: 3.0.0  
**Date**: 2025-06-16  
**Status**: Production Ready  
**Constitution Hash**: cdd01ef066bc6cf2

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Service Specifications](#service-specifications)
3. [API Documentation](#api-documentation)
4. [Deployment Architecture](#deployment-architecture)
5. [Configuration Management](#configuration-management)
6. [Integration Patterns](#integration-patterns)
7. [Performance Specifications](#performance-specifications)
8. [Security Architecture](#security-architecture)

## System Architecture

### Overview
ACGS-1 (AI Compliance Governance System) is a production-grade constitutional governance platform built on microservices architecture with blockchain integration via Quantumagi Solana deployment.

### Core Components
```
┌─────────────────────────────────────────────────────────────┐
│                    ACGS-1 Architecture                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer                                             │
│  ├── React Dashboard (Constitutional Governance UI)        │
│  └── API Gateway (HAProxy Load Balancer)                   │
├─────────────────────────────────────────────────────────────┤
│  Core Services Layer (Ports 8000-8006)                     │
│  ├── Auth Service (8000)     - Authentication & Authorization│
│  ├── AC Service (8001)       - Constitutional AI           │
│  ├── Integrity Service (8002) - Cryptographic Integrity    │
│  ├── FV Service (8003)       - Formal Verification         │
│  ├── GS Service (8004)       - Governance Synthesis        │
│  ├── PGC Service (8005)      - Policy Governance & Compliance│
│  └── EC Service (8006)       - Executive Council           │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                       │
│  ├── PostgreSQL (5432)       - Primary Database           │
│  ├── Redis (6379)           - Caching & Session Store      │
│  ├── Prometheus (9090)       - Metrics Collection          │
│  ├── Grafana (3000)         - Monitoring Dashboard         │
│  └── OPA (8181)             - Policy Engine                │
├─────────────────────────────────────────────────────────────┤
│  Blockchain Layer                                           │
│  ├── Quantumagi Constitution Program                       │
│  ├── Quantumagi Policy Program                             │
│  └── Quantumagi Logging Program                            │
└─────────────────────────────────────────────────────────────┘
```

### Service Dependencies
```mermaid
graph TD
    A[Auth Service] --> D[PostgreSQL]
    B[AC Service] --> A
    B --> D
    C[Integrity Service] --> A
    C --> D
    E[FV Service] --> B
    E --> C
    F[GS Service] --> B
    F --> C
    G[PGC Service] --> B
    G --> F
    G --> H[OPA]
    I[EC Service] --> A
    I --> G
    J[Redis] --> A
    J --> B
    J --> C
    J --> E
    J --> F
    J --> G
    J --> I
```

## Service Specifications

### 1. Auth Service (Port 8000)
**Purpose**: Authentication, authorization, and user management  
**Technology**: FastAPI, JWT, PostgreSQL  
**Key Features**:
- JWT token management with refresh tokens
- Role-based access control (RBAC)
- Multi-factor authentication support
- Session management with Redis

**Health Endpoint**: `GET /health`  
**Key APIs**:
- `POST /auth/login` - User authentication
- `POST /auth/refresh` - Token refresh
- `GET /auth/profile` - User profile
- `POST /auth/logout` - Session termination

### 2. AC Service (Port 8001)
**Purpose**: Constitutional AI and compliance management  
**Technology**: FastAPI, LangChain, Multi-Model LLM Ensemble  
**Key Features**:
- Constitutional principle management
- Multi-model consensus engine (Qwen3-32B, DeepSeek Chat v3)
- Constitutional council voting mechanisms
- Policy compliance validation

**Health Endpoint**: `GET /health`  
**Key APIs**:
- `GET /api/v1/constitutional-council/members` - Council members
- `GET /api/v1/voting/mechanisms` - Voting mechanisms
- `POST /api/v1/constitutional/validate` - Constitutional validation

### 3. Integrity Service (Port 8002)
**Purpose**: Cryptographic integrity and verification  
**Technology**: FastAPI, Cryptography, PGP  
**Key Features**:
- Digital signature verification
- Hash integrity checking
- PGP key management
- Constitutional hash validation

**Health Endpoint**: `GET /health`  
**Key APIs**:
- `POST /api/v1/verify/signature` - Signature verification
- `POST /api/v1/verify/hash` - Hash verification
- `GET /api/v1/constitutional/validate` - Constitutional validation

### 4. FV Service (Port 8003)
**Purpose**: Formal verification and mathematical proofs  
**Technology**: FastAPI, Z3 Theorem Prover  
**Key Features**:
- Policy formal verification
- Mathematical proof generation
- Constraint satisfaction solving
- Verification result caching

**Health Endpoint**: `GET /health`  
**Key APIs**:
- `POST /api/v1/verify/policy` - Policy verification
- `POST /api/v1/prove/theorem` - Theorem proving
- `GET /api/v1/verification/status` - Verification status

### 5. GS Service (Port 8004)
**Purpose**: Governance synthesis and policy generation  
**Technology**: FastAPI, LangChain, Policy Synthesis Engine  
**Key Features**:
- Four-tier risk strategy (standard/enhanced/consensus/human)
- Policy synthesis and generation
- Governance workflow orchestration
- Multi-model consensus for high-risk scenarios

**Health Endpoint**: `GET /health`  
**Key APIs**:
- `POST /api/v1/synthesize/policy` - Policy synthesis
- `POST /api/v1/governance/workflow` - Workflow management
- `GET /api/v1/synthesis/status` - Synthesis status

### 6. PGC Service (Port 8005)
**Purpose**: Policy governance and compliance enforcement  
**Technology**: FastAPI, OPA, Constitutional Validation  
**Key Features**:
- Real-time policy compliance checking
- Constitutional governance workflows
- Policy lifecycle management
- Enforcement engine with <25ms latency

**Health Endpoint**: `GET /health`  
**Key APIs**:
- `POST /api/v1/constitutional/validate` - Constitutional validation
- `POST /api/v1/governance-workflows/policy-creation` - Policy creation
- `GET /api/v1/compliance/status` - Compliance status

### 7. EC Service (Port 8006)
**Purpose**: Executive council and oversight management  
**Technology**: FastAPI, Governance Oversight  
**Key Features**:
- Executive decision tracking
- Oversight workflow management
- Audit trail generation
- WINA (What Is Not Allowed) oversight

**Health Endpoint**: `GET /health`  
**Key APIs**:
- `POST /api/v1/oversight/decision` - Executive decisions
- `GET /api/v1/audit/trail` - Audit trail
- `POST /api/v1/wina/oversight` - WINA oversight

## API Documentation

### Authentication
All API endpoints require JWT authentication except health endpoints.

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Response Format
```json
{
  "status": "success|error",
  "data": {},
  "message": "Human readable message",
  "timestamp": "2025-06-16T15:00:00Z",
  "request_id": "uuid"
}
```

### Error Codes
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limited
- `500` - Internal Server Error

## Deployment Architecture

### Host-Based Deployment
ACGS-1 uses host-based deployment for optimal performance and resource utilization.

**Service Startup Order**:
1. Infrastructure (PostgreSQL, Redis, OPA)
2. Auth Service (8000)
3. Core Services (8001-8004)
4. Governance Services (8005-8006)
5. Monitoring (Prometheus, Grafana)

**Startup Script**: `scripts/start_missing_services.sh`

### Environment Configuration
```bash
# Database
DATABASE_URL=postgresql://acgs_user:password@localhost:5432/acgs_pgp_db
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=<secure_key>
ENCRYPTION_KEY=<encryption_key>

# Services
AUTH_SERVICE_URL=http://localhost:8000
AC_SERVICE_URL=http://localhost:8001
# ... other service URLs

# Blockchain
CONSTITUTION_HASH=cdd01ef066bc6cf2
SOLANA_NETWORK=devnet
```

### Load Balancing
HAProxy configuration for service load balancing:
```
frontend acgs_frontend
    bind *:80
    default_backend acgs_services

backend acgs_services
    balance roundrobin
    server auth1 localhost:8000 check
    server ac1 localhost:8001 check
    # ... other servers
```

## Configuration Management

### Service Configuration
Each service uses environment-specific configuration files:
- `config/development.env`
- `config/staging.env`
- `config/production.env`

### Port Configuration
Centralized port management in `config/ports.yaml`:
```yaml
core_services:
  auth_service: 8000
  ac_service: 8001
  integrity_service: 8002
  fv_service: 8003
  gs_service: 8004
  pgc_service: 8005
  ec_service: 8006
```

### Redis Configuration
Production Redis configuration with persistence:
```
# Persistence
save 900 1
save 300 10
save 60 10000

# AOF
appendonly yes
appendfsync everysec

# Memory
maxmemory 4gb
maxmemory-policy allkeys-lru
```

## Integration Patterns

### 1. Service-to-Service Communication
- **Protocol**: HTTP/REST with JSON
- **Authentication**: Service-to-service JWT tokens
- **Timeout**: 30 seconds default
- **Retry**: Exponential backoff (3 attempts)

### 2. Database Integration
- **Connection Pooling**: 20 connections per service
- **Transaction Management**: ACID compliance
- **Migration**: Alembic for schema management

### 3. Blockchain Integration
- **Quantumagi Programs**: Constitution, Policy, Logging
- **Network**: Solana Devnet
- **Transaction Cost**: <0.01 SOL per governance action
- **Confirmation**: 32 slot confirmation

### 4. Caching Strategy
- **L1 Cache**: In-memory service cache
- **L2 Cache**: Redis distributed cache
- **TTL**: 300 seconds for governance data
- **Invalidation**: Event-driven cache invalidation

## Performance Specifications

### Response Time Targets
- **Health Endpoints**: <50ms
- **Authentication**: <100ms
- **Constitutional Validation**: <500ms
- **Policy Synthesis**: <2s
- **Governance Workflows**: <500ms

### Throughput Targets
- **Concurrent Users**: >1000
- **Governance Actions/sec**: >100
- **API Requests/sec**: >10,000
- **Database Queries/sec**: >5,000

### Availability Targets
- **System Uptime**: >99.9%
- **Service Availability**: >99.5%
- **Database Availability**: >99.9%
- **Blockchain Connectivity**: >99.5%

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: RS256 algorithm
- **Token Expiry**: 1 hour (access), 7 days (refresh)
- **RBAC**: Role-based access control
- **MFA**: Multi-factor authentication support

### Data Protection
- **Encryption at Rest**: AES-256
- **Encryption in Transit**: TLS 1.3
- **Key Management**: Secure key rotation
- **PII Protection**: Data anonymization

### Constitutional Security
- **Constitution Hash**: cdd01ef066bc6cf2
- **Multi-signature**: 5/7 council members required
- **Immutable Audit**: Blockchain-based audit trail
- **Compliance Validation**: Real-time constitutional compliance

### Network Security
- **Rate Limiting**: 100 requests/minute per user
- **DDoS Protection**: HAProxy rate limiting
- **Firewall**: Service-specific port restrictions
- **VPN**: Secure administrative access

---

## Governance Workflows

### 1. Policy Creation Workflow
```mermaid
sequenceDiagram
    participant User
    participant PGC as PGC Service
    participant AC as AC Service
    participant GS as GS Service
    participant FV as FV Service

    User->>PGC: POST /governance-workflows/policy-creation
    PGC->>AC: Validate constitutional compliance
    AC->>PGC: Compliance result
    PGC->>GS: Synthesize policy
    GS->>PGC: Policy synthesis
    PGC->>FV: Formal verification
    FV->>PGC: Verification result
    PGC->>User: Policy creation result
```

### 2. Constitutional Compliance Workflow
```mermaid
sequenceDiagram
    participant Service
    participant PGC as PGC Service
    participant AC as AC Service
    participant Integrity as Integrity Service

    Service->>PGC: POST /constitutional/validate
    PGC->>AC: Check constitutional principles
    PGC->>Integrity: Verify constitution hash
    Integrity->>PGC: Hash validation
    AC->>PGC: Principle compliance
    PGC->>Service: Compliance result
```

### 3. Policy Enforcement Workflow
Real-time policy enforcement with <25ms latency target.

### 4. WINA Oversight Workflow
What Is Not Allowed oversight and monitoring.

### 5. Audit & Transparency Workflow
Comprehensive audit trail and transparency reporting.

## Monitoring & Observability

### Metrics Collection
- **Prometheus**: System and application metrics
- **Grafana**: Visualization and alerting
- **Custom Metrics**: Constitutional compliance scores

### Key Metrics
- Response time percentiles (p50, p95, p99)
- Error rates by service and endpoint
- Constitutional compliance accuracy
- Governance workflow completion rates
- Resource utilization (CPU, memory, disk)

### Alerting Rules
- Service health degradation
- Constitutional compliance failures
- Performance threshold breaches
- Security incidents

### Log Management
- Structured logging with JSON format
- Centralized log aggregation
- Log retention: 90 days
- Security event logging

## Backup & Disaster Recovery

### Backup Strategy
- **Daily Backups**: Configurations, service states, blockchain data
- **Retention**: 7 daily, 4 weekly, 12 monthly
- **Storage**: Local + encrypted offsite
- **Automation**: Cron-based scheduling

### Recovery Procedures
- **RTO**: <1 hour (Recovery Time Objective)
- **RPO**: <15 minutes (Recovery Point Objective)
- **Automated Testing**: Monthly DR tests
- **Emergency Procedures**: Documented runbooks

### Emergency Contacts
- **Primary**: ACGS-1 Operations Team
- **Secondary**: Infrastructure Team
- **Escalation**: System Architecture Team

---

**Document Maintained By**: ACGS-1 Operations Team
**Last Updated**: 2025-06-16
**Next Review**: 2025-07-16
