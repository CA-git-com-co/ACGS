# ACGS-2 Structural Decomposition
**Constitutional Hash: cdd01ef066bc6cf2**
**Generated: 2025-07-18T13:13:22Z**

## Executive Summary

This document provides a comprehensive structural decomposition of the Advanced Constitutional Governance System (ACGS-2) codebase, organizing repositories into Core, Platform, Shared, Protocol, and Security layers with detailed cataloguing of entrypoints, FastAPI applications, models, and middleware.

## Service Layer Architecture

### 1. Core Services Layer
**Location**: `/services/core/`
**Purpose**: Constitutional AI governance, policy management, and core business logic

#### Services Catalog:

##### Constitutional AI Service
- **Path**: `services/core/constitutional-ai/`
- **Entry Point**: `ac_service/main.py`
- **FastAPI App**: `ac_service/app/main.py`
- **Port**: 8001
- **Models**: 
  - `app/models/constitutional.py`
  - `app/models/compliance.py`
- **Middleware**: 
  - `app/middleware/constitutional_middleware.py`
  - `app/middleware/cache_optimization.py`
- **API Endpoints**:
  - `/health` - Health check with constitutional validation
  - `/validation` - Constitutional compliance validation
  - `/compliance/score` - Compliance scoring
  - `/constitutional/compliance` - Constitutional hash verification

##### Policy Governance Service
- **Path**: `services/core/policy-governance/`
- **Entry Point**: `pgc_service/main.py`
- **FastAPI App**: `pgc_service/app/main.py`
- **Port**: 8003
- **Models**:
  - `app/models/policy.py`
  - `app/models/governance.py`
- **Middleware**:
  - `app/middleware/policy_enforcement.py`
  - `app/middleware/governance_validation.py`

##### Evolutionary Computation Service
- **Path**: `services/core/evolutionary-computation/`
- **Entry Point**: `app/main.py`
- **FastAPI App**: `app/main.py`
- **Port**: 8004
- **Models**:
  - `app/models/evolution.py`
  - `app/models/fitness.py`
- **Middleware**:
  - `app/middleware/evolution_tracking.py`

##### Formal Verification Service
- **Path**: `services/core/formal-verification/`
- **Entry Point**: `fv_service/main.py`
- **FastAPI App**: `fv_service/app/main.py`
- **Port**: 8005
- **Models**:
  - `app/models/verification.py`
  - `app/models/proof.py`
- **Middleware**:
  - `app/middleware/verification_middleware.py`

##### Governance Synthesis Service
- **Path**: `services/core/governance-synthesis/`
- **Entry Point**: `gs_service/main.py`
- **FastAPI App**: `gs_service/app/main.py`
- **Models**:
  - `app/models/synthesis.py`
  - `app/workflows/governance_workflow.py`

##### Code Analysis Service
- **Path**: `services/core/code-analysis/`
- **Entry Point**: `code_analysis_service/main.py`
- **FastAPI App**: `code_analysis_service/main.py`
- **Models**:
  - `code_analysis_service/app/models/analysis.py`
  - `code_analysis_service/app/models/metrics.py`

##### Additional Core Services:
- **Multi-Agent Coordination**: `services/core/multi-agent-coordination/main.py`
- **Consensus Engine**: `services/core/consensus-engine/main.py`
- **Audit Service**: `services/core/audit-service/main.py`
- **Security Validation**: `services/core/security-validation/main.py`
- **GDPR Compliance**: `services/core/gdpr-compliance/main.py`
- **Worker Agents**: `services/core/worker-agents/main.py`

### 2. Platform Services Layer
**Location**: `/services/platform_services/`
**Purpose**: Infrastructure services, authentication, and system-level operations

#### Services Catalog:

##### Authentication Service
- **Path**: `services/platform_services/authentication/`
- **Entry Point**: `auth_service/main.py`
- **FastAPI App**: `auth_service/app/main.py`
- **Port**: 8006
- **Models**:
  - `auth_service/app/models/user.py`
  - `auth_service/app/models/token.py`
  - `auth_service/app/schemas/auth.py`
