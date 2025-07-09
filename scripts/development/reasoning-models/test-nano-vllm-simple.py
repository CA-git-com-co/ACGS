#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
"""
Simple test script for Nano-vLLM adapter functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the services directory to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "services" / "reasoning-models"))

print("🚀 Testing Nano-vLLM Adapter")
print("=" * 40)

try:
    from nano_vllm_adapter import create_nano_vllm_adapter

    print("✅ Successfully imported Nano-vLLM adapter")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def test_adapter():
    """Test the basic adapter functionality."""
    print("\n🧪 Testing Adapter...")

    try:
        # Create adapter
        adapter = create_nano_vllm_adapter(
            model_path="test-model", tensor_parallel_size=1, gpu_memory_utilization=0.5
        )
        print("✅ Adapter created")

        # Initialize
        await adapter.initialize()
        print("✅ Adapter initialized")

        # Test chat completion
        messages = [{"role": "user", "content": "Hello, test message"}]
        response = await adapter.chat_completion(messages, max_tokens=50)

        print("✅ Chat completion successful")
        print(f"   Response: {response['choices'][0]['message']['content'][:80]}...")

        # Health check
        health = await adapter.health_check()
        print(f"✅ Health check: {health['status']}")

        # Shutdown
        await adapter.shutdown()
        print("✅ Adapter shutdown")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e!s}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the test."""
    success = await test_adapter()

    if success:
        print("\n🎉 Nano-vLLM adapter test PASSED!")
        return 0
    print("\n❌ Nano-vLLM adapter test FAILED!")
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
