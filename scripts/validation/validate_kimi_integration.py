#!/usr/bin/env python3
"""
Validate Kimi K2 Instruct integration in ACGS-2

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def validate_groq_model_enum():
    """Validate that Kimi model is available in GroqModel enum."""
    try:
        from services.shared.groq_cloud_client import GroqModel

        # Check if Kimi model is available
        kimi_model = GroqModel.KIMI_K2_INSTRUCT

        print("✅ GroqModel enum validation:")
        print(f"   - Kimi K2 Instruct: {kimi_model}")
        print(f"   - Model ID: {kimi_model.value}")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except AttributeError as e:
        print(f"❌ Kimi model not found in GroqModel enum: {e}")
        return False


def validate_router_integration():
    """Validate that Kimi model is available in the router."""
    try:
        from services.shared.routing.hybrid_inference_router import HybridInferenceRouter

        # Create router instance (without API keys for validation)
        router = HybridInferenceRouter()

        # Check if Kimi model is in the model endpoints
        kimi_endpoint = router.model_endpoints.get("moonshotai/kimi-k2-instruct")

        if kimi_endpoint:
            print("✅ Router integration validation:")
            print(f"   - Model Name: {kimi_endpoint.model_name}")
            print(f"   - Tier: {kimi_endpoint.tier}")
            print(f"   - Context Length: {kimi_endpoint.context_length:,} tokens")
            print(f"   - Constitutional Compliance: {kimi_endpoint.constitutional_compliance_score}")
            print(f"   - Capabilities: {', '.join(kimi_endpoint.capabilities)}")

            return True
        else:
            print("❌ Kimi model not found in router endpoints")
            return False

    except ImportError as e:
        print(f"❌ Router import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Router validation error: {e}")
        return False


def validate_environment_config():
    """Validate environment configuration for Groq integration."""
    try:
        import os

        print("✅ Environment configuration validation:")

        # Check for Groq API key configuration
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            print(f"   - GROQ_API_KEY: Set (length: {len(groq_key)})")
        else:
            print("   - GROQ_API_KEY: Not set (required for actual usage)")

        # Check for OpenRouter fallback
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            print(f"   - OPENROUTER_API_KEY: Set (length: {len(openrouter_key)})")
        else:
            print("   - OPENROUTER_API_KEY: Not set (optional fallback)")

        return True

    except Exception as e:
        print(f"❌ Environment validation error: {e}")
        return False


def main():
    """Main validation function."""
    print("🔍 Kimi K2 Instruct Integration Validation")
    print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 50)
    print()

    results = []

    # Validation 1: GroqModel enum
    print("1. Validating GroqModel enum...")
    results.append(validate_groq_model_enum())
    print()

    # Validation 2: Router integration
    print("2. Validating router integration...")
    results.append(validate_router_integration())
    print()

    # Validation 3: Environment configuration
    print("3. Validating environment configuration...")
    results.append(validate_environment_config())
    print()

    # Summary
    print("=" * 50)
    print("📊 Validation Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)} validations")

    if all(results):
        print("🎉 All Kimi K2 Instruct integration validations PASSED!")
        print()
        print("📝 Next Steps:")
        print("1. Set GROQ_API_KEY environment variable for actual usage")
        print("2. Run: python examples/kimi_groq_integration.py")
        print("3. Test with: python scripts/testing/test_kimi_integration.py")
        print()
        print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        return 0
    else:
        print("⚠️  Some validations FAILED!")
        print("Please check the errors above and fix the integration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())