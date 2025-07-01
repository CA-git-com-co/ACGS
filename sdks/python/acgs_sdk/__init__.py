"""
ACGS Python SDK
Enterprise-grade Python SDK for Autonomous Coding Governance System
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

__version__ = "3.0.0"
__constitutional_hash__ = "cdd01ef066bc6cf2"


@dataclass
class ValidationResult:
    """Constitutional validation result"""

    validation_id: str
    compliant: bool
    compliance_score: float
    violations: List[str]
    recommendations: List[str]
    constitutional_hash: str
    processing_time_ms: float


@dataclass
class PolicyInfo:
    """Policy information"""

    id: str
    name: str
    version: str
    description: str
    rules_count: int


@dataclass
class GovernanceDecision:
    """Governance decision result"""

    decision: str
    confidence: float
    applied_policies: List[str]
    conditions: List[str]
    constitutional_compliance: bool


@dataclass
class VerificationResult:
    """Formal verification result"""

    verification_id: str
    status: str
    properties_verified: List[Dict[str, Any]]
    constitutional_compliance: bool
    verification_time_ms: float


class ACGSError(Exception):
    """Base ACGS SDK exception"""

    pass


class ValidationError(ACGSError):
    """Constitutional validation error"""

    pass


class AuthenticationError(ACGSError):
    """Authentication error"""

    pass


class RateLimitError(ACGSError):
    """Rate limit exceeded error"""

    pass


class ConstitutionalService:
    """Constitutional AI service client"""

    def __init__(self, client):
        self.client = client

    async def validate(
        self,
        content: str,
        policy_set: str = "enterprise_policies_v3",
        validation_level: str = "strict",
    ) -> ValidationResult:
        """Validate content against constitutional policies"""

        payload = {
            "content": content,
            "policy_set": policy_set,
            "validation_level": validation_level,
            "constitutional_hash": self.client.constitutional_hash,
        }

        response = await self.client._request(
            "POST", "/constitutional/validate", payload
        )

        return ValidationResult(
            validation_id=response["validation_id"],
            compliant=response["compliant"],
            compliance_score=response["compliance_score"],
            violations=response["violations"],
            recommendations=response["recommendations"],
            constitutional_hash=response["constitutional_hash"],
            processing_time_ms=response["processing_time_ms"],
        )

    async def list_policies(self) -> List[PolicyInfo]:
        """List available constitutional policies"""

        response = await self.client._request("GET", "/constitutional/policies")

        return [
            PolicyInfo(
                id=policy["id"],
                name=policy["name"],
                version=policy["version"],
                description=policy["description"],
                rules_count=policy["rules_count"],
            )
            for policy in response["policies"]
        ]

    async def create_policy(
        self, name: str, description: str, rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create new constitutional policy"""

        payload = {
            "name": name,
            "description": description,
            "rules": rules,
            "constitutional_hash": self.client.constitutional_hash,
        }

        return await self.client._request("POST", "/constitutional/policies", payload)


class GovernanceService:
    """Policy governance service client"""

    def __init__(self, client):
        self.client = client

    async def get_status(self) -> Dict[str, Any]:
        """Get governance system status"""
        return await self.client._request("GET", "/governance/status")

    async def evaluate(
        self, context: Dict[str, Any], policies: List[str]
    ) -> GovernanceDecision:
        """Evaluate governance decision"""

        payload = {
            "context": context,
            "policies": policies,
            "constitutional_hash": self.client.constitutional_hash,
        }

        response = await self.client._request("POST", "/governance/evaluate", payload)

        return GovernanceDecision(
            decision=response["decision"],
            confidence=response["confidence"],
            applied_policies=response["applied_policies"],
            conditions=response["conditions"],
            constitutional_compliance=response["constitutional_compliance"],
        )


class VerificationService:
    """Formal verification service client"""

    def __init__(self, client):
        self.client = client

    async def verify(
        self, content: str, verification_type: str, properties: List[str]
    ) -> VerificationResult:
        """Perform formal verification"""

        payload = {
            "content": content,
            "verification_type": verification_type,
            "properties": properties,
            "constitutional_hash": self.client.constitutional_hash,
        }

        response = await self.client._request("POST", "/verification/verify", payload)

        return VerificationResult(
            verification_id=response["verification_id"],
            status=response["status"],
            properties_verified=response["properties_verified"],
            constitutional_compliance=response["constitutional_compliance"],
            verification_time_ms=response["verification_time_ms"],
        )


