"""
ACGS-1 Versioned Router Integration Examples

Demonstrates how to integrate the versioned router system with existing
ACGS-1 services, showing migration patterns and best practices.
"""

from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request

from ...api_models import APIResponse, APIStatus
from ..response_transformers import VersionedResponseBuilder
from ..version_manager import APIVersion
from ..versioned_router import (
    VersionedRouter,
    create_versioned_router,
    get_api_version,
    versioned_response,
)


# Example 1: Constitutional AI Service Integration
class ConstitutionalAIVersionedService:
    """Example integration for Constitutional AI service."""

    def __init__(self):
        self.router = create_versioned_router(
            service_name="constitutional-ai-service",
            current_version="v2.1.0",
            supported_versions=["v2.0.0", "v1.5.0"],
        )
        self.response_builder = VersionedResponseBuilder("constitutional-ai-service")

        # Register endpoints
        self._register_endpoints()

    def _register_endpoints(self):
        """Register version-specific endpoints."""

        # Version 1.5.0 - Legacy format
        @self.router.version("v1.5.0", "/principles", ["GET"])
        async def get_principles_v1_5(
            skip: int = 0, limit: int = 100, version: APIVersion = Depends(get_api_version)
        ):
            """Get principles in v1.5.0 format (snake_case fields)."""
            principles = await self._fetch_principles(skip, limit)

            # Transform to v1.5.0 format
            legacy_principles = []
            for principle in principles:
                legacy_principles.append(
                    {
                        "principle_id": principle["principleId"],
                        "created_at": principle["createdAt"],
                        "updated_at": principle["updatedAt"],
                        "content": principle["content"],
                    }
                )

            return {"principles": legacy_principles, "total_count": len(legacy_principles)}

        # Version 2.0.0 - Unified format
        @self.router.version("v2.0.0", "/principles", ["GET"])
        async def get_principles_v2_0(
            skip: int = 0, limit: int = 100, version: APIVersion = Depends(get_api_version)
        ):
            """Get principles in v2.0.0 format (camelCase fields)."""
            principles = await self._fetch_principles(skip, limit)

            return {"principles": principles, "totalCount": len(principles), "apiVersion": "v2.0.0"}

        # Version 2.1.0 - Enhanced format
        @self.router.version("v2.1.0", "/principles", ["GET"])
        @versioned_response()
        async def get_principles_v2_1(
            skip: int = 0, limit: int = 100, version: APIVersion = Depends(get_api_version)
        ):
            """Get principles in v2.1.0 format with enhanced metadata."""
            principles = await self._fetch_principles(skip, limit)

            return {
                "principles": principles,
                "totalCount": len(principles),
                "apiVersion": "v2.1.0",
                "metadata": {
                    "queryTime": "2025-06-22T10:00:00Z",
                    "performanceMetrics": {"dbQueryTime": 15.2, "transformationTime": 2.1},
                },
            }

        # Fallback handler for unsupported versions
        @self.router.fallback("/principles", ["GET"])
        async def get_principles_fallback():
            """Fallback for unsupported versions."""
            raise HTTPException(
                status_code=400,
                detail="API version not supported. Please use v1.5.0, v2.0.0, or v2.1.0",
            )

    async def _fetch_principles(self, skip: int, limit: int) -> List[Dict[str, Any]]:
        """Mock principle fetching (replace with actual database call)."""
        return [
            {
                "principleId": 1,
                "createdAt": "2025-06-22T10:00:00Z",
                "updatedAt": "2025-06-22T10:00:00Z",
                "content": "Respect human autonomy and dignity",
            },
            {
                "principleId": 2,
                "createdAt": "2025-06-22T10:00:00Z",
                "updatedAt": "2025-06-22T10:00:00Z",
                "content": "Ensure transparency in AI decision-making",
            },
        ]


