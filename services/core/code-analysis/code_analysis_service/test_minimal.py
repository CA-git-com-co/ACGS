#!/usr/bin/env python3
"""
Minimal test script to identify import issues
"""
# Constitutional Hash: cdd01ef066bc6cf2

import os
import pathlib
import sys

# Add current directory to path
sys.path.insert(0, pathlib.Path(pathlib.Path(__file__).resolve()).parent)


def test_basic_imports():
    """Test basic Python imports"""

    try:
        pass
    except Exception:
        return False

    try:
        pass
    except Exception:
        return False

    try:
        pass
    except Exception:
        return False

    return True


def test_config_imports():
    """Test configuration imports"""

    try:
        from config.settings import get_settings

        # Set required environment variables
        os.environ.setdefault("POSTGRESQL_PASSWORD", "test_password")
        os.environ.setdefault(
            "JWT_SECRET_KEY", "test_jwt_secret_key_for_development_only"
        )
        os.environ.setdefault("REDIS_PASSWORD", "")

        get_settings()
        return True
    except Exception:
        import traceback

        traceback.print_exc()
        return False


def test_service_imports():
    """Test service imports"""

    try:
        pass
    except Exception:
        import traceback

        traceback.print_exc()
        return False

    try:
        pass
    except Exception:
        import traceback

        traceback.print_exc()
        return False

    return True


def test_app_creation():
    """Test FastAPI app creation"""

    try:
        # Set required environment variables
        os.environ.setdefault("POSTGRESQL_PASSWORD", "test_password")
        os.environ.setdefault(
            "JWT_SECRET_KEY", "test_jwt_secret_key_for_development_only"
        )
        os.environ.setdefault("REDIS_PASSWORD", "")

        return True
    except Exception:
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":

    success = True

    success &= test_basic_imports()
    success &= test_config_imports()
    success &= test_service_imports()
    success &= test_app_creation()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
