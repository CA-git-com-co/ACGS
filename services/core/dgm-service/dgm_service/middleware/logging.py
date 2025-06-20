"""
Structured logging middleware for DGM Service.

Provides comprehensive request/response logging, performance tracking,
and integration with centralized logging systems.
"""

import json
import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..config import settings
from ..monitoring.metrics import metrics_collector


class StructuredLogger:
    """
    Structured logger for DGM Service.
    
    Provides JSON-formatted logging with consistent structure,
    correlation IDs, and integration with monitoring systems.
    """
    
    def __init__(self, name: str = "dgm-service"):
        self.logger = logging.getLogger(name)
        self.service_name = "dgm-service"
        self.service_version = "1.0.0"
        self.environment = settings.ENVIRONMENT
    
    def _create_base_context(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create base logging context."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name,
            "version": self.service_version,
            "environment": self.environment,
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "hostname": settings.HOSTNAME,
            "process_id": settings.PROCESS_ID
        }
    
    def info(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Log info level message."""
        context = self._create_base_context(request_id, user_id)
        context.update({
            "level": "INFO",
            "message": message,
            "extra": extra or {}
        })
        self.logger.info(json.dumps(context))
    
    def warning(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Log warning level message."""
        context = self._create_base_context(request_id, user_id)
        context.update({
            "level": "WARNING",
            "message": message,
            "extra": extra or {}
        })
        self.logger.warning(json.dumps(context))
    
    def error(
        self,
        message: str,
        error: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Log error level message."""
        context = self._create_base_context(request_id, user_id)
        context.update({
            "level": "ERROR",
            "message": message,
            "extra": extra or {}
        })
        
        if error:
            context["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": str(error.__traceback__) if error.__traceback__ else None
            }
        
        self.logger.error(json.dumps(context))
    
    def debug(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Log debug level message."""
        context = self._create_base_context(request_id, user_id)
        context.update({
            "level": "DEBUG",
            "message": message,
            "extra": extra or {}
        })
        self.logger.debug(json.dumps(context))
    
    def log_request(
        self,
        request: Request,
        request_id: str,
        user_id: Optional[str] = None
    ):
        """Log incoming HTTP request."""
        context = self._create_base_context(request_id, user_id)
        context.update({
            "level": "INFO",
            "event_type": "http_request",
            "message": f"{request.method} {request.url.path}",
            "http": {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": dict(request.headers),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "content_type": request.headers.get("content-type"),
                "content_length": request.headers.get("content-length")
            }
        })
        self.logger.info(json.dumps(context))
    
    def log_response(
        self,
        request: Request,
        response: Response,
        request_id: str,
        duration_ms: float,
        user_id: Optional[str] = None
    ):
        """Log HTTP response."""
        context = self._create_base_context(request_id, user_id)
        context.update({
            "level": "INFO",
            "event_type": "http_response",
            "message": f"{request.method} {request.url.path} - {response.status_code}",
            "http": {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "status_code": response.status_code,
                "response_time_ms": duration_ms,
                "content_type": response.headers.get("content-type"),
                "content_length": response.headers.get("content-length")
            },
            "performance": {
                "duration_ms": duration_ms,
                "slow_request": duration_ms > 1000  # Mark requests > 1s as slow
            }
        })
        self.logger.info(json.dumps(context))
    
    def log_improvement_event(
        self,
        improvement_id: str,
        event_type: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        """Log DGM improvement events."""
        context = self._create_base_context(request_id)
        context.update({
            "level": "INFO",
            "event_type": "dgm_improvement",
            "message": message,
            "improvement": {
                "improvement_id": improvement_id,
                "event_type": event_type,
                "extra": extra or {}
            }
        })
        self.logger.info(json.dumps(context))
    
    def log_constitutional_event(
        self,
        validation_id: str,
        principle: str,
        compliance_score: float,
        violations: List[str],
        message: str,
        request_id: Optional[str] = None
    ):
        """Log constitutional compliance events."""
        context = self._create_base_context(request_id)
        context.update({
            "level": "INFO" if compliance_score >= 0.95 else "WARNING",
            "event_type": "constitutional_compliance",
            "message": message,
            "constitutional": {
                "validation_id": validation_id,
                "principle": principle,
                "compliance_score": compliance_score,
                "violations": violations,
                "compliant": compliance_score >= 0.95
            }
        })
        self.logger.info(json.dumps(context))
    
    def log_performance_event(
        self,
        metric_name: str,
        metric_value: float,
        threshold: Optional[float] = None,
        message: str = "",
        request_id: Optional[str] = None
    ):
        """Log performance events."""
        context = self._create_base_context(request_id)
        context.update({
            "level": "INFO",
            "event_type": "performance_metric",
            "message": message or f"Performance metric: {metric_name} = {metric_value}",
            "performance": {
                "metric_name": metric_name,
                "metric_value": metric_value,
                "threshold": threshold,
                "threshold_exceeded": threshold and metric_value > threshold
            }
        })
        self.logger.info(json.dumps(context))


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP request/response logging middleware.
    
    Logs all HTTP requests and responses with structured data,
    performance metrics, and correlation IDs.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = StructuredLogger("dgm-service.middleware")
        self.excluded_paths = {
            "/health",
            "/metrics",
            "/favicon.ico"
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process HTTP request and response."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Extract user ID if available
        user_id = None
        if hasattr(request.state, 'user') and request.state.user:
            user_id = getattr(request.state.user, 'id', None)
        
        # Skip logging for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Log incoming request
        start_time = time.time()
        self.logger.log_request(request, request_id, user_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            self.logger.log_response(request, response, request_id, duration_ms, user_id)
            
            # Record metrics
            metrics_collector.record_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration_ms / 1000
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                error=e,
                extra={
                    "duration_ms": duration_ms,
                    "method": request.method,
                    "path": request.url.path
                },
                request_id=request_id,
                user_id=user_id
            )
            
            # Record error metrics
            metrics_collector.record_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=500,
                duration=duration_ms / 1000
            )
            
            raise


# Global structured logger instance
structured_logger = StructuredLogger()
