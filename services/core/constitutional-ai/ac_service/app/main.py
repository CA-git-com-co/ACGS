"""
Constitutional AI Service - Refactored Main Module
Constitutional Hash: cdd01ef066bc6cf2

This is the refactored main module for the Constitutional AI service,
breaking down the 1,790-line monolithic file into manageable components.

Architecture:
- api/endpoints.py: REST API endpoints
- validation/core.py: Core validation logic
- config/app_config.py: Application configuration and setup
- compliance/: Compliance calculation modules
- framework/: Framework integration modules
"""

import logging

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

# Create application using refactored configuration
# Import optimized constitutional middleware
from services.shared.middleware.constitutional_validation import (
    setup_constitutional_validation,
)

from .config.app_config import create_constitutional_ai_app

# Create the FastAPI app
app = create_constitutional_ai_app()

# Setup optimized constitutional validation middleware
setup_constitutional_validation(
    app=app,
    service_name="constitutional-ai",
    performance_target_ms=0.5,  # Optimized target
    enable_strict_validation=True,
)

# Constitutional compliance logging
logger.info("✅ Optimized constitutional middleware enabled for constitutional-ai")
logger.info("📋 Constitutional Hash: cdd01ef066bc6cf2")
logger.info("🎯 Performance Target: <0.5ms validation")


# Setup API endpoints
from .api.endpoints import setup_api_endpoints

api_endpoints = setup_api_endpoints(app)

# Setup service discovery
from services.shared.middleware.service_discovery_middleware import (
    setup_service_discovery,
)

setup_service_discovery(
    app=app,
    service_name="constitutional-ai",
    service_version="1.0.0",
    capabilities=[
        "constitutional_validation",
        "hash_verification",
        "compliance_scoring",
        "policy_enforcement",
        "audit_logging",
    ],
    heartbeat_interval=15,
    metadata={
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "service_type": "core",
        "compliance_level": "constitutional",
    },
)

# Setup cache optimization
from services.shared.middleware.cache_optimization_middleware import (
    setup_cache_optimization,
)

setup_cache_optimization(
    app=app,
    service_name="constitutional-ai",
    cache_enabled=True,
    cache_paths={
        "/health": {"ttl": 60, "data_type": "health_check", "cache_method": ["GET"]},
        "/constitutional/compliance": {
            "ttl": 1800,  # 30 minutes - constitutional data is stable
            "data_type": "constitutional_hash",
            "cache_method": ["GET"],
        },
        "/validation": {
            "ttl": 900,  # 15 minutes - validation results
            "data_type": "validation_results",
            "cache_method": ["GET", "POST"],
        },
        "/compliance/score": {
            "ttl": 600,  # 10 minutes - compliance scoring
            "data_type": "compliance_checks",
            "cache_method": ["GET", "POST"],
        },
    },
    default_ttl=300,
)


# Add constitutional compliance validation to startup
@app.on_event("startup")
async def validate_constitutional_integrity():
    """Validate constitutional integrity on startup."""
    logger.info("Validating constitutional integrity...")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Validate that all modules maintain constitutional compliance
    from .validation.core import ConstitutionalValidator

    validator = ConstitutionalValidator()
    hash_validation = validator.validate_constitutional_hash()

    if not hash_validation["is_valid"]:
        raise Exception(f"Constitutional hash validation failed: {hash_validation}")

    logger.info("✅ Constitutional integrity validated successfully")


# Export app for uvicorn
__all__ = ["app"]

if __name__ == "__main__":
    import sys
    from pathlib import Path

    import uvicorn

    # Add shared config path
    shared_path = (
        Path(__file__).parent.parent.parent.parent.parent / "services" / "shared"
    )
    sys.path.insert(0, str(shared_path))

    from config.infrastructure_config import get_acgs_config

    # Use standardized port from ACGS config
    config = get_acgs_config()

    uvicorn.run(
        "main_refactored:app",
        host="0.0.0.0",
        port=config.CONSTITUTIONAL_AI_PORT,
        reload=True,
        log_level="info",
    )
