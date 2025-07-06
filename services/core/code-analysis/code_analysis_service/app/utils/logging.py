"""
ACGS Code Analysis Engine - Structured Logging Utilities
Provides constitutional compliance-aware logging with structured output.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import structlog
from pythonjsonlogger import jsonlogger

from .constitutional import CONSTITUTIONAL_HASH


class ConstitutionalLogFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that includes constitutional compliance metadata.
    """

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """Add constitutional compliance fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add constitutional compliance metadata
        log_record["constitutional_hash"] = CONSTITUTIONAL_HASH
        log_record["service"] = "acgs-code-analysis-engine"
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


class PerformanceLogger:
    """
    Logger for performance metrics with constitutional compliance.
    """

    def __init__(self, logger_name: str = "acgs.code_analysis.performance"):
        self.logger = logging.getLogger(logger_name)
        self.start_times: dict[str, float] = {}

    def start_operation(self, operation_id: str, operation_type: str, **kwargs) -> None:
        """Start timing an operation."""
        self.start_times[operation_id] = time.time()

        self.logger.info(
            "Operation started",
            extra={
                "operation_id": operation_id,
                "operation_type": operation_type,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                **kwargs,
            },
        )

    def end_operation(self, operation_id: str, success: bool = True, **kwargs) -> float:
        """End timing an operation and log results."""
        end_time = time.time()
        start_time = self.start_times.pop(operation_id, end_time)
        duration_ms = (end_time - start_time) * 1000

        log_level = logging.INFO if success else logging.ERROR

        self.logger.log(
            log_level,
            "Operation completed",
            extra={
                "operation_id": operation_id,
                "duration_ms": round(duration_ms, 2),
                "success": success,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                **kwargs,
            },
        )

        return duration_ms

    def log_cache_operation(
        self, operation: str, cache_hit: bool, key: str, **kwargs
    ) -> None:
        """Log cache operation with performance metrics."""
        self.logger.info(
            f"Cache {operation}",
            extra={
                "cache_operation": operation,
                "cache_hit": cache_hit,
                "cache_key": key,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                **kwargs,
            },
        )

    def log_database_operation(
        self, operation: str, table: str, duration_ms: float, **kwargs
    ) -> None:
        """Log database operation with performance metrics."""
        self.logger.info(
            f"Database {operation}",
            extra={
                "db_operation": operation,
                "db_table": table,
                "duration_ms": round(duration_ms, 2),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                **kwargs,
            },
        )


class SecurityLogger:
    """
    Logger for security events with constitutional compliance.
    """

    def __init__(self, logger_name: str = "acgs.code_analysis.security"):
        self.logger = logging.getLogger(logger_name)

    def log_authentication_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        success: bool = True,
        **kwargs,
    ) -> None:
        """Log authentication events."""
        log_level = logging.INFO if success else logging.WARNING

        self.logger.log(
            log_level,
            f"Authentication {event_type}",
            extra={
                "security_event": "authentication",
                "event_type": event_type,
                "user_id": user_id,
                "success": success,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                **kwargs,
            },
        )

    def log_authorization_event(
        self,
        event_type: str,
        user_id: str,
        resource: str,
        success: bool = True,
        **kwargs,
    ) -> None:
        """Log authorization events."""
        log_level = logging.INFO if success else logging.WARNING

        self.logger.log(
            log_level,
            f"Authorization {event_type}",
            extra={
                "security_event": "authorization",
                "event_type": event_type,
                "user_id": user_id,
                "resource": resource,
                "success": success,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                **kwargs,
            },
        )

    def log_constitutional_violation(
        self, violation_type: str, details: dict[str, Any], **kwargs
    ) -> None:
        """Log constitutional compliance violations."""
        self.logger.error(
            f"Constitutional violation: {violation_type}",
            extra={
                "security_event": "constitutional_violation",
                "violation_type": violation_type,
                "violation_details": details,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                **kwargs,
            },
        )


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
    enable_console: bool = True,
) -> None:
    """
    Set up structured logging for ACGS Code Analysis Engine.

    Args:
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
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s -"
                " constitutional_hash:%(constitutional_hash)s"
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
        "acgs.code_analysis",
        "acgs.code_analysis.performance",
        "acgs.code_analysis.security",
        "acgs.code_analysis.constitutional",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level.upper()))

    # Log setup completion
    setup_logger = logging.getLogger("acgs.code_analysis.setup")
    setup_logger.info(
        "Logging configured",
        extra={
            "log_level": log_level,
            "log_format": log_format,
            "log_file": log_file,
            "console_enabled": enable_console,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with constitutional compliance metadata.

    Args:
        name: Logger name

    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(f"acgs.code_analysis.{name}")

    # Constitutional hash will be added via the formatter

    return logger


# Global logger instances
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()


def log_api_request(
    method: str,
    path: str,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs,
) -> None:
    """Log API request with constitutional compliance."""
    logger = get_logger("api")
    logger.info(
        f"API request: {method} {path}",
        extra={
            "api_method": method,
            "api_path": path,
            "user_id": user_id,
            "request_id": request_id,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            **kwargs,
        },
    )


def log_api_response(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs,
) -> None:
    """Log API response with constitutional compliance."""
    logger = get_logger("api")
    log_level = logging.INFO if status_code < 400 else logging.WARNING

    logger.log(
        log_level,
        f"API response: {method} {path} - {status_code}",
        extra={
            "api_method": method,
            "api_path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            "user_id": user_id,
            "request_id": request_id,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            **kwargs,
        },
    )
