"""
ACGS-1 Security Configuration
Enhanced security settings for production deployment
"""

import os
from typing import Dict, Any

# Security Headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}

# Secure defaults
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Password requirements
PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SYMBOLS = True

# Rate limiting
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS_PER_MINUTE = 60
RATE_LIMIT_BURST = 10

# Logging security events
SECURITY_LOG_LEVEL = "INFO"
SECURITY_LOG_FILE = "/var/log/acgs/security.log"

def get_security_config() -> Dict[str, Any]:
    """Get security configuration"""
    return {
        "headers": SECURITY_HEADERS,
        "ssl_redirect": SECURE_SSL_REDIRECT,
        "hsts_seconds": SECURE_HSTS_SECONDS,
        "session_secure": SESSION_COOKIE_SECURE,
        "csrf_secure": CSRF_COOKIE_SECURE,
        "rate_limit": RATE_LIMIT_ENABLED,
        "password_policy": {
            "min_length": PASSWORD_MIN_LENGTH,
            "require_uppercase": PASSWORD_REQUIRE_UPPERCASE,
            "require_lowercase": PASSWORD_REQUIRE_LOWERCASE,
            "require_numbers": PASSWORD_REQUIRE_NUMBERS,
            "require_symbols": PASSWORD_REQUIRE_SYMBOLS
        }
    }
