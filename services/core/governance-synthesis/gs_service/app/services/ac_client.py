"""
Constitutional AI Service Client - Updated to use shared client pattern
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
from typing import Any

from services.shared.service_clients.registry import get_service_client

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ACServiceClient:
    """
    Constitutional AI Service Client using shared service registry pattern.
    This eliminates circular dependencies between services.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._client = None

    async def _get_client(self):
        """Get the Constitutional AI client from the service registry"""
        if not self._client:
            self._client = await get_service_client("constitutional-ai")
        return self._client

    async def get_principle_by_id(
        self, principle_id: int, auth_token: str | None = None
    ) -> dict[str, Any] | None:
        """
        Fetches a single principle by its ID from the AC Service.
        """
        try:
            client = await self._get_client()
            if not client:
                self.logger.error("Constitutional AI client not available")
                return None

            return await client.request("GET", f"/api/v1/principles/{principle_id}")
        except Exception as e:
            self.logger.exception(f"Error fetching principle {principle_id}: {e}")
            return None

    async def list_principles(
        self, auth_token: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Fetches all principles from the AC Service.
        """
        try:
            client = await self._get_client()
            if not client:
                self.logger.error("Constitutional AI client not available")
                return []

            response = await client.request("GET", "/api/v1/principles")
            return response.get("principles", [])
        except Exception as e:
            self.logger.exception(f"Error listing principles: {e}")
            return []

    async def get_principles_for_context(
        self,
        context: str,
        category: str | None = None,
        auth_token: str | None = None,
    ) -> list[ACPrinciple]:
        """
        Get active principles applicable to a specific context.
        Uses the new enhanced AC service endpoint.
        """
        return await self.get_principles_by_context(context, category, auth_token)

    async def get_principles_by_context(
        self,
        context: str,
        category: str | None = None,
        auth_token: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get active principles applicable to a specific context.
        Uses the new enhanced AC service endpoint.
        """
        try:
            client = await self._get_client()
            if not client:
                self.logger.error("Constitutional AI client not available")
                return []

            params = {"context": context}
            if category:
                params["category"] = category

            response = await client.request(
                "GET", "/api/v1/principles/context", params=params
            )
            return response.get("principles", [])
        except Exception as e:
            self.logger.exception(
                f"Error fetching principles for context {context}: {e}"
            )
            return []

    async def get_principles_by_category(
        self, category: str, auth_token: str | None = None
    ) -> list[dict[str, Any]]:
        """Get principles filtered by category."""
        try:
            client = await self._get_client()
            if not client:
                self.logger.error("Constitutional AI client not available")
                return []

            response = await client.request(
                "GET", f"/api/v1/principles/category/{category}"
            )
            return response.get("principles", [])
        except Exception as e:
            self.logger.exception(
                f"Error fetching principles by category {category}: {e}"
            )
            return []

    async def search_principles_by_keywords(
        self, keywords: list[str], auth_token: str | None = None
    ) -> list[dict[str, Any]]:
        """Search principles by keywords."""
        try:
            client = await self._get_client()
            if not client:
                self.logger.error("Constitutional AI client not available")
                return []

            response = await client.request(
                "POST", "/api/v1/principles/search", data={"keywords": keywords}
            )
            return response.get("principles", [])
        except Exception as e:
            self.logger.exception(f"Error searching principles by keywords: {e}")
            return []

    async def close(self):
        """Close the service client connection."""
        if self._client:
            await self._client.disconnect()
            self._client = None


# Global client instance
ac_service_client = ACServiceClient()

# Example Usage (for testing this file)
if __name__ == "__main__":

    async def test_ac_client():
        """Test the AC Service client with new shared client pattern."""

        try:
            # Test listing principles
            await ac_service_client.list_principles()

            # Test searching by keywords
            await ac_service_client.search_principles_by_keywords(
                ["fairness", "transparency"]
            )

            await ac_service_client.close()

        except Exception:
            pass
