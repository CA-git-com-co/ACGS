"""
PGC Service client for EC Service integration.

Provides interface for communicating with the Policy Governance & Compliance service
for policy enforcement and WINA optimization insights.
"""

import logging
from typing import Any

import httpx

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Try to import shared config, fallback to default if not available
try:
    import os
    import sys

    # Add the correct path to services/shared
    current_dir = os.path.dirname(os.path.abspath(__file__))
    shared_path = os.path.join(
        current_dir, "..", "..", "..", "..", "services", "shared"
    )
    sys.path.insert(0, os.path.abspath(shared_path))

    from config import get_config
except ImportError:
    # Fallback configuration
    def get_config():
        return {
            "ac_service_url": "http://localhost:8001",
            "gs_service_url": "http://localhost:8004",
            "pgc_service_url": "http://localhost:8005",
        }


logger = logging.getLogger(__name__)
config = get_config()


class PGCServiceClient:
    """Client for communicating with PGC Service."""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.base_url = config.get("pgc_service_url", "http://localhost:8005")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Content-Type": "application/json"},
        )

    async def close(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Close the HTTP client."""
        await self.client.aclose()

    async def evaluate_policy_compliance(
        self,
        proposal: dict[str, Any],
        policies: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate policy compliance for EC proposal.

        Args:
            proposal: EC proposal to evaluate
            policies: Applicable policies
            context: Optional evaluation context

        Returns:
            Policy compliance evaluation result
        """
        try:
            request_data = {
                "proposal": proposal,
                "policies": policies,
                "context": context or {},
                "source": "ec_service",
            }

            response = await self.client.post(
                "/api/v1/enforcement/evaluate", json=request_data
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Policy compliance evaluation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in policy evaluation: {e}")
            raise

    async def get_wina_enforcement_metrics(self) -> dict[str, Any]:
        """
        Get WINA enforcement optimization metrics.

        Returns:
            WINA enforcement metrics
        """
        try:
            response = await self.client.get("/api/v1/enforcement/wina-metrics")
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get WINA enforcement metrics: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting WINA metrics: {e}")
            raise

    async def enforce_alphaevolve_policies(
        self, proposals: list[dict[str, Any]], enforcement_context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Enforce AlphaEvolve policies with WINA optimization.

        Args:
            proposals: EC proposals for enforcement
            enforcement_context: Enforcement context

        Returns:
            Enforcement result
        """
        try:
            request_data = {
                "proposals": proposals,
                "context": enforcement_context,
                "optimization_enabled": True,
                "source": "ec_service",
            }

            response = await self.client.post(
                "/api/v1/alphaevolve/enforce", json=request_data
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"AlphaEvolve policy enforcement failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in policy enforcement: {e}")
            raise

    async def get_enforcement_strategies(
        self, context: str, optimization_hints: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Get available enforcement strategies for context.

        Args:
            context: Enforcement context
            optimization_hints: Optional WINA optimization hints

        Returns:
            List of available enforcement strategies
        """
        try:
            params = {"context": context}
            if optimization_hints:
                params["optimization_hints"] = optimization_hints

            response = await self.client.get(
                "/api/v1/enforcement/strategies", params=params
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get enforcement strategies: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting strategies: {e}")
            raise


# Global client instance
pgc_service_client = PGCServiceClient()
