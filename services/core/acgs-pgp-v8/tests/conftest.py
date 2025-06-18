"""
Pytest Configuration and Fixtures for ACGS-PGP v8 Tests

Provides shared fixtures and test configuration for all test modules.
"""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from services.core.caching.cache_manager import CacheManager
from services.core.caching.diagnostic_cache import DiagnosticDataCache
from services.core.caching.execution_cache import ExecutionResultCache
from services.core.caching.policy_cache import PolicyGenerationCache
from services.core.generation_engine.engine import GenerationEngine
from services.core.sde.engine import SyndromeDiagnosticEngine
from services.core.see.environment import StabilizerExecutionEnvironment

from . import SAMPLE_ERROR_DATA, SAMPLE_POLICY_REQUEST, get_test_config


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config() -> dict[str, Any]:
    """Provide test configuration."""
    return get_test_config()


@pytest.fixture
def sample_policy_request() -> dict[str, Any]:
    """Provide sample policy generation request."""
    return SAMPLE_POLICY_REQUEST.copy()


@pytest.fixture
def sample_error_data() -> dict[str, Any]:
    """Provide sample error data for testing."""
    return SAMPLE_ERROR_DATA.copy()


@pytest_asyncio.fixture
async def mock_cache_manager() -> AsyncGenerator[CacheManager, None]:
    """Provide mock cache manager for testing."""
    cache_manager = MagicMock(spec=CacheManager)
    cache_manager.constitutional_hash = "cdd01ef066bc6cf2"
    cache_manager.initialize = AsyncMock()
    cache_manager.get = AsyncMock(return_value=None)
    cache_manager.set = AsyncMock(return_value=True)
    cache_manager.delete = AsyncMock(return_value=True)
    cache_manager.exists = AsyncMock(return_value=False)
    cache_manager.health_check = AsyncMock(return_value={"status": "healthy"})
    cache_manager.get_metrics = AsyncMock(
        return_value={
            "cache_performance": {
                "hit_rate_percent": 75.0,
                "cache_hits": 100,
                "cache_misses": 25,
                "total_operations": 125,
            }
        }
    )
    cache_manager.close = AsyncMock()

    yield cache_manager


@pytest_asyncio.fixture
async def mock_generation_engine() -> AsyncGenerator[GenerationEngine, None]:
    """Provide mock generation engine for testing."""
    engine = MagicMock(spec=GenerationEngine)
    engine.health_check = AsyncMock(return_value={"status": "healthy"})
    engine.get_metrics = AsyncMock(return_value={"status": "healthy"})
    engine.generate_policy = AsyncMock(
        return_value=MagicMock(
            generation_id="test_gen_123",
            policy_content="Test policy content",
            constitutional_compliance_score=0.85,
            confidence_score=0.92,
            semantic_hash="abc123def456",
            generation_time_ms=450.0,
            consensus_data={"consensus_achieved": True},
            recommendations=["Test recommendation"],
            constitutional_hash="cdd01ef066bc6cf2",
        )
    )
    engine.close = AsyncMock()

    yield engine


@pytest_asyncio.fixture
async def mock_stabilizer_env() -> AsyncGenerator[StabilizerExecutionEnvironment, None]:
    """Provide mock stabilizer execution environment for testing."""
    env = MagicMock(spec=StabilizerExecutionEnvironment)
    env.initialize = AsyncMock()
    env.get_health_status = AsyncMock(return_value={"status": "healthy"})
    env.get_execution_statistics = MagicMock(return_value={"status": "healthy"})
    env.cleanup = AsyncMock()

    # Mock execution context
    mock_execution = MagicMock()
    mock_execution.add_log = MagicMock()
    mock_execution.result_data = {}
    mock_execution.__aenter__ = AsyncMock(return_value=mock_execution)
    mock_execution.__aexit__ = AsyncMock(return_value=None)

    env.execute = MagicMock(return_value=mock_execution)

    yield env


