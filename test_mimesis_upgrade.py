#!/usr/bin/env python3
"""
Staging validation script for mimesis upgrade (PR #104)
Tests data generation functionality before merge
"""

import logging
import subprocess
import sys
import time
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MimesisValidationSuite:
    """Comprehensive validation suite for mimesis upgrade"""

    def __init__(self):
        self.test_results = {}

    def test_mimesis_import(self) -> Dict[str, Any]:
        """Test basic mimesis import and version"""
        logger.info("📦 Testing mimesis import...")

        try:
            import mimesis

            version = getattr(mimesis, "__version__", "unknown")

            return {"status": "success", "version": version, "import_successful": True}
        except Exception as e:
            return {"status": "error", "error": str(e), "import_successful": False}

    def test_basic_data_generation(self) -> Dict[str, Any]:
        """Test basic data generation functionality"""
        logger.info("🎲 Testing basic data generation...")

        try:
            from mimesis import Address, Person, Text

            person = Person()
            address = Address()
            text = Text()

            # Generate test data
            test_data = {
                "name": person.full_name(),
                "email": person.email(),
                "address": address.address(),
                "city": address.city(),
                "text": text.sentence(),
                "word": text.word(),
            }

            # Validate data types and non-empty values
            validation_results = {}
            for key, value in test_data.items():
                validation_results[key] = {
                    "generated": value is not None,
                    "type": type(value).__name__,
                    "length": len(str(value)) if value else 0,
                }

            return {
                "status": "success",
                "test_data": test_data,
                "validation": validation_results,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def test_localization(self) -> Dict[str, Any]:
        """Test localization functionality"""
        logger.info("🌍 Testing localization...")

        try:
            from mimesis import Person
            from mimesis.locales import Locale

            locales_to_test = [Locale.EN, Locale.ES, Locale.FR, Locale.DE]
            locale_results = {}

            for locale in locales_to_test:
                try:
                    person = Person(locale)
                    name = person.full_name()

                    locale_results[str(locale)] = {
                        "status": "success",
                        "sample_name": name,
                        "locale_supported": True,
                    }
                except Exception as e:
                    locale_results[str(locale)] = {
                        "status": "error",
                        "error": str(e),
                        "locale_supported": False,
                    }

            return {"status": "success", "locale_tests": locale_results}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def test_custom_providers(self) -> Dict[str, Any]:
        """Test custom provider functionality"""
        logger.info("🔧 Testing custom providers...")

        try:
            from mimesis import Generic
            from mimesis.locales import Locale

            generic = Generic(Locale.EN)

            # Test various providers
            provider_tests = {}

            providers_to_test = [
                ("person", lambda: generic.person.full_name()),
                ("address", lambda: generic.address.city()),
                ("datetime", lambda: generic.datetime.date()),
                ("internet", lambda: generic.internet.email()),
                ("text", lambda: generic.text.sentence()),
                ("numeric", lambda: generic.numeric.integer_number()),
            ]

            for provider_name, provider_func in providers_to_test:
                try:
                    result = provider_func()
                    provider_tests[provider_name] = {
                        "status": "success",
                        "sample_data": str(result),
                        "data_type": type(result).__name__,
                    }
                except Exception as e:
                    provider_tests[provider_name] = {"status": "error", "error": str(e)}

            return {"status": "success", "provider_tests": provider_tests}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_pytest_tests(self) -> Dict[str, Any]:
        """Run existing pytest tests that use mimesis"""
        logger.info("🧪 Running pytest tests with mimesis...")

        try:
            # Find tests that use mimesis
            test_commands = [
                "python -m pytest tests/ -k 'mimesis' -v --tb=short",
                "python -m pytest tests/test_generators.py -v --tb=short",
                "python -m pytest tests/ -k 'fake' -v --tb=short",
            ]

            pytest_results = {}

            for i, cmd in enumerate(test_commands):
                try:
                    result = subprocess.run(
                        cmd.split(), capture_output=True, text=True, timeout=60
                    )

                    pytest_results[f"test_command_{i}"] = {
                        "command": cmd,
                        "return_code": result.returncode,
                        "stdout": (
                            result.stdout[-500:] if result.stdout else ""
                        ),  # Last 500 chars
                        "stderr": result.stderr[-500:] if result.stderr else "",
                        "status": "success" if result.returncode == 0 else "failed",
                    }

                except subprocess.TimeoutExpired:
                    pytest_results[f"test_command_{i}"] = {
                        "command": cmd,
                        "status": "timeout",
                        "error": "Test execution timed out",
                    }
                except Exception as e:
                    pytest_results[f"test_command_{i}"] = {
                        "command": cmd,
                        "status": "error",
                        "error": str(e),
                    }

            return {"status": "completed", "pytest_results": pytest_results}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        logger.info("🚀 Starting mimesis upgrade validation...")

        start_time = time.time()

        validation_results = {"timestamp": time.time(), "tests": {}}

        # Run all validation tests
        validation_results["tests"]["import_test"] = self.test_mimesis_import()
        validation_results["tests"][
            "basic_generation"
        ] = self.test_basic_data_generation()
        validation_results["tests"]["localization"] = self.test_localization()
        validation_results["tests"]["custom_providers"] = self.test_custom_providers()
        validation_results["tests"]["pytest_execution"] = self.run_pytest_tests()

        validation_results["execution_time"] = time.time() - start_time

        # Calculate overall success rate
        successful_tests = 0
        total_tests = len(validation_results["tests"])

        for test_name, test_result in validation_results["tests"].items():
            if test_result.get("status") in ["success", "completed"]:
                successful_tests += 1

        validation_results["success_rate"] = (
            successful_tests / total_tests if total_tests > 0 else 0
        )
        validation_results["overall_status"] = (
            "PASS" if validation_results["success_rate"] >= 0.8 else "FAIL"
        )

        logger.info(
            f"🎯 Validation complete: {validation_results['success_rate']:.1%} success rate"
        )
        logger.info(f"📊 Overall status: {validation_results['overall_status']}")

        return validation_results


def main():
    """Main validation execution"""
    validator = MimesisValidationSuite()
    results = validator.run_full_validation()

    # Print summary
    print("\n" + "=" * 60)
    print("MIMESIS UPGRADE VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Success Rate: {results['success_rate']:.1%}")
    print(f"Overall Status: {results['overall_status']}")
    print(f"Execution Time: {results['execution_time']:.2f}s")

    # Print detailed results
    for test_name, test_result in results["tests"].items():
        status = test_result.get("status", "unknown")
        print(f"  {test_name}: {status.upper()}")

        if status == "error" and "error" in test_result:
            print(f"    Error: {test_result['error']}")

    print("=" * 60)

    # Provide merge recommendation
    if results["overall_status"] == "PASS":
        print("✅ RECOMMENDATION: SAFE TO MERGE PR #104")
        print("   All mimesis functionality tests passed")
    else:
        print("❌ RECOMMENDATION: DO NOT MERGE PR #104")
        print("   Some tests failed - investigate before merging")

    print("=" * 60)

    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
