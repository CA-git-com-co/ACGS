#!/usr/bin/env python3
"""
Test script to verify the service can start with uvicorn and respond to requests.
"""

import os
import subprocess
import sys
import time

import requests

# Set environment variables for testing
os.environ.update({
    "POSTGRESQL_PASSWORD": "test_password",
    "POSTGRESQL_HOST": "localhost",
    "POSTGRESQL_PORT": "5439",
    "POSTGRESQL_DATABASE": "acgs_test",
    "POSTGRESQL_USER": "acgs_user",
    "REDIS_URL": "redis://localhost:6389",
    "AUTH_SERVICE_URL": "http://localhost:8016",
    "CONTEXT_SERVICE_URL": "http://localhost:8012",
    "SERVICE_REGISTRY_URL": "http://localhost:8001",
    "ENVIRONMENT": "development",
    "LOG_LEVEL": "INFO",
})


def test_uvicorn_startup():
    """Test that the service can start with uvicorn and respond to requests."""
    print("🚀 Testing ACGS Code Analysis Engine startup with uvicorn...")

    # Start the service
    process = None
    try:
        print("Starting service with uvicorn...")
        process = subprocess.Popen(
            [
                "python",
                "-m",
                "uvicorn",
                "main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8007",
                "--log-level",
                "info",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait for service to start
        print("Waiting for service to start...")
        time.sleep(5)

        # Test health endpoint
        print("Testing health endpoint...")
        try:
            response = requests.get("http://localhost:8007/health", timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health endpoint: {response.status_code}")
                print(f"✅ Service status: {data.get('status', 'unknown')}")
                print(f"✅ Service name: {data.get('service', 'unknown')}")
                print(
                    "✅ Constitutional hash:"
                    f" {data.get('constitutional_hash', 'missing')}"
                )

                # Check constitutional compliance
                if data.get("constitutional_hash") == "cdd01ef066bc6cf2":
                    print("✅ Constitutional compliance validated")
                else:
                    print("❌ Constitutional compliance validation failed")
                    return False

                # Check headers
                constitutional_header = response.headers.get("X-Constitutional-Hash")
                if constitutional_header == "cdd01ef066bc6cf2":
                    print("✅ Constitutional hash in response headers")
                else:
                    print(
                        "❌ Invalid constitutional hash in headers:"
                        f" {constitutional_header}"
                    )
                    return False

            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Health endpoint request failed: {e}")
            return False

        # Test OpenAPI docs
        print("Testing OpenAPI docs...")
        try:
            response = requests.get("http://localhost:8007/docs", timeout=10)
            if response.status_code == 200:
                print("✅ OpenAPI docs accessible")
            else:
                print(f"❌ OpenAPI docs failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ OpenAPI docs request failed: {e}")
            return False

        # Test API endpoint (should return 401 without auth)
        print("Testing API endpoint...")
        try:
            response = requests.get(
                "http://localhost:8007/api/v1/search/semantic?query=test", timeout=10
            )
            if response.status_code == 401:
                print("✅ API endpoint returns 401 (authentication required)")
            else:
                print(f"❌ API endpoint unexpected status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ API endpoint request failed: {e}")
            return False

        print("🎉 All uvicorn startup tests passed!")
        return True

    except Exception as e:
        print(f"❌ Uvicorn startup test failed: {e}")
        return False

    finally:
        # Clean up
        if process:
            print("Stopping service...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            print("Service stopped.")


def main():
    """Run uvicorn startup test."""
    print("🚀 ACGS Code Analysis Engine - Uvicorn Startup Test")
    print("=" * 60)

    success = test_uvicorn_startup()

    print("\n" + "=" * 60)
    if success:
        print("🎉 UVICORN STARTUP TEST PASSED!")
        print("✅ Service can start with uvicorn and respond to requests.")
        print("✅ Ready for integration testing with ACGS infrastructure.")
    else:
        print("❌ UVICORN STARTUP TEST FAILED!")
        print("❌ Service needs fixes before deployment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
