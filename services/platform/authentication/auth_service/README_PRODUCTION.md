# ACGS-PGP Authentication Service - Production Documentation

## Overview

The Authentication Service is a critical component of the ACGS-PGP (Autonomous Constitutional Governance System - Policy Generation Platform) that provides secure JWT-based authentication and authorization for all system components.

**Service Details:**
- **Port**: 8000
- **Version**: 3.0.0
- **Constitutional Hash**: `cdd01ef066bc6cf2`
- **Resource Limits**: CPU 200m-500m, Memory 512Mi-1Gi
- **Health Check**: `/health`

## Architecture

### Core Components
- **JWT Token Management**: Secure token generation and validation
- **User Authentication**: Login/logout functionality
- **Authorization**: Role-based access control (RBAC)
- **Constitutional Compliance**: Integration with ACGS constitutional framework
- **Security Middleware**: Rate limiting, CSRF protection, audit logging

### Dependencies
- **Database**: PostgreSQL (user management, sessions)
- **Cache**: Redis (token caching, rate limiting)
- **Constitutional AI Service**: Port 8001 (compliance validation)

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/login
Authenticate user and generate JWT token.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_string",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_token": "refresh_token_string"
}
```

#### POST /api/v1/auth/refresh
Refresh expired JWT token.

**Request:**
```json
{
  "refresh_token": "refresh_token_string"
}
```

#### POST /api/v1/auth/logout
Invalidate current session.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

### Validation Endpoints

#### GET /api/v1/auth/validate
Validate JWT token and return user information.

**Headers:**
```
Authorization: Bearer <jwt_token>
X-Constitutional-Hash: cdd01ef066bc6cf2
```

**Response:**
```json
{
  "valid": true,
  "user_id": "string",
  "username": "string",
  "roles": ["string"],
  "constitutional_compliance": true
}
```

#### GET /api/v1/auth/info
Service information and constitutional hash.

**Response:**
```json
{
  "service": "auth_service",
  "version": "3.0.0",
  "status": "operational",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "endpoints": ["/health", "/metrics", "/api/v1/auth/validate"]
}
```

### Health & Monitoring

#### GET /health
Service health check.

**Response:**
```json
{
  "status": "healthy",
  "service": "auth_service",
  "version": "3.0.0",
  "timestamp": 1750820294.86,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

#### GET /metrics
Prometheus metrics endpoint.

## Configuration

### Environment Variables

```bash
# Service Configuration
SERVICE_NAME=auth_service
SERVICE_VERSION=3.0.0
SERVICE_PORT=8000
HOST=127.0.0.1  # Secure default, use 0.0.0.0 for production with firewall

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_auth
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security Configuration
CSRF_SECRET_KEY=your-csrf-secret-key
BCRYPT_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
AC_SERVICE_URL=http://localhost:8001
```

### Resource Limits (Kubernetes)

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t acgs-auth-service:latest .

# Run container
docker run -d \
  --name acgs-auth-service \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379/0 \
  -e CONSTITUTIONAL_HASH=cdd01ef066bc6cf2 \
  acgs-auth-service:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  labels:
    app: auth-service
    constitutional-hash: cdd01ef066bc6cf2
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: acgs-auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: CONSTITUTIONAL_HASH
          value: "cdd01ef066bc6cf2"
        resources:
          requests:
            memory: "512Mi"
            cpu: "200m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

## Security

### Authentication Security
- **JWT Tokens**: HS256 algorithm with 30-minute expiration
- **Password Hashing**: bcrypt with 12 rounds
- **Rate Limiting**: 120 requests per minute per IP
- **Account Lockout**: 5 failed attempts, 15-minute lockout

### Constitutional Compliance
- All requests validated against constitutional hash `cdd01ef066bc6cf2`
- Integration with Constitutional AI Service for compliance verification
- Audit logging for all authentication events

### Security Headers
- CSRF protection enabled
- HTTPS-only cookies in production
- Secure session management

## Monitoring

### Health Checks
- **Endpoint**: `/health`
- **Frequency**: Every 30 seconds
- **Timeout**: 5 seconds

### Metrics
- **Authentication Rate**: Successful/failed login attempts
- **Token Validation Rate**: JWT validation requests
- **Response Time**: P95 response time tracking
- **Constitutional Compliance**: Compliance rate monitoring

### Alerts
- **Critical**: Service down, constitutional compliance failure
- **High**: High response time (>2s), authentication failures spike
- **Moderate**: High resource usage, rate limit exceeded

## Troubleshooting

### Common Issues

1. **Service Not Starting**
   ```bash
   # Check logs
   docker logs acgs-auth-service
   
   # Verify environment variables
   env | grep -E "(DATABASE_URL|REDIS_URL|CONSTITUTIONAL_HASH)"
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connectivity
   psql $DATABASE_URL -c "SELECT 1;"
   ```

3. **JWT Token Issues**
   ```bash
   # Verify secret key configuration
   echo $SECRET_KEY | wc -c  # Should be >32 characters
   ```

### Emergency Procedures

1. **Service Recovery**
   ```bash
   # Restart service
   kubectl rollout restart deployment/auth-service
   
   # Check status
   kubectl get pods -l app=auth-service
   ```

2. **Constitutional Compliance Failure**
   ```bash
   # Verify constitutional hash
   curl -s http://localhost:8000/api/v1/auth/info | jq '.constitutional_hash'
   
   # Should return: "cdd01ef066bc6cf2"
   ```

## Performance Targets

- **Response Time**: ≤2 seconds (P95)
- **Availability**: >99.9%
- **Constitutional Compliance**: >95%
- **Throughput**: 1000 requests/second

## Contact & Support

- **Team**: ACGS Platform Team
- **Documentation**: https://docs.acgs.ai/auth-service
- **Runbooks**: https://docs.acgs.ai/runbooks/auth-service
- **Monitoring**: Grafana Dashboard "ACGS Auth Service"
