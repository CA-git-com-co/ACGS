"""
GS Service client for EC Service integration.

Provides interface for communicating with the Governance Synthesis service
for AlphaEvolve integration and constitutional governance operations.
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


class GSServiceClient:
    """Client for communicating with GS Service."""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.base_url = config.get("gs_service_url", "http://localhost:8004")
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

    async def evaluate_ec_governance(
        self,
        proposals: list[dict[str, Any]],
        context: str,
        optimization_hints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate EC proposals for constitutional compliance.

        Args:
            proposals: List of EC proposals to evaluate
            context: Context for the evaluation
            optimization_hints: Optional WINA optimization hints

        Returns:
            Governance evaluation response
        """
        try:
            request_data = {
                "proposals": proposals,
                "context": context,
                "optimization_hints": optimization_hints or {},
            }

            response = await self.client.post(
                "/api/v1/alphaevolve/governance-evaluation", json=request_data
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"GS Service governance evaluation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in governance evaluation: {e}")
            raise

    async def synthesize_ec_rules(
        self,
        ec_context: str,
        optimization_objective: str,
        constitutional_constraints: list[str],
        target_format: str = "rego",
    ) -> dict[str, Any]:
        """
        Synthesize governance rules for EC systems.

        Args:
            ec_context: EC system context
            optimization_objective: Optimization objective
            constitutional_constraints: Constitutional constraints
            target_format: Target format for rules

        Returns:
            Synthesized rules response
        """
        try:
            request_data = {
                "ec_context": ec_context,
                "optimization_objective": optimization_objective,
                "constitutional_constraints": constitutional_constraints,
                "target_format": target_format,
            }

            response = await self.client.post(
                "/api/v1/alphaevolve/synthesize-rules", json=request_data
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"GS Service rule synthesis failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in rule synthesis: {e}")
            raise

    async def get_wina_synthesis_metrics(self) -> dict[str, Any]:
        """
        Get WINA synthesis performance metrics.

        Returns:
            WINA synthesis metrics
        """
        try:
            response = await self.client.get("/api/v1/wina-rego-synthesis/metrics")
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get WINA synthesis metrics: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting WINA metrics: {e}")
            raise


# Global client instance
gs_service_client = GSServiceClient()
