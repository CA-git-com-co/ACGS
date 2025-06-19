"""
Centralized Test Configuration for ACGS-1 Integration Tests

This module provides:
1. Import path resolution for services with hyphen/underscore naming
2. Mock implementations for missing components
3. Centralized test configuration
4. Service health checking utilities
"""

import asyncio
import importlib
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project root and path setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Service path mappings (handle both hyphen and underscore variants)
SERVICE_PATH_MAPPINGS = {
    "constitutional_ai": [
        "services.core.constitutional_ai.ac_service",
        "services.core.constitutional_ai.ac_service", 
        "constitutional_ai.ac_service",
        "ac_service",
    ],
    "governance_synthesis": [
        "services.core.governance_synthesis.gs_service",
        "services.core.governance_synthesis.gs_service",
        "governance_synthesis.gs_service", 
        "gs_service",
    ],
    "formal_verification": [
        "services.core.formal_verification.fv_service",
        "services.core.formal_verification.fv_service",
        "formal_verification.fv_service",
        "fv_service", 
    ],
    "pgc": [
        "services.platform.pgc.pgc_service",
        "platform.pgc.pgc_service",
        "pgc.pgc_service",
        "pgc_service",
    ],
    "authentication": [
        "services.platform.authentication.auth_service", 
        "platform.authentication.auth_service",
        "authentication.auth_service",
        "auth_service",
    ],
    "integrity": [
        "services.platform.integrity.integrity_service",
        "platform.integrity.integrity_service", 
        "integrity.integrity_service",
        "integrity_service",
    ],
}

# Service port mappings
SERVICE_PORTS = {
    "auth": 8000,
    "ac": 8001, 
    "integrity": 8002,
    "fv": 8003,
    "gs": 8004,
    "pgc": 8005,
    "ec": 8006,
}

# Service URLs
SERVICE_URLS = {name: f"http://localhost:{port}" for name, port in SERVICE_PORTS.items()}


def safe_import(module_paths: list[str], component_name: str = None) -> Any:
    """
    Safely import a module or component, trying multiple paths.
    
    Args:
        module_paths: List of module paths to try
        component_name: Specific component to import from module
        
    Returns:
        Imported module/component or None if all fail
    """
    for module_path in module_paths:
        try:
            module = importlib.import_module(module_path)
            if component_name:
                return getattr(module, component_name, None)
            return module
        except (ImportError, AttributeError) as e:
            logger.debug(f"Failed to import {module_path}: {e}")
            continue
    
    logger.warning(f"Failed to import from any path: {module_paths}")
    return None


def create_mock_service(service_name: str) -> MagicMock:
    """Create a mock service with common methods."""
    mock_service = MagicMock()
    mock_service.health_check = AsyncMock(return_value={"status": "healthy"})
    mock_service.process_request = AsyncMock(return_value={"success": True})
    mock_service.get_metrics = AsyncMock(return_value={"requests": 0, "errors": 0})
    return mock_service


def create_mock_llm_service() -> MagicMock:
    """Create a mock LLM service."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value={
        "content": "Mock LLM response",
        "confidence": 0.95,
        "model": "mock-model"
    })
    mock_llm.validate = AsyncMock(return_value={"valid": True, "score": 0.9})
    return mock_llm


def create_mock_database() -> MagicMock:
    """Create a mock database session."""
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.close = AsyncMock()
    return mock_db


class MockComponents:
    """Container for mock implementations of missing components."""
    
    @staticmethod
    def get_lipschitz_estimator():
        """Mock Lipschitz estimator."""
        mock = MagicMock()
        mock.estimate = AsyncMock(return_value=0.65)
        mock.validate_bounds = AsyncMock(return_value=True)
        return mock
    
    @staticmethod 
    def get_llm_reliability_framework():
        """Mock LLM reliability framework."""
        mock = MagicMock()
        mock.validate_response = AsyncMock(return_value={
            "reliability_score": 0.95,
            "confidence": 0.9,
            "bias_score": 0.1
        })
        return mock
    
    @staticmethod
    def get_constitutional_council_scalability():
        """Mock constitutional council scalability framework."""
        mock = MagicMock()
        mock.process_amendment = AsyncMock(return_value={
            "processed": True,
            "voting_result": "approved",
            "processing_time": 0.5
        })
        return mock
    
    @staticmethod
    def get_adversarial_robustness_tester():
        """Mock adversarial robustness tester."""
        mock = MagicMock()
        mock.test_robustness = AsyncMock(return_value={
            "robustness_score": 0.85,
            "vulnerabilities": [],
            "test_passed": True
        })
        return mock
    
    @staticmethod
    def get_proactive_fairness_generator():
        """Mock proactive fairness generator."""
        mock = MagicMock()
        mock.generate_fair_policy = AsyncMock(return_value={
            "policy": "Mock fair policy",
            "fairness_score": 0.9,
            "bias_metrics": {"demographic": 0.05, "socioeconomic": 0.03}
        })
        return mock


# Test configuration
TEST_CONFIG = {
    "database_url": "sqlite+aiosqlite:///./test_acgs.db",
    "redis_url": "redis://localhost:6379/1", 
    "secret_key": "test-secret-key-for-testing-only",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "testing": True,
    "log_level": "INFO",
    "service_timeout": 30,
    "max_retries": 3,
}


async def check_service_health(service_url: str, timeout: int = 5) -> bool:
    """Check if a service is healthy."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{service_url}/health")
            return response.status_code == 200
    except Exception as e:
        logger.debug(f"Service health check failed for {service_url}: {e}")
        return False


async def wait_for_services(services: list[str], max_wait: int = 30) -> Dict[str, bool]:
    """Wait for services to become available."""
    results = {}
    for service in services:
        if service in SERVICE_URLS:
            url = SERVICE_URLS[service]
            for _ in range(max_wait):
                if await check_service_health(url):
                    results[service] = True
                    break
                await asyncio.sleep(1)
            else:
                results[service] = False
        else:
            results[service] = False
    return results


# Export commonly used fixtures and utilities
__all__ = [
    "safe_import",
    "create_mock_service", 
    "create_mock_llm_service",
    "create_mock_database",
    "MockComponents",
    "TEST_CONFIG",
    "SERVICE_URLS",
    "SERVICE_PORTS",
    "check_service_health",
    "wait_for_services",
    "SERVICE_PATH_MAPPINGS",
]
