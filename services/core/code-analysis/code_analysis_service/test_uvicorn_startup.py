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


def test_uvicorn_startup():
    """Test that the service can start with uvicorn and respond to requests."""

    # Start the service
    process = None
    try:
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
        time.sleep(5)

        # Test health endpoint
        try:
            response = requests.get("http://localhost:8007/health", timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Check constitutional compliance
                if data.get("constitutional_hash") == "cdd01ef066bc6cf2":
                    pass
                else:
                    return False

                # Check headers
                constitutional_header = response.headers.get("X-Constitutional-Hash")
                if constitutional_header == "cdd01ef066bc6cf2":
                    pass
                else:
                    return False

            else:
                return False

        except requests.exceptions.RequestException:
            return False

        # Test OpenAPI docs
        try:
            response = requests.get("http://localhost:8007/docs", timeout=10)
            if response.status_code == 200:
                pass
            else:
                return False
        except requests.exceptions.RequestException:
            return False

        # Test API endpoint (should return 401 without auth)
        try:
            response = requests.get(
                "http://localhost:8007/api/v1/search/semantic?query=test", timeout=10
            )
            if response.status_code == 401:
                pass
            else:
                return False
        except requests.exceptions.RequestException:
            return False

        return True

    except Exception:
        return False

    finally:
        # Clean up
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def main():
    """Run uvicorn startup test."""

    success = test_uvicorn_startup()

    if success:
        pass
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
