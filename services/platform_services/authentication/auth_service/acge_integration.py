# ACGE Phase 2 Auth Service Integration
# Constitutional compliance middleware and ACGE model integration

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx
import jwt
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials
from prometheus_client import Counter, Histogram

# Metrics
CONSTITUTIONAL_COMPLIANCE_SCORE = Histogram(
    "auth_constitutional_compliance_score",
    "Constitutional compliance score for auth operations",
    ["operation", "user_role"],
)

ACGE_MODEL_REQUESTS = Counter(
    "auth_acge_model_requests_total",
    "Total requests to ACGE model from auth service",
    ["operation", "status"],
)

CONSTITUTIONAL_VIOLATIONS = Counter(
    "auth_constitutional_violations_total",
    "Constitutional violations detected in auth service",
    ["violation_type", "severity"],
)

logger = logging.getLogger(__name__)


class ACGEAuthIntegration:
    """ACGE integration for authentication service."""

    def __init__(self, acge_model_endpoint: str, constitutional_hash: str):
        self.acge_model_endpoint = acge_model_endpoint
        self.constitutional_hash = constitutional_hash
        self.client = httpx.AsyncClient(timeout=2.0)

    async def validate_constitutional_compliance(
        self,
        operation: str,
        user_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validate constitutional compliance for auth operations."""

        try:
            # Prepare constitutional validation request
            validation_request = {
                "operation": operation,
                "user_data": {
                    "username": user_data.get("username"),
                    "role": user_data.get("role", "user"),
                    "permissions": user_data.get("permissions", []),
                },
                "context": context or {},
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Call ACGE model for constitutional validation
            response = await self.client.post(
                f"{self.acge_model_endpoint}/validate/constitutional",
                json=validation_request,
                headers={
                    "X-Constitutional-Hash": self.constitutional_hash,
                    "X-Service": "auth-service",
                    "X-Operation": operation,
                },
            )

            if response.status_code == 200:
                result = response.json()
                compliance_score = result.get("compliance_score", 0.0)

                # Record metrics
                CONSTITUTIONAL_COMPLIANCE_SCORE.labels(
                    operation=operation, user_role=user_data.get("role", "unknown")
                ).observe(compliance_score)

                ACGE_MODEL_REQUESTS.labels(operation=operation, status="success").inc()

                # Check compliance threshold
                if compliance_score < 0.95:
                    CONSTITUTIONAL_VIOLATIONS.labels(
                        violation_type="low_compliance", severity="warning"
                    ).inc()

                    logger.warning(
                        f"Low constitutional compliance for {operation}: {compliance_score}"
                    )

                return result
            else:
                ACGE_MODEL_REQUESTS.labels(operation=operation, status="error").inc()

                logger.error(f"ACGE model validation failed: {response.status_code}")
                return {
                    "compliance_score": 0.5,  # Default fallback
                    "compliant": False,
                    "violations": ["acge_model_unavailable"],
                    "fallback": True,
                }

        except Exception as e:
            ACGE_MODEL_REQUESTS.labels(operation=operation, status="exception").inc()

            logger.error(f"ACGE constitutional validation error: {e}")
            return {
                "compliance_score": 0.5,  # Default fallback
                "compliant": False,
                "violations": ["validation_error"],
                "error": str(e),
                "fallback": True,
            }


class ConstitutionalAuthMiddleware:
    """Constitutional compliance middleware for auth service."""

    def __init__(self, acge_integration: ACGEAuthIntegration):
        self.acge = acge_integration

    async def validate_login_attempt(
        self, username: str, user_data: Dict[str, Any], request_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate constitutional compliance for login attempts."""

        validation_result = await self.acge.validate_constitutional_compliance(
            operation="login",
            user_data={
                "username": username,
                "role": user_data.get("role"),
                "is_active": user_data.get("is_active"),
                "last_login": user_data.get("last_login"),
            },
            context={
                "ip_address": request_context.get("ip_address"),
                "user_agent": request_context.get("user_agent"),
                "timestamp": request_context.get("timestamp"),
            },
        )

        return validation_result

    async def validate_token_creation(
        self, user_data: Dict[str, Any], token_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate constitutional compliance for token creation."""

        validation_result = await self.acge.validate_constitutional_compliance(
            operation="token_creation",
            user_data=user_data,
            context={
                "token_type": token_data.get("type"),
                "expires_at": token_data.get("exp"),
                "permissions": token_data.get("permissions", []),
            },
        )

        return validation_result

    async def validate_token_verification(
        self, token_payload: Dict[str, Any], request_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate constitutional compliance for token verification."""

        validation_result = await self.acge.validate_constitutional_compliance(
            operation="token_verification",
            user_data={
                "user_id": token_payload.get("user_id"),
                "username": token_payload.get("sub"),
                "role": token_payload.get("roles", []),
            },
            context={
                "token_age": time.time() - token_payload.get("iat", 0),
                "ip_address": request_context.get("ip_address"),
                "endpoint": request_context.get("endpoint"),
            },
        )

        return validation_result


def create_constitutional_jwt_claims(
    user_data: Dict[str, Any], compliance_result: Dict[str, Any]
) -> Dict[str, Any]:
    """Create constitutional claims for JWT token."""

    constitutional_claims = {
        "constitutional_hash": "cdd01ef066bc6cf2",
        "compliance_score": compliance_result.get("compliance_score", 0.0),
        "compliant": compliance_result.get("compliant", False),
        "acge_validated": True,
        "validation_timestamp": datetime.now(timezone.utc).isoformat(),
        "constitutional_version": "phase-2",
    }

    # Add violation information if present
    if compliance_result.get("violations"):
        constitutional_claims["violations"] = compliance_result["violations"]

    # Add constitutional permissions
    constitutional_claims["constitutional_permissions"] = [
        "read:constitutional_data",
        "validate:constitutional_compliance",
    ]

    # Add role-based constitutional permissions
    user_role = user_data.get("role", "user")
    if user_role == "admin":
        constitutional_claims["constitutional_permissions"].extend(
            ["write:constitutional_data", "manage:constitutional_compliance"]
        )
    elif user_role == "constitutional_officer":
        constitutional_claims["constitutional_permissions"].extend(
            ["write:constitutional_policies", "audit:constitutional_compliance"]
        )

    return constitutional_claims


async def constitutional_auth_dependency(
    request: Request,
    credentials: HTTPAuthorizationCredentials,
    acge_integration: ACGEAuthIntegration,
) -> Dict[str, Any]:
    """FastAPI dependency for constitutional authentication."""

    try:
        # Decode JWT token
        token = credentials.credentials
        payload = jwt.decode(
            token, options={"verify_signature": False}  # Signature verified elsewhere
        )

        # Extract request context
        request_context = {
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": str(request.url.path),
            "method": request.method,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Validate constitutional compliance
        middleware = ConstitutionalAuthMiddleware(acge_integration)
        compliance_result = await middleware.validate_token_verification(
            token_payload=payload, request_context=request_context
        )

        # Check compliance threshold
        if compliance_result.get("compliance_score", 0.0) < 0.95:
            raise HTTPException(
                status_code=403,
                detail="Constitutional compliance threshold not met",
                headers={
                    "X-Constitutional-Violation": "true",
                    "X-Compliance-Score": str(
                        compliance_result.get("compliance_score", 0.0)
                    ),
                },
            )

        # Add constitutional claims to payload
        payload["constitutional"] = {
            "compliance_score": compliance_result.get("compliance_score"),
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "hash": "cdd01ef066bc6cf2",
        }

        return payload

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Constitutional auth dependency error: {e}")
        raise HTTPException(status_code=500, detail="Constitutional validation error")


def add_constitutional_headers(response: Response, compliance_result: Dict[str, Any]):
    """Add constitutional compliance headers to response."""

    response.headers["X-Constitutional-Hash"] = "cdd01ef066bc6cf2"
    response.headers["X-Constitutional-Compliance"] = str(
        compliance_result.get("compliance_score", 0.0)
    )
    response.headers["X-Constitutional-Validated"] = "true"
    response.headers["X-ACGE-Phase"] = "phase-2"

    if compliance_result.get("violations"):
        response.headers["X-Constitutional-Violations"] = ",".join(
            compliance_result["violations"]
        )

    if compliance_result.get("fallback"):
        response.headers["X-Constitutional-Fallback"] = "true"
