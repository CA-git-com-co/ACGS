"""
Constitutional Compliance Validator for ACGS-1 Services

Provides fast constitutional compliance validation with <5ms target response time.
Validates all requests against the constitutional framework hash (cdd01ef066bc6cf2).
"""

import logging
import time
from typing import Any, Dict, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ConstitutionalComplianceValidator:
    """
    Lightweight constitutional compliance validator for ACGS-1 services.
    
    Features:
    - Fast validation (<5ms target)
    - Constitutional hash verification (cdd01ef066bc6cf2)
    - Bypass paths for health/metrics endpoints
    - Performance monitoring
    - Graceful degradation
    """
    
    REFERENCE_HASH = "cdd01ef066bc6cf2"
    BYPASS_PATHS = ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
    
    def __init__(
        self,
        service_name: str,
        performance_target_ms: float = 5.0,
        enable_strict_validation: bool = True,
        additional_bypass_paths: Optional[list] = None,
    ):
        self.service_name = service_name
        self.performance_target_ms = performance_target_ms
        self.enable_strict_validation = enable_strict_validation
        self.bypass_paths = self.BYPASS_PATHS.copy()
        
        if additional_bypass_paths:
            self.bypass_paths.extend(additional_bypass_paths)
            
        # Performance metrics
        self.validation_count = 0
        self.validation_failures = 0
        self.avg_validation_time = 0.0
        
        logger.info(f"Constitutional validator initialized for {service_name}")
    
    async def validate_request(self, request: Request) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Fast constitutional compliance validation for incoming requests.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Tuple of (is_valid, error_response_data)
        """
        start_time = time.time()
        
        try:
            # Skip validation for bypass paths
            if request.url.path in self.bypass_paths:
                return True, None
            
            # Extract constitutional hash from headers
            request_hash = request.headers.get("X-Constitutional-Hash")
            
            # Validate constitutional hash
            if self.enable_strict_validation:
                if not request_hash:
                    self.validation_failures += 1
                    return False, {
                        "error": "Constitutional compliance violation",
                        "detail": "Missing X-Constitutional-Hash header",
                        "required_hash": self.REFERENCE_HASH,
                        "service": self.service_name,
                    }
                
                if request_hash != self.REFERENCE_HASH:
                    self.validation_failures += 1
                    return False, {
                        "error": "Constitutional compliance violation", 
                        "detail": "Invalid constitutional hash",
                        "expected_hash": self.REFERENCE_HASH,
                        "provided_hash": request_hash,
                        "service": self.service_name,
                    }
            
            # Validation successful
            return True, None
            
        except Exception as e:
            logger.error(f"Constitutional validation error: {e}")
            self.validation_failures += 1
            
            if self.enable_strict_validation:
                return False, {
                    "error": "Constitutional validation error",
                    "detail": str(e),
                    "service": self.service_name,
                }
            else:
                # Graceful degradation - allow request to proceed
                return True, None
                
        finally:
            # Update performance metrics
            validation_time = (time.time() - start_time) * 1000  # Convert to ms
            self.validation_count += 1
            
            # Update average validation time (exponential moving average)
            alpha = 0.1
            self.avg_validation_time = (alpha * validation_time) + ((1 - alpha) * self.avg_validation_time)
            
            # Log performance warning if target exceeded
            if validation_time > self.performance_target_ms:
                logger.warning(
                    f"Constitutional validation exceeded target: {validation_time:.2f}ms > {self.performance_target_ms}ms"
                )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get constitutional validation metrics."""
        success_rate = (
            (self.validation_count - self.validation_failures) / self.validation_count
            if self.validation_count > 0 else 1.0
        )
        
        return {
            "service": self.service_name,
            "validation_count": self.validation_count,
            "validation_failures": self.validation_failures,
            "success_rate": success_rate,
            "avg_validation_time_ms": self.avg_validation_time,
            "performance_target_ms": self.performance_target_ms,
            "constitutional_hash": self.REFERENCE_HASH,
        }


class ConstitutionalValidationMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for constitutional compliance validation.
    """
    
    def __init__(self, app, service_name: str, **kwargs):
        super().__init__(app)
        self.validator = ConstitutionalComplianceValidator(service_name, **kwargs)
    
    async def dispatch(self, request: Request, call_next):
        """Process request with constitutional validation."""
        # Validate constitutional compliance
        is_valid, error_data = await self.validator.validate_request(request)
        
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content=error_data,
                headers={"X-Constitutional-Validation": "failed"}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add constitutional compliance headers
        response.headers["X-Constitutional-Hash"] = self.validator.REFERENCE_HASH
        response.headers["X-Constitutional-Validation"] = "passed"
        
        return response
