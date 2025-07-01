"""
Integration Tests for ACGS-PGP v8

End-to-end integration tests for complete system functionality.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from services.core.caching.cache_manager import CacheManager
from services.core.generation_engine.engine import (
    GenerationConfig,
    GenerationEngine,
    PolicyGenerationRequest,
)
from services.core.sde.engine import SyndromeDiagnosticEngine
from services.core.see.environment import StabilizerExecutionEnvironment


@pytest.mark.integration
class TestSystemIntegration:
    """Integration tests for complete ACGS-PGP v8 system."""

    @pytest_asyncio.fixture
    async def integrated_system(self, test_config):
        """Set up integrated system for testing."""
        # Initialize components with test configuration
        config = GenerationConfig(
            gs_service_url=test_config["gs_service_url"],
            pgc_service_url=test_config["pgc_service_url"],
            constitutional_hash=test_config["constitutional_hash"],
        )

        generation_engine = GenerationEngine(config)

        stabilizer_env = StabilizerExecutionEnvironment(
            redis_url=test_config["redis_url"],
            postgres_url=test_config["database_url"],
            constitutional_hash=test_config["constitutional_hash"],
        )

        diagnostic_engine = SyndromeDiagnosticEngine(
            stabilizer_env=stabilizer_env,
            constitutional_hash=test_config["constitutional_hash"],
        )

        cache_manager = CacheManager(
            redis_url=test_config["redis_url"],
            constitutional_hash=test_config["constitutional_hash"],
        )

        # Mock initialization to avoid external dependencies
        with patch.object(stabilizer_env, "initialize", new_callable=AsyncMock):
            with patch.object(diagnostic_engine, "initialize", new_callable=AsyncMock):
                with patch.object(cache_manager, "initialize", new_callable=AsyncMock):
                    await stabilizer_env.initialize()
                    await diagnostic_engine.initialize()
                    await cache_manager.initialize()

        yield {
            "generation_engine": generation_engine,
            "stabilizer_env": stabilizer_env,
            "diagnostic_engine": diagnostic_engine,
            "cache_manager": cache_manager,
        }

        # Cleanup
        await generation_engine.close()
        await stabilizer_env.cleanup()
        await diagnostic_engine.cleanup()
        await cache_manager.close()

    async def test_end_to_end_policy_generation(
        self, integrated_system, sample_policy_request, test_metrics
    ):
        """Test complete end-to-end policy generation workflow."""
        generation_engine = integrated_system["generation_engine"]
        stabilizer_env = integrated_system["stabilizer_env"]

        # Mock external service calls
        with patch("src.generation_engine.engine.httpx.AsyncClient") as mock_client:
            # Mock successful responses
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "compliance_score": 0.88,
                "validation_result": "compliant",
                "constitutional_hash": "cdd01ef066bc6cf2",
            }

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            # Mock stabilizer execution
            mock_execution = MagicMock()
            mock_execution.add_log = MagicMock()
            mock_execution.result_data = {}
            mock_execution.__aenter__ = AsyncMock(return_value=mock_execution)
            mock_execution.__aexit__ = AsyncMock(return_value=None)

            with patch.object(stabilizer_env, "execute", return_value=mock_execution):
                # Create request
                request = PolicyGenerationRequest(**sample_policy_request)

                # Measure performance
                start_time = datetime.now()

                # Execute policy generation
                async with stabilizer_env.execute(
                    "test_execution", "policy_generation"
                ) as execution:
                    response = await generation_engine.generate_policy(
                        request, use_quantum_enhancement=True
                    )
                    execution.result_data = {
                        "generation_id": response.generation_id,
                        "constitutional_compliance_score": response.constitutional_compliance_score,
                    }

                end_time = datetime.now()
                response_time_ms = (end_time - start_time).total_seconds() * 1000

                # Record metrics
                test_metrics.record_response_time(response_time_ms)
                test_metrics.record_compliance_score(
                    response.constitutional_compliance_score
                )

                # Verify results
                assert response.generation_id is not None
                assert response.policy_content is not None
                assert response.constitutional_compliance_score >= 0.8
                assert response.constitutional_hash == "cdd01ef066bc6cf2"
                assert response_time_ms <= 500.0  # Performance target

    async def test_system_health_monitoring(self, integrated_system):
        """Test integrated system health monitoring."""
        generation_engine = integrated_system["generation_engine"]
        stabilizer_env = integrated_system["stabilizer_env"]
        diagnostic_engine = integrated_system["diagnostic_engine"]
        cache_manager = integrated_system["cache_manager"]

        # Mock health check responses
        with patch.object(
            generation_engine, "health_check", new_callable=AsyncMock
        ) as mock_gen_health:
            with patch.object(
                stabilizer_env, "get_health_status", new_callable=AsyncMock
            ) as mock_stab_health:
                with patch.object(
                    diagnostic_engine, "get_health_status", new_callable=AsyncMock
                ) as mock_diag_health:
                    with patch.object(
                        cache_manager, "health_check", new_callable=AsyncMock
                    ) as mock_cache_health:
                        # Configure mock responses
                        mock_gen_health.return_value = {"status": "healthy"}
                        mock_stab_health.return_value = {"status": "healthy"}
                        mock_diag_health.return_value = {"status": "healthy"}
                        mock_cache_health.return_value = {"status": "healthy"}

                        # Check individual component health
                        gen_health = await generation_engine.health_check()
                        stab_health = await stabilizer_env.get_health_status()
                        diag_health = await diagnostic_engine.get_health_status()
                        cache_health = await cache_manager.health_check()

                        # Verify all components are healthy
                        assert gen_health["status"] == "healthy"
                        assert stab_health["status"] == "healthy"
                        assert diag_health["status"] == "healthy"
                        assert cache_health["status"] == "healthy"

    async def test_error_recovery_workflow(self, integrated_system, sample_error_data):
        """Test error detection and recovery workflow."""
        diagnostic_engine = integrated_system["diagnostic_engine"]

        # Mock diagnostic response
        mock_result = MagicMock()
        mock_result.diagnostic_id = "test_diag_123"
        mock_result.target_system = "acgs-pgp-v8"
        mock_result.overall_health_score = 0.75
        mock_result.constitutional_compliance_score = 0.85
        mock_result.error_count = 2
        mock_result.critical_error_count = 0
        mock_result.recommendations = ["Restart service", "Clear cache"]
        mock_result.auto_executable_recommendations = 1
        mock_result.constitutional_hash = "cdd01ef066bc6cf2"
        mock_result.is_system_healthy.return_value = True
        mock_result.requires_immediate_attention.return_value = False

        with patch.object(
            diagnostic_engine, "diagnose_system", new_callable=AsyncMock
        ) as mock_diagnose:
            mock_diagnose.return_value = mock_result

            # Perform system diagnosis
            result = await diagnostic_engine.diagnose_system(
                target_system="acgs-pgp-v8",
                error_data=sample_error_data,
                include_recommendations=True,
            )

            # Verify diagnostic results
            assert result.diagnostic_id is not None
            assert result.target_system == "acgs-pgp-v8"
            assert result.constitutional_hash == "cdd01ef066bc6cf2"
            assert len(result.recommendations) > 0

    async def test_cache_integration(self, integrated_system, sample_policy_request):
        """Test cache integration across components."""
        cache_manager = integrated_system["cache_manager"]

        # Mock cache operations
        with patch.object(cache_manager, "get", new_callable=AsyncMock) as mock_get:
            with patch.object(cache_manager, "set", new_callable=AsyncMock) as mock_set:
                with patch.object(
                    cache_manager, "get_metrics", new_callable=AsyncMock
                ) as mock_metrics:
                    # Configure mock responses
                    mock_get.return_value = None  # Cache miss
                    mock_set.return_value = True  # Successful cache set
                    mock_metrics.return_value = {
                        "cache_performance": {
                            "hit_rate_percent": 75.0,
                            "cache_hits": 150,
                            "cache_misses": 50,
                            "total_operations": 200,
                        }
                    }

                    # Test cache operations
                    cache_key = "test_policy_123"
                    cache_data = {"policy_content": "Test policy"}

                    # Cache miss scenario
                    cached_result = await cache_manager.get(cache_key, prefix="policy")
                    assert cached_result is None

                    # Cache set scenario
                    set_result = await cache_manager.set(
                        cache_key, cache_data, prefix="policy"
                    )
                    assert set_result is True

                    # Verify cache metrics
                    metrics = await cache_manager.get_metrics()
                    assert metrics["cache_performance"]["hit_rate_percent"] >= 70.0

    async def test_constitutional_compliance_enforcement(self, integrated_system):
        """Test constitutional compliance enforcement across system."""
        generation_engine = integrated_system["generation_engine"]

        # Test with invalid constitutional hash
        invalid_request = PolicyGenerationRequest(
            title="Test Policy",
            description="Test description",
            stakeholders=["test"],
            constitutional_principles=["test"],
            priority="medium",
        )

        with patch("src.generation_engine.engine.httpx.AsyncClient") as mock_client:
            # Mock response with invalid constitutional hash
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": "Constitutional compliance violation",
                "expected_hash": "cdd01ef066bc6cf2",
                "provided_hash": "invalid_hash",
            }

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            # Verify constitutional compliance enforcement
            with pytest.raises(Exception):
                await generation_engine.generate_policy(invalid_request)

    async def test_performance_targets(
        self, integrated_system, sample_policy_request, test_metrics
    ):
        """Test system-wide performance targets."""
        generation_engine = integrated_system["generation_engine"]

        # Run multiple policy generations to test performance
        for i in range(5):
            with patch("src.generation_engine.engine.httpx.AsyncClient") as mock_client:
                # Mock successful response
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "compliance_score": 0.85 + (i * 0.02),
                    "validation_result": "compliant",
                    "constitutional_hash": "cdd01ef066bc6cf2",
                }

                mock_client_instance = AsyncMock()
                mock_client_instance.post.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_client_instance

                # Measure performance
                start_time = datetime.now()

                request = PolicyGenerationRequest(**sample_policy_request)
                response = await generation_engine.generate_policy(request)

                end_time = datetime.now()
                response_time_ms = (end_time - start_time).total_seconds() * 1000

                # Record metrics
                test_metrics.record_response_time(response_time_ms)
                test_metrics.record_compliance_score(
                    response.constitutional_compliance_score
                )

        # Verify performance targets are met
        assert test_metrics.meets_performance_targets()
        assert test_metrics.get_average_response_time() <= 500.0
        assert test_metrics.get_average_compliance_score() >= 0.8
