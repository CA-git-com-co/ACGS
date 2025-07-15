<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# CLAUDE.md - API Gateway Service

## Directory Overview

The API Gateway service provides centralized routing, authentication, rate limiting, and security middleware for all ACGS-2 constitutional AI governance services. It serves as the primary entry point for external requests with constitutional compliance validation.

## File Inventory

- **CLAUDE.md**: This documentation file
- **gateway_service/**: Core gateway service implementation
- **gateway_service_standardized/**: Standardized gateway service components
- **AUTHENTICATION_CONSOLIDATION.md**: Authentication integration documentation

## Dependencies & Interactions

- **Authentication Service**: JWT token validation and user authentication
- **Constitutional AI Service**: Constitutional compliance validation
- **All Core Services**: Routing and proxy functionality
- **Rate Limiting**: Redis-based rate limiting and throttling
- **Constitutional Framework**: Compliance with hash `cdd01ef066bc6cf2`

## Key Components

### Gateway Core
- **Request Routing**: Intelligent routing to appropriate backend services
- **Load Balancing**: Distribution of requests across service instances
- **Circuit Breaker**: Fault tolerance and graceful degradation
- **Request/Response Transformation**: Protocol adaptation and data transformation
- **Constitutional Middleware**: Constitutional compliance validation for all requests

### Security Features
- **JWT Authentication**: Token-based authentication and authorization
- **Rate Limiting**: Per-user and per-endpoint rate limiting
- **CORS Handling**: Cross-origin request security
- **Request Validation**: Input validation and sanitization
- **Security Headers**: Automatic security header injection

### Monitoring and Observability
- **Request Logging**: Comprehensive request and response logging
- **Metrics Collection**: Performance and usage metrics
- **Health Checks**: Service health monitoring and reporting
- **Distributed Tracing**: Request tracing across services
- **Constitutional Audit**: Audit trail for constitutional compliance

## Constitutional Compliance Status

✅ **IMPLEMENTED**: Constitutional hash validation (`cdd01ef066bc6cf2`)
✅ **IMPLEMENTED**: JWT authentication integration
✅ **IMPLEMENTED**: Rate limiting and security middleware
✅ **IMPLEMENTED**: Request routing and load balancing
🔄 **IN PROGRESS**: Advanced circuit breaker patterns
🔄 **IN PROGRESS**: Enhanced security features
❌ **PLANNED**: AI-driven routing optimization
❌ **PLANNED**: Advanced threat detection

## Performance Considerations

- **Gateway Latency**: <1ms overhead for request routing
- **Constitutional Validation**: <1ms additional latency
- **Throughput**: >10,000 RPS with horizontal scaling
- **Memory Usage**: Efficient connection pooling and caching
- **Scalability**: Auto-scaling based on traffic patterns

## Implementation Status

### ✅ IMPLEMENTED
- Core API gateway functionality with routing
- JWT authentication and authorization
- Rate limiting and security middleware
- Basic monitoring and health checks
- Constitutional compliance validation

### 🔄 IN PROGRESS
- Advanced circuit breaker and fault tolerance
- Enhanced security features and threat detection
- Performance optimization and caching
- Advanced monitoring and analytics
- Multi-tenant routing and isolation

### ❌ PLANNED
- AI-driven routing optimization
- Advanced threat detection and prevention
- Intelligent load balancing algorithms
- Real-time security policy enforcement
- Advanced API analytics and insights

## API Endpoints

### Gateway Management
- **GET /health**: Gateway health check
- **GET /metrics**: Prometheus metrics endpoint
- **GET /routes**: List configured routes and their status
- **POST /routes/reload**: Reload routing configuration
- **GET /circuit-breaker/status**: Circuit breaker status

### Authentication
- **POST /auth/login**: User authentication
- **POST /auth/refresh**: Token refresh
- **POST /auth/logout**: User logout
- **GET /auth/validate**: Token validation

### Monitoring
- **GET /stats**: Gateway performance statistics
- **GET /logs**: Recent gateway logs
- **GET /trace/{id}**: Distributed trace information

## Configuration

```yaml
# API Gateway Configuration
gateway:
  port: 8010
  constitutional_hash: cdd01ef066bc6cf2
  request_timeout: 30s
  max_concurrent_requests: 10000

routing:
  constitutional_ai: http://localhost:8001
  integrity: http://localhost:8002
  multi_agent_coordinator: http://localhost:8008
  worker_agents: http://localhost:8009
  blackboard: http://localhost:8010

security:
  jwt_secret: ${JWT_SECRET}
  cors_origins: ["http://localhost:3000"]
  rate_limit_requests_per_minute: 1000
  enable_request_validation: true

monitoring:
  enable_metrics: true
  enable_tracing: true
  log_level: INFO
  metrics_interval: 30s
```

## Usage Examples

```bash
# Route request through gateway
curl -X POST http://localhost:8010/api/v1/constitutional-ai/validate \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"constitutional_hash": "cdd01ef066bc6cf2", "request": "governance_query"}'

# Check gateway health
curl http://localhost:8010/health

# Get gateway metrics
curl http://localhost:8010/metrics
```

## Security Features

### Authentication and Authorization
- **JWT Token Validation**: Automatic token validation for protected routes
- **Role-Based Access Control**: Fine-grained permissions based on user roles
- **Service-to-Service Authentication**: Secure inter-service communication
- **Constitutional Context**: Authentication context includes constitutional compliance

### Rate Limiting and Throttling
- **Per-User Limits**: Individual user rate limiting
- **Per-Endpoint Limits**: Endpoint-specific rate limiting
- **Burst Handling**: Configurable burst capacity
- **Constitutional Priority**: Priority handling for constitutional compliance requests

## Cross-References & Navigation

**Navigation**:
- [Platform Services](../CLAUDE.md)
- [Authentication Service](../authentication/CLAUDE.md)
- [Integrity Service](../integrity/CLAUDE.md)
- [Blackboard Service](../blackboard/CLAUDE.md)

**Related Components**:
- [Constitutional AI Service](../../core/constitutional-ai/CLAUDE.md)
- [Multi-Agent Coordinator](../../core/multi_agent_coordinator/CLAUDE.md)
- [Infrastructure Services](../../../infrastructure/CLAUDE.md)

**External References**:
- [API Gateway Pattern](https://microservices.io/patterns/apigateway.html)
- [JWT Authentication](https://jwt.io/introduction/)

---

**Constitutional Compliance**: All gateway operations maintain constitutional hash `cdd01ef066bc6cf2` validation
