# Authentication Consolidation into API Gateway
**Constitutional Hash: cdd01ef066bc6cf2**


**Constitutional Hash**: `cdd01ef066bc6cf2`

## Overview

This document outlines the consolidation of authentication functionality into the API Gateway, reducing service sprawl while maintaining full authentication capabilities.

## Architecture Changes

### Before: Separate Services
```
┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │  Auth Service   │
│   (Port 8080)   │    │   (Port 8016)   │
│                 │    │                 │
│ - Routing       │    │ - JWT Tokens    │
│ - Rate Limiting │    │ - User Auth     │
│ - CORS          │    │ - Role/Permissions │
└─────────────────┘    └─────────────────┘
```

### After: Integrated Authentication
```
┌─────────────────────────────────────┐    ┌─────────────────┐
│        Enhanced API Gateway         │    │  Auth Service   │
│           (Port 8080)               │    │   (Port 8016)   │
│                                     │    │   [Optional]    │
│ - Routing                           │    │                 │
│ - Rate Limiting                     │    │ - Advanced Auth │
│ - CORS                              │    │ - Enterprise    │
│ - JWT Tokens (Integrated)           │    │ - Multi-tenant  │
│ - User Authentication               │    │                 │
│ - Role/Permission Management        │    │                 │
│ - Constitutional Compliance         │    │                 │
└─────────────────────────────────────┘    └─────────────────┘
```

## Features Implemented

### ✅ Core Authentication
- JWT token generation and validation
- User login/logout with credentials
- Password hashing with bcrypt
- Token blacklisting for secure logout
- Rate limiting for authentication attempts

### ✅ Authorization
- Role-based access control (RBAC)
- Permission-based access control
- Multi-tenant context support
- Constitutional compliance validation

### ✅ Security Features
- Rate limiting (5 attempts per 5 minutes)
- Token expiration handling
- Secure password hashing
- Constitutional hash validation
- Request authentication middleware

### ✅ API Endpoints

#### Authentication Endpoints
```bash
POST /auth/login          # User authentication
POST /auth/logout         # User logout
GET  /auth/me            # Get current user info
POST /auth/validate      # Validate token
GET  /auth/health        # Auth module health
```

#### Admin Endpoints
```bash
POST /auth/admin/users   # Create user (admin only)
```

#### Gateway Endpoints
```bash
GET  /gateway/health     # Gateway health
GET  /gateway/config     # Gateway configuration
GET  /gateway/metrics    # Gateway metrics
```

## User Accounts (Default Setup)

The integrated authentication includes these default accounts:

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Roles**: `["admin", "user"]`
- **Permissions**: `["read", "write", "admin", "constitutional_access"]`

### Standard User
- **Username**: `user`
- **Password**: `user123`
- **Roles**: `["user"]`
- **Permissions**: `["read"]`

### Constitutional Expert
- **Username**: `constitutional_expert`
- **Password**: `const123`
- **Roles**: `["constitutional_expert", "user"]`
- **Permissions**: `["read", "write", "constitutional_review", "policy_synthesis"]`

## API Usage Examples

### 1. User Login
```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_id": "admin_001",
  "username": "admin",
  "tenant_id": "system",
  "roles": ["admin", "user"],
  "permissions": ["read", "write", "admin", "constitutional_access"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2. Access Protected Resource
```bash
curl -X GET http://localhost:8080/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Validate Token
```bash
curl -X POST http://localhost:8080/auth/validate \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Create New User (Admin Only)
```bash
curl -X POST http://localhost:8080/auth/admin/users \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepass",
    "roles": ["user"],
    "permissions": ["read"]
  }'
