#!/usr/bin/env python3
"""
Import Verification Test for AlphaEvolve-ACGS Integration Components

This test verifies that all required components can be imported successfully
and helps identify specific import issues.
"""

import sys
from pathlib import Path

# Add project root and service directories to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services"))
sys.path.insert(0, str(project_root / "services/core"))
sys.path.insert(0, str(project_root / "services/core/governance-synthesis"))
sys.path.insert(0, str(project_root / "services/core/constitutional-ai"))
sys.path.insert(0, str(project_root / "services/core/formal-verification"))
sys.path.insert(0, str(project_root / "services/core/policy-governance"))


def test_lipschitz_estimator_import():
    """Test importing Lipschitz estimator components."""
    try:
        from governance_synthesis.gs_service.app.services.lipschitz_estimator import (
            LipschitzEstimationConfig,
            LipschitzEstimationResult,
            LipschitzEstimator,
        )

        print("✅ Lipschitz estimator components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Lipschitz estimator import failed: {e}")
        return False


def test_llm_reliability_framework_import():
    """Test importing LLM reliability framework components."""
    try:
        from services.core.governance_synthesis.gs_service.app.core.llm_reliability_framework import (
            LLMReliabilityConfig,
            LLMReliabilityFramework,
            ReliabilityLevel,
        )

        print("✅ LLM reliability framework components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ LLM reliability framework import failed: {e}")
        return False


def test_constitutional_council_scalability_import():
    """Test importing Constitutional Council scalability components."""
    try:
        from services.core.constitutional_ai.ac_service.app.core.constitutional_council_scalability import (
            CoEvolutionMode,
            ConstitutionalCouncilScalabilityFramework,
            ScalabilityConfig,
        )

        print("✅ Constitutional Council scalability components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Constitutional Council scalability import failed: {e}")
        return False


def test_adversarial_robustness_tester_import():
    """Test importing Adversarial robustness tester components."""
    try:
        from services.core.formal_verification.fv_service.app.core.adversarial_robustness_tester import (
            AdversarialRobustnessTester,
            AdversarialTestConfig,
            AdversarialTestType,
        )

        print("✅ Adversarial robustness tester components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Adversarial robustness tester import failed: {e}")
        return False


def test_proactive_fairness_generator_import():
    """Test importing Proactive fairness generator components."""
    try:
        from services.core.policy_governance.pgc_service.app.core.proactive_fairness_generator import (
            FairnessGenerationConfig,
            FairnessMetric,
            ProactiveFairnessGenerator,
        )

        print("✅ Proactive fairness generator components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Proactive fairness generator import failed: {e}")
        return False


def test_schemas_import():
    """Test importing schema components."""
    try:
        from services.core.governance_synthesis.gs_service.app.schemas import (
            LLMInterpretationInput,
            LLMStructuredOutput,
        )

        print("✅ Schema components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Schema import failed: {e}")
        return False


def main():
    """Run all import verification tests."""
    print("🚀 Running AlphaEvolve-ACGS Import Verification Tests")
    print("=" * 60)

    tests = [
        test_lipschitz_estimator_import,
        test_llm_reliability_framework_import,
        test_constitutional_council_scalability_import,
        test_adversarial_robustness_tester_import,
        test_proactive_fairness_generator_import,
        test_schemas_import,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)

    print("\n" + "=" * 60)
    print(f"📊 Import Verification Results: {sum(results)}/{len(results)} passed")

    if all(results):
        print("🎉 All components imported successfully!")
        return True
    else:
        print("⚠️  Some components failed to import. Check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
