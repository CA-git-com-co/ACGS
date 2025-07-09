#!/usr/bin/env python3
"""
ACGS-1 API Versioning Components Validation Script

Validates the core versioning system components without requiring
all services to be running. Tests the versioning middleware,
managers, and compatibility systems directly.
"""

import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services" / "shared"))


@dataclass
class ValidationResult:
    """Result of a validation test."""

    component: str
    test_name: str
    success: bool
    message: str
    details: dict[str, Any] | None = None


class VersioningComponentValidator:
    """
    Validates ACGS-1 API versioning system components.

    Tests core functionality without requiring running services:
    - Version manager functionality
    - Compatibility manager
    - Response transformers
    - Middleware components
    - Deprecation mechanisms
    """

    def __init__(self):
        self.results: list[ValidationResult] = []
        self.components_available = self._check_component_availability()

    def _check_component_availability(self) -> dict[str, bool]:
        """Check which versioning components are available for testing."""
        components = {}

        try:
            from services.shared.versioning.version_manager import (
                APIVersion,
                VersionManager,
            )

            components["version_manager"] = True
            logger.info("✅ Version Manager components available")
        except ImportError as e:
            components["version_manager"] = False
            logger.warning(f"⚠️ Version Manager not available: {e}")

        try:
            from services.shared.versioning.compatibility_manager import (
                CompatibilityManager,
            )

            components["compatibility_manager"] = True
            logger.info("✅ Compatibility Manager available")
        except ImportError as e:
            components["compatibility_manager"] = False
            logger.warning(f"⚠️ Compatibility Manager not available: {e}")

        try:
            from services.shared.versioning.response_transformers import (
                VersionedResponseBuilder,
            )

            components["response_transformers"] = True
            logger.info("✅ Response Transformers available")
        except ImportError as e:
            components["response_transformers"] = False
            logger.warning(f"⚠️ Response Transformers not available: {e}")

        try:
            from services.shared.middleware.version_routing_middleware import (
                VersionRoutingMiddleware,
            )

            components["middleware"] = True
            logger.info("✅ Version Routing Middleware available")
        except ImportError as e:
            components["middleware"] = False
            logger.warning(f"⚠️ Version Routing Middleware not available: {e}")

        return components

    def validate_version_manager(self) -> list[ValidationResult]:
        """Validate version manager functionality."""
        results = []

        if not self.components_available.get("version_manager"):
            results.append(
                ValidationResult(
                    component="VersionManager",
                    test_name="Component Availability",
                    success=False,
                    message="Version Manager components not available",
                )
            )
            return results

        try:
            from services.shared.versioning.version_manager import (
                APIVersion,
                VersionManager,
            )

            # Test APIVersion creation and parsing
            try:
                version = APIVersion.from_string("v1.2.3")
                assert version.major == 1
                assert version.minor == 2
                assert version.patch == 3

                results.append(
                    ValidationResult(
                        component="VersionManager",
                        test_name="APIVersion Parsing",
                        success=True,
                        message="APIVersion parsing works correctly",
                        details={"parsed_version": str(version)},
                    )
                )
            except Exception as e:
                results.append(
                    ValidationResult(
                        component="VersionManager",
                        test_name="APIVersion Parsing",
                        success=False,
                        message=f"APIVersion parsing failed: {e}",
                    )
                )

            # Test VersionManager initialization
            try:
                manager = VersionManager("test-service", "v1.0.0")
                assert manager.service_name == "test-service"
                assert str(manager.current_version) == "v1.0.0"

                results.append(
                    ValidationResult(
                        component="VersionManager",
                        test_name="Manager Initialization",
                        success=True,
                        message="VersionManager initializes correctly",
                        details={"service_name": manager.service_name},
                    )
                )
            except Exception as e:
                results.append(
                    ValidationResult(
                        component="VersionManager",
                        test_name="Manager Initialization",
                        success=False,
                        message=f"VersionManager initialization failed: {e}",
                    )
                )

            # Test version registration
            try:
                manager = VersionManager("test-service", "v1.0.0")
                compatibility = manager.register_version("v1.1.0")
                assert "v1.1.0" in manager.supported_versions

                results.append(
                    ValidationResult(
                        component="VersionManager",
                        test_name="Version Registration",
                        success=True,
                        message="Version registration works correctly",
                        details={
                            "registered_versions": list(
                                manager.supported_versions.keys()
                            )
                        },
                    )
                )
            except Exception as e:
                results.append(
                    ValidationResult(
                        component="VersionManager",
                        test_name="Version Registration",
                        success=False,
                        message=f"Version registration failed: {e}",
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    component="VersionManager",
                    test_name="General Functionality",
                    success=False,
                    message=f"Version Manager validation failed: {e}",
                )
            )

        return results

    def validate_compatibility_manager(self) -> list[ValidationResult]:
        """Validate compatibility manager functionality."""
        results = []

        if not self.components_available.get("compatibility_manager"):
            results.append(
                ValidationResult(
                    component="CompatibilityManager",
                    test_name="Component Availability",
                    success=False,
                    message="Compatibility Manager components not available",
                )
            )
            return results

        try:
            from services.shared.versioning.compatibility_manager import (
                CompatibilityManager,
            )

            # Test CompatibilityManager initialization
            try:
                manager = CompatibilityManager("test-service")
                assert manager.service_name == "test-service"
                assert manager.deprecation_period_days == 180  # 6 months
                assert manager.max_concurrent_versions == 2

                results.append(
                    ValidationResult(
                        component="CompatibilityManager",
                        test_name="Manager Initialization",
                        success=True,
                        message="CompatibilityManager initializes with correct defaults",
                        details={
                            "service_name": manager.service_name,
                            "deprecation_period": manager.deprecation_period_days,
                            "max_versions": manager.max_concurrent_versions,
                        },
                    )
                )
            except Exception as e:
                results.append(
                    ValidationResult(
                        component="CompatibilityManager",
                        test_name="Manager Initialization",
                        success=False,
                        message=f"CompatibilityManager initialization failed: {e}",
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    component="CompatibilityManager",
                    test_name="General Functionality",
                    success=False,
                    message=f"Compatibility Manager validation failed: {e}",
                )
            )

        return results

    def validate_response_transformers(self) -> list[ValidationResult]:
        """Validate response transformer functionality."""
        results = []

        if not self.components_available.get("response_transformers"):
            results.append(
                ValidationResult(
                    component="ResponseTransformers",
                    test_name="Component Availability",
                    success=False,
                    message="Response Transformers components not available",
                )
            )
            return results

        try:
            from services.shared.versioning.response_transformers import (
                VersionedResponseBuilder,
            )

            # Test VersionedResponseBuilder initialization
            try:
                builder = VersionedResponseBuilder("test-service")
                assert builder is not None
                assert builder.service_name == "test-service"

                results.append(
                    ValidationResult(
                        component="ResponseTransformers",
                        test_name="Builder Initialization",
                        success=True,
                        message="VersionedResponseBuilder initializes correctly",
                    )
                )
            except Exception as e:
                results.append(
                    ValidationResult(
                        component="ResponseTransformers",
                        test_name="Builder Initialization",
                        success=False,
                        message=f"VersionedResponseBuilder initialization failed: {e}",
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    component="ResponseTransformers",
                    test_name="General Functionality",
                    success=False,
                    message=f"Response Transformers validation failed: {e}",
                )
            )

        return results

    async def run_all_validations(self) -> dict[str, Any]:
        """Run all validation tests."""
        logger.info("🔍 Starting ACGS-1 API Versioning Components Validation...")

        start_time = datetime.now(timezone.utc)

        # Run component validations
        self.results.extend(self.validate_version_manager())
        self.results.extend(self.validate_compatibility_manager())
        self.results.extend(self.validate_response_transformers())

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        # Generate summary
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - successful_tests

        # Group results by component
        component_results = {}
        for result in self.results:
            if result.component not in component_results:
                component_results[result.component] = {
                    "passed": 0,
                    "failed": 0,
                    "tests": [],
                }

            if result.success:
                component_results[result.component]["passed"] += 1
            else:
                component_results[result.component]["failed"] += 1

            component_results[result.component]["tests"].append(
                {
                    "test_name": result.test_name,
                    "success": result.success,
                    "message": result.message,
                    "details": result.details,
                }
            )

        report = {
            "validation_summary": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": round(duration, 2),
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (
                    round((successful_tests / total_tests) * 100, 1)
                    if total_tests > 0
                    else 0
                ),
            },
            "component_availability": self.components_available,
            "component_results": component_results,
            "success_criteria": {
                "core_components_available": sum(self.components_available.values())
                >= 3,
                "all_tests_passed": failed_tests == 0,
                "version_manager_functional": any(
                    r.component == "VersionManager" and r.success for r in self.results
                ),
            },
        }

        logger.info(f"✅ Validation completed in {duration:.2f}s")
        return report