# Example 2: Policy Governance Service Integration
class PolicyGovernanceVersionedService:
    """Example integration for Policy Governance service."""

    def __init__(self):
        self.router = create_versioned_router(
            service_name="policy-governance-service",
            current_version="v8.0.0",
            supported_versions=["v7.2.0"],
        )

    def register_endpoints(self):
        """Register policy governance endpoints."""

        # Version 7.2.0 - Legacy policy format
        @self.router.version("v7.2.0", "/policies", ["GET", "POST"])
        async def handle_policies_v7_2(
            request: Request, version: APIVersion = Depends(get_api_version)
        ):
            """Handle policies in v7.2.0 format."""
            if request.method == "GET":
                return await self._get_policies_v7_2()
            elif request.method == "POST":
                return await self._create_policy_v7_2(await request.json())

        # Version 8.0.0 - Enhanced policy format
        @self.router.version("v8.0.0", "/policies", ["GET", "POST"])
        async def handle_policies_v8_0(
            request: Request, version: APIVersion = Depends(get_api_version)
        ):
            """Handle policies in v8.0.0 format with quantum-inspired features."""
            if request.method == "GET":
                return await self._get_policies_v8_0()
            elif request.method == "POST":
                return await self._create_policy_v8_0(await request.json())

    async def _get_policies_v7_2(self) -> Dict[str, Any]:
        """Get policies in v7.2.0 format."""
        return {
            "policies": [
                {
                    "policy_id": "pol_123",
                    "name": "Data Privacy Policy",
                    "status": "active",
                    "created_at": "2025-06-22T10:00:00Z",
                }
            ],
            "count": 1,
        }

    async def _get_policies_v8_0(self) -> Dict[str, Any]:
        """Get policies in v8.0.0 format with quantum features."""
        return {
            "policies": [
                {
                    "policyId": "pol_123",
                    "name": "Data Privacy Policy",
                    "status": "active",
                    "createdAt": "2025-06-22T10:00:00Z",
                    "quantumHash": "cdd01ef066bc6cf2",
                    "semanticFaultTolerance": {"enabled": True, "confidence": 0.95},
                }
            ],
            "totalCount": 1,
            "quantumMetrics": {"coherenceLevel": 0.98, "entanglementStrength": 0.87},
        }

    async def _create_policy_v7_2(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create policy in v7.2.0 format."""
        return {
            "policy_id": "pol_124",
            "status": "created",
            "message": "Policy created successfully",
        }

    async def _create_policy_v8_0(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create policy in v8.0.0 format with quantum validation."""
        return {
            "policyId": "pol_124",
            "status": "created",
            "message": "Policy created with quantum validation",
            "quantumValidation": {
                "passed": True,
                "confidence": 0.97,
                "validationHash": "abc123def456",
            },
        }


# Example 3: FastAPI Application Integration
def create_versioned_app() -> FastAPI:
    """Create FastAPI application with versioned routing."""

    app = FastAPI(
        title="ACGS-1 Versioned API Example",
        description="Example of versioned API implementation",
        version="multi-version",
    )

    # Initialize versioned services
    constitutional_ai = ConstitutionalAIVersionedService()
    policy_governance = PolicyGovernanceVersionedService()
    policy_governance.register_endpoints()

    # Add version routing middleware
    from ..middleware.version_routing_middleware import VersionRoutingMiddleware
    from ..version_manager import VersionManager

    version_manager = VersionManager(service_name="example-service", current_version="v2.1.0")

    app.add_middleware(
        VersionRoutingMiddleware, service_name="example-service", version_manager=version_manager
    )

    # Include versioned routers
    for version_str, router in constitutional_ai.router.routers.items():
        app.include_router(router, prefix=f"/constitutional-ai")

    for version_str, router in policy_governance.router.routers.items():
        app.include_router(router, prefix=f"/policy-governance")

    # Add version info endpoint
    @app.get("/version-info")
    async def get_version_info():
        """Get comprehensive version information."""
        return {
            "constitutional_ai": constitutional_ai.router.get_version_info(),
            "policy_governance": policy_governance.router.get_version_info(),
        }

    # Add OpenAPI spec endpoint
    @app.get("/openapi-versioned")
    async def get_versioned_openapi():
        """Get versioned OpenAPI specification."""
        return {
            "constitutional_ai": constitutional_ai.router.create_openapi_spec(),
            "policy_governance": policy_governance.router.create_openapi_spec(),
        }

    return app


# Example 4: Migration Helper Functions
class MigrationHelper:
    """Helper functions for API version migrations."""

    @staticmethod
    def snake_to_camel_case(snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split("_")
        return components[0] + "".join(word.capitalize() for word in components[1:])

    @staticmethod
    def camel_to_snake_case(camel_str: str) -> str:
        """Convert camelCase to snake_case."""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_str)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @staticmethod
    def transform_dict_keys(data: Dict[str, Any], transformer: callable) -> Dict[str, Any]:
        """Transform dictionary keys using provided transformer function."""
        if not isinstance(data, dict):
            return data

        transformed = {}
        for key, value in data.items():
            new_key = transformer(key)
            if isinstance(value, dict):
                transformed[new_key] = MigrationHelper.transform_dict_keys(value, transformer)
            elif isinstance(value, list):
                transformed[new_key] = [
                    (
                        MigrationHelper.transform_dict_keys(item, transformer)
                        if isinstance(item, dict)
                        else item
                    )
                    for item in value
                ]
            else:
                transformed[new_key] = value

        return transformed

    @staticmethod
    def v1_to_v2_transform(data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform v1.x data to v2.x format."""
        # Convert snake_case to camelCase
        transformed = MigrationHelper.transform_dict_keys(data, MigrationHelper.snake_to_camel_case)

        # Add v2.x specific fields
        transformed["apiVersion"] = "v2.0.0"

        # Remove deprecated fields
        deprecated_fields = ["legacy_field", "deprecated_field"]
        for field in deprecated_fields:
            camel_field = MigrationHelper.snake_to_camel_case(field)
            transformed.pop(camel_field, None)

        return transformed

    @staticmethod
    def v2_to_v1_transform(data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform v2.x data to v1.x format for backward compatibility."""
        # Convert camelCase to snake_case
        transformed = MigrationHelper.transform_dict_keys(data, MigrationHelper.camel_to_snake_case)

        # Remove v2.x specific fields
        v2_fields = ["api_version", "quantum_hash", "semantic_fault_tolerance"]
        for field in v2_fields:
            transformed.pop(field, None)

        # Add legacy fields if needed
        if "user_id" in transformed:
            transformed["legacy_user_ref"] = transformed["user_id"]

        return transformed


# Usage example
if __name__ == "__main__":
    import uvicorn

    app = create_versioned_app()

    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
