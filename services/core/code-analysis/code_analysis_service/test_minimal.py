#!/usr/bin/env python3
"""
Minimal test script to identify import issues
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_basic_imports():
    """Test basic Python imports"""
    print("Testing basic imports...")

    try:
        print("✓ FastAPI imported")
    except Exception as e:
        print(f"✗ FastAPI failed: {e}")
        return False

    try:
        print("✓ Uvicorn imported")
    except Exception as e:
        print(f"✗ Uvicorn failed: {e}")
        return False

    try:
        print("✓ Pydantic imported")
    except Exception as e:
        print(f"✗ Pydantic failed: {e}")
        return False

    return True


def test_config_imports():
    """Test configuration imports"""
    print("\nTesting config imports...")

    try:
        from config.settings import get_settings

        print("✓ Settings imported")

        # Set required environment variables
        os.environ.setdefault("POSTGRESQL_PASSWORD", "test_password")
        os.environ.setdefault(
            "JWT_SECRET_KEY", "test_jwt_secret_key_for_development_only"
        )
        os.environ.setdefault("REDIS_PASSWORD", "")

        settings = get_settings()
        print("✓ Settings instantiated")
        print(f"  - Host: {settings.host}")
        print(f"  - Port: {settings.port}")
        print(f"  - Environment: {settings.environment}")
        return True
    except Exception as e:
        print(f"✗ Config failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_service_imports():
    """Test service imports"""
    print("\nTesting service imports...")

    try:
        print("✓ CacheService imported")
    except Exception as e:
        print(f"✗ CacheService failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    try:
        print("✓ ServiceRegistryClient imported")
    except Exception as e:
        print(f"✗ ServiceRegistryClient failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def test_app_creation():
    """Test FastAPI app creation"""
    print("\nTesting app creation...")

    try:
        # Set required environment variables
        os.environ.setdefault("POSTGRESQL_PASSWORD", "test_password")
        os.environ.setdefault(
            "JWT_SECRET_KEY", "test_jwt_secret_key_for_development_only"
        )
        os.environ.setdefault("REDIS_PASSWORD", "")

        from main import app

        print("✓ Main app imported successfully")
        print(f"  - App title: {app.title}")
        return True
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("ACGS Code Analysis Engine - Import Test")
    print("=" * 50)

    success = True

    success &= test_basic_imports()
    success &= test_config_imports()
    success &= test_service_imports()
    success &= test_app_creation()

    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)
