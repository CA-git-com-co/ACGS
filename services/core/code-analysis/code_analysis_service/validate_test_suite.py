#!/usr/bin/env python3
"""
ACGS Code Analysis Engine - Test Suite Validation
Quick validation to ensure all Priority 3 test files are properly structured.

Constitutional Hash: cdd01ef066bc6cf2
"""

import ast
import os
import sys
from typing import Any


def validate_test_file(filepath: str) -> dict[str, Any]:
    """Validate a test file for proper structure and imports"""

    if not os.path.exists(filepath):
        return {
            "status": "failed",
            "error": "File does not exist",
            "filepath": filepath,
        }

    try:
        with open(filepath) as f:
            content = f.read()

        # Parse the AST to check for syntax errors
        tree = ast.parse(content)

        # Check for constitutional hash
        constitutional_hash_present = "cdd01ef066bc6cf2" in content

        # Check for main function or class
        has_main_function = "def main(" in content
        has_test_class = any(
            "class " in line and "Test" in line for line in content.split("\n")
        )

        # Check for proper imports
        has_imports = any(
            line.strip().startswith("import ") or line.strip().startswith("from ")
            for line in content.split("\n")
        )

        # Count lines of code
        lines_of_code = len(
            [
                line
                for line in content.split("\n")
                if line.strip() and not line.strip().startswith("#")
            ]
        )

        return {
            "status": "ok",
            "filepath": filepath,
            "constitutional_hash_present": constitutional_hash_present,
            "has_main_function": has_main_function,
            "has_test_class": has_test_class,
            "has_imports": has_imports,
            "lines_of_code": lines_of_code,
            "file_size_bytes": len(content),
        }

    except SyntaxError as e:
        return {"status": "failed", "error": f"Syntax error: {e}", "filepath": filepath}
    except Exception as e:
        return {"status": "failed", "error": str(e), "filepath": filepath}


def main():
    """Validate all Priority 3 test files"""
    print("=" * 80)
    print("ACGS Code Analysis Engine - Test Suite Validation")
    print("=" * 80)

    # Test files to validate
    test_files = [
        "test_priority3_integration.py",
        "test_performance_benchmarks.py",
        "test_monitoring_setup.py",
        "run_priority3_validation.py",
    ]

    validation_results = {}
    all_valid = True

    for test_file in test_files:
        print(f"\nValidating {test_file}...")
        result = validate_test_file(test_file)
        validation_results[test_file] = result

        if result["status"] == "ok":
            print(f"✅ {test_file}: Valid")
            print(
                "   - Constitutional hash:"
                f" {'✓' if result['constitutional_hash_present'] else '✗'}"
            )
            print(f"   - Main function: {'✓' if result['has_main_function'] else '✗'}")
            print(f"   - Imports: {'✓' if result['has_imports'] else '✗'}")
            print(f"   - Lines of code: {result['lines_of_code']}")
            print(f"   - File size: {result['file_size_bytes']} bytes")
        else:
            print(f"❌ {test_file}: Invalid - {result['error']}")
            all_valid = False

    # Check for required dependencies
    print("\nChecking dependencies...")

    required_modules = [
        "requests",
        "asyncio",
        "json",
        "time",
        "statistics",
        "concurrent.futures",
        "datetime",
        "typing",
    ]

    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: Available")
        except ImportError:
            print(f"❌ {module}: Missing")
            missing_modules.append(module)
            all_valid = False

    # Check for additional testing dependencies
    optional_modules = ["matplotlib", "numpy", "pytest", "asyncpg", "redis"]

    print("\nChecking optional testing dependencies...")
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module}: Available")
        except ImportError:
            print(f"⚠️  {module}: Not available (install with: pip install {module})")

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    valid_files = len([r for r in validation_results.values() if r["status"] == "ok"])
    total_files = len(validation_results)

    print(f"Test files validated: {valid_files}/{total_files}")
    print(
        "Required dependencies:"
        f" {'All available' if not missing_modules else f'Missing: {missing_modules}'}"
    )
    print(f"Overall status: {'✅ READY' if all_valid else '❌ ISSUES FOUND'}")

    if all_valid:
        print("\n🎉 Test suite validation PASSED!")
        print("You can now run the Priority 3 validation suite:")
        print("   python run_priority3_validation.py")
    else:
        print("\n⚠️  Test suite validation found issues.")
        print("Please resolve the issues above before running the validation suite.")

    # Check if service configuration files exist
    print("\nChecking service configuration...")
    config_files = ["main.py", "config/settings.py", "requirements.txt"]

    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ {config_file}: Found")
        else:
            print(f"❌ {config_file}: Missing")
            all_valid = False

    # Final recommendation
    if all_valid:
        print("\n✅ RECOMMENDATION: Priority 3 validation suite is ready for execution")
        print("   Constitutional Hash: cdd01ef066bc6cf2")
        print("   Service Port: 8007")
        print("   Next step: python run_priority3_validation.py")
    else:
        print("\n❌ RECOMMENDATION: Resolve validation issues before proceeding")

    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
