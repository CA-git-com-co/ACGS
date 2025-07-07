# ACGS Security Implementation Guide
Constitutional Hash: cdd01ef066bc6cf2

## Overview

This document describes the security hardening implemented across all ACGS services.

## Security Features

### 1. Input Validation
- **XSS Protection**: All string inputs are validated and sanitized
- **SQL Injection Prevention**: Comprehensive pattern detection
- **Command Injection Prevention**: System command pattern blocking
- **Path Traversal Protection**: File path validation
- **LDAP Injection Prevention**: LDAP query sanitization

### 2. Rate Limiting
- **Request Rate Limiting**: Configurable per-minute limits
- **Burst Protection**: Additional burst capacity
- **IP-based Tracking**: Per-client tracking and enforcement

### 3. CSRF Protection
- **Token-based Protection**: Secure token generation and validation
- **Session Integration**: Token tied to user sessions
- **Automatic Cleanup**: Expired token removal

### 4. Security Headers
- **Content Security Policy**: Strict CSP enforcement
- **XSS Protection Headers**: Browser XSS filtering
- **Frame Options**: Clickjacking prevention
- **Content Type Options**: MIME type sniffing prevention

### 5. File Upload Security
- **File Type Validation**: Whitelist-based file type checking
- **Magic Number Validation**: Content verification
- **Size Limits**: Configurable file size limits
- **Filename Sanitization**: Secure filename handling

## Usage

### Automatic Integration

Security middleware is automatically applied to all services through the standardized integration:

```python
from middleware_integration import apply_acgs_security_middleware

# Automatically applied during service startup
environment = os.getenv("ENVIRONMENT", "development")
apply_acgs_security_middleware(app, "service-name", environment)
```

### Manual Validation

For endpoint-specific validation:

```python
from middleware_integration import validate_request_body, SecurityLevel

# Validate request body
sanitized_data = validate_request_body(request_data, SecurityLevel.HIGH)
```

### Security Monitoring

Monitor security metrics:

```bash
curl http://service:port/security/metrics
curl http://service:port/security/health
```

## Configuration

### Environment Variables

```bash
# Rate limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=200

# CSRF protection
CSRF_SECRET_KEY=your-secure-csrf-key

# Security level
SECURITY_LEVEL=production  # or development
```

### Development vs Production

- **Development**: More permissive settings for easier testing
- **Production**: Strict security enforcement

## Security Levels

1. **LOW**: Basic sanitization
2. **MEDIUM**: Standard security validation (default)
3. **HIGH**: Strict validation with aggressive sanitization
4. **CRITICAL**: Maximum security with blocking

## Troubleshooting

### Common Issues

1. **Rate Limit Exceeded**: Adjust `RATE_LIMIT_PER_MINUTE` environment variable
2. **CSRF Token Validation Failed**: Ensure `CSRF_SECRET_KEY` is properly set
3. **Input Validation Failed**: Check security level configuration

### Debugging

Enable debug logging for security events:

```python
import logging
logging.getLogger("acgs.security").setLevel(logging.DEBUG)
```

## Constitutional Compliance

All security features maintain constitutional compliance with hash validation: `cdd01ef066bc6cf2`

## Support

For security-related issues, refer to the security team or create an issue in the project repository.
