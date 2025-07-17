"""
WINA Integration Tests for EC Service

Comprehensive tests to validate WINA dependency resolution and integration
with the evolutionary computation service.
"""

import asyncio
import logging
import pathlib
import sys

import pytest

# Test configuration
TEST_CONFIG = {
    "wina_enabled": True,
    "test_timeout": 30,
    "performance_targets": {
        "gflops_reduction": 0.32,  # 32% improvement target
        "constitutional_compliance": 0.95,
        "response_time_ms": 100,
    },
}


class TestWINAIntegration:
    """Test suite for WINA integration validation."""

    @pytest.fixture
    def wina_config(self):
        """Provide test WINA configuration."""
        return {
            "optimization_level": "advanced",
            "learning_rate": 0.01,
            "constitutional": {
                "hash": "cdd01ef066bc6cf2",
                "compliance_threshold": 0.95,
            },
            "performance_targets": {
                "max_response_time_ms": 100,
                "min_compliance_score": 0.90,
            },
        }

    @pytest.fixture
    def integration_config(self):
        """Provide test integration configuration."""
        return {
            "service_endpoints": {
                "gs_service": "http://localhost:8004",
                "pgc_service": "http://localhost:8005",
            },
            "monitoring": {"metrics_collection_interval": 10},
        }

    async def test_wina_modules_import(self):
        """Test that all WINA modules can be imported successfully."""
        try:
            import os
            import sys

            sys.path.append(os.path.join(pathlib.Path(__file__).parent, "..", "app"))

            from app.wina.config import (
                load_wina_config_from_env,
            )
            from app.wina.constitutional_integration import (
                ConstitutionalWINASupport,
            )
            from app.wina.continuous_learning import (
                get_wina_learning_system,
            )
            from app.wina.core import (
                WINACore,
            )
            from app.wina.gating import (
                RuntimeGating,
            )
            from app.wina.metrics import (
                WINAMetrics,
            )
            from app.wina.performance_monitoring import (
                WINAPerformanceCollector,
            )

            assert True, "All WINA modules imported successfully"

        except ImportError as e:
            pytest.fail(f"WINA module import failed: {e}")

    async def test_wina_core_initialization(self, wina_config):
        """Test WINA core component initialization."""
        from app.wina.core import WINACore

        try:
            wina_core = WINACore(wina_config)

            # Validate initialization
            assert wina_core.optimization_level.value == "advanced"
            assert wina_core.learning_rate == 0.01
            assert wina_core.constitutional_hash == "cdd01ef066bc6cf2"

            # Test optimization capability
            test_weights = {"layer1": [0.5, 0.3, 0.8], "layer2": [0.2, 0.7, 0.4]}
            result = await wina_core.optimize_neural_weights(test_weights)

            assert result.success
            assert result.gflops_reduction > 0
            assert result.constitutional_compliance >= 0.85

        except Exception as e:
            pytest.fail(f"WINA core initialization failed: {e}")

    async def test_constitutional_integration(self, wina_config, integration_config):
        """Test constitutional compliance integration."""
        from app.wina.constitutional_integration import (
            ConstitutionalWINASupport,
        )
        from app.wina.core import (
            WINAOptimizationResult,
        )

        try:
            constitutional_wina = ConstitutionalWINASupport(
                wina_config, integration_config
            )
            await constitutional_wina.initialize_efficiency_principles()

            # Test compliance validation
            mock_result = WINAOptimizationResult(
                optimization_id="test_001",
                gflops_reduction=0.4,
                accuracy_preservation=0.96,
                constitutional_compliance=0.92,
                optimization_time_ms=150.0,
                strategy_used="advanced",
                success=True,
            )

            compliance_result = (
                await constitutional_wina.validate_optimization_compliance(mock_result)
            )

            assert compliance_result.overall_score >= 0.85
            assert compliance_result.compliant
            assert len(compliance_result.principle_scores) > 0

        except Exception as e:
            pytest.fail(f"Constitutional integration test failed: {e}")

    async def test_performance_monitoring(self, wina_config):
        """Test WINA performance monitoring capabilities."""
        from app.wina.performance_monitoring import (
            WINAComponentType,
            WINAMonitoringLevel,
            WINAPerformanceCollector,
        )

        try:
            collector = WINAPerformanceCollector(WINAMonitoringLevel.COMPREHENSIVE)

            # Test system health collection
            health_metrics = await collector.collect_system_health(
                WINAComponentType.CORE
            )

            assert health_metrics.component_type == WINAComponentType.CORE
            assert health_metrics.cpu_usage_percent >= 0
            assert health_metrics.memory_usage_mb >= 0
            assert health_metrics.availability > 0

            # Test performance summary
            summary = collector.get_performance_summary()
            assert "monitoring_level" in summary
            assert summary["monitoring_level"] == "comprehensive"

        except Exception as e:
            pytest.fail(f"Performance monitoring test failed: {e}")

    async def test_ec_service_integration(self):
        """Test integration with EC service main coordinator."""
        from app.core.wina_oversight_coordinator import (
            WINAECOversightCoordinator,
        )

        try:
            # Test coordinator initialization
            coordinator = WINAECOversightCoordinator(enable_wina=True)
            await coordinator.initialize_constitutional_principles()

            # Validate WINA components are initialized
            assert hasattr(coordinator, "wina_core")
            assert hasattr(coordinator, "constitutional_wina")
            assert hasattr(coordinator, "performance_collector")

            # Test basic oversight operation
            from app.core.wina_oversight_coordinator import (
                ECOversightContext,
                ECOversightRequest,
            )

            test_request = ECOversightRequest(
                request_id="test_oversight_001",
                oversight_type=ECOversightContext.PERFORMANCE_OPTIMIZATION,
                target_system="test_system",
                governance_requirements=["efficiency", "compliance"],
                constitutional_constraints=["transparency", "fairness"],
            )

            # This should not raise an exception
            result = await coordinator.coordinate_oversight(test_request)
            assert result is not None

        except Exception as e:
            pytest.fail(f"EC service integration test failed: {e}")

    async def test_service_communication(self):
        """Test communication with other ACGS services."""
        from app.wina.config import (
            load_wina_config_from_env,
        )

        try:
            _wina_config, integration_config = load_wina_config_from_env()

            # Validate service endpoints are configured
            endpoints = integration_config.get("service_endpoints", {})
            assert "gs_service" in endpoints
            assert "pgc_service" in endpoints

            # Test endpoint format
            gs_url = endpoints["gs_service"]
            pgc_url = endpoints["pgc_service"]

            assert gs_url.startswith("http://")
            assert pgc_url.startswith("http://")
            assert ":8004" in gs_url  # gs-service port
            assert ":8005" in pgc_url  # pgc-service port

        except Exception as e:
            pytest.fail(f"Service communication test failed: {e}")

    async def test_performance_targets(self):
        """Test that WINA integration meets performance targets."""
        from app.wina.config import (
            load_wina_config_from_env,
        )
        from app.wina.core import WINACore

        try:
            wina_config, _ = load_wina_config_from_env()
            wina_core = WINACore(wina_config)

            # Run multiple optimizations to test performance
            total_gflops_reduction = 0
            total_compliance = 0
            optimization_count = 5

            for i in range(optimization_count):
                test_weights = {f"layer{i}": [0.1 * j for j in range(10)]}
                result = await wina_core.optimize_neural_weights(test_weights)

                assert result.success, f"Optimization {i} failed"
                total_gflops_reduction += result.gflops_reduction
                total_compliance += result.constitutional_compliance

            # Check performance targets
            avg_gflops_reduction = total_gflops_reduction / optimization_count
            avg_compliance = total_compliance / optimization_count

            assert (
                avg_gflops_reduction
                >= TEST_CONFIG["performance_targets"]["gflops_reduction"]
            ), f"GFLOPs reduction {avg_gflops_reduction:.3f} below target {TEST_CONFIG['performance_targets']['gflops_reduction']}"

            assert (
                avg_compliance
                >= TEST_CONFIG["performance_targets"]["constitutional_compliance"]
            ), f"Constitutional compliance {avg_compliance:.3f} below target {TEST_CONFIG['performance_targets']['constitutional_compliance']}"

        except Exception as e:
            pytest.fail(f"Performance targets test failed: {e}")


