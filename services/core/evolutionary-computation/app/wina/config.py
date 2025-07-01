"""
WINA Configuration Management

Provides configuration loading and management for WINA optimization components.
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_WINA_CONFIG = {
    "optimization_level": "advanced",
    "monitoring_level": "comprehensive",
    "learning_rate": 0.01,
    "performance_targets": {
        "max_response_time_ms": 100,
        "min_throughput_ops_per_sec": 150,
        "max_error_rate_percent": 2.0,
        "min_compliance_score": 0.90,
    },
    "gating": {"strategy": "adaptive", "threshold": 0.7, "fallback_enabled": True},
    "constitutional": {
        "hash": "cdd01ef066bc6cf2",
        "compliance_threshold": 0.95,
        "enforcement_mode": "strict",
    },
    "neural_optimization": {
        "gflops_reduction_target": 0.5,
        "accuracy_preservation_threshold": 0.95,
        "adaptive_weights": True,
    },
}

DEFAULT_INTEGRATION_CONFIG = {
    "service_endpoints": {
        "gs_service": "http://localhost:8004",
        "pgc_service": "http://localhost:8005",
        "ac_service": "http://localhost:8001",
    },
    "data_pipeline": {
        "batch_size": 100,
        "update_frequency_seconds": 30,
        "buffer_size": 1000,
    },
    "monitoring": {
        "metrics_collection_interval": 10,
        "health_check_interval": 60,
        "alert_thresholds": {
            "response_time_ms": 200,
            "error_rate": 0.05,
            "compliance_score": 0.85,
        },
    },
}


def load_wina_config_from_env() -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Load WINA configuration from environment variables with fallback to defaults.

    Returns:
        Tuple of (wina_config, integration_config)
    """
    try:
        wina_config = DEFAULT_WINA_CONFIG.copy()
        integration_config = DEFAULT_INTEGRATION_CONFIG.copy()

        # Override with environment variables if present
        if os.getenv("WINA_OPTIMIZATION_LEVEL"):
            wina_config["optimization_level"] = os.getenv("WINA_OPTIMIZATION_LEVEL")

        if os.getenv("WINA_LEARNING_RATE"):
            wina_config["learning_rate"] = float(os.getenv("WINA_LEARNING_RATE"))

        if os.getenv("WINA_GFLOPS_REDUCTION_TARGET"):
            wina_config["neural_optimization"]["gflops_reduction_target"] = float(
                os.getenv("WINA_GFLOPS_REDUCTION_TARGET")
            )

        # Service endpoint overrides
        if os.getenv("GS_SERVICE_URL"):
            integration_config["service_endpoints"]["gs_service"] = os.getenv(
                "GS_SERVICE_URL"
            )

        if os.getenv("PGC_SERVICE_URL"):
            integration_config["service_endpoints"]["pgc_service"] = os.getenv(
                "PGC_SERVICE_URL"
            )

        if os.getenv("AC_SERVICE_URL"):
            integration_config["service_endpoints"]["ac_service"] = os.getenv(
                "AC_SERVICE_URL"
            )

        # Constitutional hash override
        if os.getenv("CONSTITUTIONAL_HASH"):
            wina_config["constitutional"]["hash"] = os.getenv("CONSTITUTIONAL_HASH")

        logger.info("WINA configuration loaded successfully")
        return wina_config, integration_config

    except Exception as e:
        logger.error(f"Failed to load WINA configuration: {e}")
        logger.info("Using default WINA configuration")
        return DEFAULT_WINA_CONFIG.copy(), DEFAULT_INTEGRATION_CONFIG.copy()


def validate_wina_config(config: dict[str, Any]) -> bool:
    """
    Validate WINA configuration for required fields and valid values.

    Args:
        config: WINA configuration dictionary

    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        required_fields = [
            "optimization_level",
            "monitoring_level",
            "learning_rate",
            "performance_targets",
        ]

        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required WINA config field: {field}")
                return False

        # Validate learning rate
        if not 0.001 <= config["learning_rate"] <= 0.1:
            logger.error(f"Invalid learning rate: {config['learning_rate']}")
            return False

        # Validate performance targets
        targets = config["performance_targets"]
        if targets["min_compliance_score"] < 0.8:
            logger.error("Minimum compliance score must be >= 0.8")
            return False

        logger.info("WINA configuration validation passed")
        return True

    except Exception as e:
        logger.error(f"WINA configuration validation failed: {e}")
        return False


def get_wina_config_summary(config: dict[str, Any]) -> dict[str, Any]:
    """
    Get a summary of WINA configuration for logging/monitoring.

    Args:
        config: WINA configuration dictionary

    Returns:
        Configuration summary
    """
    return {
        "optimization_level": config.get("optimization_level"),
        "monitoring_level": config.get("monitoring_level"),
        "learning_rate": config.get("learning_rate"),
        "gflops_reduction_target": config.get("neural_optimization", {}).get(
            "gflops_reduction_target"
        ),
        "compliance_threshold": config.get("constitutional", {}).get(
            "compliance_threshold"
        ),
        "constitutional_hash": config.get("constitutional", {}).get("hash"),
    }
