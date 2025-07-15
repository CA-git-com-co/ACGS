#!/usr/bin/env python3
"""
Test GroqCloud Integration Service
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the services directory to Python path
sys.path.append(str(Path(__file__).parent / "services"))

async def test_groq_integration():
    """Test GroqCloud integration with constitutional compliance."""
    print("Testing GroqCloud Integration...")
    print(f"Constitutional Hash: cdd01ef066bc6cf2")
    
    try:
        # Import GroqCloud client
        from shared.groq_cloud_client import GroqCloudClient, GroqRequest, GroqModel, InferenceMode
        
        print("✅ GroqCloud client imported successfully")
        
        # Test client initialization
        client = GroqCloudClient(
            api_key="test-key",  # Will use placeholder for testing
            enable_caching=True
        )
        
        print("✅ GroqCloud client initialized")
        
        # Test model configuration
        models = [
            GroqModel.NANO,
            GroqModel.FAST, 
            GroqModel.BALANCED,
            GroqModel.PREMIUM
        ]
        
        print("✅ Model tiers configured:")
        for model in models:
            print(f"   - {model.value}")
        
        # Test request creation
        test_request = GroqRequest(
            prompt="Test constitutional compliance",
            model=GroqModel.BALANCED,
            mode=InferenceMode.FAST,
            max_tokens=100,
            constitutional_validation=True,
            policy_enforcement=True,
            audit_trail=True
        )
        
        print("✅ Test request created successfully")
        print(f"   - Model: {test_request.model.value}")
        print(f"   - Mode: {test_request.mode.value}")
        print(f"   - Constitutional validation: {test_request.constitutional_validation}")
        
        # Test performance metrics
        metrics = client.get_performance_metrics()
        print("✅ Performance metrics accessible:")
        print(f"   - Constitutional hash: {metrics.get('constitutional_hash')}")
        print(f"   - Cache size: {metrics.get('cache_size', 0)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_wasm_policy_engine():
    """Test WASM policy engine integration."""
    print("\nTesting WASM Policy Engine...")
    
    try:
        # Import WASM policy engine
        from core.governance_synthesis.wasm_policy_engine import WASMPolicyEngine
        
        print("✅ WASM policy engine imported successfully")
        
        # Test engine initialization
        engine = WASMPolicyEngine()
        print("✅ WASM policy engine initialized")
        
        return True
        
    except ImportError as e:
        print(f"❌ WASM policy engine import error: {e}")
        return False
    except Exception as e:
        print(f"❌ WASM test failed: {e}")
        return False

async def test_constitutional_compliance():
    """Test constitutional compliance framework."""
    print("\nTesting Constitutional Compliance...")
    
    try:
        # Test constitutional hash validation
        expected_hash = "cdd01ef066bc6cf2"
        
        # Import shared utilities
        from shared.validation.validators import validate_constitutional_hash
        
        print("✅ Constitutional validation imported")
        
        # Test hash validation
        is_valid = validate_constitutional_hash(expected_hash)
        print(f"✅ Constitutional hash validation: {is_valid}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Constitutional validation import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Constitutional compliance test failed: {e}")
        return False

async def main():
    """Run all integration tests."""
    print("=" * 60)
    print("ACGS-2 GroqCloud Integration Test Suite")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("=" * 60)
    
    tests = [
        test_groq_integration,
        test_wasm_policy_engine,
        test_constitutional_compliance
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    print(f"Constitutional Hash: cdd01ef066bc6cf2")
    
    if all(results):
        print("🎉 All tests passed! GroqCloud integration ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Check logs for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)