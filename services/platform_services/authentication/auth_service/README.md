# ACGS-1 Authentication Service
**Constitutional Hash: cdd01ef066bc6cf2**


**Status**: ✅ **Production Ready**  
**Last Updated**: 2025-06-27

## Overview

The Authentication Service is a production-grade microservice that provides comprehensive user authentication, authorization, and access control for the ACGS-PGP system. It implements enterprise-level security features including JWT tokens, multi-factor authentication (MFA), and role-based access control (RBAC).

**Service Port**: 8000
**Service Version**: 3.0.0
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Health Check**: http://localhost:8000/health

## Core Features

### Authentication & Authorization

- **User Management**: Registration, login, and profile management
- **JWT Tokens**: Access and refresh token lifecycle management
- **Multi-Factor Authentication**: TOTP and SMS-based MFA support
- **Role-Based Access Control**: Granular permission system
- **Session Management**: Secure session handling with CSRF protection

### Security Features

- **Password Security**: Bcrypt hashing with salt
- **Rate Limiting**: Brute force protection
- **Security Headers**: CORS, CSP, and security middleware
- **Audit Logging**: Comprehensive authentication event logging
- **Constitutional Compliance**: Integration with AC service for governance validation

## API Endpoints

### Authentication

- `POST /register` - Create new user account with validation
- `POST /token` - Authenticate and obtain JWT tokens
- `POST /login` - Alternative login endpoint
- `POST /token/refresh` - Refresh expired access tokens
- `POST /logout` - Revoke current session and tokens
- `GET /me` - Retrieve authenticated user profile

### User Management

- `GET /users` - List users (admin only)
- `PUT /users/{user_id}` - Update user profile
- `DELETE /users/{user_id}` - Deactivate user account
- `POST /users/{user_id}/reset-password` - Password reset flow

### Multi-Factor Authentication

- `POST /mfa/setup` - Initialize MFA for user
- `POST /mfa/verify` - Verify MFA token
- `DELETE /mfa/disable` - Disable MFA (requires verification)

## Configuration

### Environment Variables

Create `config/environments/development.env` file with the following configuration:

```bash
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

# Service Configuration
SERVICE_NAME=auth-service
SERVICE_VERSION=3.0.0
SERVICE_PORT=8000
LOG_LEVEL=INFO

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
AC_SERVICE_URL=http://localhost:8002
```

### Resource Limits

```yaml
resources:
  requests:
    cpu: 200m
    memory: 512Mi
  limits:
    cpu: 500m
    memory: 1Gi
```

## Installation & Deployment

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis 6+

### Local Development

```bash
# 1. Install dependencies (UV recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv sync

# Alternative: Traditional pip
pip install -r requirements.txt

# 2. Setup database
createdb acgs_auth
alembic upgrade head

# 3. Configure environment
cp config/environments/developmentconfig/environments/example.env config/environments/development.env
# Edit config/environments/development.env with your configuration

# 4. Start service
uv run uvicorn main:app --reload --port 8000
```

### Production Deployment

```bash
# Using Docker
docker build -t acgs-auth-service .
docker run -p 8000:8000 --env-file config/environments/development.env acgs-auth-service

# Using systemd
sudo cp auth-service.service /etc/systemd/system/
sudo systemctl enable auth-service
sudo systemctl start auth-service
```

## Testing

### Unit Tests

```bash
# Run all tests
uv run pytest app/tests/ -v

# Run with coverage
uv run pytest app/tests/ --cov=app --cov-report=html
```

### Integration Tests

```bash
# Test authentication flow
uv run pytest app/tests/test_auth_integration.py -v

# Test MFA functionality
uv run pytest app/tests/test_mfa_integration.py -v
```

### Load Testing

```bash
# Test authentication endpoints
python scripts/test_authentication_workflow.py --concurrent 10
```

## Usage Examples

### Basic Authentication Flow

```python
import httpx

async def authenticate_user():
    async with httpx.AsyncClient() as client:
        # Register new user
        register_response = await client.post(
            "http://localhost:8000/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "SecurePassword123!",
                "full_name": "Test User"
            }
        )

        # Login and get tokens
        login_response = await client.post(
            "http://localhost:8000/token",
            data={
                "username": "testuser",
                "password": "SecurePassword123!"
            }
        )

        tokens = login_response.json()
        access_token = tokens["access_token"]

        # Use token for authenticated requests
        profile_response = await client.get(
            "http://localhost:8000/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        return profile_response.json()
```

### Multi-Factor Authentication

```python
async def setup_mfa():
    async with httpx.AsyncClient() as client:
        # Setup MFA
        mfa_setup = await client.post(
            "http://localhost:8000/mfa/setup",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        qr_code_url = mfa_setup.json()["qr_code_url"]
        secret = mfa_setup.json()["secret"]

        # Verify MFA token
        mfa_verify = await client.post(
            "http://localhost:8000/mfa/verify",
            json={"token": "123456"},  # From authenticator app
            headers={"Authorization": f"Bearer {access_token}"}
        )

        return mfa_verify.json()
```

## Monitoring & Observability

### Health Checks

```bash
# Service health
curl http://localhost:8000/health

# Detailed health with dependencies
curl http://localhost:8000/health?detailed=true
```

### Metrics

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Authentication metrics
curl http://localhost:8000/api/v1/metrics/auth
```

### Logging

```bash
# View service logs
tail -f /logs/auth_service.log

# Filter authentication events
grep "AUTH_EVENT" /logs/auth_service.log
```

## Security Considerations

### Password Policy

- Minimum 8 characters
- Must contain uppercase, lowercase, number, and special character
- Password history: Last 5 passwords cannot be reused
- Password expiration: 90 days (configurable)

### Rate Limiting

- Login attempts: 5 per 15 minutes per IP
- Registration: 3 per hour per IP
- Password reset: 3 per hour per email

### Session Security

- JWT tokens signed with HS256
- Refresh tokens stored securely with rotation
- CSRF protection for state-changing operations
- Secure cookie settings (HttpOnly, Secure, SameSite)

## Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check PostgreSQL connectivity
pg_isready -h localhost -p 5432

# Verify database exists
psql -h localhost -U postgres -l | grep acgs_auth
```

#### JWT Token Issues

```bash
# Verify JWT configuration
python -c "
import jwt
from app.core.config import settings
print('Secret key configured:', bool(settings.SECRET_KEY))
print('Algorithm:', settings.ALGORITHM)
"
```

#### MFA Setup Problems

```bash
# Check TOTP library installation
python -c "import pyotp; print('TOTP library available')"

# Verify time synchronization
ntpdate -s time.nist.gov
```

### Performance Optimization

#### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_auth_events_timestamp ON auth_events(timestamp);
```

#### Redis Caching

```bash
# Monitor Redis performance
redis-cli info stats

# Check session storage
redis-cli keys "session:*" | wc -l
```

## Contributing

1. Follow ACGS-1 coding standards
2. Ensure >90% test coverage for new features
3. Update API documentation for endpoint changes
4. Test authentication flows thoroughly
5. Validate constitutional compliance integration

## Support

- **Documentation**: [Auth Service API](../../../../pids/auth_service.pid)
- **Health Check**: http://localhost:8000/health
- **Interactive API Docs**: http://localhost:8000/docs
- **Logs**: `/logs/auth_service.log`
- **Configuration**: `services/platform/authentication/auth_service/config/environments/development.env`


## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.
