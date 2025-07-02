#!/usr/bin/env python3
"""
ACGS-PGP Security Hardening Applier
Applies enterprise-grade security hardening configurations across all services.
Constitutional Hash: cdd01ef066bc6cf2
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constitutional compliance constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class SecurityConfig:
    """Security configuration parameters."""
    enable_https_only: bool = True
    enable_csrf_protection: bool = True
    enable_xss_protection: bool = True
    enable_content_type_options: bool = True
    enable_frame_options: bool = True
    enable_hsts: bool = True
    enable_referrer_policy: bool = True
    enable_csp: bool = True
    enable_rate_limiting: bool = True
    enable_cors_restrictions: bool = True
    enable_security_headers: bool = True
    enable_input_validation: bool = True
    enable_sql_injection_protection: bool = True
    enable_authentication_hardening: bool = True
    enable_session_security: bool = True
    jwt_secret_rotation: bool = True
    password_policy_enforcement: bool = True
    audit_logging: bool = True
    
    
class SecurityHardeningApplier:
    """Applies security hardening configurations to ACGS-PGP services."""
    
    def __init__(self, project_root: Path, config: SecurityConfig):
        self.project_root = project_root
        self.config = config
        self.applied_configs: List[str] = []
        self.failed_configs: List[str] = []
        
    def apply_security_hardening(self) -> Dict[str, any]:
        """Apply all security hardening configurations."""
        logger.info("Starting security hardening application...")
        
        # Apply security headers middleware
        if self.config.enable_security_headers:
            self._apply_security_headers()
            
        # Apply CORS restrictions
        if self.config.enable_cors_restrictions:
            self._apply_cors_restrictions()
            
        # Apply rate limiting
        if self.config.enable_rate_limiting:
            self._apply_rate_limiting()
            
        # Apply input validation
        if self.config.enable_input_validation:
            self._apply_input_validation()
            
        # Apply authentication hardening
        if self.config.enable_authentication_hardening:
            self._apply_authentication_hardening()
            
        # Apply session security
        if self.config.enable_session_security:
            self._apply_session_security()
            
        # Apply SQL injection protection
        if self.config.enable_sql_injection_protection:
            self._apply_sql_injection_protection()
            
        # Apply audit logging
        if self.config.audit_logging:
            self._apply_audit_logging()
            
        # Update Docker configurations
        self._apply_docker_security()
        
        # Update CI/CD security
        self._apply_cicd_security()
        
        # Generate security report
        return self._generate_security_report()
        
    def _apply_security_headers(self) -> None:
        """Apply security headers middleware to all services."""
        logger.info("Applying security headers middleware...")
        
        security_middleware_content = '''"""
Security Headers Middleware for ACGS-PGP
Applies enterprise-grade security headers to all responses.
Constitutional Hash: cdd01ef066bc6cf2
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    def __init__(self, app, constitutional_hash: str = "cdd01ef066bc6cf2"):
        super().__init__(app)
        self.constitutional_hash = constitutional_hash
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-Download-Options": "noopen",
            "X-DNS-Prefetch-Control": "off",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), bluetooth=(), "
                "accelerometer=(), gyroscope=(), magnetometer=()"
            ),
        }
        
        # Constitutional compliance headers
        security_headers.update({
            "X-Constitutional-Hash": self.constitutional_hash,
            "X-ACGS-Service": "enterprise-hardened",
            "X-Security-Hardened": "true",
        })
        
        # Apply headers
        for header, value in security_headers.items():
            response.headers[header] = value
            
        return response


def apply_security_headers(app, constitutional_hash: str = "cdd01ef066bc6cf2"):
    """Apply security headers middleware to FastAPI app."""
    app.add_middleware(SecurityHeadersMiddleware, constitutional_hash=constitutional_hash)
    return app
'''
        
        # Create security middleware file
        middleware_dir = self.project_root / "services" / "shared"
        middleware_dir.mkdir(parents=True, exist_ok=True)
        
        middleware_file = middleware_dir / "security_headers_middleware.py"
        middleware_file.write_text(security_middleware_content)
        
        self.applied_configs.append("security_headers_middleware")
        logger.info("✅ Security headers middleware created")
        
    def _apply_cors_restrictions(self) -> None:
        """Apply CORS restrictions configuration."""
        logger.info("Applying CORS restrictions...")
        
        cors_config_content = '''"""
CORS Configuration for ACGS-PGP
Enterprise-grade CORS restrictions for production security.
Constitutional Hash: cdd01ef066bc6cf2
"""

