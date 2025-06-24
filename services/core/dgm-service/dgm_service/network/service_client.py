"""
ACGS Service Client for DGM Service.

Provides HTTP client functionality for communicating with all ACGS core services
with authentication, retries, circuit breaker, and monitoring.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..config import settings
from .circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class ACGSServiceClient:
    """HTTP client for ACGS services with resilience patterns."""

    def __init__(self):
        self.timeout = httpx.Timeout(settings.MODEL_TIMEOUT)
        self.circuit_breakers = {}
        self.service_urls = {
            "auth": settings.AUTH_SERVICE_URL,
            "ac": settings.AC_SERVICE_URL,
            "integrity": settings.INTEGRITY_SERVICE_URL,
            "fv": settings.FV_SERVICE_URL,
            "gs": settings.GS_SERVICE_URL,
            "pgc": settings.PGC_SERVICE_URL,
            "ec": settings.EC_SERVICE_URL,
        }

        # Initialize circuit breakers for each service
        for service_name in self.service_urls.keys():
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=5, recovery_timeout=30, expected_exception=httpx.RequestError
            )

    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for service-to-service communication."""
        # In production, this would use service account tokens or mTLS
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "DGM-Service/1.0.0",
            "X-Service-Name": "dgm-service",
        }

        # Add service authentication token if available
        if hasattr(settings, "SERVICE_TOKEN") and settings.SERVICE_TOKEN:
            headers["Authorization"] = f"Bearer {settings.SERVICE_TOKEN}"

        return headers

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
    async def _make_request(
        self,
        service_name: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retries and circuit breaker."""
        if service_name not in self.service_urls:
            raise ValueError(f"Unknown service: {service_name}")

        base_url = self.service_urls[service_name]
        url = urljoin(base_url, endpoint)
        headers = await self._get_auth_headers()

        circuit_breaker = self.circuit_breakers[service_name]

        async def make_call():
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method, url=url, json=data, params=params, headers=headers
                )
                response.raise_for_status()
                return response.json()

        try:
            return await circuit_breaker.call(make_call)
        except Exception as e:
            logger.error(f"Request to {service_name} failed: {e}")
            raise

    # Auth Service Methods
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token with Auth Service."""
        return await self._make_request(
            "auth", "POST", "/api/v1/auth/validate", data={"token": token}
        )

    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions from Auth Service."""
        response = await self._make_request("auth", "GET", f"/api/v1/users/{user_id}/permissions")
        return response.get("permissions", [])

    # Constitutional AI Service Methods
    async def validate_constitutional_compliance(
        self, improvement_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate constitutional compliance with AC Service."""
        return await self._make_request(
            "ac", "POST", "/api/v1/constitutional/validate", data=improvement_data
        )

    async def get_constitutional_principles(self) -> List[Dict[str, Any]]:
        """Get constitutional principles from AC Service."""
        response = await self._make_request("ac", "GET", "/api/v1/principles")
        return response.get("principles", [])

    # Governance Synthesis Service Methods
    async def synthesize_policy(
        self, principles: List[str], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize policy using GS Service."""
        return await self._make_request(
            "gs",
            "POST",
            "/api/v1/synthesis/policy",
            data={"principles": principles, "context": context},
        )

    async def evaluate_improvement_impact(
        self, improvement_id: str, changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate improvement impact using GS Service."""
        return await self._make_request(
            "gs",
            "POST",
            "/api/v1/evaluation/impact",
            data={"improvement_id": improvement_id, "changes": changes},
        )

    # Formal Verification Service Methods
    async def verify_improvement_safety(self, improvement_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Verify improvement safety using FV Service."""
        return await self._make_request(
            "fv", "POST", "/api/v1/verification/safety", data=improvement_spec
        )

    async def check_invariants(
        self, system_state: Dict[str, Any], invariants: List[str]
    ) -> Dict[str, Any]:
        """Check system invariants using FV Service."""
        return await self._make_request(
            "fv",
            "POST",
            "/api/v1/verification/invariants",
            data={"system_state": system_state, "invariants": invariants},
        )

    # Policy Governance & Compliance Service Methods
    async def enforce_policy(self, policy_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce policy using PGC Service."""
        return await self._make_request(
            "pgc",
            "POST",
            "/api/v1/enforcement/policy",
            data={"policy_id": policy_id, "context": context},
        )

    async def log_compliance_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log compliance event using PGC Service."""
        return await self._make_request("pgc", "POST", "/api/v1/compliance/log", data=event_data)

    # Executive Council Service Methods
    async def request_oversight_approval(
        self, improvement_proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Request oversight approval from EC Service."""
        return await self._make_request(
            "ec", "POST", "/api/v1/oversight/approval", data=improvement_proposal
        )

    async def report_performance_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Report performance metrics to EC Service."""
        return await self._make_request("ec", "POST", "/api/v1/metrics/report", data=metrics)

    # Integrity Service Methods
    async def create_audit_log(self, action: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create audit log entry using Integrity Service."""
        return await self._make_request(
            "integrity", "POST", "/api/v1/audit/log", data={"action": action, "details": details}
        )

    async def verify_data_integrity(self, data_hash: str, signature: str) -> Dict[str, Any]:
        """Verify data integrity using Integrity Service."""
        return await self._make_request(
            "integrity",
            "POST",
            "/api/v1/integrity/verify",
            data={"data_hash": data_hash, "signature": signature},
        )

    # Health check methods
    async def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy."""
        try:
            await self._make_request(service_name, "GET", "/health")
            return True
        except Exception:
            return False

    async def check_all_services_health(self) -> Dict[str, bool]:
        """Check health of all ACGS services."""
        health_status = {}

        tasks = [
            (service_name, self.check_service_health(service_name))
            for service_name in self.service_urls.keys()
        ]

        results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)

        for (service_name, _), result in zip(tasks, results):
            health_status[service_name] = result if isinstance(result, bool) else False

        return health_status

    async def close(self):
        """Close all circuit breakers and cleanup resources."""
        for circuit_breaker in self.circuit_breakers.values():
            await circuit_breaker.close()
