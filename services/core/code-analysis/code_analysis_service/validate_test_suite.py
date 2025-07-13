#!/usr/bin/env python3
"""
ACGS Code Analysis Engine - Test Suite Validation
Quick validation to ensure all Priority 3 test files are properly structured.

Constitutional Hash: cdd01ef066bc6cf2
"""

import ast
import contextlib
import pathlib
import sys
from typing import Any


def validate_test_file(filepath: str) -> dict[str, Any]:
    """Validate a test file for proper structure and imports"""

    if not pathlib.Path(filepath).exists():
        return {
            "status": "failed",
            "error": "File does not exist",
            "filepath": filepath,
        }

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Parse the AST to check for syntax errors
        ast.parse(content)

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
        result = validate_test_file(test_file)
        validation_results[test_file] = result

        if result["status"] == "ok":
            pass
        else:
            all_valid = False

    # Check for required dependencies

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
        except ImportError:
            missing_modules.append(module)
            all_valid = False

    # Check for additional testing dependencies
    optional_modules = ["matplotlib", "numpy", "pytest", "asyncpg", "redis"]

    for module in optional_modules:
        with contextlib.suppress(ImportError):
            __import__(module)

    # Summary

    len([r for r in validation_results.values() if r["status"] == "ok"])
    len(validation_results)

    if all_valid:
        pass

    # Check if service configuration files exist
    config_files = ["main.py", "config/settings.py", "requirements.txt"]

    for config_file in config_files:
        if pathlib.Path(config_file).exists():
            pass
        else:
            all_valid = False

    # Final recommendation
    if all_valid:
        pass

    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