- **Middleware**:
  - `auth_service/app/middleware/jwt_middleware.py`
  - `auth_service/app/middleware/rate_limiting.py`
- **Database**: PostgreSQL integration via `auth_service/app/db/`

##### Integrity Service
- **Path**: `services/platform_services/integrity/`
- **Entry Point**: `integrity_service/main.py`
- **FastAPI App**: `integrity_service/app/main.py`
- **Port**: 8002
- **Models**:
  - `integrity_service/app/models/audit.py`
  - `integrity_service/app/models/integrity.py`
- **Middleware**:
  - `integrity_service/app/middleware/audit_middleware.py`

##### API Gateway Service
- **Path**: `services/platform_services/api_gateway/`
- **Entry Point**: `gateway_service/main.py`
- **FastAPI App**: `gateway_service/app/main.py`
- **Port**: 8000
- **Models**:
  - `gateway_service/app/models/routing.py`
  - `gateway_service/app/models/load_balancing.py`
- **Services**:
  - `gateway_service/app/services/routing_service.py`
  - `gateway_service/app/services/auth_service.py`

##### Additional Platform Services:
- **Audit Aggregator**: `services/platform_services/audit_aggregator/main.py`
- **Blockchain Audit**: `services/platform_services/blockchain-audit/app/main.py`
- **Human Review**: `services/platform_services/human-review/app/main.py`
- **Image Compliance**: `services/platform_services/image-compliance/app/main.py`
- **Dialogue Assistant**: `services/platform_services/dialogue-assistant/app/main.py`
- **Recommendation System**: `services/platform_services/recommendation-system/app/main.py`

### 3. Shared Services Layer
**Location**: `/services/shared/`
**Purpose**: Common utilities, models, middleware, and infrastructure components

#### Shared Components:

##### Core Modules:
- **Models**: `services/shared/models/`
  - Base models for all services
  - Common data structures
  - Validation schemas

##### Middleware Components:
- **Path**: `services/shared/middleware/`
- **Components**:
  - `constitutional_middleware.py`
  - `cache_optimization_middleware.py`
  - `service_discovery_middleware.py`
  - `audit_middleware.py`
  - `rate_limiting_middleware.py`
  - `security_middleware.py`

##### Configuration Management:
- **Path**: `services/shared/config/`
- **Components**:
  - `infrastructure_config.py`
  - `service_config.py`
  - `database_config.py`
  - `monitoring_config.py`

##### Authentication & Security:
- **Path**: `services/shared/auth/`
- **Components**:
  - JWT token management
  - OAuth2 integration
  - Permission management
  - Security validations

##### Database & Persistence:
- **Path**: `services/shared/database/`
- **Components**:
  - Connection pooling
  - Migration management
  - Repository patterns
  - Data access objects

##### Monitoring & Observability:
- **Path**: `services/shared/monitoring/`
- **Components**:
  - Metrics collection
  - Logging frameworks
  - Health checks
  - Performance monitoring

##### Additional Shared Services:
- **Blackboard Coordination**: `services/shared/blackboard/main.py`
- **Routing Service**: `services/shared/routing/main.py`
- **Event Management**: `services/shared/events/`
- **Compliance Framework**: `services/shared/compliance/`

### 4. Protocol Services Layer
**Location**: `/services/mcp/`
**Purpose**: Model Context Protocol services and external integrations

#### MCP Services:

##### MCP Aggregator
- **Path**: `services/mcp/aggregator/`
- **Entry Point**: `main.py`
- **Purpose**: Aggregate multiple MCP services
- **Port**: 8010

##### MCP Browser
- **Path**: `services/mcp/browser/`
- **Entry Point**: `main.py`
- **Purpose**: Web browsing and content extraction
- **Port**: 8011

##### MCP Filesystem
- **Path**: `services/mcp/filesystem/`
- **Entry Point**: `main.py`
- **Purpose**: File system operations and management
- **Port**: 8012

