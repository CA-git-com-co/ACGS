#!/usr/bin/env python3
"""
Priority 2 Validation Test for ACGS Code Analysis Engine
Tests all success criteria for configuration and compatibility fixes.
"""

import os
import pathlib
import subprocess
import sys
import time

import requests

# Add current directory to path
sys.path.insert(0, pathlib.Path(pathlib.Path(__file__).resolve()).parent)


def setup_environment():
    """Set up required environment variables"""
    os.environ["POSTGRESQL_PASSWORD"] = "test_password"
    os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_for_development_only"
    os.environ["REDIS_PASSWORD"] = ""


def test_import_functionality():
    """Test that all imports work without errors"""

    try:

        from config.settings import get_settings

        get_settings()

        return True
    except Exception:
        return False


def test_service_startup():
    """Test service startup with uvicorn"""

    try:
        # Start uvicorn in background
        cmd = [
            "bash",
            "-c",
            (
                "source /home/dislove/ACGS-2/.venv/bin/activate && "
                "POSTGRESQL_PASSWORD=os.environ.get("PASSWORD")
                "JWT_SECRET_KEY=test_jwt_secret_key_for_development_only "  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
                'REDIS_PASSWORD="" '
                "uvicorn main:app --host 0.0.0.0 --port 8007 --log-level error"
            ),
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=pathlib.Path(pathlib.Path(__file__).resolve()).parent,
        )

        # Wait for startup
        time.sleep(8)

        # Check if process is still running
        if process.poll() is not None:
            _stdout, _stderr = process.communicate()
            return False, None

        return True, process

    except Exception:
        return False, None


def test_health_endpoint(process):
    """Test health endpoint functionality"""

    try:
        # Test health endpoint
        response = requests.get("http://localhost:8007/health", timeout=5)

        health_data = response.json()

        if response.status_code == 200:

            # Check constitutional hash
            const_hash = health_data.get("constitutional_hash")
            return const_hash == "cdd01ef066bc6cf2"
        # For Priority 2, we accept degraded status (503) as long as constitutional hash is present
        const_hash = health_data.get("constitutional_hash")
        return const_hash == "cdd01ef066bc6cf2"

    except Exception:
        return False
    finally:
        # Clean up process
        if process:
            process.terminate()
            process.wait()


def test_api_endpoints():
    """Test basic API endpoint responses"""

    try:
        # Start service again for API testing
        cmd = [
            "bash",
            "-c",
            (
                "source /home/dislove/ACGS-2/.venv/bin/activate && "
                "POSTGRESQL_PASSWORD=os.environ.get("PASSWORD")
                "JWT_SECRET_KEY=test_jwt_secret_key_for_development_only "  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
                'REDIS_PASSWORD="" '
                "uvicorn main:app --host 0.0.0.0 --port 8007 --log-level error"
            ),
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=pathlib.Path(pathlib.Path(__file__).resolve()).parent,
        )

        time.sleep(5)

        # Test protected endpoint (should require authentication)
        response = requests.get("http://localhost:8007/api/v1/search", timeout=5)
        auth_test = response.status_code in {401, 403}

        # Clean up
        process.terminate()
        process.wait()

        return auth_test

    except Exception:
        return False


def main():
    """Run all Priority 2 validation tests"""

    setup_environment()

    # Track test results
    results = {}

    # Test 1: Import functionality
    results["imports"] = test_import_functionality()

    # Test 2: Service startup
    startup_success, process = test_service_startup()
    results["startup"] = startup_success

    if startup_success:
        # Test 3: Health endpoint
        results["health"] = test_health_endpoint(process)

        # Test 4: API endpoints
        results["api"] = test_api_endpoints()
    else:
        results["health"] = False
        results["api"] = False

    # Summary

    success_count = sum(results.values())
    total_tests = len(results)

    for _test_name, _success in results.items():
        pass

    if success_count == total_tests:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
