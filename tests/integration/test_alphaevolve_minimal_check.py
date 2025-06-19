#!/usr/bin/env python3
"""
Minimal AlphaEvolve-ACGS Integration Check

This test performs a minimal check to verify that the AlphaEvolve-ACGS
integration components are available and can be imported.
"""

import sys
from pathlib import Path

# Add service directories to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services/core/governance-synthesis"))
sys.path.insert(0, str(project_root / "services/core/constitutional-ai"))
sys.path.insert(0, str(project_root / "services/core/formal-verification"))
sys.path.insert(0, str(project_root / "services/core/policy-governance"))

def test_minimal_import_check():
    """Test minimal import of AlphaEvolve-ACGS components."""
    print("🔍 Testing AlphaEvolve-ACGS component imports...")
    
    # Test 1: Lipschitz Estimator
    try:
        from gs_service.app.services.lipschitz_estimator import LipschitzEstimator
        print("✅ LipschitzEstimator imported successfully")
        lipschitz_available = True
    except ImportError as e:
        print(f"❌ LipschitzEstimator import failed: {e}")
        lipschitz_available = False
    
    # Test 2: LLM Reliability Framework
    try:
        from gs_service.app.core.llm_reliability_framework import LLMReliabilityFramework
        print("✅ LLMReliabilityFramework imported successfully")
        reliability_available = True
    except ImportError as e:
        print(f"❌ LLMReliabilityFramework import failed: {e}")
        reliability_available = False
    
    # Test 3: Constitutional Council Scalability
    try:
        from ac_service.app.core.constitutional_council_scalability import ConstitutionalCouncilScalabilityFramework
        print("✅ ConstitutionalCouncilScalabilityFramework imported successfully")
        council_available = True
    except ImportError as e:
        print(f"❌ ConstitutionalCouncilScalabilityFramework import failed: {e}")
        council_available = False
    
    # Test 4: Adversarial Robustness Tester
    try:
        from fv_service.app.core.adversarial_robustness_tester import AdversarialRobustnessTester
        print("✅ AdversarialRobustnessTester imported successfully")
        adversarial_available = True
    except ImportError as e:
        print(f"❌ AdversarialRobustnessTester import failed: {e}")
        adversarial_available = False
    
    # Test 5: Proactive Fairness Generator
    try:
        from pgc_service.app.core.proactive_fairness_generator import ProactiveFairnessGenerator
        print("✅ ProactiveFairnessGenerator imported successfully")
        fairness_available = True
    except ImportError as e:
        print(f"❌ ProactiveFairnessGenerator import failed: {e}")
        fairness_available = False
    
    # Test 6: Schemas
    try:
        from gs_service.app.schemas import LLMInterpretationInput, LLMStructuredOutput
        print("✅ Schemas imported successfully")
        schemas_available = True
    except ImportError as e:
        print(f"❌ Schemas import failed: {e}")
        schemas_available = False
    
    # Summary
    total_components = 6
    available_components = sum([
        lipschitz_available,
        reliability_available,
        council_available,
        adversarial_available,
        fairness_available,
        schemas_available
    ])
    
    print(f"\n📊 Component Availability: {available_components}/{total_components}")
    
    if available_components == total_components:
        print("🎉 All AlphaEvolve-ACGS components are available!")
        return True
    else:
        print("⚠️  Some components are missing. Integration tests may be skipped.")
        return False

def test_basic_initialization():
    """Test basic initialization of available components."""
    print("\n🔧 Testing basic component initialization...")
    
    try:
        from gs_service.app.services.lipschitz_estimator import LipschitzEstimator, LipschitzEstimationConfig
        
        # Test basic config creation
        config = LipschitzEstimationConfig()
        print(f"✅ LipschitzEstimationConfig created: theoretical_bound={config.theoretical_bound}")
        
        # Test estimator creation
        estimator = LipschitzEstimator(config)
        print("✅ LipschitzEstimator created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Component initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AlphaEvolve-ACGS Minimal Integration Check")
    print("=" * 60)
    
    import_success = test_minimal_import_check()
    init_success = test_basic_initialization()
    
    print("\n" + "=" * 60)
    if import_success and init_success:
        print("✅ AlphaEvolve-ACGS integration is ready!")
        sys.exit(0)
    else:
        print("❌ AlphaEvolve-ACGS integration has issues.")
        sys.exit(1)
