#!/usr/bin/env python3
"""
Model Connectivity Test Script for NVIDIA LLM Router

Tests connectivity to NVIDIA API and validates model availability.
"""

import asyncio
import aiohttp
import os
import sys
from typing import List, Dict, Any

async def test_nvidia_api_connectivity(api_key: str, base_url: str) -> bool:
    """
    Test basic connectivity to NVIDIA API
    
    Args:
        api_key: NVIDIA API key
        base_url: NVIDIA API base URL
        
    Returns:
        bool: True if connection successful
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base_url}/models",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return True
                else:
                    print(f"❌ API returned status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def test_model_availability(api_key: str, base_url: str, model_name: str) -> Dict[str, Any]:
    """
    Test availability of a specific model
    
    Args:
        api_key: NVIDIA API key
        base_url: NVIDIA API base URL
        model_name: Name of the model to test
        
    Returns:
        dict: Test results
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "Hello, this is a test message."}
        ],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            start_time = asyncio.get_event_loop().time()
            
            async with session.post(
                f"{base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                end_time = asyncio.get_event_loop().time()
                latency_ms = (end_time - start_time) * 1000
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        "status": "available",
                        "latency_ms": round(latency_ms, 2),
                        "response": result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "error",
                        "error_code": response.status,
                        "error_message": error_text,
                        "latency_ms": round(latency_ms, 2)
                    }
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "error_message": "Request timed out"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }

async def main():
    """Main test function"""
    print("🧪 NVIDIA LLM Router Model Connectivity Test")
    print("=" * 50)
    
    # Get configuration
    api_key = os.getenv("NVIDIA_API_KEY")
    base_url = os.getenv("NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1")
    
    if not api_key:
        print("❌ NVIDIA_API_KEY environment variable not set")
        sys.exit(1)
    
    print(f"🔗 Testing connection to: {base_url}")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print()
    
    # Test basic connectivity
    print("1️⃣ Testing basic API connectivity...")
    is_connected = await test_nvidia_api_connectivity(api_key, base_url)
    
    if not is_connected:
        print("❌ Basic connectivity test failed")
        sys.exit(1)
    else:
        print("✅ Basic connectivity test passed")
    
    print()
    
    # Test specific models
    test_models = [
        "nvidia/llama-3.1-8b-instruct",
        "nvidia/llama-3.1-70b-instruct", 
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "nvidia/mistral-7b-instruct-v0.3"
    ]
    
    print("2️⃣ Testing model availability...")
    print()
    
    results = {}
    for model in test_models:
        print(f"   Testing {model}...")
        result = await test_model_availability(api_key, base_url, model)
        results[model] = result
        
        if result["status"] == "available":
            print(f"   ✅ Available (latency: {result['latency_ms']}ms)")
        elif result["status"] == "timeout":
            print(f"   ⏰ Timeout")
        else:
            print(f"   ❌ Error: {result.get('error_message', 'Unknown error')}")
    
    print()
    print("📊 Test Summary:")
    print("-" * 30)
    
    available_count = sum(1 for r in results.values() if r["status"] == "available")
    total_count = len(results)
    
    print(f"Available models: {available_count}/{total_count}")
    
    if available_count > 0:
        avg_latency = sum(
            r["latency_ms"] for r in results.values() 
            if r["status"] == "available" and "latency_ms" in r
        ) / available_count
        print(f"Average latency: {avg_latency:.2f}ms")
    
    print()
    
    if available_count == total_count:
        print("🎉 All models are available!")
        sys.exit(0)
    elif available_count > 0:
        print("⚠️  Some models are unavailable")
        sys.exit(0)
    else:
        print("❌ No models are available")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
