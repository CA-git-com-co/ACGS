#!/usr/bin/env python3
"""
Generate test JWT tokens for ACGS-1 authentication testing
"""

import time

import jwt

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Use the same secret key as the services
SECRET_KEY = "acgs-development-secret-key-2024-phase1-infrastructure-stabilization-jwt-token-signing"
ALGORITHM = "HS256"


def generate_admin_token():
    """Generate an admin JWT token for testing."""
    payload = {
        "sub": "admin",
        "user_id": "admin-user-id",
        "username": "admin",
        "roles": ["admin", "pgc_admin", "gs_admin", "internal_service"],
        "permissions": [
            "read:policies",
            "write:policies",
            "manage:governance",
            "system:admin",
            "constitutional:validate",
            "workflow:execute",
        ],
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,  # 1 hour expiration
        "jti": f"test-token-{int(time.time())}",
        "service": "test-client",
        "session_id": f"session-{int(time.time())}",
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def generate_user_token():
    """Generate a regular user JWT token for testing."""
    payload = {
        "sub": "user",
        "user_id": "user-id",
        "username": "user",
        "roles": ["user"],
        "permissions": ["read:policies"],
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,  # 1 hour expiration
        "jti": f"user-token-{int(time.time())}",
        "service": "test-client",
        "session_id": f"user-session-{int(time.time())}",
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


if __name__ == "__main__":
    print("🔑 ACGS-1 Test Token Generator")
    print("=" * 40)

    admin_token = generate_admin_token()
    user_token = generate_user_token()

    print("\n👑 Admin Token:")
    print(f"Bearer {admin_token}")

    print("\n👤 User Token:")
    print(f"Bearer {user_token}")

    print("\n📋 Test Commands:")
    print("# Test with admin token:")
    print(
        f'curl -H "Authorization: Bearer {admin_token}" http://localhost:8005/api/v1/workflows/policy-creation'
    )

    print("\n# Test with user token:")
    print(
        f'curl -H "Authorization: Bearer {user_token}" http://localhost:8005/api/v1/workflows/policy-creation'
    )

    print("\n# Test without token (should fail):")
    print("curl http://localhost:8005/api/v1/workflows/policy-creation")
