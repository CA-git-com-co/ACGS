import os

import httpx

from ..schemas import IntegrityPolicyRule  # Using the schema defined in pgc_service

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Load environment variables
INTEGRITY_SERVICE_URL = os.getenv(
    "INTEGRITY_SERVICE_URL", "http://localhost:8002/api/v1"
)


class IntegrityServiceClient:
    def __init__(self, base_url: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.base_url = base_url
        timeout_config = httpx.Timeout(10.0, connect=5.0)
        # Initialize HTTP client with secure SSL verification
        # For development with self-signed certificates, set INTEGRITY_SERVICE_VERIFY_SSL=false
        verify_ssl = os.getenv("INTEGRITY_SERVICE_VERIFY_SSL", "true").lower() == "true"

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout_config,
            verify=verify_ssl,  # Secure by default, configurable for development
        )

    async def list_verified_policy_rules(
        self, auth_token: str | None = None
    ) -> list[IntegrityPolicyRule]:
        """
        Fetches all 'verified' policy rules from the Integrity Service.
        """
        headers = {}
        if auth_token:
            headers["Authorization"] = (
                f"Bearer {auth_token}"  # Assuming Bearer token auth for Integrity Service
            )

        try:
            # Integrity service endpoint for listing rules, with a query parameter for status
            response = await self.client.get(
                "/policies/", params={"status": "verified"}, headers=headers
            )
            response.raise_for_status()
            data = (
                response.json()
            )  # Integrity service returns {"rules": [...], "total": ...}

            # Ensure 'rules' key exists and is a list
            rules_data = data.get("rules", [])
            if not isinstance(rules_data, list):
                return []

            return [IntegrityPolicyRule(**rule) for rule in rules_data]
        except httpx.HTTPStatusError:
            return []
        except httpx.RequestError:
            return []
        except Exception:  # Catch other potential errors like JSON decoding
            return []

    async def close(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        await self.client.aclose()


# Global client instance
integrity_service_client = IntegrityServiceClient(base_url=INTEGRITY_SERVICE_URL)

# Example Usage (for testing this file)
if __name__ == "__main__":

    async def test_integrity_client_for_pgc():
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        # This test requires integrity_service to be running and have some 'verified' rules.

        # Placeholder token for Integrity Service (if its placeholder auth expects one)
        # The integrity_service placeholder auth uses "internal_service_token" for GET /policies/

        # print("\nListing verified policy rules...")
        # verified_rules = await integrity_service_client.list_verified_policy_rules(auth_token=test_auth_token)

        # if verified_rules:
        #     print(f"\nFetched {len(verified_rules)} verified policy rules:")
        #     for rule in verified_rules:
        #         print(f"  - ID: {rule.id}, Content: {rule.rule_content[:50]}..., Status: {rule.verification_status}")
        # else:
        #     print("\nNo verified policy rules found or an error occurred.")

        await integrity_service_client.close()

    # To run this test, ensure integrity_service is running.
    # asyncio.run(test_integrity_client_for_pgc())
