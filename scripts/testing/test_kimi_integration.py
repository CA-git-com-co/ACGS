#!/usr/bin/env python3
"""
Test script for Kimi K2 Instruct model integration via Groq

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from groq import Groq
from services.shared.groq_cloud_client import GroqCloudClient, GroqRequest, GroqModel, InferenceMode


def test_basic_groq_kimi():
    """Test basic Groq client with Kimi model."""
    print("🧪 Testing Basic Groq Client with Kimi K2 Instruct")
    print(f"🔐 Constitutional Hash: cdd01ef066bc6cf2")
    print()

    # Initialize Groq client
    client = Groq()

    try:
        completion = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct",
            messages=[
                {
                    "role": "user",
                    "content": "Explain why fast inference is critical for reasoning models"
                }
            ]
        )

        print("✅ Kimi K2 Instruct Response:")
        print(completion.choices[0].message.content)
        print()

        return True

    except Exception as e:
        print(f"❌ Error with basic Groq client: {e}")
        return False


async def test_acgs_groq_client():
    """Test ACGS GroqCloud client with Kimi model."""
    print("🧪 Testing ACGS GroqCloud Client with Kimi K2 Instruct")
    print()

    try:
        # Initialize ACGS GroqCloud client
        groq_client = GroqCloudClient(
            api_key=os.getenv("GROQ_API_KEY"),
            enable_caching=True
        )

        # Create request for Kimi model
        request = GroqRequest(
            prompt="Explain why fast inference is critical for reasoning models in constitutional AI systems",
            model=GroqModel.KIMI_K2_INSTRUCT,
            mode=InferenceMode.BALANCED,
            max_tokens=1000,
            temperature=0.7,
            constitutional_validation=True
        )

        # Generate response
        response = await groq_client.generate(request)

        print("✅ ACGS GroqCloud Client Response:")
        print(f"Model: {response.model}")
        print(f"Latency: {response.latency_ms:.2f}ms")
        print(f"Constitutional Compliance: {response.constitutional_compliance_score:.2f}")
        print(f"Response: {response.content}")
        print()

        return True

    except Exception as e:
        print(f"❌ Error with ACGS GroqCloud client: {e}")
        return False


async def test_router_integration():
    """Test router integration with Kimi model."""
    print("🧪 Testing Router Integration with Kimi K2 Instruct")
    print()

    try:
        from services.shared.routing.hybrid_inference_router import HybridInferenceRouter

        # Initialize router
        router = HybridInferenceRouter(
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        # Test routing to Kimi model
        query_request = {
            "text": "Analyze the constitutional implications of fast inference in AI governance systems",
            "max_tokens": 1000,
            "temperature": 0.7
        }

        # Route query (should select Kimi for reasoning tasks)
        result = await router.route_query(query_request, strategy="constitutional_reasoning")

        print("✅ Router Selection:")
        print(f"Selected Model: {result['model_name']}")
        print(f"Tier: {result['tier']}")
        print(f"Estimated Cost: ${result['estimated_cost']:.8f}")
        print(f"Estimated Latency: {result['estimated_latency_ms']}ms")
        print(f"Constitutional Compliance: {result['constitutional_compliance_score']:.2f}")
        print()

        return True

    except Exception as e:
        print(f"❌ Error with router integration: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Kimi K2 Instruct Integration Test Suite")
    print("=" * 50)
    print()

    # Check for Groq API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY environment variable not set")
        print("Please set your Groq API key: export GROQ_API_KEY='your_key_here'")
        return 1

    results = []

    # Test 1: Basic Groq client
    results.append(test_basic_groq_kimi())

    # Test 2: ACGS GroqCloud client
    results.append(await test_acgs_groq_client())

    # Test 3: Router integration
    results.append(await test_router_integration())

    # Summary
    print("=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")

    if all(results):
        print("🎉 All Kimi K2 Instruct integration tests PASSED!")
        print("🔐 Constitutional Hash: cdd01ef066bc6cf2")
        return 0
    else:
        print("⚠️  Some tests FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))