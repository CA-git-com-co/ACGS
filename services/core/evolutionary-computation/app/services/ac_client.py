"""
AC Service client for EC Service integration.

Provides interface for communicating with the Audit & Compliance service
for constitutional principles and compliance verification.
"""

import logging
from typing import Any

import httpx

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


class ACServiceClient:
    """Client for communicating with AC Service."""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.base_url = config.get("ac_service_url", "http://localhost:8001")
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

    async def get_constitutional_principles(
        self, context: str | None = None, scope: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get constitutional principles for EC oversight.

        Args:
            context: Optional context filter
            scope: Optional scope filter

        Returns:
            List of constitutional principles
        """
        try:
            params = {}
            if context:
                params["context"] = context
            if scope:
                params["scope"] = scope

            response = await self.client.get("/api/v1/principles/", params=params)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get constitutional principles: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting principles: {e}")
            raise

    async def verify_constitutional_compliance(
        self, proposal: dict[str, Any], principles: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Verify constitutional compliance of an EC proposal.

        Args:
            proposal: EC proposal to verify
            principles: Applicable constitutional principles

        Returns:
            Compliance verification result
        """
        try:
            request_data = {"proposal": proposal, "principles": principles}

            response = await self.client.post(
                "/api/v1/principles/verify-compliance", json=request_data
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Constitutional compliance verification failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in compliance verification: {e}")
            raise

    async def get_fidelity_metrics(self) -> dict[str, Any]:
        """
        Get constitutional fidelity metrics.

        Returns:
            Constitutional fidelity metrics
        """
        try:
            response = await self.client.get("/api/v1/fidelity/metrics")
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get fidelity metrics: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting fidelity metrics: {e}")
            raise

    async def report_oversight_activity(
        self, activity_type: str, details: dict[str, Any], metrics: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Report EC oversight activity to AC service.

        Args:
            activity_type: Type of oversight activity
            details: Activity details
            metrics: Performance metrics

        Returns:
            Report acknowledgment
        """
        try:
            request_data = {
                "activity_type": activity_type,
                "details": details,
                "metrics": metrics,
                "source": "ec_service",
            }

            response = await self.client.post(
                "/api/v1/fidelity/report-activity", json=request_data
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to report oversight activity: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error reporting activity: {e}")
            raise


# Global client instance
ac_service_client = ACServiceClient()