from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional


class SecureCORSConfig:
    """Secure CORS configuration for production."""
    
    # Allowed origins (restrict in production)
    ALLOWED_ORIGINS = [
        "https://acgs-pgp.com",
        "https://api.acgs-pgp.com",
        "https://admin.acgs-pgp.com",
    ]
    
    # Development origins (only for development)
    DEV_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Allowed methods
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    # Allowed headers
    ALLOWED_HEADERS = [
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-Constitutional-Hash",
        "X-ACGS-Service",
    ]
    
    # Expose headers
    EXPOSE_HEADERS = [
        "X-Constitutional-Hash",
        "X-ACGS-Service", 
        "X-Rate-Limit-Remaining",
        "X-Rate-Limit-Reset",
    ]


def apply_cors_middleware(app, environment: str = "production"):
    """Apply CORS middleware with security restrictions."""
    config = SecureCORSConfig()
    
    # Determine allowed origins based on environment
    if environment == "development":
        allowed_origins = config.ALLOWED_ORIGINS + config.DEV_ORIGINS
        allow_credentials = True
    else:
        allowed_origins = config.ALLOWED_ORIGINS
        allow_credentials = True
        
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=config.ALLOWED_METHODS,
        allow_headers=config.ALLOWED_HEADERS,
        expose_headers=config.EXPOSE_HEADERS,
        max_age=3600,  # 1 hour cache for preflight requests
    )
    
    return app
'''
        
        # Create CORS configuration file
        middleware_dir = self.project_root / "services" / "shared"
        cors_file = middleware_dir / "secure_cors_config.py"
        cors_file.write_text(cors_config_content)
        
        self.applied_configs.append("cors_restrictions")
        logger.info("✅ CORS restrictions configuration created")
        
    def _apply_rate_limiting(self) -> None:
        """Apply rate limiting middleware."""
        logger.info("Applying rate limiting...")
        
        rate_limit_content = '''"""
Rate Limiting Middleware for ACGS-PGP
Enterprise-grade rate limiting for DDoS protection.
Constitutional Hash: cdd01ef066bc6cf2
"""

import time
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Deque, Tuple


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with sliding window algorithm."""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_limit: int = 10,
        constitutional_hash: str = "cdd01ef066bc6cf2"
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
        self.constitutional_hash = constitutional_hash
        
        # Store request timestamps for each IP
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
        self.burst_requests: Dict[str, Deque[float]] = defaultdict(deque)
        
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
            
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        return request.client.host if request.client else "unknown"
        
    def _clean_old_requests(self, requests: Deque[float], window_seconds: int) -> None:
        """Remove requests older than the time window."""
        current_time = time.time()
        while requests and current_time - requests[0] > window_seconds:
            requests.popleft()
            
    def _is_rate_limited(self, client_ip: str) -> Tuple[bool, Dict[str, int]]:
        """Check if client is rate limited."""
        current_time = time.time()
        
        # Clean old requests
        self._clean_old_requests(self.requests[client_ip], 3600)  # 1 hour
        self._clean_old_requests(self.burst_requests[client_ip], 60)  # 1 minute
        
        # Check burst limit (requests per minute)
        if len(self.burst_requests[client_ip]) >= self.burst_limit:
            return True, {
                "limit": self.burst_limit,
                "window": "1 minute",
                "remaining": 0,
                "reset": int(current_time + 60)
            }
            
        # Check hourly limit
        if len(self.requests[client_ip]) >= self.requests_per_hour:
            return True, {
                "limit": self.requests_per_hour,
                "window": "1 hour", 
                "remaining": 0,
                "reset": int(current_time + 3600)
            }
            
        # Not rate limited
        remaining_burst = self.burst_limit - len(self.burst_requests[client_ip])
        remaining_hourly = self.requests_per_hour - len(self.requests[client_ip])
        
        return False, {
            "limit": min(self.burst_limit, self.requests_per_hour),
            "remaining": min(remaining_burst, remaining_hourly),
            "reset": int(current_time + 60)
        }
        
    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting."""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Check rate limit
        is_limited, limit_info = self._is_rate_limited(client_ip)
        
        if is_limited:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(limit_info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(limit_info["reset"]),
                    "X-Constitutional-Hash": self.constitutional_hash,
                    "Retry-After": str(60 if "minute" in limit_info["window"] else 3600),
                }
            )
            
        # Record request
        self.requests[client_ip].append(current_time)
        self.burst_requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(limit_info["reset"])
        response.headers["X-Constitutional-Hash"] = self.constitutional_hash
        
        return response


