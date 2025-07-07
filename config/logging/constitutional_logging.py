"""
ACGS-2 Constitutional Structured Logging Framework
Provides constitutional hash validation and compliance-aware logging.

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
import logging.config
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from pythonjsonlogger import jsonlogger

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ConstitutionalLogFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that includes constitutional compliance metadata.
    """

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add constitutional compliance fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add constitutional compliance metadata
        log_record["chash"] = CONSTITUTIONAL_HASH  # Short key for constitutional hash
        log_record["constitutional_hash"] = CONSTITUTIONAL_HASH
        log_record["service"] = getattr(record, "service", "acgs-service")
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Add request context if available
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id

        # Add performance metrics if available
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms

        if hasattr(record, "cache_hit"):
            log_record["cache_hit"] = record.cache_hit

        # Add constitutional validation context
        if hasattr(record, "constitutional_validation"):
            log_record["constitutional_validation"] = record.constitutional_validation

        # Add operation context
        if hasattr(record, "operation_type"):
            log_record["operation_type"] = record.operation_type

        # Add compliance score if available
        if hasattr(record, "compliance_score"):
            log_record["compliance_score"] = record.compliance_score


class ConstitutionalLogger:
    """
    Constitutional compliance-aware logger for ACGS services.
    """

    def __init__(self, name: str, service_name: str = "acgs-service"):
        self.logger = logging.getLogger(name)
        self.service_name = service_name

    def log_constitutional_validation(
        self,
        level: str,
        message: str,
        validation_result: Dict[str, Any],
        **kwargs
    ) -> None:
        """Log constitutional validation events."""
        extra = {
            "chash": CONSTITUTIONAL_HASH,
            "service": self.service_name,
            "constitutional_validation": validation_result,
            "operation_type": kwargs.get("operation_type", "validation"),
            **kwargs
        }

        self.logger.log(
            getattr(logging, level.upper()),
            f"Constitutional validation: {message}",
            extra=extra
        )

    def info(self, message: str, **kwargs) -> None:
        """Log info message with constitutional context."""
        extra = {
            "chash": CONSTITUTIONAL_HASH,
            "service": self.service_name,
            **kwargs
        }
        self.logger.info(message, extra=extra)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with constitutional context."""
        extra = {
            "chash": CONSTITUTIONAL_HASH,
            "service": self.service_name,
            **kwargs
        }
        self.logger.warning(message, extra=extra)

    def error(self, message: str, **kwargs) -> None:
        """Log error message with constitutional context."""
        extra = {
            "chash": CONSTITUTIONAL_HASH,
            "service": self.service_name,
            **kwargs
        }
        self.logger.error(message, extra=extra)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with constitutional context."""
        extra = {
            "chash": CONSTITUTIONAL_HASH,
            "service": self.service_name,
            **kwargs
        }
        self.logger.critical(message, extra=extra)


class PerformanceLogger:
    """
    Logger for performance metrics with constitutional compliance.
    """

    def __init__(self, service_name: str = "acgs-service"):
        self.logger = ConstitutionalLogger(
            f"acgs.{service_name}.performance", 
            service_name
        )
        self.start_times: Dict[str, float] = {}

    def start_operation(self, operation_id: str, operation_type: str, **kwargs) -> None:
        """Start timing an operation."""
        self.start_times[operation_id] = time.time()

        self.logger.info(
            "Operation started",
            operation_id=operation_id,
            operation_type=operation_type,
            **kwargs
        )

    def end_operation(
        self, 
        operation_id: str, 
        success: bool = True, 
        compliance_score: Optional[float] = None,
        **kwargs
    ) -> float:
        """End timing an operation and log results."""
        end_time = time.time()
        start_time = self.start_times.pop(operation_id, end_time)
        duration_ms = (end_time - start_time) * 1000

        log_level = "info" if success else "error"

        log_kwargs = {
            "operation_id": operation_id,
            "duration_ms": round(duration_ms, 2),
            "success": success,
            **kwargs
        }

        if compliance_score is not None:
            log_kwargs["compliance_score"] = compliance_score

        self.logger.log_constitutional_validation(
            log_level,
            "Operation completed",
            {"operation_success": success, "duration_ms": duration_ms},
            **log_kwargs
        )

        return duration_ms


class SecurityLogger:
    """
    Logger for security events with constitutional compliance.
    """

    def __init__(self, service_name: str = "acgs-service"):
        self.logger = ConstitutionalLogger(
            f"acgs.{service_name}.security", 
            service_name
        )

    def log_authentication_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        success: bool = True,
        **kwargs
    ) -> None:
        """Log authentication events."""
        self.logger.log_constitutional_validation(
            "info" if success else "warning",
            f"Authentication {event_type}",
            {
                "event_type": "authentication",
                "auth_type": event_type,
                "success": success
            },
            user_id=user_id,
            **kwargs
        )

    def log_constitutional_violation(
        self, 
        violation_type: str, 
        details: Dict[str, Any], 
        **kwargs
    ) -> None:
        """Log constitutional compliance violations."""
        self.logger.log_constitutional_validation(
            "error",
            f"Constitutional violation: {violation_type}",
            {
                "violation_type": violation_type,
                "violation_details": details,
                "severity": "critical"
            },
            **kwargs
        )


def setup_constitutional_logging(
    service_name: str,
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
    enable_console: bool = True,
) -> None:
    """
    Set up constitutional structured logging for ACGS services.

    Args:
        service_name: Name of the service
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: Format type (json, text)
        log_file: Optional log file path
        enable_console: Whether to enable console logging
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Set up formatters
    if log_format.lower() == "json":
        formatter = ConstitutionalLogFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            fmt=(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s - "
                "chash:%(constitutional_hash)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set up specific loggers
    loggers = [
        f"acgs.{service_name}",
        f"acgs.{service_name}.performance",
        f"acgs.{service_name}.security",
        f"acgs.{service_name}.constitutional",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level.upper()))

    # Log setup completion
    setup_logger = ConstitutionalLogger(f"acgs.{service_name}.setup", service_name)
    setup_logger.info(
        "Constitutional logging configured",
        log_level=log_level,
        log_format=log_format,
        log_file=log_file,
        console_enabled=enable_console,
    )


def get_constitutional_logger(name: str, service_name: str = "acgs-service") -> ConstitutionalLogger:
    """
    Get a constitutional logger with compliance metadata.

    Args:
        name: Logger name
        service_name: Service name

    Returns:
        ConstitutionalLogger: Configured logger
    """
    return ConstitutionalLogger(f"acgs.{service_name}.{name}", service_name)


# Example usage functions
def log_constitutional_validation_example():
    """Example usage of constitutional validation logging."""
    logger = get_constitutional_logger("validation", "constitutional-ai")
    
    # Log constitutional validation
    logger.info(
        "Constitutional validation", 
        extra={"chash": CONSTITUTIONAL_HASH}
    )
    
    # Log validation with results
    validation_result = {
        "is_valid": True,
        "compliance_score": 0.95,
        "violations": [],
        "constitutional_hash": CONSTITUTIONAL_HASH
    }
    
    logger.log_constitutional_validation(
        "info",
        "Policy validation completed",
        validation_result,
        policy_id="policy_123",
        user_id="user_456"
    )


# Global logger instances for common use cases
def get_performance_logger(service_name: str) -> PerformanceLogger:
    """Get performance logger for a service."""
    return PerformanceLogger(service_name)


def get_security_logger(service_name: str) -> SecurityLogger:
    """Get security logger for a service."""
    return SecurityLogger(service_name)
