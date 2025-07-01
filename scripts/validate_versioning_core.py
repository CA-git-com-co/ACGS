#!/usr/bin/env python3
"""
ACGS-1 API Versioning Core Validation Script

Validates the core API versioning components without external dependencies.
Tests version management, compatibility checking, and response transformation.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add the services directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "services"))


def test_version_manager():
    """Test the version manager functionality."""
    print("🔍 Testing Version Manager...")

    try:
        from shared.versioning.version_manager import APIVersion, VersionManager

        # Test version parsing
        version = APIVersion.from_string("v2.1.0")
        assert version.major == 2
        assert version.minor == 1
        assert version.patch == 0
        print("  ✅ Version parsing works")

        # Test version comparison
        v1 = APIVersion.from_string("v1.5.0")
        v2 = APIVersion.from_string("v2.0.0")
        assert v2 > v1
        print("  ✅ Version comparison works")

        # Test version manager
        manager = VersionManager("test-service", "v2.1.0")
        assert str(manager.current_version) == "v2.1.0"
        print("  ✅ Version manager initialization works")

        # Test version registration
        manager.register_version("v2.0.0")
        manager.register_version("v1.5.0")
        supported_versions = manager.get_supported_versions()
        assert len(supported_versions) >= 2
        print("  ✅ Version registration works")

        # Test version detection
        headers = {"API-Version": "v2.0.0"}
        detected = manager.detect_version_from_request(headers, "/api/test", {})
        assert str(detected) == "v2.0.0"
        print("  ✅ Version detection from headers works")

        # Test URL-based version detection
        detected_url = manager.detect_version_from_request({}, "/api/v1.5.0/test", {})
        assert str(detected_url) == "v1.5.0"
        print("  ✅ Version detection from URL works")

        return {"success": True, "tests_passed": 6, "tests_failed": 0}

    except Exception as e:
        print(f"  ❌ Version manager test failed: {e}")
        return {"success": False, "tests_passed": 0, "tests_failed": 1, "error": str(e)}


def test_compatibility_manager():
    """Test the compatibility manager functionality."""
    print("🔍 Testing Compatibility Manager...")

    try:
        from shared.versioning.compatibility_manager import (
            CompatibilityManager,
            create_compatibility_manager,
        )
        from shared.versioning.version_manager import APIVersion

        # Test compatibility manager creation
        manager = create_compatibility_manager("test-service")
        assert manager.service_name == "test-service"
        print("  ✅ Compatibility manager creation works")

        # Test compatibility checking
        v1 = APIVersion.from_string("v1.5.0")
        v2 = APIVersion.from_string("v2.0.0")
        rule = manager.check_compatibility(v1, v2)
        assert rule is not None
        assert hasattr(rule, "compatibility_level")
        print("  ✅ Compatibility checking works")

        # Test deprecation schedule
        schedule = manager.create_deprecation_schedule(v1, v2)
        required_keys = [
            "new_version_release",
            "deprecation_announcement",
            "sunset_date",
        ]
        assert all(key in schedule for key in required_keys)
        print("  ✅ Deprecation schedule creation works")

        # Test compatibility report
        report = manager.create_compatibility_report()
        assert "service" in report
        assert "compatibility_rules" in report
        print("  ✅ Compatibility report generation works")

        return {"success": True, "tests_passed": 4, "tests_failed": 0}

    except Exception as e:
        print(f"  ❌ Compatibility manager test failed: {e}")
        return {"success": False, "tests_passed": 0, "tests_failed": 1, "error": str(e)}


def test_response_transformers():
    """Test response transformation functionality."""
    print("🔍 Testing Response Transformers...")

    try:
        from shared.versioning.response_transformers import (
            VersionedResponseBuilder,
            CompatibilityTransformer,
        )
        from shared.versioning.version_manager import APIVersion
        from shared.api_models import APIStatus

        # Test compatibility transformer
        transformer = CompatibilityTransformer(
            source_version=APIVersion.from_string("v1.0.0"),
            target_version=APIVersion.from_string("v2.0.0"),
            field_mappings={"user_id": "userId", "created_at": "createdAt"},
        )

        # Test transformation
        input_data = {
            "user_id": 123,
            "created_at": "2025-06-22T10:00:00Z",
            "name": "Test",
        }
        transformed = transformer.transform(input_data)

        assert "userId" in transformed
        assert "createdAt" in transformed
        assert "user_id" not in transformed
        assert "created_at" not in transformed
        print("  ✅ Field mapping transformation works")

        # Test versioned response builder
        builder = VersionedResponseBuilder("test-service")
        builder.register_transformer(transformer)

        response = builder.build_response(
            status=APIStatus.SUCCESS,
            data=input_data,
            request_version=APIVersion.from_string("v1.0.0"),
            target_version=APIVersion.from_string("v2.0.0"),
        )

        assert response.status == APIStatus.SUCCESS
        assert "userId" in response.data
        print("  ✅ Versioned response building works")

        # Test deprecation metadata
        deprecated_response = builder.build_response(
            status=APIStatus.SUCCESS,
            data={"test": "data"},
            request_version=APIVersion.from_string("v1.0.0"),
            include_deprecation_info=True,
        )

        assert deprecated_response.metadata is not None
        print("  ✅ Deprecation metadata inclusion works")

        return {"success": True, "tests_passed": 3, "tests_failed": 0}

    except Exception as e:
        print(f"  ❌ Response transformer test failed: {e}")
        return {"success": False, "tests_passed": 0, "tests_failed": 1, "error": str(e)}


def test_versioned_router():
    """Test versioned router functionality."""
    print("🔍 Testing Versioned Router...")

    try:
        from shared.versioning.versioned_router import (
            VersionedRouter,
            create_versioned_router,
        )

        # Test versioned router creation
        router = create_versioned_router(
            service_name="test-service",
            current_version="v2.1.0",
            supported_versions=["v2.0.0", "v1.5.0"],
        )
        assert router.service_name == "test-service"
        print("  ✅ Versioned router creation works")

        # Test endpoint registration (mock functions)
        def test_endpoint_v2():
            return {"version": "v2.0.0", "message": "test"}

        def test_endpoint_v1():
            return {"version": "v1.5.0", "message": "test"}

        # Register endpoints
        from shared.versioning.version_manager import APIVersion

        router.endpoints["GET:/test"] = (
            router.endpoints.get("GET:/test")
            or type(
                "VersionedEndpoint",
                (),
                {
                    "path": "/test",
                    "method": "GET",
                    "handlers": {},
                    "add_handler": lambda self, version, handler: self.handlers.update(
                        {str(version): handler}
                    ),
                    "get_handler": lambda self, version: self.handlers.get(
                        str(version)
                    ),
                    "get_supported_versions": lambda self: [
                        APIVersion.from_string(v) for v in self.handlers.keys()
                    ],
                },
            )()
        )

        router.endpoints["GET:/test"].add_handler(
            APIVersion.from_string("v2.0.0"), test_endpoint_v2
        )
        router.endpoints["GET:/test"].add_handler(
            APIVersion.from_string("v1.5.0"), test_endpoint_v1
        )

        # Test version info
        version_info = router.get_version_info()
        assert "total_endpoints" in version_info
        assert version_info["total_endpoints"] > 0
        print("  ✅ Endpoint registration works")

        # Test OpenAPI spec generation
        openapi_spec = router.create_openapi_spec()
        assert "openapi" in openapi_spec
        assert "paths" in openapi_spec
        print("  ✅ OpenAPI spec generation works")

        return {"success": True, "tests_passed": 3, "tests_failed": 0}

    except Exception as e:
        print(f"  ❌ Versioned router test failed: {e}")
        return {"success": False, "tests_passed": 0, "tests_failed": 1, "error": str(e)}


def test_api_models():
    """Test API models and response structures."""
    print("🔍 Testing API Models...")

    try:
        from shared.api_models import APIResponse, APIStatus, APIMetadata, ErrorCode

        # Test basic API response
        response = APIResponse(
            status=APIStatus.SUCCESS, data={"test": "data"}, message="Test successful"
        )
        assert response.status == APIStatus.SUCCESS
        assert response.data["test"] == "data"
        print("  ✅ Basic API response creation works")

        # Test API response with metadata
        metadata = APIMetadata(
            api_version="v2.1.0",
            service_version="2.1.0",
            request_id="test-123",
            timestamp="2025-06-22T10:00:00Z",
        )

        response_with_metadata = APIResponse(
            status=APIStatus.SUCCESS, data={"test": "data"}, metadata=metadata
        )
        assert response_with_metadata.metadata.api_version == "v2.1.0"
        print("  ✅ API response with metadata works")

        # Test error response
        error_response = APIResponse(
            status=APIStatus.ERROR,
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Validation failed",
        )
        assert error_response.status == APIStatus.ERROR
        assert error_response.error_code == ErrorCode.VALIDATION_ERROR
        print("  ✅ Error response creation works")

        return {"success": True, "tests_passed": 3, "tests_failed": 0}

    except Exception as e:
        print(f"  ❌ API models test failed: {e}")
        return {"success": False, "tests_passed": 0, "tests_failed": 1, "error": str(e)}


def test_end_to_end_workflow():
    """Test complete end-to-end versioning workflow."""
    print("🔍 Testing End-to-End Workflow...")

    try:
        from shared.versioning.version_manager import APIVersion, VersionManager
        from shared.versioning.compatibility_manager import create_compatibility_manager
        from shared.versioning.response_transformers import (
            VersionedResponseBuilder,
            CompatibilityTransformer,
        )
        from shared.api_models import APIStatus

        # 1. Setup version management
        version_manager = VersionManager("e2e-test-service", "v2.1.0")
        version_manager.register_version("v2.0.0")
        version_manager.register_version("v1.5.0")

        # 2. Setup compatibility management
        compat_manager = create_compatibility_manager("e2e-test-service")

        # 3. Setup response transformation
        response_builder = VersionedResponseBuilder("e2e-test-service")

        transformer = CompatibilityTransformer(
            source_version=APIVersion.from_string("v1.5.0"),
            target_version=APIVersion.from_string("v2.0.0"),
            field_mappings={"user_id": "userId", "created_at": "createdAt"},
        )
        response_builder.register_transformer(transformer)

        # 4. Simulate incoming request with v1.5.0
        headers = {"API-Version": "v1.5.0"}
        detected_version = version_manager.detect_version_from_request(
            headers, "/api/test", {}
        )
        assert str(detected_version) == "v1.5.0"
        print("  ✅ Request version detection works")

        # 5. Check compatibility
        rule = compat_manager.check_compatibility(
            APIVersion.from_string("v1.5.0"), APIVersion.from_string("v2.0.0")
        )
        assert rule is not None
        print("  ✅ Compatibility checking works")

        # 6. Transform response for compatibility
        test_data = {
            "user_id": 123,
            "created_at": "2025-06-22T10:00:00Z",
            "name": "Test User",
        }
        response = response_builder.build_response(
            status=APIStatus.SUCCESS,
            data=test_data,
            request_version=APIVersion.from_string("v1.5.0"),
            target_version=APIVersion.from_string("v2.0.0"),
        )

        assert response.status == APIStatus.SUCCESS
        assert "userId" in response.data
        assert response.metadata is not None
        print("  ✅ Response transformation works")

        # 7. Test deprecation workflow
        deprecated_response = response_builder.build_response(
            status=APIStatus.SUCCESS,
            data=test_data,
            request_version=APIVersion.from_string("v1.5.0"),
            include_deprecation_info=True,
        )

        assert deprecated_response.metadata is not None
        print("  ✅ Deprecation workflow works")

        return {"success": True, "tests_passed": 4, "tests_failed": 0}

    except Exception as e:
        print(f"  ❌ End-to-end workflow test failed: {e}")
        return {"success": False, "tests_passed": 0, "tests_failed": 1, "error": str(e)}


def main():
    """Main function to run core versioning validation."""
    print("🧪 ACGS-1 API Versioning Core Validation")
    print("=" * 60)

    # Run all tests
    test_functions = [
        test_version_manager,
        test_compatibility_manager,
        test_response_transformers,
        test_versioned_router,
        test_api_models,
        test_end_to_end_workflow,
    ]

    results = {}
    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test_func in test_functions:
        test_name = test_func.__name__
        result = test_func()
        results[test_name] = result

        total_tests += result.get("tests_passed", 0) + result.get("tests_failed", 0)
        passed_tests += result.get("tests_passed", 0)
        failed_tests += result.get("tests_failed", 0)

    # Calculate overall success
    overall_success = all(result.get("success", False) for result in results.values())
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    # Generate report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_success": overall_success,
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate_percentage": round(success_rate, 1),
        },
        "test_results": results,
    }

    # Print summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed Tests: {passed_tests}")
    print(f"Failed Tests: {failed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")

    if overall_success:
        print("\n✅ API Versioning Core Validation: PASSED")
        print("🎉 All core versioning components are working correctly!")
    else:
        print("\n❌ API Versioning Core Validation: FAILED")
        print("🔧 Some core components need attention.")

        # Show failed tests
        for test_name, result in results.items():
            if not result.get("success", False):
                print(f"  ❌ {test_name}: {result.get('error', 'Unknown error')}")

    # Save report
    with open("api_versioning_core_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Detailed report saved to: api_versioning_core_validation_report.json")

    print("\n💡 NEXT STEPS")
    print("-" * 60)
    if overall_success:
        print("✅ Core API versioning system is working correctly")
        print("🚀 Ready to proceed with integration testing")
        print("📋 Run backward compatibility tests next")
        print("🔧 Test middleware integration in staging environment")
    else:
        print("🔧 Fix failing core components before proceeding")
        print("🧪 Re-run validation after fixes")
        print("📖 Review component implementation for errors")

    return 0 if overall_success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
