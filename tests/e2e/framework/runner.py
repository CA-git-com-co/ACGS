"""
ACGS E2E Test Runner

Provides test execution orchestration with support for parallel execution,
test discovery, filtering, and comprehensive result collection.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Type, Union, Callable, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import importlib
import inspect

from .config import E2ETestConfig, E2ETestMode
from .base import BaseE2ETest, E2ETestResult
from .core import E2ETestFramework
from .utils import TestReportGenerator


logger = logging.getLogger(__name__)


@dataclass
class TestFilter:
    """Test filtering criteria."""
    include_patterns: List[str] = None
    exclude_patterns: List[str] = None
    test_types: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        self.include_patterns = self.include_patterns or []
        self.exclude_patterns = self.exclude_patterns or []
        self.test_types = self.test_types or []
        self.tags = self.tags or []


@dataclass
class TestExecutionPlan:
    """Test execution plan."""
    test_classes: List[Type[BaseE2ETest]]
    execution_order: List[str]
    parallel_groups: List[List[str]]
    estimated_duration_seconds: float


class E2ETestRunner:
    """
    Main test runner for ACGS E2E tests.
    
    Provides comprehensive test execution capabilities including:
    - Test discovery and registration
    - Parallel test execution
    - Test filtering and selection
    - Result collection and reporting
    - Performance monitoring
    """
    
    def __init__(self, config: Optional[E2ETestConfig] = None):
        self.config = config or E2ETestConfig.from_environment()
        self.framework = E2ETestFramework(self.config)
        self.test_filter: Optional[TestFilter] = None
        self.execution_plan: Optional[TestExecutionPlan] = None
        self.results: List[E2ETestResult] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # Test discovery
        self.discovered_tests: Dict[str, Type[BaseE2ETest]] = {}
        
        # Reporting
        self.report_generator = TestReportGenerator(self.config.report_directory)
    
    async def discover_tests(self, test_directories: Optional[List[Path]] = None) -> Dict[str, Type[BaseE2ETest]]:
        """Discover test classes in specified directories."""
        if test_directories is None:
            test_directories = [
                self.config.project_root / "tests" / "e2e" / "tests",
                self.config.project_root / "tests" / "e2e" / "suites"
            ]
        
        discovered = {}
        
        for test_dir in test_directories:
            if not test_dir.exists():
                logger.warning(f"Test directory not found: {test_dir}")
                continue
            
            logger.info(f"Discovering tests in: {test_dir}")
            
            # Find all Python files
            for py_file in test_dir.rglob("*.py"):
                if py_file.name.startswith("test_") or py_file.name.endswith("_test.py"):
                    await self._discover_tests_in_file(py_file, discovered)
        
        self.discovered_tests = discovered
        logger.info(f"Discovered {len(discovered)} test classes")
        
        return discovered
    
    async def _discover_tests_in_file(self, py_file: Path, discovered: Dict[str, Type[BaseE2ETest]]):
        """Discover test classes in a Python file."""
        try:
            # Convert file path to module name
            relative_path = py_file.relative_to(self.config.project_root)
            module_name = str(relative_path.with_suffix("")).replace("/", ".")
            
            # Import module
            module = importlib.import_module(module_name)
            
            # Find test classes
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseE2ETest) and 
                    obj != BaseE2ETest):
                    
                    test_name = f"{module_name}.{name}"
                    discovered[test_name] = obj
                    logger.debug(f"Discovered test class: {test_name}")
        
        except Exception as e:
            logger.warning(f"Failed to discover tests in {py_file}: {e}")
    
    def apply_filter(self, test_filter: TestFilter):
        """Apply test filter to discovered tests."""
        self.test_filter = test_filter
        
        if not self.discovered_tests:
            logger.warning("No tests discovered to filter")
            return
        
        filtered_tests = {}
        
        for test_name, test_class in self.discovered_tests.items():
            # Check include patterns
            if test_filter.include_patterns:
                if not any(pattern in test_name for pattern in test_filter.include_patterns):
                    continue
            
            # Check exclude patterns
            if test_filter.exclude_patterns:
                if any(pattern in test_name for pattern in test_filter.exclude_patterns):
                    continue
            
            # Check test types
            if test_filter.test_types:
                test_type = getattr(test_class, 'test_type', 'unknown')
                if test_type not in test_filter.test_types:
                    continue
            
            # Check tags
            if test_filter.tags:
                test_tags = getattr(test_class, 'tags', [])
                if not any(tag in test_tags for tag in test_filter.tags):
                    continue
            
            filtered_tests[test_name] = test_class
        
        logger.info(f"Filtered tests: {len(filtered_tests)}/{len(self.discovered_tests)}")
        
        # Update framework registry
        self.framework.test_registry.clear()
        for test_name, test_class in filtered_tests.items():
            self.framework.register_test(test_class, test_name)
    
    def create_execution_plan(self) -> TestExecutionPlan:
        """Create test execution plan with parallelization strategy."""
        test_classes = list(self.framework.test_registry.values())
        test_names = list(self.framework.test_registry.keys())
        
        # Simple execution order (can be enhanced with dependency analysis)
        execution_order = test_names.copy()
        
        # Create parallel groups based on test types
        parallel_groups = []
        current_group = []
        
        for test_name in execution_order:
            test_class = self.framework.test_registry[test_name]
            test_type = getattr(test_class, 'test_type', 'default')
            
            # Group tests by type for parallel execution
            if len(current_group) < self.config.parallel_workers:
                current_group.append(test_name)
            else:
                parallel_groups.append(current_group)
                current_group = [test_name]
        
        if current_group:
            parallel_groups.append(current_group)
        
        # Estimate duration (rough estimate)
        estimated_duration = len(test_names) * 30  # 30 seconds per test average
        
        self.execution_plan = TestExecutionPlan(
            test_classes=test_classes,
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            estimated_duration_seconds=estimated_duration
        )
        
        logger.info(f"Created execution plan: {len(test_names)} tests in {len(parallel_groups)} groups")
        
        return self.execution_plan
    
    async def run_tests(self, test_names: Optional[List[str]] = None) -> List[E2ETestResult]:
        """Run specified tests or all registered tests."""
        self.start_time = time.time()
        
        try:
            # Initialize framework
            await self.framework.initialize()
            
            # Run tests
            if test_names:
                results = await self.framework.run_test_suite(test_names)
            else:
                results = await self.framework.run_all_tests()
            
            self.results = results
            
            return results
        
        finally:
            self.end_time = time.time()
            await self.framework.cleanup()
    
    async def run_parallel_tests(self) -> List[E2ETestResult]:
        """Run tests in parallel according to execution plan."""
        if not self.execution_plan:
            self.create_execution_plan()
        
        self.start_time = time.time()
        all_results = []
        
        try:
            await self.framework.initialize()
            
            # Execute parallel groups
            for group_idx, test_group in enumerate(self.execution_plan.parallel_groups):
                logger.info(f"Executing test group {group_idx + 1}/{len(self.execution_plan.parallel_groups)}")
                
                # Run tests in group concurrently
                tasks = [
                    self.framework.run_test(test_name)
                    for test_name in test_group
                ]
                
                group_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for test_name, result in zip(test_group, group_results):
                    if isinstance(result, Exception):
                        error_result = E2ETestResult(
                            test_name=test_name,
                            success=False,
                            duration_ms=0.0,
                            error_message=str(result)
                        )
                        all_results.append(error_result)
                    else:
                        all_results.extend(result)
            
            self.results = all_results
            return all_results
        
        finally:
            self.end_time = time.time()
            await self.framework.cleanup()
    
    async def run_smoke_tests(self) -> List[E2ETestResult]:
        """Run quick smoke tests for basic validation."""
        smoke_filter = TestFilter(tags=["smoke"])
        self.apply_filter(smoke_filter)
        
        return await self.run_tests()
    
    async def run_performance_tests(self) -> List[E2ETestResult]:
        """Run performance-focused tests."""
        perf_filter = TestFilter(test_types=["performance"])
        self.apply_filter(perf_filter)
        
        return await self.run_tests()
    
    async def run_security_tests(self) -> List[E2ETestResult]:
        """Run security-focused tests."""
        security_filter = TestFilter(test_types=["security"])
        self.apply_filter(security_filter)
        
        return await self.run_tests()
    
    def generate_reports(self) -> Dict[str, Path]:
        """Generate comprehensive test reports."""
        if not self.results:
            logger.warning("No test results available for reporting")
            return {}
        
        # Convert results to dict format for reporting
        results_data = [
            {
                "test_name": r.test_name,
                "success": r.success,
                "duration_ms": r.duration_ms,
                "error_message": r.error_message,
                "constitutional_compliance": r.constitutional_compliance,
                "performance_metrics": r.performance_metrics
            }
            for r in self.results
        ]
        
        # Generate summary
        summary = self.framework.get_test_summary()
        
        # Generate reports
        reports = {}
        
        # JUnit XML
        if self.config.junit_xml_path:
            junit_path = self.report_generator.generate_junit_xml(results_data)
            reports["junit"] = junit_path
        
        # HTML Report
        html_path = self.report_generator.generate_html_report(results_data, summary)
        reports["html"] = html_path
        
        # JSON Report
        json_path = self.config.report_directory / "results.json"
        self.framework.export_results(json_path)
        reports["json"] = json_path
        
        logger.info(f"Generated reports: {list(reports.keys())}")
        
        return reports
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary with timing and performance data."""
        if not self.start_time or not self.end_time:
            return {}
        
        total_duration = self.end_time - self.start_time
        
        summary = {
            "execution_time_seconds": total_duration,
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r.success),
            "failed_tests": sum(1 for r in self.results if not r.success),
            "test_mode": self.config.test_mode,
            "constitutional_hash": self.config.constitutional_hash,
            "parallel_workers": self.config.parallel_workers
        }
        
        if self.results:
            summary.update(self.framework.get_test_summary())
        
        return summary


# Convenience functions for common test execution patterns
async def run_quick_validation(config: Optional[E2ETestConfig] = None) -> bool:
    """Run quick validation tests."""
    runner = E2ETestRunner(config)
    
    # Discover and run smoke tests
    await runner.discover_tests()
    results = await runner.run_smoke_tests()
    
    # Generate reports
    runner.generate_reports()
    
    # Check if all tests passed
    return all(r.success for r in results)


async def run_full_test_suite(config: Optional[E2ETestConfig] = None) -> Dict[str, Any]:
    """Run complete test suite with reporting."""
    runner = E2ETestRunner(config)
    
    # Discover all tests
    await runner.discover_tests()
    
    # Create execution plan
    runner.create_execution_plan()
    
    # Run tests in parallel
    results = await runner.run_parallel_tests()
    
    # Generate reports
    reports = runner.generate_reports()
    
    # Get summary
    summary = runner.get_execution_summary()
    summary["reports"] = reports
    
    return summary
