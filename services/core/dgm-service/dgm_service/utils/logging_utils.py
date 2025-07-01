"""
Logging utilities for DGM Service.

Provides centralized logging configuration, log management,
and specialized loggers for different components.
"""

import logging
import logging.config
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ..config import settings


class LogManager:
    """
    Centralized log management for DGM Service.

    Handles logging configuration, log directory setup,
    and provides specialized loggers for different components.
    """

    def __init__(self):
        self.log_dir = Path("/var/log/dgm-service")
        self.config_loaded = False
        self._loggers: dict[str, logging.Logger] = {}

    def setup_logging(self, config_path: str | None = None) -> None:
        """
        Set up logging configuration.

        Args:
            config_path: Path to logging configuration file
        """
        if self.config_loaded:
            return

        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Load logging configuration
        if config_path is None:
            config_path = (
                Path(__file__).parent.parent.parent / "config" / "logging.yaml"
            )

        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)

            # Apply environment-specific overrides
            env = getattr(settings, "ENVIRONMENT", "development").lower()
            if env in config:
                self._apply_env_overrides(config, config[env])

            # Configure logging
            logging.config.dictConfig(config)
            self.config_loaded = True

            # Log successful setup
            logger = logging.getLogger("dgm_service.logging")
            logger.info(f"Logging configured successfully for environment: {env}")

        except Exception as e:
            # Fallback to basic configuration
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
                handlers=[
                    logging.StreamHandler(sys.stdout),
                    logging.FileHandler(self.log_dir / "dgm-service.log"),
                ],
            )
            logger = logging.getLogger("dgm_service.logging")
            logger.error(f"Failed to load logging configuration: {e}")
            logger.info("Using fallback logging configuration")

    def _apply_env_overrides(
        self, base_config: dict[str, Any], env_config: dict[str, Any]
    ) -> None:
        """Apply environment-specific configuration overrides."""
        if "loggers" in env_config:
            for logger_name, logger_config in env_config["loggers"].items():
                if logger_name in base_config.get("loggers", {}):
                    base_config["loggers"][logger_name].update(logger_config)
                else:
                    base_config.setdefault("loggers", {})[logger_name] = logger_config

        if "root" in env_config:
            base_config.setdefault("root", {}).update(env_config["root"])

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance.

        Args:
            name: Logger name

        Returns:
            Logger instance
        """
        if not self.config_loaded:
            self.setup_logging()

        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)

        return self._loggers[name]

    def get_component_logger(self, component: str) -> logging.Logger:
        """
        Get a logger for a specific DGM component.

        Args:
            component: Component name (e.g., 'core', 'api', 'database')

        Returns:
            Logger instance
        """
        return self.get_logger(f"dgm_service.{component}")

    def log_structured(
        self,
        logger: logging.Logger,
        level: int,
        message: str,
        extra: dict[str, Any] | None = None,
        **kwargs,
    ) -> None:
        """
        Log a structured message with additional context.

        Args:
            logger: Logger instance
            level: Log level
            message: Log message
            extra: Additional context data
            **kwargs: Additional keyword arguments
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": "dgm-service",
            "environment": getattr(settings, "ENVIRONMENT", "development"),
            **(extra or {}),
            **kwargs,
        }

        logger.log(level, message, extra=log_data)

    def log_improvement_event(
        self,
        improvement_id: str,
        event_type: str,
        message: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Log DGM improvement events."""
        logger = self.get_component_logger("core")
        self.log_structured(
            logger,
            logging.INFO,
            message,
            extra={
                "event_type": "dgm_improvement",
                "improvement_id": improvement_id,
                "improvement_event_type": event_type,
                **(extra or {}),
            },
        )

    def log_constitutional_event(
        self,
        validation_id: str,
        principle: str,
        compliance_score: float,
        violations: list,
        message: str,
    ) -> None:
        """Log constitutional compliance events."""
        logger = self.get_component_logger("constitutional")
        level = logging.INFO if compliance_score >= 0.95 else logging.WARNING

        self.log_structured(
            logger,
            level,
            message,
            extra={
                "event_type": "constitutional_compliance",
                "validation_id": validation_id,
                "principle": principle,
                "compliance_score": compliance_score,
                "violations": violations,
                "compliant": compliance_score >= 0.95,
            },
        )

    def log_performance_event(
        self,
        metric_name: str,
        metric_value: float,
        threshold: float | None = None,
        message: str = "",
    ) -> None:
        """Log performance events."""
        logger = self.get_component_logger("performance")

        self.log_structured(
            logger,
            logging.INFO,
            message or f"Performance metric: {metric_name} = {metric_value}",
            extra={
                "event_type": "performance_metric",
                "metric_name": metric_name,
                "metric_value": metric_value,
                "threshold": threshold,
                "threshold_exceeded": threshold and metric_value > threshold,
            },
        )

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        user_id: str | None = None,
        resource_id: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Log security events."""
        logger = self.get_component_logger("security")
        level = getattr(logging, severity.upper(), logging.INFO)

        self.log_structured(
            logger,
            level,
            message,
            extra={
                "event_type": event_type,
                "severity": severity,
                "user_id": user_id,
                "resource_id": resource_id,
                **(extra or {}),
            },
        )

    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        request_id: str,
        user_id: str | None = None,
    ) -> None:
        """Log API requests."""
        logger = self.get_component_logger("api")

        self.log_structured(
            logger,
            logging.INFO,
            f"{method} {path} - {status_code}",
            extra={
                "event_type": "api_request",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "request_id": request_id,
                "user_id": user_id,
            },
        )

    def log_database_operation(
        self,
        operation: str,
        table: str,
        duration_ms: float,
        rows_affected: int | None = None,
        error: str | None = None,
    ) -> None:
        """Log database operations."""
        logger = self.get_component_logger("database")
        level = logging.ERROR if error else logging.INFO

        message = f"Database {operation} on {table}"
        if error:
            message += f" failed: {error}"

        self.log_structured(
            logger,
            level,
            message,
            extra={
                "event_type": "database_operation",
                "operation": operation,
                "table": table,
                "duration_ms": duration_ms,
                "rows_affected": rows_affected,
                "error": error,
            },
        )

    def cleanup_old_logs(self, days: int = 30) -> None:
        """
        Clean up old log files.

        Args:
            days: Number of days to keep logs
        """
        logger = self.get_logger("dgm_service.logging")
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)

        cleaned_count = 0
        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete old log file {log_file}: {e}")

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old log files")


# Global log manager instance
log_manager = LogManager()


# Convenience functions
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return log_manager.get_logger(name)


def get_component_logger(component: str) -> logging.Logger:
    """Get a component-specific logger."""
    return log_manager.get_component_logger(component)


def setup_logging(config_path: str | None = None) -> None:
    """Set up logging configuration."""
    log_manager.setup_logging(config_path)