async def main():
    """Main function to run versioning components validation."""
    validator = VersioningComponentValidator()

    # Run validation tests
    report = await validator.run_all_validations()

    # Save report
    output_path = Path(
        "docs/implementation/reports/versioning_components_validation.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 80)
    print("ACGS-1 API VERSIONING COMPONENTS VALIDATION SUMMARY")
    print("=" * 80)

    summary = report["validation_summary"]
    print(f"📊 Total Tests: {summary['total_tests']}")
    print(f"✅ Successful: {summary['successful_tests']}")
    print(f"❌ Failed: {summary['failed_tests']}")
    print(f"📈 Success Rate: {summary['success_rate']}%")
    print(f"⏱️  Duration: {summary['duration_seconds']}s")

    print("\n🧩 COMPONENT AVAILABILITY:")
    for component, available in report["component_availability"].items():
        status = "✅ Available" if available else "❌ Not Available"
        print(f"   {component}: {status}")

    print("\n🎯 SUCCESS CRITERIA:")
    criteria = report["success_criteria"]
    for criterion, passed in criteria.items():
        status = "PASS" if passed else "FAIL"
        print(f"   {criterion}: {status}")

    if report["validation_summary"]["failed_tests"] > 0:
        print("\n⚠️  FAILED TESTS:")
        for component, results in report["component_results"].items():
            for test in results["tests"]:
                if not test["success"]:
                    print(f"   - {component}: {test['test_name']} - {test['message']}")

    print("\n" + "=" * 80)
    print(f"📄 Full report saved to: {output_path}")

    # Return exit code based on success criteria
    all_criteria_passed = all(criteria.values())
    return 0 if all_criteria_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