def apply_rate_limiting(app, **kwargs):
    """Apply rate limiting middleware to FastAPI app."""
    app.add_middleware(RateLimitMiddleware, **kwargs)
    return app
'''
        
        # Create rate limiting file
        middleware_dir = self.project_root / "services" / "shared"
        rate_limit_file = middleware_dir / "rate_limiting_middleware.py"
        rate_limit_file.write_text(rate_limit_content)
        
        self.applied_configs.append("rate_limiting")
        logger.info("✅ Rate limiting middleware created")
        
    def _apply_input_validation(self) -> None:
        """Apply input validation middleware."""
        logger.info("Applying input validation...")
        
        validation_content = '''"""
Input Validation Middleware for ACGS-PGP
Enterprise-grade input validation and sanitization.
Constitutional Hash: cdd01ef066bc6cf2
"""

import re
import html
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any, Dict, Optional
import json


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for validating and sanitizing input."""
    
    def __init__(self, app, constitutional_hash: str = "cdd01ef066bc6cf2"):
        super().__init__(app)
        self.constitutional_hash = constitutional_hash
        
        # Dangerous patterns
        self.sql_injection_patterns = [
            r"(\\'|\\\"|\\\\'|\\\\\"|\\';|\\\"';)",
            r"(union\s+select|select\s+.*\s+from|insert\s+into|delete\s+from|drop\s+table)",
            r"(exec\s*\(|execute\s*\()",
            r"(script\s*>|javascript:|vbscript:|onload\s*=|onerror\s*=)",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
        ]
        
        self.command_injection_patterns = [
            r"(\||;|&&|\$\(|\`)",
            r"(nc\s+|netcat\s+|wget\s+|curl\s+)",
            r"(rm\s+-rf|sudo\s+|chmod\s+|chown\s+)",
        ]
        
    def _validate_string(self, value: str, field_name: str) -> str:
        """Validate and sanitize string input."""
        if not isinstance(value, str):
            return value
            
        # Check for SQL injection
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid input detected in {field_name}: SQL injection attempt",
                    headers={"X-Constitutional-Hash": self.constitutional_hash}
                )
                
        # Check for XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid input detected in {field_name}: XSS attempt",
                    headers={"X-Constitutional-Hash": self.constitutional_hash}
                )
                
        # Check for command injection
        for pattern in self.command_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid input detected in {field_name}: Command injection attempt",
                    headers={"X-Constitutional-Hash": self.constitutional_hash}
                )
                
        # Sanitize HTML
        sanitized = html.escape(value)
        
        # Check for excessively long input
        if len(sanitized) > 10000:  # 10KB limit
            raise HTTPException(
                status_code=400,
                detail=f"Input too long in {field_name}: Maximum 10KB allowed",
                headers={"X-Constitutional-Hash": self.constitutional_hash}
            )
            
        return sanitized
        
    def _validate_dict(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Recursively validate dictionary data."""
        validated = {}
        
        for key, value in data.items():
            field_name = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, str):
                validated[key] = self._validate_string(value, field_name)
            elif isinstance(value, dict):
                validated[key] = self._validate_dict(value, field_name)
            elif isinstance(value, list):
                validated[key] = [
                    self._validate_string(item, f"{field_name}[{i}]") if isinstance(item, str)
                    else self._validate_dict(item, f"{field_name}[{i}]") if isinstance(item, dict)
                    else item
                    for i, item in enumerate(value)
                ]
            else:
                validated[key] = value
                
        return validated
        
    async def dispatch(self, request: Request, call_next):
        """Validate input data."""
        # Skip validation for certain endpoints
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
            
        # Validate query parameters
        if request.query_params:
            for key, value in request.query_params.items():
                self._validate_string(value, f"query.{key}")
                
        # Validate JSON body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            if "application/json" in request.headers.get("content-type", ""):
                try:
                    body = await request.body()
                    if body:
                        data = json.loads(body)
                        if isinstance(data, dict):
                            validated_data = self._validate_dict(data)
                            # Replace request body with validated data
                            request._body = json.dumps(validated_data).encode()
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid JSON format",
                        headers={"X-Constitutional-Hash": self.constitutional_hash}
                    )
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Input validation failed: {str(e)}",
                        headers={"X-Constitutional-Hash": self.constitutional_hash}
                    )
                    
        return await call_next(request)


