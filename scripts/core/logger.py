"""
ACGS Logging Utilities
Constitutional Hash: cdd01ef066bc6cf2

Standardized logging functionality for ACGS scripts.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ConstitutionalFormatter(logging.Formatter):
    """Custom formatter that includes constitutional hash in logs."""

    def __init__(self, include_hash: bool = True):
        self.include_hash = include_hash
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with constitutional compliance."""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        # Color coding for different log levels
        colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
        }
        reset_color = "\033[0m"

        color = colors.get(record.levelname, "")

        # Basic log format
        log_parts = [
            f"[{timestamp}]",
            f"{color}[{record.levelname}]{reset_color}",
            f"[{record.name}]",
            record.getMessage(),
        ]

        # Add constitutional hash for important operations
        if self.include_hash and record.levelname in ["WARNING", "ERROR", "CRITICAL"]:
            log_parts.append(f"[Constitutional Hash: {CONSTITUTIONAL_HASH}]")

        return " ".join(log_parts)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


class Logger:
    """Enhanced logger with constitutional compliance features."""

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        format_type: str = "console",  # "console" or "json"
        log_file: Optional[Path] = None,
        include_constitutional_hash: bool = True,
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.include_constitutional_hash = include_constitutional_hash

        # Clear existing handlers
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        if format_type == "json":
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(
                ConstitutionalFormatter(include_constitutional_hash)
            )
        self.logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(JSONFormatter())  # Always use JSON for files
            self.logger.addHandler(file_handler)

    def step(self, step_name: str, message: str, **kwargs):
        """Log a step in a process with constitutional compliance."""
        extra_data = {
            "step": step_name,
            "constitutional_hash": self.constitutional_hash,
            **kwargs,
        }
        self.logger.info(f"🔧 {step_name}: {message}", extra=extra_data)

    def success(self, message: str, **kwargs):
        """Log a successful operation."""
        extra_data = {
            "status": "success",
            "constitutional_hash": self.constitutional_hash,
            **kwargs,
        }
        self.logger.info(f"✅ {message}", extra=extra_data)

    def warning(self, message: str, **kwargs):
        """Log a warning with constitutional context."""
        extra_data = {"constitutional_hash": self.constitutional_hash, **kwargs}
        self.logger.warning(f"⚠️ {message}", extra=extra_data)

    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log an error with constitutional context."""
        extra_data = {"constitutional_hash": self.constitutional_hash, **kwargs}
        if error:
            extra_data["error_type"] = error.__class__.__name__
            extra_data["error_details"] = str(error)

        self.logger.error(f"❌ {message}", extra=extra_data, exc_info=error)

    def performance(self, operation: str, duration_ms: float, **kwargs):
        """Log performance metrics."""
        extra_data = {
            "operation": operation,
            "duration_ms": duration_ms,
            "constitutional_hash": self.constitutional_hash,
            **kwargs,
        }

        if duration_ms > 5000:  # > 5 seconds
            self.logger.warning(
                f"⏱️ Slow operation: {operation} took {duration_ms:.2f}ms",
                extra=extra_data,
            )
        else:
            self.logger.info(
                f"⏱️ {operation} completed in {duration_ms:.2f}ms", extra=extra_data
            )

    def validation_result(
        self,
        validation_type: str,
        passed: bool,
        details: Optional[dict[str, Any]] = None,
    ):
        """Log validation results."""
        extra_data = {
            "validation_type": validation_type,
            "passed": passed,
            "constitutional_hash": self.constitutional_hash,
            **(details or {}),
        }

        if passed:
            self.logger.info(
                f"✅ Validation passed: {validation_type}", extra=extra_data
            )
        else:
            self.logger.error(
                f"❌ Validation failed: {validation_type}", extra=extra_data
            )

    def service_health(
        self,
        service_name: str,
        healthy: bool,
        response_time_ms: Optional[float] = None,
        **kwargs,
    ):
        """Log service health check results."""
        extra_data = {
            "service_name": service_name,
            "healthy": healthy,
            "constitutional_hash": self.constitutional_hash,
            **kwargs,
        }

        if response_time_ms is not None:
            extra_data["response_time_ms"] = response_time_ms

        if healthy:
            self.logger.info(f"💚 Service healthy: {service_name}", extra=extra_data)
        else:
            self.logger.error(f"💔 Service unhealthy: {service_name}", extra=extra_data)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        extra_data = {"constitutional_hash": self.constitutional_hash, **kwargs}
        self.logger.debug(message, extra=extra_data)

    def info(self, message: str, **kwargs):
        """Log info message."""
        extra_data = {"constitutional_hash": self.constitutional_hash, **kwargs}
        self.logger.info(message, extra=extra_data)


# Global logger instance
_logger: Optional[Logger] = None


def get_logger(
    name: Optional[str] = None,
    level: str = "INFO",
    format_type: str = "console",
    log_file: Optional[Path] = None,
) -> Logger:
    """Get a logger instance."""
    global _logger

    if name is None:
        name = "acgs-scripts"

    # For now, create a new logger each time
    # In the future, we could cache loggers by name
    return Logger(name=name, level=level, format_type=format_type, log_file=log_file)


def set_global_logger(logger: Logger) -> None:
    """Set the global logger instance."""
    global _logger
    _logger = logger