```

## Service Routing

The enhanced API Gateway now handles authentication AND routing:

### Authentication Routes
- `/auth/*` → Handled directly by integrated auth module

### Service Routes
- `/api/constitutional-ai/*` → `http://ac_service:8002`
- `/api/governance-engine/*` → `http://governance_engine:8004`
- `/api/integrity/*` → `http://integrity_service:8002`
- `/api/formal-verification/*` → `http://fv_service:8004`

## Configuration

### Environment Variables

#### Gateway Configuration
```bash
SERVICE_NAME=api_gateway
SERVICE_PORT=8080
JWT_SECRET_KEY=acgs-gateway-secret-key-2024
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
RATE_LIMIT_BURST=100
ENABLE_DOCS=true
```

#### Service URLs
```bash
CONSTITUTIONAL_AI_URL=http://ac_service:8002
GOVERNANCE_ENGINE_URL=http://governance_engine:8004
INTEGRITY_SERVICE_URL=http://integrity_service:8002
FORMAL_VERIFICATION_URL=http://fv_service:8004
```

### Docker Profiles

The auth service is now optional and can be enabled with profiles:

```bash
# Run without separate auth service (default)
docker-compose up

# Run with separate auth service for enterprise features
docker-compose --profile backend-auth up

# Run full stack including all optional services
docker-compose --profile full up
```

## Performance Benefits

### Resource Optimization
- **Memory**: Reduced from 1Gi + 1Gi to 1.5Gi total
- **CPU**: Optimized from 500m + 500m to 750m total
- **Network**: Eliminated internal auth service calls
- **Latency**: Direct auth processing (no network overhead)

#
## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets
- **Authentication**: < 50ms P99
- **Token Validation**: < 5ms P99
- **Rate Limiting**: < 1ms P99
- **Gateway Routing**: < 10ms P99

## Security Considerations

### Constitutional Compliance
- All auth operations validate constitutional hash `cdd01ef066bc6cf2`
- Constitutional compliance is enforced at the gateway level
- Audit trails maintained for all authentication events

### Security Features
- JWT tokens with expiration
- Token blacklisting for secure logout
- Password hashing with bcrypt + salt
- Rate limiting to prevent brute force attacks
- CORS and trusted host protection

### Multi-Tenant Support
- Tenant context in JWT tokens
- Tenant isolation at gateway level
- Per-tenant rate limiting capabilities

## Migration Steps

### 1. Update Service References
Replace authentication service calls with gateway auth:

**Before:**
```python
auth_client = await get_service_client("authentication")
result = await auth_client.authenticate(credentials)
```

**After:**
```python
# Direct gateway auth API
response = await httpx.post("http://api_gateway:8080/auth/login", json=credentials)
```

### 2. Update Environment Variables
```bash
# Remove
AUTH_SERVICE_URL=http://auth_service:8016

# Add
API_GATEWAY_URL=http://api_gateway:8080
```

### 3. Update Client Code
Use gateway auth endpoints instead of separate auth service:
- Replace `/auth/*` calls to point to gateway
- Update token validation to use `/auth/validate`
- Use `/auth/me` for user information

## Rollback Plan

If needed, the separate auth service can be re-enabled:

1. Enable the auth service profile:
   ```bash
   docker-compose --profile backend-auth up
   ```

2. Update service configurations to use `http://auth_service:8016`

3. Disable integrated auth in gateway configuration

## Testing

### Unit Tests
```bash
cd services/platform_services/api_gateway/gateway_service
python3 -m pytest tests/test_integrated_auth.py -v
```

### Integration Tests
```bash
# Test login flow
curl -X POST http://localhost:8080/auth/login -d '{"username":"admin","password":"admin123"}'

# Test protected endpoint
TOKEN=$(curl -s -X POST http://localhost:8080/auth/login -d '{"username":"admin","password":"admin123"}' | jq -r .access_token)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/auth/me

# Test service routing through gateway
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/governance-engine/health
```

## Monitoring

### Metrics
- Authentication success/failure rates
- Token validation performance
- Rate limiting effectiveness
- Gateway routing performance

### Health Checks
- `/gateway/health` - Overall gateway health
- `/auth/health` - Authentication module health
- Individual service health through gateway routing

## Constitutional Compliance

All changes maintain constitutional compliance with hash `cdd01ef066bc6cf2`:

- ✅ Authentication consolidation preserves all constitutional validation
- ✅ JWT tokens include constitutional hash verification
- ✅ Audit trails continue for all authentication events
- ✅ Performance targets meet constitutional requirements
- ✅ Multi-tenant isolation maintains constitutional principles

## Benefits Summary

1. **Reduced Service Sprawl**: 2 services → 1 primary service + 1 optional
2. **Improved Performance**: Eliminated network calls for auth
3. **Simplified Architecture**: Single entry point for all requests
4. **Better Security**: Unified security policy enforcement
5. **Easier Deployment**: Fewer services to manage and monitor
6. **Cost Optimization**: Reduced resource usage

## Performance Requirements

### ACGS-2 Performance Targets
- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)  
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

### Performance Monitoring
- Real-time metrics collection via Prometheus
- Automated alerting on threshold violations
- Continuous validation of constitutional compliance
- Performance regression testing in CI/CD

### Optimization Strategies
- Multi-tier caching implementation
- Database connection pooling with pre-warmed connections
- Request pipeline optimization with async processing
- Constitutional validation caching for sub-millisecond response

These targets are validated continuously and must be maintained across all operations.