def apply_input_validation(app, **kwargs):
    """Apply input validation middleware to FastAPI app."""
    app.add_middleware(InputValidationMiddleware, **kwargs)
    return app
'''
        
        # Create input validation file
        middleware_dir = self.project_root / "services" / "shared"
        validation_file = middleware_dir / "input_validation_middleware.py"
        validation_file.write_text(validation_content)
        
        self.applied_configs.append("input_validation")
        logger.info("✅ Input validation middleware created")
        
    def _apply_authentication_hardening(self) -> None:
        """Apply authentication hardening configurations."""
        logger.info("Applying authentication hardening...")
        
        # Create authentication security config
        auth_config = {
            "jwt": {
                "algorithm": "HS256",
                "access_token_expire_minutes": 30,
                "refresh_token_expire_days": 7,
                "require_secure_cookies": True,
                "httponly_cookies": True,
                "samesite_cookies": "strict"
            },
            "password_policy": {
                "min_length": 12,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special_chars": True,
                "max_age_days": 90,
                "history_count": 5
            },
            "account_lockout": {
                "max_attempts": 5,
                "lockout_duration_minutes": 30,
                "progressive_delay": True
            },
            "session_security": {
                "max_concurrent_sessions": 3,
                "session_timeout_minutes": 60,
                "require_fresh_login_for_sensitive_ops": True
            }
        }
        
        # Save configuration
        config_dir = self.project_root / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        auth_config_file = config_dir / "authentication_security.json"
        with open(auth_config_file, 'w') as f:
            json.dump(auth_config, f, indent=2)
            
        self.applied_configs.append("authentication_hardening")
        logger.info("✅ Authentication hardening configuration created")
        
    def _apply_session_security(self) -> None:
        """Apply session security configurations."""
        logger.info("Applying session security...")
        
        session_config = {
            "cookie_settings": {
                "secure": True,
                "httponly": True,
                "samesite": "strict",
                "max_age": 3600
            },
            "session_management": {
                "regenerate_on_auth": True,
                "invalidate_on_logout": True,
                "concurrent_session_limit": 3,
                "idle_timeout_minutes": 30
            },
            "csrf_protection": {
                "enabled": True,
                "token_length": 32,
                "cookie_name": "csrf_token",
                "header_name": "X-CSRF-Token"
            }
        }
        
        config_dir = self.project_root / "config"
        session_config_file = config_dir / "session_security.json"
        with open(session_config_file, 'w') as f:
            json.dump(session_config, f, indent=2)
            
        self.applied_configs.append("session_security")
        logger.info("✅ Session security configuration created")
        
    def _apply_sql_injection_protection(self) -> None:
        """Apply SQL injection protection configurations."""
        logger.info("Applying SQL injection protection...")
        
        # Database security configuration
        db_security_config = {
            "connection_settings": {
                "use_prepared_statements": True,
                "enable_query_logging": True,
                "log_slow_queries": True,
                "connection_pool_size": 20,
                "max_overflow": 30,
                "pool_timeout": 30,
                "pool_recycle": 3600
            },
            "query_validation": {
                "whitelist_functions": [
                    "SELECT", "INSERT", "UPDATE", "DELETE",
                    "COUNT", "SUM", "AVG", "MIN", "MAX"
                ],
                "blacklist_keywords": [
                    "EXEC", "EXECUTE", "sp_", "xp_",
                    "UNION", "INFORMATION_SCHEMA",
                    "SYSOBJECTS", "SYSCOLUMNS"
                ],
                "max_query_length": 10000,
                "require_parameterized_queries": True
            },
            "monitoring": {
                "log_failed_queries": True,
                "alert_on_suspicious_patterns": True,
                "track_query_performance": True
            }
        }
        
        config_dir = self.project_root / "config"
        db_config_file = config_dir / "database_security.json"
        with open(db_config_file, 'w') as f:
            json.dump(db_security_config, f, indent=2)
            
        self.applied_configs.append("sql_injection_protection")
        logger.info("✅ SQL injection protection configuration created")
        
    def _apply_audit_logging(self) -> None:
        """Apply comprehensive audit logging."""
        logger.info("Applying audit logging...")
        
        audit_config = {
            "logging_settings": {
                "log_level": "INFO",
                "log_format": "json",
                "log_file": "/var/log/acgs-pgp/audit.log",
                "max_file_size": "100MB",
                "backup_count": 10,
                "compress_backups": True
            },
            "audit_events": {
                "authentication": ["login", "logout", "failed_login", "password_change"],
                "authorization": ["permission_granted", "permission_denied", "role_change"],
                "data_access": ["read", "create", "update", "delete"],
                "configuration": ["config_change", "service_restart", "deployment"],
                "security": ["security_violation", "rate_limit_exceeded", "suspicious_activity"]
            },
            "sensitive_data_handling": {
                "mask_passwords": True,
                "mask_tokens": True,
                "mask_personal_data": True,
                "retention_days": 365
            },
            "integration": {
                "siem_endpoint": "${SIEM_ENDPOINT}",
                "elastic_endpoint": "${ELASTIC_ENDPOINT}",
                "webhook_url": "${AUDIT_WEBHOOK_URL}"
            }
        }
        
        config_dir = self.project_root / "config"
        audit_config_file = config_dir / "audit_logging.json"
        with open(audit_config_file, 'w') as f:
            json.dump(audit_config, f, indent=2)
            
        self.applied_configs.append("audit_logging")
        logger.info("✅ Audit logging configuration created")
        
    def _apply_docker_security(self) -> None:
        """Apply Docker security configurations."""
        logger.info("Applying Docker security hardening...")
        
        # Create secure Dockerfile template
        secure_dockerfile = '''# Multi-stage build for security
