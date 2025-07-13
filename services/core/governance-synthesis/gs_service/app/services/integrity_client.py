import logging
import os
import pathlib

import httpx

from ..schemas import PolicyRule, PolicyRuleCreate

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Import auth utilities with multiple fallback paths
try:
    from services.shared.auth import get_auth_headers, get_service_token
except ImportError:
    try:
        # Try relative import from project root
        import os
        import sys

        project_root = pathlib.Path(
            os.path.join(pathlib.Path(__file__).parent, "../../../../..")
        ).resolve()
        if project_root not in sys.path:
            sys.path.append(project_root)
        from services.shared.auth import get_auth_headers, get_service_token
    except ImportError:
        # Final fallback - create stub functions
        logger.warning("Could not import auth utilities, using stub functions")

        async def get_service_token() -> str:
            return "internal_service_token"

        async def get_auth_headers(token: str | None = None) -> dict:
            return {"Authorization": f"Bearer {token or await get_service_token()}"}


logger = logging.getLogger(__name__)

# Load environment variables
INTEGRITY_SERVICE_URL = os.getenv(
    "INTEGRITY_SERVICE_URL", "http://integrity_service:8000/api/v1"
)


class IntegrityServiceClient:
    """Enhanced Integrity Service Client with real authentication and error handling."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        timeout_config = httpx.Timeout(30.0, connect=10.0)  # Increased timeouts
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout_config,
            headers={"Content-Type": "application/json"},
        )
        logger.info(f"Initialized Integrity Service Client for {base_url}")

    async def store_policy_rule(
        self,
        rule_data: PolicyRuleCreate,
        auth_token: str | None = None,
    ) -> PolicyRule | None:
        """
        Stores a new policy rule in the Integrity Service with real authentication.
        """
        # Use real authentication
        if not auth_token:
            auth_token = await get_service_token()

        headers = await get_auth_headers(auth_token)

        try:
            logger.info(f"Storing policy rule: {rule_data.rule_content[:50]}...")

            # Validate rule data before sending
            if not rule_data.rule_content or not rule_data.rule_content.strip():
                logger.error("Empty rule content provided")
                return None

            # The Integrity Service expects POST requests to /policies/
            response = await self.client.post(
                "/policies/", json=rule_data.model_dump(), headers=headers
            )
            response.raise_for_status()
            data = response.json()

            logger.info(f"Successfully stored policy rule with ID: {data.get('id')}")
            return PolicyRule(**data)

        except httpx.HTTPStatusError as e:
            logger.exception(
                f"HTTP error storing policy rule: {e.response.status_code} -"
                f" {e.response.text}"
            )
            # Attempt to parse error response for better debugging
            try:
                error_details = e.response.json()
                logger.exception(f"Error details: {error_details}")
            except Exception:
                pass  # Ignore if error response is not JSON
            return None

        except httpx.RequestError as e:
            logger.exception(f"Request error storing policy rule: {e}")
            return None

        except Exception as e:
            logger.exception(f"Unexpected error storing policy rule: {e}")
            return None

    async def get_policy_rule_by_id(
        self, rule_id: int, auth_token: str | None = None
    ) -> PolicyRule | None:
        """
        Fetches a policy rule by its ID from the Integrity Service with real authentication.
        """
        # Use real authentication
        if not auth_token:
            auth_token = await get_service_token()

        headers = await get_auth_headers(auth_token)

        try:
            logger.info(f"Fetching policy rule with ID: {rule_id}")

            response = await self.client.get(f"/policies/{rule_id}", headers=headers)
            response.raise_for_status()
            data = response.json()

            logger.info(f"Successfully fetched policy rule {rule_id}")
            return PolicyRule(**data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Policy rule {rule_id} not found")
            else:
                logger.exception(
                    f"HTTP error fetching rule {rule_id}: {e.response.status_code} -"
                    f" {e.response.text}"
                )
            return None

        except httpx.RequestError as e:
            logger.exception(f"Request error fetching rule {rule_id}: {e}")
            return None

        except Exception as e:
            logger.exception(f"Unexpected error fetching rule {rule_id}: {e}")
            return None

    async def get_all_policy_rules(
        self, auth_token: str | None = None
    ) -> list[PolicyRule]:
        """
        Fetches all policy rules from the Integrity Service.
        """
        # Use real authentication
        if not auth_token:
            auth_token = await get_service_token()

        headers = await get_auth_headers(auth_token)

        try:
            logger.info("Fetching all policy rules")

            response = await self.client.get("/policies/", headers=headers)
            response.raise_for_status()
            data = response.json()

            # Handle different response formats
            if isinstance(data, list):
                rules = [PolicyRule(**rule) for rule in data]
            elif isinstance(data, dict) and "rules" in data:
                rules = [PolicyRule(**rule) for rule in data["rules"]]
            elif isinstance(data, dict) and "policies" in data:
                rules = [PolicyRule(**rule) for rule in data["policies"]]
            else:
                logger.warning(f"Unexpected response format: {data}")
                rules = []

            logger.info(f"Successfully fetched {len(rules)} policy rules")
            return rules

        except httpx.HTTPStatusError as e:
            logger.exception(
                f"HTTP error fetching all policy rules: {e.response.status_code} -"
                f" {e.response.text}"
            )
            return []

        except httpx.RequestError as e:
            logger.exception(f"Request error fetching all policy rules: {e}")
            return []

        except Exception as e:
            logger.exception(f"Unexpected error fetching all policy rules: {e}")
            return []

    async def health_check(self) -> bool:
        """
        Check if the Integrity Service is healthy and reachable.
        """
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.exception(f"Health check failed: {e}")
            return False

    async def close(self):
        """Close the HTTP client connection."""
        await self.client.aclose()
        logger.info("Integrity Service Client closed")


# Factory function for creating client instances
def get_integrity_service_client(
    base_url: str | None = None,
) -> IntegrityServiceClient:
    """Factory function to create an Integrity Service client."""
    return IntegrityServiceClient(base_url or INTEGRITY_SERVICE_URL)


# Global client instance (for backward compatibility)
integrity_service_client = get_integrity_service_client()

# Example Usage (for testing this file)
if __name__ == "__main__":

    async def test_integrity_client():
        """Test the enhanced Integrity Service client."""

        client = IntegrityServiceClient(INTEGRITY_SERVICE_URL)

        try:
            # Test health check
            is_healthy = await client.health_check()

            if is_healthy:
                # Test fetching all rules
                await client.get_all_policy_rules()

                # Test creating a new rule
                new_rule_data = PolicyRuleCreate(
                    rule_content=(
                        "test_enhanced_rule(X) :- enhanced_condition(X),"
                        " constitutional_compliance(X)."
                    ),
                    source_principle_ids=[101, 102],
                )
                created_rule = await client.store_policy_rule(new_rule_data)

                if created_rule:

                    # Test fetching the created rule
                    fetched_rule = await client.get_policy_rule_by_id(created_rule.id)
                    if fetched_rule:
                        pass

        except Exception as e:
            logger.exception(f"Test failed with error: {e}")
        finally:
            await client.close()

    # Run the test
    # asyncio.run(test_integrity_client())
