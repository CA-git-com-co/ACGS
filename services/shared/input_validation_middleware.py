
"""
Input Validation Middleware for ACGS-1 Services
Implements comprehensive input validation and sanitization.
"""

import re
import json
from typing import Any, Dict, List
from fastapi import Request, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Enhanced input validation middleware."""
    
    def __init__(self, app):
        super().__init__(app)
        self.malicious_patterns = [
            # SQL Injection patterns
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            
            # XSS patterns
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            
            # Path traversal
            r"\.\.[\\/]",
            r"[\\/]etc[\\/]passwd",
            r"[\\/]windows[\\/]system32",
            
            # Command injection
            r"[;&|`$]",
            r"\b(cat|ls|pwd|whoami|id|uname)\b",
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.malicious_patterns]
    
    async def dispatch(self, request: Request, call_next):
        # Validate URL parameters
        if request.query_params:
            for key, value in request.query_params.items():
                if self._contains_malicious_content(str(value)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "Invalid input detected",
                            "parameter": key,
                            "reason": "Potentially malicious content blocked"
                        }
                    )
        
        # Validate headers
        for header_name, header_value in request.headers.items():
            if self._contains_malicious_content(header_value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Invalid header detected",
                        "header": header_name,
                        "reason": "Potentially malicious content blocked"
                    }
                )
        
        # Validate request body for POST/PUT/PATCH requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8')
                    if self._contains_malicious_content(body_str):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail={
                                "error": "Invalid request body",
                                "reason": "Potentially malicious content blocked"
                            }
                        )
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"error": "Invalid request encoding"}
                )
        
        # Process request
        response = await call_next(request)
        
        # Add validation headers
        response.headers["X-Input-Validation"] = "enabled"
        response.headers["X-Security-Level"] = "enhanced"
        
        return response
    
    def _contains_malicious_content(self, content: str) -> bool:
        """Check if content contains malicious patterns."""
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                return True
        return False
