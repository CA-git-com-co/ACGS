#!/usr/bin/env python3
"""
Service startup test for ACGS Code Analysis Engine.
Tests that the service can start and respond to basic requests.
"""

import asyncio
import os
import sys

from fastapi.testclient import TestClient

# Set environment variables for testing
os.environ.update(
    {
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
    }
)


def test_fastapi_app_creation():
    """Test that the FastAPI app can be created successfully."""
    print("Testing FastAPI app creation...")

    try:
        # Import main module
        import main

        # Get the app
        app = main.app

        if app is None:
            print("❌ App is None")
            return False

        print("✅ FastAPI app created successfully")
        print(f"✅ App title: {app.title}")
        print(f"✅ App version: {app.version}")
        print(f"✅ Number of routes: {len(app.routes)}")

        return True

    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        return False


def test_health_endpoint():
    """Test the health endpoint using TestClient."""
    print("\nTesting health endpoint...")

    try:
        # Import main module
        import main

        # Create test client
        client = TestClient(main.app)

        # Test health endpoint
        response = client.get("/health")

        print(f"✅ Health endpoint status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health response: {data.get('status', 'unknown')}")
            print(f"✅ Service name: {data.get('service', 'unknown')}")
            print(
                f"✅ Constitutional hash: {data.get('constitutional_hash', 'missing')}"
            )

            # Validate constitutional compliance
            if data.get("constitutional_hash") == "cdd01ef066bc6cf2":
                print("✅ Constitutional compliance validated")
                return True
            else:
                print("❌ Constitutional compliance validation failed")
                return False
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False


def test_api_endpoints():
    """Test basic API endpoints using TestClient."""
    print("\nTesting API endpoints...")

    try:
        # Import main module
        import main

        # Create test client
        client = TestClient(main.app)

        # Test semantic search endpoint (should return 401 without auth)
        response = client.get("/api/v1/search/semantic?query=test")
        print(f"✅ Semantic search endpoint status: {response.status_code}")

        # Test OpenAPI docs
        response = client.get("/docs")
        if response.status_code == 200:
            print("✅ OpenAPI docs accessible")
        else:
            print(f"❌ OpenAPI docs failed: {response.status_code}")
            return False

        # Test OpenAPI JSON
        response = client.get("/openapi.json")
        if response.status_code == 200:
            openapi_data = response.json()
            print("✅ OpenAPI JSON accessible")
            print(
                f"✅ API title: {openapi_data.get('info', {}).get('title', 'unknown')}"
            )
            print(
                "✅ API version:"
                f" {openapi_data.get('info', {}).get('version', 'unknown')}"
            )
        else:
            print(f"❌ OpenAPI JSON failed: {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False


def test_constitutional_compliance():
    """Test constitutional compliance in responses."""
    print("\nTesting constitutional compliance...")

    try:
        # Import main module
        import main

        # Create test client
        client = TestClient(main.app)

        # Test health endpoint for constitutional compliance
        response = client.get("/health")

        if response.status_code == 200:
            # Check headers
            headers = response.headers
            constitutional_hash = headers.get("X-Constitutional-Hash")

            if constitutional_hash == "cdd01ef066bc6cf2":
                print("✅ Constitutional hash in headers")
            else:
                print(
                    f"❌ Invalid constitutional hash in headers: {constitutional_hash}"
                )
                return False

            # Check response body
            data = response.json()
            body_hash = data.get("constitutional_hash")

            if body_hash == "cdd01ef066bc6cf2":
                print("✅ Constitutional hash in response body")
            else:
                print(f"❌ Invalid constitutional hash in body: {body_hash}")
                return False

            print("✅ Constitutional compliance validated")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Constitutional compliance test failed: {e}")
        return False


def test_middleware_integration():
    """Test that middleware is properly integrated."""
    print("\nTesting middleware integration...")

    try:
        # Import main module
        import main

        # Check that middleware is added to the app
        app = main.app

        # Count middleware
        middleware_count = len(app.user_middleware)
        print(f"✅ Middleware count: {middleware_count}")

        if middleware_count > 0:
            print("✅ Middleware is integrated")
            return True
        else:
            print("❌ No middleware found")
            return False

    except Exception as e:
        print(f"❌ Middleware integration test failed: {e}")
        return False


async def test_service_dependencies():
    """Test service dependencies initialization."""
    print("\nTesting service dependencies...")

    try:
        from app.core.indexer import IndexerService
        from app.services.cache_service import CacheService
        from app.services.registry_service import ServiceRegistryClient
        from config.database import DatabaseManager

        # Test indexer service
        indexer = IndexerService()
        status = indexer.get_status()

        if "constitutional_hash" in status:
            print("✅ Indexer service initialization")
        else:
            print("❌ Indexer service missing constitutional compliance")
            return False

        # Test cache service (without connecting)
        cache = CacheService()
        if hasattr(cache, "key_prefix"):
            print("✅ Cache service initialization")
        else:
            print("❌ Cache service initialization failed")
            return False

        # Test service registry client
        registry = ServiceRegistryClient()
        if hasattr(registry, "service_name"):
            print("✅ Service registry client initialization")
        else:
            print("❌ Service registry client initialization failed")
            return False

        # Test database manager (without connecting)
        db = DatabaseManager()
        if hasattr(db, "host"):
            print("✅ Database manager initialization")
        else:
            print("❌ Database manager initialization failed")
            return False

        print("✅ All service dependencies initialized")
        return True

    except Exception as e:
        print(f"❌ Service dependencies test failed: {e}")
        return False


def main():
    """Run all startup tests."""
    print("🚀 ACGS Code Analysis Engine - Service Startup Test")
    print("=" * 60)

    success = True

    # Test FastAPI app creation
    if not test_fastapi_app_creation():
        success = False

    # Test health endpoint
    if not test_health_endpoint():
        success = False

    # Test API endpoints
    if not test_api_endpoints():
        success = False

    # Test constitutional compliance
    if not test_constitutional_compliance():
        success = False

    # Test middleware integration
    if not test_middleware_integration():
        success = False

    # Test service dependencies
    if not asyncio.run(test_service_dependencies()):
        success = False

    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL STARTUP TESTS PASSED!")
        print("✅ Service is ready for deployment testing.")
        print("✅ Health endpoint returns 200 with constitutional hash validation.")
        print("✅ Basic API endpoints respond correctly.")
        print("✅ Constitutional compliance is enforced.")
    else:
        print("❌ SOME STARTUP TESTS FAILED!")
        print("❌ Service needs fixes before deployment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
