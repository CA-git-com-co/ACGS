#!/usr/bin/env python3
"""
Minimal ACGS Auth Service for Security Testing
Constitutional Hash: cdd01ef066bc6cf2

This is a minimal version to test the critical security fixes:
1. Token validation endpoint
2. Security headers
3. Constitutional hash validation
"""

import json
import jwt
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, ValidationError
import uvicorn

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Simple JWT configuration
JWT_SECRET = "test-secret-key-for-acgs-auth"
JWT_ALGORITHM = "HS256"

# Data Models
class TokenValidationRequest(BaseModel):
    token: str
    constitutional_hash: str

class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: int | None = None
    username: str | None = None
    roles: list[str] | None = None
    reason: str | None = None
    constitutional_hash: str
    validated_at: str

class LoginRequest(BaseModel):
    username: str
    password: str

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add comprehensive security headers to all responses"""
    
    def __init__(self, app):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-Constitutional-Hash": CONSTITUTIONAL_HASH
        }
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add all security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        return response

# Create FastAPI app
app = FastAPI(
    title="ACGS Minimal Auth Service - Security Testing",
    description="Minimal auth service for testing critical security fixes",
    version="1.0.0"
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Custom exception handlers for constitutional compliance
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with constitutional compliance"""
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "constitutional_compliance": True,
            "message": "Request validation failed - ensure constitutional_hash is provided"
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with constitutional compliance"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "constitutional_compliance": True,
            "status_code": exc.status_code
        }
    )

# Simple token validation function
def validate_jwt_token(token: str) -> Dict[str, Any]:
    """Validate JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Create a test token for validation
def create_test_token(username: str = "testuser", user_id: int = 1) -> str:
    """Create a test JWT token"""
    payload = {
        "sub": username,
        "user_id": user_id,
        "roles": ["user"],
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Health endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with constitutional compliance"""
    return {
        "status": "healthy",
        "service": "ACGS Minimal Auth Service",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "constitutional_compliance": True,
        "security_features": [
            "secure_token_validation",
            "constitutional_hash_enforcement", 
            "security_headers",
            "injection_protection"
        ],
        "timestamp": datetime.now().isoformat()
    }

# Critical security endpoint - Token validation
@app.post("/api/v1/auth/validate", response_model=TokenValidationResponse)
async def validate_token(request: TokenValidationRequest):
    """
    Validate JWT token with constitutional compliance.
    
    Critical security endpoint that validates tokens from other services.
    """
    
    # Validate constitutional hash in request
    if request.constitutional_hash != CONSTITUTIONAL_HASH:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid constitutional hash",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "valid": False
            }
        )
    
    try:
        # Validate the JWT token
        payload = validate_jwt_token(request.token)
        
        # Return successful validation
        return TokenValidationResponse(
            valid=True,
            user_id=payload.get("user_id"),
            username=payload.get("sub"),
            roles=payload.get("roles", []),
            constitutional_hash=CONSTITUTIONAL_HASH,
            validated_at=datetime.now().isoformat()
        )
        
    except HTTPException as e:
        # Re-raise HTTP exceptions (401, etc.)
        raise e
    except Exception as e:
        # For other errors, return 401 with constitutional hash
        raise HTTPException(
            status_code=401,
            detail={
                "error": f"Token validation error: {str(e)}",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "valid": False
            }
        )

# Login endpoint for testing
@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    """Simple login endpoint for testing"""
    
    # Simple test credentials
    if request.username == "testuser" and request.password == "testpass":
        token = create_test_token(request.username, 1)
        return {
            "access_token": token,
            "token_type": "bearer",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "expires_in": 3600
        }
    else:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Invalid credentials",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        )

# Status endpoint
@app.get("/api/v1/auth/status")
async def auth_status():
    """Auth service status with constitutional compliance"""
    return {
        "service": "ACGS Minimal Auth Service",
        "status": "operational",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "constitutional_compliance": True,
        "endpoints": [
            "/health",
            "/api/v1/auth/validate",
            "/api/v1/auth/login", 
            "/api/v1/auth/status"
        ],
        "security_features_active": True,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print(f"🚀 Starting ACGS Minimal Auth Service on port 8017")
    print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"🔒 Security headers enabled")
    print(f"🎯 Test credentials: testuser/testpass")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8017,
        log_level="info"
    )