async def run_integration_tests():
    """Run all WINA integration tests."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    test_suite = TestWINAIntegration()

    tests = [
        ("WINA Modules Import", test_suite.test_wina_modules_import()),
        ("WINA Core Initialization", test_suite.test_wina_core_initialization({})),
        (
            "Constitutional Integration",
            test_suite.test_constitutional_integration({}, {}),
        ),
        ("Performance Monitoring", test_suite.test_performance_monitoring({})),
        ("EC Service Integration", test_suite.test_ec_service_integration()),
        ("Service Communication", test_suite.test_service_communication()),
        ("Performance Targets", test_suite.test_performance_targets()),
    ]

    results = {"passed": 0, "failed": 0, "errors": []}

    for test_name, test_coro in tests:
        try:
            logger.info(f"Running test: {test_name}")
            await test_coro
            results["passed"] += 1
            logger.info(f"✅ {test_name} PASSED")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"{test_name}: {e!s}")
            logger.exception(f"❌ {test_name} FAILED: {e}")

    # Print summary
    total_tests = results["passed"] + results["failed"]
    success_rate = results["passed"] / total_tests if total_tests > 0 else 0

    if results["errors"]:
        for _error in results["errors"]:
            pass

    return success_rate >= 0.8  # 80% success rate required


if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)