class AuthService:
    """Authentication service client"""

    def __init__(self, client):
        self.client = client

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and obtain access token"""

        payload = {
            "username": username,
            "password": password,
            "constitutional_hash": self.client.constitutional_hash,
        }

        return await self.client._request("POST", "/auth/login", payload)

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""

        payload = {
            "refresh_token": refresh_token,
            "constitutional_hash": self.client.constitutional_hash,
        }

        return await self.client._request("POST", "/auth/refresh", payload)

    async def validate_token(self) -> Dict[str, Any]:
        """Validate current token"""
        return await self.client._request("GET", "/auth/validate")


class ACGSClient:
    """Main ACGS SDK client"""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://api.acgs.enterprise.com/v3",
        constitutional_hash: str = __constitutional_hash__,
        timeout: int = 30,
    ):
        """
        Initialize ACGS client

        Args:
            api_key: API key for authentication
            base_url: Base URL for ACGS API
            constitutional_hash: Constitutional hash for compliance validation
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.constitutional_hash = constitutional_hash
        self.timeout = timeout
        self.session = None

        # Initialize service clients
        self.constitutional = ConstitutionalService(self)
        self.governance = GovernanceService(self)
        self.verification = VerificationService(self)
        self.auth = AuthService(self)

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def _ensure_session(self):
        """Ensure HTTP session is created"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _request(
        self, method: str, endpoint: str, data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to ACGS API"""

        await self._ensure_session()

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "X-Constitutional-Hash": self.constitutional_hash,
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with self.session.request(
                method, url, headers=headers, json=data if data else None
            ) as response:

                # Handle rate limiting
                if response.status == 429:
                    raise RateLimitError("Rate limit exceeded")

                # Handle authentication errors
                if response.status == 401:
                    raise AuthenticationError("Authentication failed")

                # Handle validation errors
                if response.status == 422:
                    error_data = await response.json()
                    raise ValidationError(
                        f"Validation failed: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    )

                # Handle other client errors
                if 400 <= response.status < 500:
                    error_data = await response.json()
                    raise ACGSError(
                        f"Client error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    )

                # Handle server errors
                if response.status >= 500:
                    raise ACGSError(f"Server error: HTTP {response.status}")

                # Parse successful response
                response_data = await response.json()

                # Validate constitutional hash in response
                if "constitutional_hash" in response_data:
                    if response_data["constitutional_hash"] != self.constitutional_hash:
                        raise ValidationError(
                            "Constitutional hash mismatch in response"
                        )

                return response_data

        except aiohttp.ClientError as e:
            raise ACGSError(f"Network error: {str(e)}")


# Synchronous wrapper for backwards compatibility
class SyncACGSClient:
    """Synchronous wrapper for ACGS client"""

    def __init__(self, *args, **kwargs):
        self._client = ACGSClient(*args, **kwargs)
        self._loop = None

    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        return self._loop.run_until_complete(coro)

    def validate(self, content: str, **kwargs) -> ValidationResult:
        """Synchronous constitutional validation"""

        async def _validate():
            async with self._client as client:
                return await client.constitutional.validate(content, **kwargs)

        return self._run_async(_validate())

    def list_policies(self) -> List[PolicyInfo]:
        """Synchronous policy listing"""

        async def _list_policies():
            async with self._client as client:
                return await client.constitutional.list_policies()

        return self._run_async(_list_policies())

    def evaluate_governance(
        self, context: Dict[str, Any], policies: List[str]
    ) -> GovernanceDecision:
        """Synchronous governance evaluation"""

        async def _evaluate():
            async with self._client as client:
                return await client.governance.evaluate(context, policies)

        return self._run_async(_evaluate())

    def verify(
        self, content: str, verification_type: str, properties: List[str]
    ) -> VerificationResult:
        """Synchronous formal verification"""

        async def _verify():
            async with self._client as client:
                return await client.verification.verify(
                    content, verification_type, properties
                )

        return self._run_async(_verify())

    def close(self):
        """Close client resources"""
        if self._loop:
            self._loop.run_until_complete(self._client.close())
            self._loop.close()
            self._loop = None


# Convenience functions
async def validate_content(content: str, api_key: str, **kwargs) -> ValidationResult:
    """Convenience function for content validation"""
    async with ACGSClient(api_key=api_key) as client:
        return await client.constitutional.validate(content, **kwargs)


async def evaluate_governance(
    context: Dict[str, Any], policies: List[str], api_key: str
) -> GovernanceDecision:
    """Convenience function for governance evaluation"""
    async with ACGSClient(api_key=api_key) as client:
        return await client.governance.evaluate(context, policies)


# Export main classes and functions
__all__ = [
    "ACGSClient",
    "SyncACGSClient",
    "ValidationResult",
    "PolicyInfo",
    "GovernanceDecision",
    "VerificationResult",
    "ACGSError",
    "ValidationError",
    "AuthenticationError",
    "RateLimitError",
    "validate_content",
    "evaluate_governance",
]
