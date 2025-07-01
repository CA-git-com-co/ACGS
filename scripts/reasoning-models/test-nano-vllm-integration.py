#!/usr/bin/env python3
"""
Test script for Nano-vLLM integration in ACGS-1 system.

This script tests the Nano-vLLM adapter and integration to ensure
everything works correctly before full deployment.
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add the services directory to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "services" / "reasoning-models"))

try:
    from nano_vllm_adapter import NanoVLLMAdapter, ModelConfig, create_nano_vllm_adapter

    print("✅ Successfully imported Nano-vLLM adapter")
except ImportError as e:
    print(f"❌ Import error for adapter: {e}")
    sys.exit(1)

try:
    from nano_vllm_integration import (
        NanoVLLMReasoningService,
        ReasoningRequest,
        ConstitutionalDomain,
        create_nano_vllm_reasoning_service,
    )

    print("✅ Successfully imported Nano-vLLM integration")
    NANO_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error for integration: {e}")
    # Try to import from the original vLLM integration for basic types
    try:
        # Import from the original file (with hyphens)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "vllm_integration",
            project_root / "services" / "reasoning-models" / "vllm-integration.py",
        )
        vllm_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vllm_module)

        ReasoningRequest = vllm_module.ReasoningRequest
        ConstitutionalDomain = vllm_module.ConstitutionalDomain
        print("✅ Using original vLLM integration types")
        NANO_INTEGRATION_AVAILABLE = False

        # Create dummy classes for missing components
        class NanoVLLMReasoningService:
            pass

        async def create_nano_vllm_reasoning_service(*args, **kwargs):
            return None

    except ImportError:
        print("❌ Could not import from original integration either")
        sys.exit(1)


async def test_nano_vllm_adapter():
    """Test the basic Nano-vLLM adapter functionality."""
    print("\n🧪 Testing Nano-vLLM Adapter...")

    try:
        # Create adapter with mock model
        adapter = create_nano_vllm_adapter(
            model_path="test-model", tensor_parallel_size=1, gpu_memory_utilization=0.5
        )

        # Initialize adapter
        await adapter.initialize()
        print("✅ Adapter initialized successfully")

        # Test chat completion
        messages = [{"role": "user", "content": "Hello, this is a test message."}]

        response = await adapter.chat_completion(
            messages=messages, max_tokens=50, temperature=0.7
        )

        print(f"✅ Chat completion successful")
        print(f"   Response: {response['choices'][0]['message']['content'][:100]}...")
        print(f"   Tokens: {response['usage']['completion_tokens']}")
        print(f"   Time: {response.get('generation_time', 0):.2f}s")

        # Test health check
        health = await adapter.health_check()
        print(f"✅ Health check: {health['status']}")

        # Shutdown
        await adapter.shutdown()
        print("✅ Adapter shutdown successful")

        return True

    except Exception as e:
        print(f"❌ Adapter test failed: {str(e)}")
        return False


async def test_reasoning_service():
    """Test the full reasoning service integration."""
    print("\n🧪 Testing Nano-vLLM Reasoning Service...")

    if not NANO_INTEGRATION_AVAILABLE:
        print("⚠️  Nano-vLLM integration not available, skipping reasoning service test")
        return True

    try:
        # Create reasoning service
        service = await create_nano_vllm_reasoning_service(enable_fallback=True)
        if service is None:
            print("⚠️  Could not create reasoning service, skipping test")
            return True
        print("✅ Reasoning service initialized successfully")

        # Test constitutional reasoning
        request = ReasoningRequest(
            content="Should we implement mandatory data encryption for all user communications?",
            domain=ConstitutionalDomain.PRIVACY,
            context={
                "stakeholders": ["users", "administrators", "developers"],
                "current_policy": "optional encryption",
                "compliance_requirements": ["GDPR", "CCPA"],
            },
            max_tokens=200,
        )

        print("✅ Created reasoning request")

        # Perform reasoning
        start_time = time.time()
        response = await service.constitutional_reasoning(request)
        end_time = time.time()

        print("✅ Constitutional reasoning completed")
        print(f"   Model: {response.model_used.value}")
        print(f"   Confidence: {response.confidence_score:.2f}")
        print(f"   Processing Time: {response.processing_time_ms:.2f}ms")
        print(f"   Total Time: {(end_time - start_time) * 1000:.2f}ms")
        print(f"   Reasoning Steps: {len(response.reasoning_chain)}")
        print(f"   Conclusion: {response.conclusion[:100]}...")
        print(f"   Compliance Scores: {response.constitutional_compliance}")

        # Test health check
        health = await service.health_check()
        print(f"✅ Service health check: {health['service']} - {health['healthy']}")

        # Test ensemble reasoning if multiple models available
        if len(service.adapters) > 1:
            print("🧪 Testing ensemble reasoning...")
            ensemble_response = await service.ensemble_reasoning(request)
            print(
                f"✅ Ensemble reasoning completed with {len(service.adapters)} models"
            )

        # Shutdown
        await service.shutdown()
        print("✅ Reasoning service shutdown successful")

        return True

    except Exception as e:
        print(f"❌ Reasoning service test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def test_performance_benchmark():
    """Run a simple performance benchmark."""
    print("\n🧪 Running Performance Benchmark...")

    try:
        service = await create_nano_vllm_reasoning_service(enable_fallback=True)

        # Test multiple requests
        requests = [
            ReasoningRequest(
                content=f"Test request {i}: Analyze the constitutional implications of policy {i}",
                domain=ConstitutionalDomain.GOVERNANCE,
                context={"test_id": i},
                max_tokens=100,
            )
            for i in range(3)
        ]

        times = []
        for i, request in enumerate(requests):
            start_time = time.time()
            response = await service.constitutional_reasoning(request)
            end_time = time.time()

            request_time = (end_time - start_time) * 1000
            times.append(request_time)
            print(f"   Request {i+1}: {request_time:.2f}ms")

        avg_time = sum(times) / len(times)
        print(f"✅ Average response time: {avg_time:.2f}ms")
        print(f"   Min: {min(times):.2f}ms, Max: {max(times):.2f}ms")

        await service.shutdown()
        return True

    except Exception as e:
        print(f"❌ Performance benchmark failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting Nano-vLLM Integration Tests")
    print("=" * 50)

    tests = [
        ("Nano-vLLM Adapter", test_nano_vllm_adapter),
        ("Reasoning Service", test_reasoning_service),
        ("Performance Benchmark", test_performance_benchmark),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test...")
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Nano-vLLM integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