##### MCP GitHub
- **Path**: `services/mcp/github/`
- **Entry Point**: `main.py`
- **Purpose**: GitHub API integration and repository management
- **Port**: 8013

### 5. Security Services Layer
**Distributed across layers with dedicated security components**

#### Security Components:

##### Core Security Services:
- **Security Validation**: `services/core/security-validation/main.py`
- **GDPR Compliance**: `services/core/gdpr-compliance/main.py`
- **Constitutional Compliance**: Embedded in Constitutional AI service

##### Platform Security:
- **Authentication Service**: JWT, OAuth2, multi-factor authentication
- **Integrity Service**: Audit logging, tamper detection
- **Blockchain Audit**: Immutable audit trails

##### Shared Security:
- **Security Middleware**: `services/shared/security/`
  - Rate limiting
  - Input validation
  - CSRF protection
  - Security headers
- **Encryption**: `services/shared/security/encryption/`
- **Access Control**: `services/shared/security/access_control/`

## Service Dependencies and Communication

### Inter-Service Communication Patterns:

1. **HTTP REST APIs**: Primary communication method
2. **Event-Driven Architecture**: Async messaging via message queues
3. **Service Discovery**: Dynamic service registration and discovery
4. **Load Balancing**: Round-robin and weighted routing
5. **Circuit Breakers**: Fault tolerance and resilience

### Port Allocation:
- **API Gateway**: 8000
- **Constitutional AI**: 8001
- **Integrity Service**: 8002
- **Policy Governance**: 8003
- **Evolutionary Computation**: 8004
- **Formal Verification**: 8005
- **Authentication**: 8006
- **MCP Aggregator**: 8010
- **MCP Browser**: 8011
- **MCP Filesystem**: 8012
- **MCP GitHub**: 8013

## Docker Compose Integration

### Service Orchestration:
- **Base Infrastructure**: `infrastructure/docker/docker-compose.base.yml`
- **Core Services**: `infrastructure/docker/docker-compose.core.yml`
- **Platform Services**: `infrastructure/docker/docker-compose.services.yml`
- **MCP Services**: `infrastructure/docker/docker-compose.mcp.yml`
- **Production**: `infrastructure/docker/docker-compose.production.yml`

### Environment Configuration:
- **Development**: `.env.development`
- **Production**: `.env.production`
- **Testing**: `.env.testing`

## Performance and Monitoring

### Performance Targets:
- **P99 Latency**: <5ms (cached <2ms)
- **Throughput**: >1000 RPS
- **Cache Hit Rate**: >85%
- **Availability**: 99.99%

### Monitoring Stack:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **ELK Stack**: Logging and analysis
- **Jaeger**: Distributed tracing
- **Health Checks**: Service health monitoring

## Security and Compliance

### Constitutional Compliance:
- **Hash Verification**: `cdd01ef066bc6cf2`
- **Audit Logging**: All operations logged
- **Access Control**: Role-based permissions
- **Encryption**: End-to-end encryption

### Security Measures:
- **JWT Authentication**: Stateless token-based auth
- **Rate Limiting**: DDoS protection
- **Input Validation**: XSS and injection prevention
- **HTTPS**: TLS 1.3 encryption
- **GDPR Compliance**: Data protection and privacy

## Deployment Architecture

### Container Orchestration:
- **Docker Compose**: Local development and testing
- **Kubernetes**: Production orchestration (planned)
- **Service Mesh**: Istio integration (planned)

### CI/CD Pipeline:
- **GitHub Actions**: Automated testing and deployment
- **Docker Registry**: Container image management
- **Environment Promotion**: Dev → Staging → Production

## Future Enhancements

### Planned Improvements:
1. **Kubernetes Migration**: Container orchestration
2. **Service Mesh**: Istio integration
3. **GraphQL Gateway**: Unified API layer
4. **Event Sourcing**: Audit trail improvements
5. **Machine Learning**: Predictive governance

---

**HASH-OK:cdd01ef066bc6cf2**

This structural decomposition provides a comprehensive overview of the ACGS-2 architecture, enabling effective governance, monitoring, and scaling of the constitutional AI system.
