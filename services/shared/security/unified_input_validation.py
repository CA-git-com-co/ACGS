"""
Unified Input Validation and Security Middleware for ACGS

This module provides comprehensive input validation, XSS protection, 
SQL injection prevention, and CSRF protection across all ACGS services.
"""

import re
import html
import json
import secrets
import hashlib
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field

import structlog
from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class SecurityLevel(Enum):
    """Security validation levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationRule(Enum):
    """Input validation rule types."""
    LENGTH = "length"
    PATTERN = "pattern"
    ENCODING = "encoding"
    INJECTION = "injection"
    XSS = "xss"
    CSRF = "csrf"


@dataclass
class SecurityConfig:
    """Security configuration for input validation."""
    max_string_length: int = 1000
    max_json_size: int = 1024 * 1024  # 1MB
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: Set[str] = field(default_factory=lambda: {
        'jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'json', 'xml'
    })
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    csrf_token_expiry: int = 3600  # 1 hour
    enable_strict_csp: bool = True
    enable_xss_protection: bool = True
    enable_csrf_protection: bool = True


@dataclass
class ValidationResult:
    """Result of input validation."""
    is_valid: bool
    sanitized_value: Any = None
    errors: List[str] = field(default_factory=list)
    security_warnings: List[str] = field(default_factory=list)
    risk_score: float = 0.0


class SecurityPatterns:
    """Comprehensive security patterns for various attacks."""
    
    # Enhanced SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|SCRIPT)\b)",
        r"(\b(UNION|OR|AND)\s+[\d\w]+\s*[=<>!]+\s*[\d\w]+)",
        r"(--|#|/\*|\*/|;)",
        r"(\bxp_|\bsp_|\bms_)",
        r"(\bCAST\s*\(|\bCONVERT\s*\(|\bCHAR\s*\(|\bASCII\s*\()",
        r"(\bINTO\s+OUTFILE|\bLOAD_FILE\s*\()",
        r"(\bSLEEP\s*\(|\bBENCHMARK\s*\()",
        r"(\b0x[0-9a-fA-F]+)",
        r"(\bCONCAT\s*\(|\bSUBSTRING\s*\()",
        r"(\bINFORMATION_SCHEMA\b|\bSYS\b|\bUSER\s*\()",
    ]
    
    # Enhanced XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript\s*:",
        r"vbscript\s*:",
        r"data\s*:",
        r"on\w+\s*=",  # Event handlers
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<applet[^>]*>",
        r"<meta[^>]*>",
        r"<link[^>]*>",
        r"<base[^>]*>",
        r"<form[^>]*>",
        r"<svg[^>]*>.*?</svg>",
        r"expression\s*\(",
        r"@import\s*[\"']?",
        r"background\s*:\s*url\s*\(",
        r"style\s*=.*expression",
        r"&[#x]?[0-9a-fA-F]{2,8};",  # HTML entities
    ]
    
    # LDAP injection patterns
    LDAP_INJECTION_PATTERNS = [
        r"[()&|!*\\]",
        r"[\x00-\x1f\x7f-\x9f]",  # Control characters
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$]",
        r"\b(cat|ls|pwd|id|whoami|uname|ps|kill|rm|mv|cp|chmod|chown)\b",
        r"(\.\./|\.\.\\)",
        r"(/bin/|/usr/bin/|/sbin/|/usr/sbin/)",
        r"(cmd|powershell|bash|sh|zsh|fish)\s",
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e\\",
        r"..%2f",
        r"..%5c",
        r"%252e%252e%252f",
    ]
    
    # File upload validation patterns
    SUSPICIOUS_FILE_PATTERNS = [
        r"\.(php|asp|aspx|jsp|exe|bat|cmd|com|scr|vbs|js|jar|sh|py|pl|rb)$",
        r"^\.ht",  # .htaccess, .htpasswd
        r"^web\.config$",
        r"^php\.ini$",
    ]


class EnhancedInputValidator:
    """Enhanced input validator with comprehensive security checks."""
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.csrf_tokens: Dict[str, datetime] = {}
        
    def validate_string(
        self,
        value: str,
        max_length: Optional[int] = None,
        min_length: int = 0,
        allowed_chars: Optional[str] = None,
        security_level: SecurityLevel = SecurityLevel.MEDIUM
    ) -> ValidationResult:
        """Comprehensive string validation with security checks."""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(value, str):
            result.is_valid = False
            result.errors.append("Input must be a string")
            return result
        
        original_value = value
        risk_score = 0.0
        
        # Length validation
        max_len = max_length or self.config.max_string_length
        if len(value) > max_len:
            result.is_valid = False
            result.errors.append(f"Input exceeds maximum length of {max_len}")
            return result
        
        if len(value) < min_length:
            result.is_valid = False
            result.errors.append(f"Input is shorter than minimum length of {min_length}")
            return result
        
        # Character validation
        if allowed_chars and not re.match(f"^[{re.escape(allowed_chars)}]*$", value):
            result.is_valid = False
            result.errors.append("Input contains disallowed characters")
            return result
        
        # Security pattern detection
        security_checks = [
            (SecurityPatterns.SQL_INJECTION_PATTERNS, "SQL injection", 0.8),
            (SecurityPatterns.XSS_PATTERNS, "XSS", 0.7),
            (SecurityPatterns.COMMAND_INJECTION_PATTERNS, "Command injection", 0.9),
            (SecurityPatterns.PATH_TRAVERSAL_PATTERNS, "Path traversal", 0.6),
            (SecurityPatterns.LDAP_INJECTION_PATTERNS, "LDAP injection", 0.5),
        ]
        
        value_lower = value.lower()
        for patterns, attack_type, weight in security_checks:
            for pattern in patterns:
                if re.search(pattern, value_lower, re.IGNORECASE | re.MULTILINE):
                    risk_score += weight
                    warning = f"Potential {attack_type} detected in input"
                    result.security_warnings.append(warning)
                    
                    if security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                        result.is_valid = False
                        result.errors.append(warning)
        
        # Encoding detection
        try:
            # Check for URL encoding
            decoded_url = urllib.parse.unquote(value)
            if decoded_url != value:
                risk_score += 0.2
                # Recursively check decoded content
                decoded_result = self.validate_string(
                    decoded_url, max_length, min_length, allowed_chars, security_level
                )
                if not decoded_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(decoded_result.errors)
                    result.security_warnings.extend(decoded_result.security_warnings)
            
            # Check for HTML encoding
            decoded_html = html.unescape(value)
            if decoded_html != value:
                risk_score += 0.2
                
        except Exception as e:
            result.security_warnings.append(f"Encoding detection error: {str(e)}")
        
        # Sanitization
        sanitized_value = self._sanitize_string(value, security_level)
        
        result.sanitized_value = sanitized_value
        result.risk_score = min(1.0, risk_score)
        
        # Log high-risk inputs
        if result.risk_score > 0.5:
            logger.warning(
                "High-risk input detected",
                original_value=original_value[:100],  # Truncate for logging
                risk_score=result.risk_score,
                warnings=result.security_warnings,
                constitutional_hash=CONSTITUTIONAL_HASH
            )
        
        return result
    
    def _sanitize_string(self, value: str, security_level: SecurityLevel) -> str:
        """Sanitize string based on security level."""
        # Always trim whitespace
        value = value.strip()
        
        if security_level in [SecurityLevel.LOW, SecurityLevel.MEDIUM]:
            # HTML encoding for XSS prevention
            value = html.escape(value)
        
        elif security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            # Aggressive sanitization
            # Remove all HTML tags
            value = re.sub(r'<[^>]+>', '', value)
            # HTML encode
            value = html.escape(value)
            # Remove JavaScript protocol
            value = re.sub(r'javascript\s*:', '', value, flags=re.IGNORECASE)
            # Remove data URLs
            value = re.sub(r'data\s*:', '', value, flags=re.IGNORECASE)
        
        return value
    
    def validate_email(self, email: str) -> ValidationResult:
        """Validate email with enhanced security checks."""
        result = ValidationResult(is_valid=True)
        
        if not email:
            result.is_valid = False
            result.errors.append("Email is required")
            return result
        
        # Length check
        if len(email) > 254:
            result.is_valid = False
            result.errors.append("Email address is too long")
            return result
        
        # Format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            result.is_valid = False
            result.errors.append("Invalid email format")
            return result
        
        # Security validation
        string_result = self.validate_string(email, security_level=SecurityLevel.HIGH)
        if not string_result.is_valid:
            result.is_valid = False
            result.errors.extend(string_result.errors)
            result.security_warnings.extend(string_result.security_warnings)
        else:
            result.sanitized_value = string_result.sanitized_value.lower()
        
        return result
    
    def validate_file_upload(
        self,
        filename: str,
        content: bytes,
        allowed_types: Optional[Set[str]] = None
    ) -> ValidationResult:
        """Validate file upload with security checks."""
        result = ValidationResult(is_valid=True)
        
        # Size check
        if len(content) > self.config.max_file_size:
            result.is_valid = False
            result.errors.append("File size exceeds maximum limit")
            return result
        
        # Filename validation
        filename_result = self.validate_string(
            filename,
            max_length=255,
            security_level=SecurityLevel.HIGH
        )
        if not filename_result.is_valid:
            result.is_valid = False
            result.errors.extend(filename_result.errors)
            return result
        
        # File extension validation
        allowed_types = allowed_types or self.config.allowed_file_types
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if file_ext not in allowed_types:
            result.is_valid = False
            result.errors.append(f"File type .{file_ext} is not allowed")
            return result
        
        # Suspicious filename patterns
        for pattern in SecurityPatterns.SUSPICIOUS_FILE_PATTERNS:
            if re.search(pattern, filename.lower()):
                result.is_valid = False
                result.errors.append("Suspicious filename detected")
                return result
        
        # Content validation (magic number check)
        if not self._validate_file_content(content, file_ext):
            result.is_valid = False
            result.errors.append("File content does not match extension")
            return result
        
        result.sanitized_value = filename_result.sanitized_value
        return result
    
    def _validate_file_content(self, content: bytes, expected_ext: str) -> bool:
        """Validate file content matches expected type."""
        if not content:
            return False
        
        # Magic number validation for common file types
        magic_numbers = {
            'jpg': [b'\xff\xd8\xff'],
            'jpeg': [b'\xff\xd8\xff'],
            'png': [b'\x89\x50\x4e\x47'],
            'gif': [b'\x47\x49\x46\x38'],
            'pdf': [b'\x25\x50\x44\x46'],
        }
        
        if expected_ext in magic_numbers:
            for magic in magic_numbers[expected_ext]:
                if content.startswith(magic):
                    return True
            return False
        
        # For text files, check for reasonable content
        if expected_ext in ['txt', 'json', 'xml']:
            try:
                content.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
        
        return True
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate a secure CSRF token."""
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(f"{token}:{session_id}:{CONSTITUTIONAL_HASH}".encode()).hexdigest()
        
        # Store token with expiry
        self.csrf_tokens[token_hash] = datetime.now() + timedelta(seconds=self.config.csrf_token_expiry)
        
        return token
    
    def validate_csrf_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token."""
        if not token or not session_id:
            return False
        
        token_hash = hashlib.sha256(f"{token}:{session_id}:{CONSTITUTIONAL_HASH}".encode()).hexdigest()
        
        if token_hash not in self.csrf_tokens:
            return False
        
        # Check expiry
        if datetime.now() > self.csrf_tokens[token_hash]:
            del self.csrf_tokens[token_hash]
            return False
        
        return True
    
    def cleanup_expired_tokens(self):
        """Clean up expired CSRF tokens."""
        now = datetime.now()
        expired_tokens = [
            token for token, expiry in self.csrf_tokens.items()
            if now > expiry
        ]
        
        for token in expired_tokens:
            del self.csrf_tokens[token]


class SecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware for all ACGS services."""
    
    def __init__(self, app, config: SecurityConfig = None):
        super().__init__(app)
        self.config = config or SecurityConfig()
        self.validator = EnhancedInputValidator(config)
        self.rate_limits: Dict[str, List[datetime]] = {}
        
    async def dispatch(self, request: Request, call_next):
        """Process request through security middleware."""
        start_time = datetime.now()
        
        try:
            # Rate limiting
            if not await self._check_rate_limit(request):
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={"Retry-After": "60"}
                )
            
            # CSRF protection for state-changing methods
            if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                if self.config.enable_csrf_protection:
                    if not await self._validate_csrf(request):
                        return Response(
                            content="CSRF token validation failed",
                            status_code=403
                        )
            
            # Content length validation
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.config.max_json_size:
                return Response(
                    content="Request too large",
                    status_code=413
                )
            
            # Input validation for JSON payloads
            if request.headers.get("content-type") == "application/json":
                await self._validate_json_payload(request)
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response = self._add_security_headers(response)
            
            # Log request
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                "Request processed",
                method=request.method,
                path=request.url.path,
                duration=duration,
                status=response.status_code,
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
            return response
            
        except HTTPException as e:
            logger.warning(
                "Security middleware blocked request",
                method=request.method,
                path=request.url.path,
                error=str(e),
                client_ip=request.client.host if request.client else None
            )
            raise
        except Exception as e:
            logger.error(
                "Security middleware error",
                error=str(e),
                method=request.method,
                path=request.url.path
            )
            return Response(
                content="Internal security error",
                status_code=500
            )
    
    async def _check_rate_limit(self, request: Request) -> bool:
        """Check rate limiting for client."""
        client_ip = request.client.host if request.client else "unknown"
        current_time = datetime.now()
        
        # Clean old entries
        if client_ip in self.rate_limits:
            self.rate_limits[client_ip] = [
                timestamp for timestamp in self.rate_limits[client_ip]
                if current_time - timestamp < timedelta(seconds=self.config.rate_limit_window)
            ]
        else:
            self.rate_limits[client_ip] = []
        
        # Check limit
        if len(self.rate_limits[client_ip]) >= self.config.rate_limit_requests:
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                request_count=len(self.rate_limits[client_ip])
            )
            return False
        
        # Add current request
        self.rate_limits[client_ip].append(current_time)
        return True
    
    async def _validate_csrf(self, request: Request) -> bool:
        """Validate CSRF token."""
        if not self.config.enable_csrf_protection:
            return True
        
        # Skip CSRF for API endpoints with proper authentication
        if request.url.path.startswith("/api/"):
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                return True
        
        csrf_token = request.headers.get("x-csrf-token")
        session_id = request.cookies.get("session_id")
        
        if not csrf_token or not session_id:
            return False
        
        return self.validator.validate_csrf_token(csrf_token, session_id)
    
    async def _validate_json_payload(self, request: Request):
        """Validate JSON payload for security issues."""
        try:
            # This is a simplified validation - in practice you'd want to
            # validate the actual JSON content after parsing
            body = await request.body()
            if body:
                # Basic JSON structure validation
                json.loads(body)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        except Exception:
            raise HTTPException(status_code=400, detail="Payload validation failed")
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response."""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }
        
        if self.config.enable_strict_csp:
            headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        
        # Add constitutional compliance header
        headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
        
        for key, value in headers.items():
            response.headers[key] = value
        
        return response


# Pydantic models for secure request validation
class SecureBaseModel(BaseModel):
    """Base model with enhanced security validation."""
    
    class Config:
        str_strip_whitespace = True
        validate_assignment = True
        extra = "forbid"  # Prevent extra fields


class SecureStringField(BaseModel):
    """Secure string field with validation."""
    value: str = Field(..., min_length=1, max_length=1000)
    
    @field_validator('value')
    @classmethod
    def validate_secure_string(cls, v: str) -> str:
        validator = EnhancedInputValidator()
        result = validator.validate_string(v, security_level=SecurityLevel.HIGH)
        
        if not result.is_valid:
            raise ValueError(f"Validation failed: {', '.join(result.errors)}")
        
        return result.sanitized_value


class SecureLoginRequest(SecureBaseModel):
    """Secure login request with enhanced validation."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    csrf_token: Optional[str] = Field(None, min_length=16, max_length=128)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        validator = EnhancedInputValidator()
        result = validator.validate_string(
            v,
            allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
            security_level=SecurityLevel.HIGH
        )
        
        if not result.is_valid:
            raise ValueError(f"Username validation failed: {', '.join(result.errors)}")
        
        return result.sanitized_value
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        # Password strength validation
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        
        return v


