"""
Enhanced Security Middleware for ACGS
Constitutional Hash: cdd01ef066bc6cf2

This module provides comprehensive security middleware including:
- Input validation and sanitization
- Rate limiting with constitutional compliance
- Security headers enforcement
- Path traversal protection
- SQL injection prevention
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration for enhanced middleware."""
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60  # seconds
    
    # Input validation
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_HEADER_SIZE = 8192  # 8KB
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\./',
        r'\.\.\.',
        r'%2e%2e%2f',
        r'%2e%2e/',
        r'\.\.%2f',
        r'%2e%2e%5c',
        r'\.\.\\',
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
        r'(\s*(or|and)\s*\d+\s*=\s*\d+)',
        r'(\s*(or|and)\s*[\'"][^\'"]*[\'"])',
        r'(\s*;\s*(drop|delete|update|insert))',
        r'(\s*--\s*)',
        r'(\s*/\*.*\*/\s*)',
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
    ]


class RateLimiter:
    """Simple in-memory rate limiter with constitutional compliance."""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        
    def is_allowed(self, client_id: str, max_requests: int = 100, window: int = 60) -> bool:
        """Check if request is allowed under rate limit."""
        now = time.time()
        
        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if now - req_time < window
            ]
        else:
            self.requests[client_id] = []
            
        # Check rate limit
        if len(self.requests[client_id]) >= max_requests:
            logger.warning(
                f"Rate limit exceeded for client {client_id}: "
                f"{len(self.requests[client_id])} requests in {window}s"
            )
            return False
            
        # Add current request
        self.requests[client_id].append(now)
        return True


class InputValidator:
    """Enhanced input validation with constitutional compliance."""
    
    @staticmethod
    def validate_path(path: str) -> bool:
        """Validate URL path for security issues."""
        # Decode URL encoding
        decoded_path = unquote(path)
        
        # Check for path traversal
        for pattern in SecurityConfig.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, decoded_path, re.IGNORECASE):
                logger.warning(f"Path traversal attempt detected: {path}")
                return False
                
        return True
    
    @staticmethod
    def validate_query_params(params: Dict[str, Any]) -> bool:
        """Validate query parameters for SQL injection and XSS."""
        for key, value in params.items():
            if isinstance(value, str):
                # Check for SQL injection
                for pattern in SecurityConfig.SQL_INJECTION_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        logger.warning(f"SQL injection attempt in param {key}: {value}")
                        return False
                
                # Check for XSS
                for pattern in SecurityConfig.XSS_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        logger.warning(f"XSS attempt in param {key}: {value}")
                        return False
                        
        return True
    
    @staticmethod
    def validate_headers(headers: Dict[str, str]) -> bool:
        """Validate HTTP headers for security issues."""
        for name, value in headers.items():
            # Check header size
            if len(f"{name}: {value}") > SecurityConfig.MAX_HEADER_SIZE:
                logger.warning(f"Oversized header detected: {name}")
                return False
                
            # Check for injection attempts in headers
            if re.search(r'[\r\n]', value):
                logger.warning(f"Header injection attempt: {name}")
                return False
                
        return True


class EnhancedSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enhanced security middleware with constitutional compliance.
    
    Features:
    - Rate limiting per client IP
    - Input validation and sanitization
    - Security headers enforcement
    - Path traversal protection
    - SQL injection prevention
    - XSS protection
    - Request size limits
    """
    
    def __init__(self, app, config: Optional[SecurityConfig] = None):
        super().__init__(app)
        self.config = config or SecurityConfig()
        self.rate_limiter = RateLimiter()
        self.validator = InputValidator()
        
    async def dispatch(self, request: Request, call_next):
        """Process request through security middleware."""
        start_time = time.time()
        
        try:
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Rate limiting
            if not self.rate_limiter.is_allowed(
                client_ip, 
                self.config.RATE_LIMIT_REQUESTS, 
                self.config.RATE_LIMIT_WINDOW
            ):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                        "retry_after": self.config.RATE_LIMIT_WINDOW
                    }
                )
            
            # Request size validation
            content_length = request.headers.get('content-length')
            if content_length and int(content_length) > self.config.MAX_REQUEST_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail={
                        "error": "Request too large",
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                        "max_size": self.config.MAX_REQUEST_SIZE
                    }
                )
            
            # Path validation
            if not self.validator.validate_path(str(request.url.path)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Invalid path detected",
                        "constitutional_hash": CONSTITUTIONAL_HASH
                    }
                )
            
            # Query parameter validation
            if not self.validator.validate_query_params(dict(request.query_params)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Invalid query parameters",
                        "constitutional_hash": CONSTITUTIONAL_HASH
                    }
                )
            
            # Header validation
            if not self.validator.validate_headers(dict(request.headers)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Invalid headers detected",
                        "constitutional_hash": CONSTITUTIONAL_HASH
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response = self._add_security_headers(response)
            
            # Log security metrics
            processing_time = time.time() - start_time
            logger.info(
                f"Security middleware processed request: "
                f"path={request.url.path}, "
                f"client_ip={client_ip}, "
                f"processing_time={processing_time:.3f}s, "
                f"constitutional_hash={CONSTITUTIONAL_HASH}"
            )
            
            return response
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.exception(f"Security middleware error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Security processing failed",
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
            
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
            
        # Fallback to direct connection
        if request.client:
            return request.client.host
            
        return "unknown"
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response."""
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'X-Constitutional-Hash': CONSTITUTIONAL_HASH,
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
            
        return response


def create_security_middleware(
    max_requests: int = 100,
    window_seconds: int = 60,
    max_request_size: int = 10 * 1024 * 1024
) -> EnhancedSecurityMiddleware:
    """
    Factory function to create configured security middleware.
    
    Args:
        max_requests: Maximum requests per window
        window_seconds: Rate limit window in seconds
        max_request_size: Maximum request size in bytes
    
    Returns:
        Configured security middleware instance
    """
    config = SecurityConfig()
    config.RATE_LIMIT_REQUESTS = max_requests
    config.RATE_LIMIT_WINDOW = window_seconds
    config.MAX_REQUEST_SIZE = max_request_size
    
    return lambda app: EnhancedSecurityMiddleware(app, config)


# Export for easy import
__all__ = [
    'EnhancedSecurityMiddleware',
    'SecurityConfig',
    'RateLimiter',
    'InputValidator',
    'create_security_middleware',
    'CONSTITUTIONAL_HASH'
]