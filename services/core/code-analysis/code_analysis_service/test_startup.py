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

    try:
        # Import main module
        import main

        # Get the app
        app = main.app

        return app is not None

    except Exception:
        return False


def test_health_endpoint():
    """Test the health endpoint using TestClient."""

    try:
        # Import main module
        import main

        # Create test client
        client = TestClient(main.app)

        # Test health endpoint
        response = client.get("/health")

        if response.status_code == 200:
            data = response.json()

            # Validate constitutional compliance
            return data.get("constitutional_hash") == "cdd01ef066bc6cf2"
        return False

    except Exception:
        return False


def test_api_endpoints():
    """Test basic API endpoints using TestClient."""

    try:
        # Import main module
        import main

        # Create test client
        client = TestClient(main.app)

        # Test semantic search endpoint (should return 401 without auth)
        response = client.get("/api/v1/search/semantic?query=test")

        # Test OpenAPI docs
        response = client.get("/docs")
        if response.status_code == 200:
            pass
        else:
            return False

        # Test OpenAPI JSON
        response = client.get("/openapi.json")
        if response.status_code == 200:
            response.json()
        else:
            return False

        return True

    except Exception:
        return False


def test_constitutional_compliance():
    """Test constitutional compliance in responses."""

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
                pass
            else:
                return False

            # Check response body
            data = response.json()
            body_hash = data.get("constitutional_hash")

            if body_hash == "cdd01ef066bc6cf2":
                pass
            else:
                return False

            return True
        return False

    except Exception:
        return False


def test_middleware_integration():
    """Test that middleware is properly integrated."""

    try:
        # Import main module
        import main

        # Check that middleware is added to the app
        app = main.app

        # Count middleware
        middleware_count = len(app.user_middleware)

        return middleware_count > 0

    except Exception:
        return False


async def test_service_dependencies():
    """Test service dependencies initialization."""

    try:
        from app.core.indexer import IndexerService
        from app.services.cache_service import CacheService
        from app.services.registry_service import ServiceRegistryClient
        from config.database import DatabaseManager

        # Test indexer service
        indexer = IndexerService()
        status = indexer.get_status()

        if "constitutional_hash" in status:
            pass
        else:
            return False

        # Test cache service (without connecting)
        cache = CacheService()
        if hasattr(cache, "key_prefix"):
            pass
        else:
            return False

        # Test service registry client
        registry = ServiceRegistryClient()
        if hasattr(registry, "service_name"):
            pass
        else:
            return False

        # Test database manager (without connecting)
        db = DatabaseManager()
        if hasattr(db, "host"):
            pass
        else:
            return False

        return True

    except Exception:
        return False


def main():
    """Run all startup tests."""

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

    if success:
        pass
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
