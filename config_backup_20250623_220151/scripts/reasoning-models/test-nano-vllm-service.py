#!/usr/bin/env python3
"""
Test script for Nano-vLLM HTTP service.
Tests the FastAPI service endpoints without requiring Docker.
"""

import asyncio
import sys
import os
import time
import subprocess
import signal
from pathlib import Path
import requests
import json

# Add the services directory to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "services" / "reasoning-models"))

print("🚀 Testing Nano-vLLM HTTP Service")
print("=" * 50)

# Global process handle
service_process = None


def start_service():
    """Start the Nano-vLLM service in the background."""
    global service_process
    
    print("🔄 Starting Nano-vLLM service...")
    
    # Change to the service directory
    service_dir = project_root / "services" / "reasoning-models"
    
    # Start the service
    service_process = subprocess.Popen(
        [sys.executable, "nano-vllm-service.py"],
        cwd=service_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PORT": "8010", "LOG_LEVEL": "INFO"}
    )
    
    # Wait for service to start
    print("⏳ Waiting for service to start...")
    for i in range(30):
        try:
            response = requests.get("http://localhost:8010/health", timeout=2)
            if response.status_code == 200:
                print("✅ Service started successfully")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        print(f"   Attempt {i+1}/30...")
    
    print("❌ Service failed to start")
    return False


def stop_service():
    """Stop the Nano-vLLM service."""
    global service_process
    
    if service_process:
        print("🛑 Stopping service...")
        service_process.terminate()
        try:
            service_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            service_process.kill()
        service_process = None
        print("✅ Service stopped")


def test_health_endpoint():
    """Test the health endpoint."""
    print("\n🧪 Testing Health Endpoint...")
    
    try:
        response = requests.get("http://localhost:8010/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"   Status: {data.get('status')}")
            print(f"   Healthy: {data.get('healthy')}")
            print(f"   Models: {len(data.get('models', {}))}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False


def test_root_endpoint():
    """Test the root endpoint."""
    print("\n🧪 Testing Root Endpoint...")
    
    try:
        response = requests.get("http://localhost:8010/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Endpoints: {len(data.get('endpoints', {}))}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False


def test_chat_completion():
    """Test the chat completion endpoint."""
    print("\n🧪 Testing Chat Completion Endpoint...")
    
    try:
        payload = {
            "model": "nano-vllm",
            "messages": [
                {"role": "user", "content": "Hello, this is a test message."}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        response = requests.post(
            "http://localhost:8010/v1/chat/completions",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat completion working")
            print(f"   Model: {data.get('model')}")
            print(f"   Response: {data['choices'][0]['message']['content'][:80]}...")
            print(f"   Tokens: {data['usage']['total_tokens']}")
            return True
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat completion error: {e}")
        return False


def test_constitutional_reasoning():
    """Test the constitutional reasoning endpoint."""
    print("\n🧪 Testing Constitutional Reasoning Endpoint...")
    
    try:
        payload = {
            "content": "Should we implement mandatory data encryption for all user communications?",
            "domain": "privacy",
            "context": {
                "stakeholders": ["users", "administrators"],
                "current_policy": "optional encryption"
            },
            "max_tokens": 200
        }
        
        response = requests.post(
            "http://localhost:8010/v1/constitutional/reasoning",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Constitutional reasoning working")
            print(f"   Conclusion: {data.get('conclusion', '')[:80]}...")
            print(f"   Confidence: {data.get('confidence_score')}")
            print(f"   Reasoning steps: {len(data.get('reasoning_chain', []))}")
            print(f"   Processing time: {data.get('processing_time_ms')}ms")
            return True
        else:
            print(f"❌ Constitutional reasoning failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Constitutional reasoning error: {e}")
        return False


def test_performance():
    """Test service performance with multiple requests."""
    print("\n🧪 Testing Performance...")
    
    try:
        times = []
        
        for i in range(3):
            start_time = time.time()
            
            response = requests.get("http://localhost:8010/health", timeout=10)
            
            end_time = time.time()
            request_time = (end_time - start_time) * 1000
            times.append(request_time)
            
            print(f"   Request {i+1}: {request_time:.2f}ms")
        
        avg_time = sum(times) / len(times)
        print(f"✅ Average response time: {avg_time:.2f}ms")
        print(f"   Min: {min(times):.2f}ms, Max: {max(times):.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False


def main():
    """Run all tests."""
    try:
        # Start the service
        if not start_service():
            return 1
        
        # Run tests
        tests = [
            ("Health Endpoint", test_health_endpoint),
            ("Root Endpoint", test_root_endpoint),
            ("Chat Completion", test_chat_completion),
            ("Constitutional Reasoning", test_constitutional_reasoning),
            ("Performance", test_performance),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name} test PASSED")
                else:
                    print(f"❌ {test_name} test FAILED")
            except Exception as e:
                print(f"❌ {test_name} test ERROR: {e}")
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
            print("🎉 All tests passed! Nano-vLLM HTTP service is working correctly.")
            return 0
        else:
            print("⚠️  Some tests failed. Please check the output above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        return 1
    finally:
        # Always stop the service
        stop_service()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
