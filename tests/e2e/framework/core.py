"""
ACGS E2E Test Framework Core

Main framework class that orchestrates end-to-end testing with support for
different testing modes and comprehensive validation capabilities.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type, Union
from datetime import datetime

from .config import E2ETestConfig, E2ETestMode, ServiceType
from .base import BaseE2ETest, E2ETestResult
from .mocks import MockServiceManager
from .utils import TestEnvironmentManager


logger = logging.getLogger(__name__)


class E2ETestFramework:
    """
    Main framework for ACGS end-to-end testing.
    
    Provides comprehensive testing capabilities including:
    - Service health validation
    - Constitutional compliance testing
    - Performance benchmarking
    - Security testing
    - Multi-agent coordination testing
    """
    
    def __init__(self, config: Optional[E2ETestConfig] = None):
        self.config = config or E2ETestConfig.from_environment()
        self.mock_manager: Optional[MockServiceManager] = None
        self.env_manager = TestEnvironmentManager(self.config)
        self.test_registry: Dict[str, Type[BaseE2ETest]] = {}
        self.results: List[E2ETestResult] = []
        
        # Setup logging
        self._setup_logging()
        
        logger.info(f"Initialized E2E Test Framework in {self.config.test_mode} mode")
        logger.info(f"Constitutional hash: {self.config.constitutional_hash}")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = logging.DEBUG if self.config.debug_mode else logging.INFO
        
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Reduce noise from external libraries
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    async def initialize(self):
        """Initialize the test framework."""
        logger.info("Initializing E2E Test Framework...")
        
        # Setup test environment
        await self.env_manager.setup()
        
        # Initialize mock services if needed
        if self.config.test_mode in [E2ETestMode.OFFLINE, E2ETestMode.HYBRID]:
            self.mock_manager = MockServiceManager(self.config)
            await self.mock_manager.start()
            logger.info("Mock services started")
        
        # Validate infrastructure
        await self._validate_infrastructure()
        
        logger.info("E2E Test Framework initialized successfully")
    
    async def cleanup(self):
        """Cleanup test framework resources."""
        logger.info("Cleaning up E2E Test Framework...")
        
        if self.mock_manager:
            await self.mock_manager.stop()
            logger.info("Mock services stopped")
        
        await self.env_manager.cleanup()
        
        logger.info("E2E Test Framework cleanup completed")
    
    async def _validate_infrastructure(self):
        """Validate required infrastructure components."""
        logger.info("Validating infrastructure components...")
        
        if self.config.test_mode == E2ETestMode.ONLINE:
            # Check live services
            for service_type in ServiceType:
                if self.config.is_service_enabled(service_type):
                    service = self.config.services[service_type]
                    logger.info(f"Checking {service_type.value} service at {service.url}")
                    
                    # Health check would go here
                    # For now, just log the configuration
        
        logger.info("Infrastructure validation completed")
    
    def register_test(self, test_class: Type[BaseE2ETest], name: Optional[str] = None):
        """Register a test class."""
        test_name = name or test_class.__name__
        self.test_registry[test_name] = test_class
        logger.debug(f"Registered test: {test_name}")
    
    async def run_test(self, test_name: str) -> List[E2ETestResult]:
        """Run a specific test by name."""
        if test_name not in self.test_registry:
            raise ValueError(f"Test '{test_name}' not found in registry")
        
        test_class = self.test_registry[test_name]
        test_instance = test_class(self.config)
        
        logger.info(f"Running test: {test_name}")
        
        try:
            results = await test_instance.execute()
            self.results.extend(results)
            
            success_count = sum(1 for r in results if r.success)
            logger.info(f"Test {test_name} completed: {success_count}/{len(results)} passed")
            
            return results
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            error_result = E2ETestResult(
                test_name=test_name,
                success=False,
                duration_ms=0.0,
                error_message=str(e)
            )
            self.results.append(error_result)
            return [error_result]
    
    async def run_all_tests(self) -> List[E2ETestResult]:
        """Run all registered tests."""
        logger.info(f"Running {len(self.test_registry)} registered tests...")
        
        all_results = []
        
        for test_name in self.test_registry:
            results = await self.run_test(test_name)
            all_results.extend(results)
        
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.success)
        
        logger.info(f"All tests completed: {passed_tests}/{total_tests} passed")
        
        return all_results
    
    async def run_test_suite(self, test_names: List[str]) -> List[E2ETestResult]:
        """Run a specific suite of tests."""
        logger.info(f"Running test suite with {len(test_names)} tests...")
        
        all_results = []
        
        for test_name in test_names:
            results = await self.run_test(test_name)
            all_results.extend(results)
        
        return all_results
    
    def get_test_summary(self) -> Dict[str, Union[int, float]]:
        """Get summary of test results."""
        if not self.results:
            return {}
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r.duration_ms for r in self.results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        constitutional_tests = [r for r in self.results if r.constitutional_compliance is not None]
        constitutional_compliance_rate = (
            sum(1 for r in constitutional_tests if r.constitutional_compliance) / len(constitutional_tests)
            if constitutional_tests else 0
        )
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "total_duration_ms": total_duration,
            "average_duration_ms": avg_duration,
            "constitutional_compliance_rate": constitutional_compliance_rate,
        }
    
    async def validate_performance_targets(self) -> bool:
        """Validate that performance targets are met across all tests."""
        performance_results = [
            r for r in self.results 
            if r.performance_metrics is not None
        ]
        
        if not performance_results:
            logger.warning("No performance metrics available for validation")
            return True
        
        targets = self.config.performance
        violations = []
        
        for result in performance_results:
            metrics = result.performance_metrics
            
            if metrics.get("latency_p99_ms", 0) > targets.p99_latency_ms:
                violations.append(f"{result.test_name}: P99 latency exceeded")
            
            if metrics.get("success_rate", 1.0) < targets.success_rate:
                violations.append(f"{result.test_name}: Success rate below target")
            
            cache_hit_rate = metrics.get("cache_hit_rate")
            if cache_hit_rate is not None and cache_hit_rate < targets.cache_hit_rate:
                violations.append(f"{result.test_name}: Cache hit rate below target")
        
        if violations:
            logger.error(f"Performance target violations: {violations}")
            return False
        
        logger.info("All performance targets met")
        return True
    
    async def validate_constitutional_compliance(self) -> bool:
        """Validate constitutional compliance across all tests."""
        constitutional_results = [
            r for r in self.results 
            if r.constitutional_compliance is not None
        ]
        
        if not constitutional_results:
            logger.warning("No constitutional compliance data available")
            return True
        
        failed_compliance = [
            r for r in constitutional_results 
            if not r.constitutional_compliance
        ]
        
        if failed_compliance:
            logger.error(f"Constitutional compliance failures: {[r.test_name for r in failed_compliance]}")
            return False
        
        logger.info("All tests passed constitutional compliance")
        return True
    
    def export_results(self, output_path: Path):
        """Export test results to file."""
        import json
        
        summary = self.get_test_summary()
        
        export_data = {
            "framework_version": "1.0.0",
            "test_mode": self.config.test_mode,
            "constitutional_hash": self.config.constitutional_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": summary,
            "results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "error_message": r.error_message,
                    "performance_metrics": r.performance_metrics,
                    "constitutional_compliance": r.constitutional_compliance,
                }
                for r in self.results
            ]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Test results exported to {output_path}")


# Convenience function for quick testing
async def run_quick_validation(config: Optional[E2ETestConfig] = None) -> bool:
    """Run quick validation of ACGS system."""
    framework = E2ETestFramework(config)
    
    try:
        await framework.initialize()
        
        # Register basic validation tests
        from ..tests.health import HealthCheckTest
        from ..tests.constitutional import BasicConstitutionalTest
        
        framework.register_test(HealthCheckTest, "health_check")
        framework.register_test(BasicConstitutionalTest, "constitutional_basic")
        
        # Run tests
        results = await framework.run_all_tests()
        
        # Validate results
        performance_ok = await framework.validate_performance_targets()
        constitutional_ok = await framework.validate_constitutional_compliance()
        
        return performance_ok and constitutional_ok
        
    finally:
        await framework.cleanup()