class SecureEmailRequest(SecureBaseModel):
    """Secure email validation request."""
    email: str = Field(..., min_length=5, max_length=254)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        validator = EnhancedInputValidator()
        result = validator.validate_email(v)
        
        if not result.is_valid:
            raise ValueError(f"Email validation failed: {', '.join(result.errors)}")
        
        return result.sanitized_value


# Utility functions for easy integration
def create_security_middleware(config: SecurityConfig = None) -> SecurityMiddleware:
    """Create security middleware with configuration."""
    return SecurityMiddleware(None, config)


def validate_input_secure(
    value: str,
    max_length: int = 1000,
    security_level: SecurityLevel = SecurityLevel.MEDIUM
) -> str:
    """Quick utility function for secure input validation."""
    validator = EnhancedInputValidator()
    result = validator.validate_string(value, max_length=max_length, security_level=security_level)
    
    if not result.is_valid:
        raise ValueError(f"Input validation failed: {', '.join(result.errors)}")
    
    return result.sanitized_value


def sanitize_dict(data: Dict[str, Any], security_level: SecurityLevel = SecurityLevel.MEDIUM) -> Dict[str, Any]:
    """Sanitize dictionary data recursively."""
    validator = EnhancedInputValidator()
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(key, str):
            key_result = validator.validate_string(key, max_length=100, security_level=security_level)
            clean_key = key_result.sanitized_value if key_result.is_valid else key
        else:
            clean_key = str(key)
        
        if isinstance(value, str):
            value_result = validator.validate_string(value, security_level=security_level)
            clean_value = value_result.sanitized_value if value_result.is_valid else value
        elif isinstance(value, dict):
            clean_value = sanitize_dict(value, security_level)
        elif isinstance(value, list):
            clean_value = [
                sanitize_dict(item, security_level) if isinstance(item, dict)
                else validate_input_secure(item, security_level=security_level) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            clean_value = value
        
        sanitized[clean_key] = clean_value
    
    return sanitized