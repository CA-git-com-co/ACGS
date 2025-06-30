"""
Comprehensive Input Validation Module for ACGS-2
Implements security-hardened input validation to prevent injection attacks.
"""

import re
import html
import json
import logging
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class SecurityInputValidator:
    """Security-focused input validator with comprehensive protection."""
    
    def __init__(self):
        # Dangerous patterns for different attack types
        self.sql_injection_patterns = [
            r"('|(\'))+.*(;|--|#)",
            r"(union|select|insert|update|delete|drop|create|alter)\s",
            r"'\s*(or|and)\s*'",
            r"'\s*(or|and)\s*\d+\s*=\s*\d+",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]
        
        self.command_injection_patterns = [
            r"[;&|`]\s*(rm|del|format|cat|type|whoami|id|ps|ls|dir)",
            r"\$\([^)]*\)",
            r"`[^`]*`",
            r"\|\s*(curl|wget|nc|netcat)",
        ]
        
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"\.\.[\\/]",
            r"\.\.%2f",
            r"\.\.%5c",
        ]

        self.ldap_injection_patterns = [
            r"\*\)\(&\(",
            r"\*\)\(\|\(",
            r"\)\(&\(",
            r"\*\)\)%00",
            r"objectClass=\*",
            r"\(\|\(",
        ]

        self.xml_injection_patterns = [
            r"<\?xml.*\?>",
            r"<!DOCTYPE.*>",
            r"<!ENTITY.*>",
            r"<!\[CDATA\[",
            r"<\?xml-stylesheet",
            r"SYSTEM\s+['\"]",
        ]

        self.nosql_injection_patterns = [
            r"\$ne\s*:",
            r"\$gt\s*:",
            r"\$where\s*:",
            r"\$regex\s*:",
            r"\$or\s*:",
            r"\$and\s*:",
        ]
        
        # Maximum lengths for different input types
        self.max_lengths = {
            "username": 50,
            "email": 254,
            "password": 128,
            "title": 200,
            "description": 2000,
            "general": 1000
        }
    
    def validate_input(self, input_data: Any, input_type: str = "general") -> Dict[str, Any]:
        """
        Comprehensive input validation.
        
        Args:
            input_data: The input to validate
            input_type: Type of input (username, email, password, etc.)
            
        Returns:
            Dict with validation results
        """
        result = {
            "is_valid": True,
            "sanitized_input": input_data,
            "violations": [],
            "risk_level": "LOW"
        }
        
        # Convert to string for validation
        if input_data is None:
            result["is_valid"] = False
            result["violations"].append("Input cannot be None")
            result["risk_level"] = "HIGH"
            return result
        
        input_str = str(input_data)
        
        # Check length limits
        max_length = self.max_lengths.get(input_type, self.max_lengths["general"])
        if len(input_str) > max_length:
            result["is_valid"] = False
            result["violations"].append(f"Input exceeds maximum length of {max_length}")
            result["risk_level"] = "MEDIUM"
        
        # Check for null bytes
        if "\x00" in input_str or "\0" in input_str:
            result["is_valid"] = False
            result["violations"].append("Null bytes not allowed")
            result["risk_level"] = "HIGH"
        
        # Check for SQL injection patterns
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                result["is_valid"] = False
                result["violations"].append("Potential SQL injection detected")
                result["risk_level"] = "CRITICAL"
                break
        
        # Check for XSS patterns
        for pattern in self.xss_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                result["is_valid"] = False
                result["violations"].append("Potential XSS attack detected")
                result["risk_level"] = "CRITICAL"
                break
        
        # Check for command injection patterns
        for pattern in self.command_injection_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                result["is_valid"] = False
                result["violations"].append("Command injection detected")
                result["risk_level"] = "CRITICAL"
                break
        
        # Check for path traversal patterns
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                result["is_valid"] = False
                result["violations"].append("Path traversal detected")
                result["risk_level"] = "HIGH"
                break

        # Check for LDAP injection patterns
        for pattern in self.ldap_injection_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                result["is_valid"] = False
                result["violations"].append("LDAP injection detected")
                result["risk_level"] = "HIGH"
                break

        # Check for XML injection patterns
        for pattern in self.xml_injection_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                result["is_valid"] = False
                result["violations"].append("XML injection detected")
                result["risk_level"] = "HIGH"
                break

        # Check for NoSQL injection patterns
        for pattern in self.nosql_injection_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                result["is_valid"] = False
                result["violations"].append("NoSQL injection detected")
                result["risk_level"] = "HIGH"
                break
        
        # Sanitize input if valid
        if result["is_valid"]:
            result["sanitized_input"] = self.sanitize_input(input_str, input_type)
        
        return result
    
    def sanitize_input(self, input_str: str, input_type: str = "general") -> str:
        """Sanitize input string based on type."""
        if input_type == "email":
            # Basic email sanitization
            return re.sub(r'[^a-zA-Z0-9@._-]', '', input_str)
        elif input_type == "username":
            # Allow alphanumeric and basic punctuation
            return re.sub(r'[^a-zA-Z0-9._-]', '', input_str)
        elif input_type == "html":
            # HTML escape
            return html.escape(input_str)
        else:
            # General sanitization - remove dangerous characters
            sanitized = re.sub(r'[<>"\'`]', '', input_str)
            return sanitized.strip()
    
    def validate_json_input(self, json_str: str) -> Dict[str, Any]:
        """Validate JSON input for injection attacks."""
        result = {
            "is_valid": True,
            "parsed_json": None,
            "violations": [],
            "risk_level": "LOW"
        }
        
        try:
            # Parse JSON
            parsed = json.loads(json_str)
            
            # Check for dangerous keys/values
            dangerous_keys = ["$ne", "$gt", "$lt", "$regex", "$where", "eval", "function"]
            
            def check_dangerous_content(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key in dangerous_keys:
                            result["is_valid"] = False
                            result["violations"].append(f"Dangerous key '{key}' found at {path}")
                            result["risk_level"] = "HIGH"
                        check_dangerous_content(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        check_dangerous_content(item, f"{path}[{i}]")
                elif isinstance(obj, str):
                    # Check string values for injection patterns
                    validation_result = self.validate_input(obj)
                    if not validation_result["is_valid"]:
                        result["is_valid"] = False
                        result["violations"].extend(validation_result["violations"])
                        if validation_result["risk_level"] == "CRITICAL":
                            result["risk_level"] = "CRITICAL"
            
            check_dangerous_content(parsed)
            result["parsed_json"] = parsed
            
        except json.JSONDecodeError as e:
            result["is_valid"] = False
            result["violations"].append(f"Invalid JSON format: {str(e)}")
            result["risk_level"] = "MEDIUM"
        
        return result

# Global validator instance
security_validator = SecurityInputValidator()

def validate_user_input(input_data: Any, input_type: str = "general") -> Dict[str, Any]:
    """
    Main function for validating user input.

    Args:
        input_data: The input to validate
        input_type: Type of input for context-specific validation

    Returns:
        Validation result dictionary
    """
    return security_validator.validate_input(input_data, input_type)


class SecurityValidationMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic input validation on all API endpoints.
    Validates request bodies, query parameters, and path parameters.
    """

    def __init__(self, app, exempt_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            "/health", "/metrics", "/docs", "/openapi.json", "/redoc", "/favicon.ico"
        ]
        self.validator = SecurityInputValidator()

    async def dispatch(self, request: Request, call_next):
        """Process request through security validation."""

        # Skip validation for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        # Skip validation for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        try:
            # Validate request body for POST/PUT/PATCH requests
            if request.method in ["POST", "PUT", "PATCH"]:
                await self._validate_request_body(request)

            # Validate query parameters
            await self._validate_query_params(request)

            # Continue with request processing
            response = await call_next(request)
            return response

        except HTTPException as e:
            logger.warning(f"Security validation failed for {request.url.path}: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"error": "Input validation failed", "detail": e.detail}
            )
        except Exception as e:
            logger.error(f"Security validation error for {request.url.path}: {e}")
            return JSONResponse(
                status_code=400,
                content={"error": "Input validation error", "detail": str(e)}
            )

    async def _validate_request_body(self, request: Request):
        """Validate request body content."""
        try:
            # Get request body
            body = await request.body()
            if not body:
                return

            # Parse JSON body
            try:
                json_data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                # If not JSON, validate as string
                body_str = body.decode('utf-8')
                result = self.validator.validate_input(body_str, "general")
                if not result["is_valid"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Request body validation failed: {', '.join(result['violations'])}"
                    )
                return

            # Recursively validate JSON data
            self._validate_json_data(json_data, "request_body")

        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Invalid request body encoding")

    async def _validate_query_params(self, request: Request):
        """Validate query parameters."""
        for key, value in request.query_params.items():
            result = self.validator.validate_input(value, "general")
            if not result["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Query parameter '{key}' validation failed: {', '.join(result['violations'])}"
                )

    def _validate_json_data(self, data: Any, context: str = "json"):
        """Recursively validate JSON data structure."""
        if isinstance(data, dict):
            for key, value in data.items():
                # Validate key
                key_result = self.validator.validate_input(key, "general")
                if not key_result["is_valid"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"JSON key '{key}' validation failed: {', '.join(key_result['violations'])}"
                    )

                # Recursively validate value
                self._validate_json_data(value, f"{context}.{key}")

        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._validate_json_data(item, f"{context}[{i}]")

        elif isinstance(data, str):
            # Determine input type based on context
            input_type = self._determine_input_type(context, data)
            result = self.validator.validate_input(data, input_type)
            if not result["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Field '{context}' validation failed: {', '.join(result['violations'])}"
                )

    def _determine_input_type(self, context: str, value: str) -> str:
        """Determine appropriate input type based on context and value."""
        context_lower = context.lower()

        # Email detection
        if "email" in context_lower or "@" in value:
            return "email"

        # Username detection
        if "username" in context_lower or "user" in context_lower:
            return "username"

        # Password detection
        if "password" in context_lower or "pass" in context_lower:
            return "password"

        # Title detection
        if "title" in context_lower or "name" in context_lower:
            return "title"

        # Description/content detection
        if any(keyword in context_lower for keyword in ["description", "content", "text", "body", "message"]):
            return "description"

        # HTML content detection
        if any(keyword in context_lower for keyword in ["html", "markup"]):
            return "html"

        return "general"


def create_security_validation_dependency():
    """
    Create a FastAPI dependency for manual input validation in specific endpoints.
    Use this for endpoints that need custom validation logic.
    """
    def validate_input_dependency(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dependency function for input validation."""
        validator = SecurityInputValidator()

        # Validate all string values in the input data
        for key, value in input_data.items():
            if isinstance(value, str):
                input_type = "email" if "email" in key.lower() else "general"
                result = validator.validate_input(value, input_type)

                if not result["is_valid"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Input validation failed for '{key}': {', '.join(result['violations'])}"
                    )

                # Replace with sanitized input
                input_data[key] = result["sanitized_input"]

        return input_data

    return validate_input_dependency


# Validation decorators for specific use cases
def validate_policy_input(func):
    """Decorator for policy-related endpoints."""
    async def wrapper(*args, **kwargs):
        # Extract request data from kwargs
        for key, value in kwargs.items():
            if hasattr(value, 'dict'):  # Pydantic model
                data = value.dict()
                for field_name, field_value in data.items():
                    if isinstance(field_value, str):
                        input_type = "description" if field_name in ["content", "description", "text"] else "general"
                        result = security_validator.validate_input(field_value, input_type)
                        if not result["is_valid"]:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Policy input validation failed for '{field_name}': {', '.join(result['violations'])}"
                            )

        return await func(*args, **kwargs)
    return wrapper


def validate_governance_input(func):
    """Decorator for governance workflow endpoints."""
    async def wrapper(*args, **kwargs):
        # Extract request data from kwargs
        for key, value in kwargs.items():
            if hasattr(value, 'dict'):  # Pydantic model
                data = value.dict()
                for field_name, field_value in data.items():
                    if isinstance(field_value, str):
                        input_type = "description" if field_name in ["reasoning", "justification", "rationale"] else "general"
                        result = security_validator.validate_input(field_value, input_type)
                        if not result["is_valid"]:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Governance input validation failed for '{field_name}': {', '.join(result['violations'])}"
                            )

        return await func(*args, **kwargs)
    return wrapper

def sanitize_user_input(input_data: str, input_type: str = "general") -> str:
    """
    Main function for sanitizing user input.
    
    Args:
        input_data: The input to sanitize
        input_type: Type of input for context-specific sanitization
        
    Returns:
        Sanitized input string
    """
    return security_validator.sanitize_input(input_data, input_type)