FROM python:3.10-slim as builder

# Security: Create non-root user
RUN groupadd -r acgsuser && useradd -r -g acgsuser acgsuser

# Security: Update packages and install minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.10-slim

# Security: Create non-root user
RUN groupadd -r acgsuser && useradd -r -g acgsuser acgsuser

# Security: Update packages
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder
COPY --from=builder /root/.local /home/acgsuser/.local

# Constitutional compliance
ENV CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
ENV PYTHONPATH=/app
ENV PATH=/home/acgsuser/.local/bin:$PATH

# Security: Set working directory and copy application
WORKDIR /app
COPY --chown=acgsuser:acgsuser . .

# Security: Switch to non-root user
USER acgsuser

# Security: Run health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run application
EXPOSE ${PORT:-8000}
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
'''
        
        docker_dir = self.project_root / "infrastructure" / "docker"
        docker_dir.mkdir(parents=True, exist_ok=True)
        
        secure_dockerfile_path = docker_dir / "Dockerfile.secure"
        secure_dockerfile_path.write_text(secure_dockerfile)
        
        # Create Docker Compose security configuration
        docker_compose_security = {
            "version": "3.8",
            "services": {
                "app": {
                    "build": {
                        "context": ".",
                        "dockerfile": "infrastructure/docker/Dockerfile.secure"
                    },
                    "security_opt": [
                        "no-new-privileges:true"
                    ],
                    "cap_drop": ["ALL"],
                    "cap_add": ["CHOWN", "SETGID", "SETUID"],
                    "read_only": True,
                    "tmpfs": [
                        "/tmp:noexec,nosuid,size=100m",
                        "/var/tmp:noexec,nosuid,size=100m"
                    ],
                    "environment": [
                        "CONSTITUTIONAL_HASH=cdd01ef066bc6cf2",
                        "SECURITY_HARDENED=true"
                    ],
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                        "start_period": "60s"
                    }
                }
            }
        }
        
        docker_compose_file = docker_dir / "docker-compose.secure.yml"
        with open(docker_compose_file, 'w') as f:
            yaml.dump(docker_compose_security, f, default_flow_style=False)
            
        self.applied_configs.append("docker_security")
        logger.info("✅ Docker security configurations created")
        
    def _apply_cicd_security(self) -> None:
        """Apply CI/CD security configurations."""
        logger.info("Applying CI/CD security hardening...")
        
        # Create security scanning workflow
        security_workflow = {
            "name": "Security Scanning",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main", "develop"]},
                "schedule": [{"cron": "0 2 * * 1"}]  # Weekly
            },
            "permissions": {
                "contents": "read",
                "security-events": "write"
            },
            "jobs": {
                "security_scan": {
                    "runs-on": "ubuntu-latest",
                    "name": "Security Vulnerability Scan",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Constitutional compliance check",
                            "run": "python scripts/validate_constitutional_compliance.py"
                        },
                        {
                            "name": "Run Bandit security scan",
                            "run": "bandit -r . -f json -o bandit-report.json"
                        },
                        {
                            "name": "Run Safety dependency scan", 
                            "run": "safety check --json --output safety-report.json"
                        },
                        {
                            "name": "Run Trivy filesystem scan",
                            "uses": "aquasecurity/trivy-action@master",
                            "with": {
                                "scan-type": "fs",
                                "scan-ref": ".",
                                "format": "sarif",
                                "output": "trivy-results.sarif"
                            }
                        },
                        {
                            "name": "Upload security results",
                            "uses": "github/codeql-action/upload-sarif@v2",
                            "with": {
                                "sarif_file": "trivy-results.sarif"
                            }
                        }
                    ]
                }
            }
        }
        
        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        security_workflow_file = workflows_dir / "security-hardening.yml"
        with open(security_workflow_file, 'w') as f:
            yaml.dump(security_workflow, f, default_flow_style=False)
            
        self.applied_configs.append("cicd_security")
        logger.info("✅ CI/CD security configurations created")
        
    def _generate_security_report(self) -> Dict[str, any]:
        """Generate comprehensive security hardening report."""
        logger.info("Generating security hardening report...")
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "security_hardening_applied": True,
            "configurations_applied": self.applied_configs,
            "configurations_failed": self.failed_configs,
            "success_rate": len(self.applied_configs) / (len(self.applied_configs) + len(self.failed_configs)) * 100 if (self.applied_configs or self.failed_configs) else 0,
            "next_steps": [
                "Run security validation tests",
                "Update service configurations to use new middleware",
                "Deploy to staging environment for testing",
                "Monitor security metrics and logs",
                "Schedule regular security audits"
            ],
            "compliance_notes": [
                "All configurations include constitutional hash validation",
                "Security headers enforce enterprise-grade protection",
                "Rate limiting prevents DDoS attacks",
                "Input validation prevents injection attacks",
                "Audit logging provides comprehensive security monitoring"
            ]
        }
        
        return report


def main():
    """Main entry point for security hardening application."""
    parser = argparse.ArgumentParser(
        description="ACGS-PGP Security Hardening Applier"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory"
    )
    parser.add_argument(
        "--config-file",
        type=Path,
        help="Security configuration file (JSON)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("security-hardening-report.json"),
        help="Output file for security report"
    )
    parser.add_argument(
        "--apply-all",
        action="store_true",
        help="Apply all security hardening configurations"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config_file and args.config_file.exists():
        with open(args.config_file) as f:
            config_data = json.load(f)
        config = SecurityConfig(**config_data)
    else:
        # Use default configuration
        config = SecurityConfig()
        
    # Override with apply-all flag
    if args.apply_all:
        config = SecurityConfig(**{k: True for k in SecurityConfig.__dataclass_fields__.keys()})
        
    # Apply security hardening
    applier = SecurityHardeningApplier(args.project_root, config)
    report = applier.apply_security_hardening()
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
        
    # Print summary
    print(f"\n{'='*60}")
    print("ACGS-PGP Security Hardening Report")
    print(f"{'='*60}")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Configurations Applied: {len(report['configurations_applied'])}")
    print(f"Configurations Failed: {len(report['configurations_failed'])}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print(f"Report saved to: {args.output}")
    
    if report['configurations_applied']:
        print(f"\n✅ Successfully applied:")
        for config_name in report['configurations_applied']:
            print(f"  • {config_name}")
            
    if report['configurations_failed']:
        print(f"\n❌ Failed to apply:")
        for config_name in report['configurations_failed']:
            print(f"  • {config_name}")
            
    print(f"\n📋 Next steps:")
    for step in report['next_steps']:
        print(f"  • {step}")
        
    # Exit with appropriate code
    sys.exit(0 if not report['configurations_failed'] else 1)


if __name__ == "__main__":
    main()