"""
ACGS Code Analysis Engine - Constitutional Compliance Middleware
Hash validation and constitutional compliance enforcement for all requests/responses.

Constitutional Hash: cdd01ef066bc6cf2
"""

import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.constitutional import (
    CONSTITUTIONAL_HASH, 
    ConstitutionalValidator,
    validate_constitutional_hash,
    get_constitutional_headers
)
from ..utils.logging import security_logger, get_logger

logger = get_logger("middleware.constitutional")


class ConstitutionalComplianceMiddleware(BaseHTTPMiddleware):
    """
    Constitutional compliance middleware for ACGS Code Analysis Engine.
    
    Enforces constitutional hash validation and compliance for all requests and responses.
    """
    
    def __init__(
        self,
        app,
        strict_mode: bool = True,
        bypass_paths: Optional[List[str]] = None,
        enable_request_validation: bool = True,
        enable_response_validation: bool = True
    ):
        """
        Initialize constitutional compliance middleware.
        
        Args:
            app: FastAPI application
            strict_mode: Whether to enforce strict constitutional compliance
            bypass_paths: Paths to bypass constitutional validation
            enable_request_validation: Whether to validate incoming requests
            enable_response_validation: Whether to validate outgoing responses
        """
        super().__init__(app)
        self.strict_mode = strict_mode
        self.bypass_paths = bypass_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
        self.enable_request_validation = enable_request_validation
        self.enable_response_validation = enable_response_validation
        
        # Constitutional validator
        self.validator = ConstitutionalValidator()
        
        # Compliance tracking
        self.compliance_violations = 0
        self.total_validations = 0
        
        logger.info(
            "Constitutional compliance middleware initialized",
            extra={
                "strict_mode": strict_mode,
                "bypass_paths": self.bypass_paths,
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        )
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request through constitutional compliance middleware."""
        start_time = time.time()
        
        try:
            # Check if path should bypass validation
            if self._should_bypass_validation(request.url.path):
                response = await call_next(request)
                self._add_constitutional_headers(response, bypassed=True)
                return response
            
            # Validate incoming request
            if self.enable_request_validation:
                request_validation = await self._validate_request_compliance(request)
                if not request_validation["compliant"] and self.strict_mode:
                    return self._create_compliance_error_response(
                        "Request constitutional compliance validation failed",
                        request_validation["issues"]
                    )
            
            # Process request
            response = await call_next(request)
            
            # Validate outgoing response
            if self.enable_response_validation:
                response_validation = await self._validate_response_compliance(response)
                if not response_validation["compliant"] and self.strict_mode:
                    logger.error(
                        "Response constitutional compliance validation failed",
                        extra={
                            "issues": response_validation["issues"],
                            "constitutional_hash": CONSTITUTIONAL_HASH
                        }
                    )
                    # Don't block response, but log the violation
                    self.compliance_violations += 1
            
            # Add constitutional compliance headers
            self._add_constitutional_headers(response)
            
            # Log compliance validation
            duration_ms = (time.time() - start_time) * 1000
            self._log_compliance_validation(request, response, duration_ms)
            
            self.total_validations += 1
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Constitutional compliance middleware error: {e}",
                extra={
                    "request_path": request.url.path,
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                exc_info=True
            )
            
            if self.strict_mode:
                return self._create_compliance_error_response(
                    "Constitutional compliance validation failed",
                    [f"Internal validation error: {str(e)}"]
                )
            else:
                # In non-strict mode, continue with request but log the error
                response = await call_next(request)
                self._add_constitutional_headers(response, error=str(e))
                return response
    
    def _should_bypass_validation(self, path: str) -> bool:
        """Check if path should bypass constitutional validation."""
        return any(path.startswith(bypass_path) for bypass_path in self.bypass_paths)
    
    async def _validate_request_compliance(self, request: Request) -> Dict[str, Any]:
        """
        Validate constitutional compliance of incoming request.
        
        Args:
            request: HTTP request to validate
            
        Returns:
            dict: Validation result
        """
        validation_result = {
            "compliant": True,
            "issues": [],
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        try:
            # Extract request data for validation
            request_data = {
                "method": request.method,
                "path": request.url.path,
                "headers": dict(request.headers),
                "user_id": getattr(request.state, 'user_id', None),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Check for constitutional hash in headers
            client_hash = request.headers.get("X-Constitutional-Hash")
            if client_hash and not validate_constitutional_hash(client_hash):
                validation_result["compliant"] = False
                validation_result["issues"].append("Invalid constitutional hash in request headers")
            
            # Validate request body if present
            if request.method in ["POST", "PUT", "PATCH"]:
                # Note: We can't easily read the body here without consuming it
                # This would require more complex middleware setup
                pass
            
            # Perform constitutional validation
            compliance_check = self.validator.validate_compliance(request_data)
            if not compliance_check["compliant"]:
                validation_result["compliant"] = False
                validation_result["issues"].extend(compliance_check["issues"])
            
            return validation_result
            
        except Exception as e:
            logger.error(
                f"Request compliance validation error: {e}",
                extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                exc_info=True
            )
            
            validation_result["compliant"] = False
            validation_result["issues"].append(f"Validation error: {str(e)}")
            return validation_result
    
    async def _validate_response_compliance(self, response: Response) -> Dict[str, Any]:
        """
        Validate constitutional compliance of outgoing response.
        
        Args:
            response: HTTP response to validate
            
        Returns:
            dict: Validation result
        """
        validation_result = {
            "compliant": True,
            "issues": [],
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        try:
            # Extract response data for validation
            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Check for constitutional hash in response headers
            response_hash = response.headers.get("X-Constitutional-Hash")
            if not response_hash or not validate_constitutional_hash(response_hash):
                validation_result["compliant"] = False
                validation_result["issues"].append("Missing or invalid constitutional hash in response headers")
            
            # Validate response body if JSON
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                # Note: Reading response body is complex in middleware
                # This would require custom response handling
                pass
            
            # Perform constitutional validation
            compliance_check = self.validator.validate_compliance(response_data)
            if not compliance_check["compliant"]:
                validation_result["compliant"] = False
                validation_result["issues"].extend(compliance_check["issues"])
            
            return validation_result
            
        except Exception as e:
            logger.error(
                f"Response compliance validation error: {e}",
                extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                exc_info=True
            )
            
            validation_result["compliant"] = False
            validation_result["issues"].append(f"Validation error: {str(e)}")
            return validation_result
    
    def _add_constitutional_headers(self, response: Response, bypassed: bool = False, 
                                  error: Optional[str] = None) -> None:
        """Add constitutional compliance headers to response."""
        headers = get_constitutional_headers()
        
        for key, value in headers.items():
            response.headers[key] = value
        
        # Add compliance status
        if bypassed:
            response.headers["X-Constitutional-Status"] = "bypassed"
        elif error:
            response.headers["X-Constitutional-Status"] = "error"
            response.headers["X-Constitutional-Error"] = error
        else:
            response.headers["X-Constitutional-Status"] = "validated"
        
        # Add service identification
        response.headers["X-Service"] = "acgs-code-analysis-engine"
        response.headers["X-Service-Version"] = "1.0.0"
    
    def _create_compliance_error_response(self, message: str, issues: List[str]) -> Response:
        """Create standardized constitutional compliance error response."""
        error_response = {
            "error": "constitutional_compliance_violation",
            "message": message,
            "issues": issues,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "service": "acgs-code-analysis-engine",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Log the violation
        security_logger.log_constitutional_violation(
            violation_type="compliance_validation_failed",
            details={
                "message": message,
                "issues": issues
            }
        )
        
        response = Response(
            content=json.dumps(error_response),
            status_code=status.HTTP_403_FORBIDDEN,
            headers={
                "Content-Type": "application/json",
                **get_constitutional_headers(),
                "X-Constitutional-Status": "violation"
            }
        )
        
        return response
    
    def _log_compliance_validation(self, request: Request, response: Response, duration_ms: float) -> None:
        """Log constitutional compliance validation results."""
        logger.info(
            "Constitutional compliance validation completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "compliance_status": response.headers.get("X-Constitutional-Status", "unknown")
            }
        )
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get constitutional compliance summary."""
        compliance_rate = 1.0
        if self.total_validations > 0:
            compliance_rate = 1.0 - (self.compliance_violations / self.total_validations)
        
        return {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "total_validations": self.total_validations,
            "compliance_violations": self.compliance_violations,
            "compliance_rate": round(compliance_rate, 4),
            "strict_mode": self.strict_mode,
            "validator_version": "1.0.0"
        }