@pytest_asyncio.fixture
async def mock_diagnostic_engine() -> AsyncGenerator[SyndromeDiagnosticEngine, None]:
    """Provide mock diagnostic engine for testing."""
    engine = MagicMock(spec=SyndromeDiagnosticEngine)
    engine.initialize = AsyncMock()
    engine.get_health_status = AsyncMock(return_value={"status": "healthy"})
    engine.get_metrics = AsyncMock(return_value={"status": "healthy"})
    engine.diagnose_system = AsyncMock(
        return_value=MagicMock(
            diagnostic_id="diag_test_123",
            target_system="acgs-pgp-v8",
            overall_health_score=0.95,
            constitutional_compliance_score=0.88,
            error_count=0,
            critical_error_count=0,
            recommendations=[],
            auto_executable_recommendations=0,
            diagnostic_timestamp=MagicMock(),
            constitutional_hash="cdd01ef066bc6cf2",
            is_system_healthy=MagicMock(return_value=True),
            requires_immediate_attention=MagicMock(return_value=False),
        )
    )
    engine.cleanup = AsyncMock()

    yield engine


@pytest_asyncio.fixture
async def policy_cache(mock_cache_manager) -> PolicyGenerationCache:
    """Provide policy generation cache for testing."""
    return PolicyGenerationCache(mock_cache_manager)


@pytest_asyncio.fixture
async def execution_cache(mock_cache_manager) -> ExecutionResultCache:
    """Provide execution result cache for testing."""
    return ExecutionResultCache(mock_cache_manager)


@pytest_asyncio.fixture
async def diagnostic_cache(mock_cache_manager) -> DiagnosticDataCache:
    """Provide diagnostic data cache for testing."""
    return DiagnosticDataCache(mock_cache_manager)


@pytest.fixture
def mock_jwt_token() -> str:
    """Provide mock JWT token for authentication testing."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoidGVzdF91c2VyIiwicm9sZSI6ImFkbWluIiwiZXhwIjo5OTk5OTk5OTk5fQ.test_signature"


@pytest.fixture
def mock_user_data() -> dict[str, Any]:
    """Provide mock user data for authentication testing."""
    return {
        "user_id": "test_user",
        "role": "admin",
        "permissions": ["policy_generation", "system_diagnosis"],
        "exp": 9999999999,
    }


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.security = pytest.mark.security


# Test utilities
class TestMetrics:
    """Utility class for tracking test performance metrics."""

    def __init__(self):
        self.response_times = []
        self.cache_hit_rates = []
        self.compliance_scores = []

    def record_response_time(self, time_ms: float):
        """Record response time for performance analysis."""
        self.response_times.append(time_ms)

    def record_cache_hit_rate(self, hit_rate: float):
        """Record cache hit rate for performance analysis."""
        self.cache_hit_rates.append(hit_rate)

    def record_compliance_score(self, score: float):
        """Record constitutional compliance score."""
        self.compliance_scores.append(score)

    def get_average_response_time(self) -> float:
        """Get average response time."""
        return (
            sum(self.response_times) / len(self.response_times)
            if self.response_times
            else 0.0
        )

    def get_average_cache_hit_rate(self) -> float:
        """Get average cache hit rate."""
        return (
            sum(self.cache_hit_rates) / len(self.cache_hit_rates)
            if self.cache_hit_rates
            else 0.0
        )

    def get_average_compliance_score(self) -> float:
        """Get average constitutional compliance score."""
        return (
            sum(self.compliance_scores) / len(self.compliance_scores)
            if self.compliance_scores
            else 0.0
        )

    def meets_performance_targets(self) -> bool:
        """Check if performance targets are met."""
        avg_response_time = self.get_average_response_time()
        avg_cache_hit_rate = self.get_average_cache_hit_rate()
        avg_compliance_score = self.get_average_compliance_score()

        return (
            avg_response_time <= 500.0  # <500ms response time
            and avg_cache_hit_rate >= 70.0  # >70% cache hit rate
            and avg_compliance_score >= 0.8  # >80% constitutional compliance
        )


@pytest.fixture
def test_metrics() -> TestMetrics:
    """Provide test metrics tracker."""
    return TestMetrics()
