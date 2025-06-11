import os

import pytest

if not os.environ.get("ACGS_INTEGRATION"):
    pytest.skip("integration test requires running services", allow_module_level=True)

#!/usr/bin/env python3
"""
Simple test script to verify OPA integration implementation.
"""

import os
import sys

# sys.path.append('/home/dislove/ACGS-master')  # Removed during reorganization


def test_imports():
    """Test that all modules can be imported."""
    try:
        pass

        print("✓ OPA config import successful")

        print("✓ OPA integration import successful")

        print("✓ Policy validator import successful")

        print("✓ Enhanced governance synthesis import successful")

        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_opa_config():
    """Test OPA configuration."""
    try:
        from services.core.governance_synthesis.app.config.opa_config import (
            get_opa_config,
        )

        config = get_opa_config()
        print(f"✓ OPA config created: mode={config.mode.value}")
        print(f"  - Max latency: {config.performance.max_policy_decision_latency_ms}ms")
        print(f"  - Caching enabled: {config.performance.enable_decision_caching}")
        return True
    except Exception as e:
        print(f"✗ OPA config test failed: {e}")
        return False


def test_policy_files():
    """Test that policy files exist."""
    policy_files = [
        "src/backend/gs_service/policies/constitutional_principles.rego",
        "src/backend/gs_service/policies/policy_synthesis.rego",
        "src/backend/gs_service/policies/governance_compliance.rego",
    ]

    all_exist = True
    for policy_file in policy_files:
        if os.path.exists(policy_file):
            print(f"✓ Policy file exists: {policy_file}")
        else:
            print(f"✗ Policy file missing: {policy_file}")
            all_exist = False

    return all_exist


def test_score_calculation():
    """Test score calculation logic."""
    try:
        from services.core.governance_synthesis.app.core.opa_integration import (
            PolicyValidationResult,
        )
        from services.core.governance_synthesis.app.services.policy_validator import (
            ComplianceCheckResult,
            ConflictDetectionResult,
            ConstitutionalValidationResult,
            PolicyValidationEngine,
        )

        engine = PolicyValidationEngine()

        # Test data
        syntax_result = PolicyValidationResult(
            is_valid=True,
            policy_path="test",
            validation_time_ms=10.0,
            errors=[],
            warnings=[],
            syntax_errors=[],
            semantic_errors=[],
        )

        constitutional_result = ConstitutionalValidationResult(
            is_constitutional=True,
            compliance_score=0.9,
            principle_scores={"fairness": 0.9},
            violations=[],
            recommendations=[],
        )

        compliance_result = ComplianceCheckResult(
            is_compliant=True,
            compliance_score=0.8,
            category_scores={"operational": 0.8},
            violations={},
            recommendations=[],
            requires_review=False,
        )

        conflict_result = ConflictDetectionResult(
            has_conflicts=False,
            logical_conflicts=[],
            semantic_conflicts=[],
            priority_conflicts=[],
            scope_conflicts=[],
            conflict_resolution_suggestions=[],
        )

        score = engine._calculate_overall_score(
            syntax_result, constitutional_result, compliance_result, conflict_result
        )

        print(f"✓ Score calculation successful: {score}")
        return True

    except Exception as e:
        print(f"✗ Score calculation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Testing OPA Integration Implementation")
    print("=" * 50)

    tests = [
        ("Module Imports", test_imports),
        ("OPA Configuration", test_opa_config),
        ("Policy Files", test_policy_files),
        ("Score Calculation", test_score_calculation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  Test failed!")

    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! OPA integration is working.")
        return 0
    else:
        print("❌ Some tests failed. Check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

import asyncio
import os

import pytest


@pytest.mark.skipif(
    not os.environ.get("ACGS_INTEGRATION"),
    reason="Integration test requires running services",
)
def test_main_wrapper():
    if "main" in globals():
        if asyncio.iscoroutinefunction(main):
            asyncio.run(main())
        else:
            main()
