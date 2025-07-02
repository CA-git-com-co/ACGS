#!/usr/bin/env python3
"""
Simple ACGS-1 API Versioning Test

Basic test to verify our versioning components are working without complex imports.
"""

import sys
from pathlib import Path

# Add the services directory to Python path
services_path = Path(__file__).parent.parent / "services"
sys.path.insert(0, str(services_path))


def test_basic_imports():
    """Test that we can import our versioning modules."""
    print("🔍 Testing Basic Imports...")

    try:
        # Test version manager import
        sys.path.insert(0, str(services_path / "shared" / "versioning"))

        # Import version manager components
        from version_manager import APIVersion, VersionManager

        print("  ✅ Version manager import successful")

        # Test basic version creation
        version = APIVersion(2, 1, 0)
        assert version.major == 2
        assert version.minor == 1
        assert version.patch == 0
        print("  ✅ Version creation works")

        # Test version string parsing
        parsed_version = APIVersion.from_string("v2.1.0")
        assert parsed_version.major == 2
        assert parsed_version.minor == 1
        assert parsed_version.patch == 0
        print("  ✅ Version string parsing works")

        # Test version comparison
        v1 = APIVersion(1, 5, 0)
        v2 = APIVersion(2, 0, 0)
        assert v2 > v1
        assert v1 < v2
        print("  ✅ Version comparison works")

        # Test version manager
        manager = VersionManager("test-service", "v2.1.0")
        assert str(manager.current_version) == "v2.1.0"
        print("  ✅ Version manager creation works")

        return True

    except Exception as e:
        print(f"  ❌ Import test failed: {e}")
        return False


def test_api_models():
    """Test API models."""
    print("🔍 Testing API Models...")

    try:
        # Import API models
        sys.path.insert(0, str(services_path / "shared"))
        from api_models import APIMetadata, APIResponse, APIStatus

        # Test basic response
        response = APIResponse(
            status=APIStatus.SUCCESS, data={"test": "data"}, message="Test successful"
        )
        assert response.status == APIStatus.SUCCESS
        assert response.data["test"] == "data"
        print("  ✅ Basic API response works")

        # Test response with metadata
        metadata = APIMetadata(
            api_version="v2.1.0", service_version="2.1.0", request_id="test-123"
        )

        response_with_metadata = APIResponse(
            status=APIStatus.SUCCESS, data={"test": "data"}, metadata=metadata
        )
        assert response_with_metadata.metadata.api_version == "v2.1.0"
        print("  ✅ API response with metadata works")

        return True

    except Exception as e:
        print(f"  ❌ API models test failed: {e}")
        return False


def test_file_structure():
    """Test that all expected files exist."""
    print("🔍 Testing File Structure...")

    expected_files = [
        "services/shared/versioning/__init__.py",
        "services/shared/versioning/version_manager.py",
        "services/shared/versioning/compatibility_manager.py",
        "services/shared/versioning/response_transformers.py",
        "services/shared/versioning/versioned_router.py",
        "services/shared/api_models.py",
        "services/shared/middleware/version_routing_middleware.py",
        "docs/api/DEPRECATION_POLICY.md",
        "docs/api/VERSION_COMPATIBILITY_MATRIX.md",
        "tools/versioning/__init__.py",
        "tools/versioning/api_diff.py",
        "tools/versioning/migration_generator.py",
        "tools/versioning/deployment_manager.py",
        ".github/workflows/api-versioning-ci.yml",
        ".github/workflows/api-compatibility-matrix.yml",
    ]

    missing_files = []
    existing_files = []

    for file_path in expected_files:
        full_path = Path(__file__).parent.parent / file_path
        if full_path.exists():
            existing_files.append(file_path)
            print(f"  ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"  ❌ {file_path} - MISSING")

    print("\n📊 File Structure Summary:")
    print(f"  Existing: {len(existing_files)}")
    print(f"  Missing: {len(missing_files)}")

    if missing_files:
        print("\n⚠️ Missing Files:")
        for file_path in missing_files:
            print(f"    - {file_path}")

    return len(missing_files) == 0


def test_documentation():
    """Test that documentation files are properly created."""
    print("🔍 Testing Documentation...")

    doc_files = [
        "docs/api/DEPRECATION_POLICY.md",
        "docs/api/VERSION_COMPATIBILITY_MATRIX.md",
        "docs/api/SDK_COMPATIBILITY_MATRIX.md",
        "docs/implementation/IMPLEMENTATION_VALIDATION_ROLLOUT_PLAN.md",
    ]

    doc_results = []

    for doc_file in doc_files:
        full_path = Path(__file__).parent.parent / doc_file
        if full_path.exists():
            # Check if file has content
            content = full_path.read_text()
            if len(content) > 100:  # Basic content check
                print(f"  ✅ {doc_file} - {len(content)} characters")
                doc_results.append(True)
            else:
                print(f"  ⚠️ {doc_file} - Too short ({len(content)} characters)")
                doc_results.append(False)
        else:
            print(f"  ❌ {doc_file} - MISSING")
            doc_results.append(False)

    return all(doc_results)


def test_github_workflows():
    """Test that GitHub workflows are created."""
    print("🔍 Testing GitHub Workflows...")

    workflow_files = [
        ".github/workflows/api-versioning-ci.yml",
        ".github/workflows/api-compatibility-matrix.yml",
    ]

    workflow_results = []

    for workflow_file in workflow_files:
        full_path = Path(__file__).parent.parent / workflow_file
        if full_path.exists():
            content = full_path.read_text()
            # Check for key workflow elements
            if "name:" in content and "on:" in content and "jobs:" in content:
                print(f"  ✅ {workflow_file} - Valid workflow")
                workflow_results.append(True)
            else:
                print(f"  ⚠️ {workflow_file} - Invalid workflow structure")
                workflow_results.append(False)
        else:
            print(f"  ❌ {workflow_file} - MISSING")
            workflow_results.append(False)

    return all(workflow_results)


def main():
    """Run simple versioning tests."""
    print("🧪 ACGS-1 API Versioning Simple Test")
    print("=" * 50)

    tests = [
        ("File Structure", test_file_structure),
        ("Documentation", test_documentation),
        ("GitHub Workflows", test_github_workflows),
        ("Basic Imports", test_basic_imports),
        ("API Models", test_api_models),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")

    if passed == total:
        print("\n🎉 All tests passed! API versioning system is properly implemented.")
        print("\n💡 NEXT STEPS:")
        print("  1. Run integration tests in staging environment")
        print("  2. Test backward compatibility with existing services")
        print("  3. Validate CI/CD pipeline integration")
        print("  4. Begin phased rollout according to implementation plan")
        return 0
    print(f"\n⚠️ {total - passed} tests failed. Review implementation.")
    print("\n🔧 RECOMMENDED ACTIONS:")
    print("  1. Check missing files and create them")
    print("  2. Fix import issues")
    print("  3. Validate file contents and structure")
    print("  4. Re-run tests after fixes")
    return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
