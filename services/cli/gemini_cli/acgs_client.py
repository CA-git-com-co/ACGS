"""
ACGS Client wrapper for Gemini CLI integration
"""

import logging
from datetime import datetime

import requests
from gemini_config import get_config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class ACGSClient:
    """Client for interacting with ACGS services"""

    def __init__(self, config=None):
        self.config = config or get_config()
        self.session = self._create_session()
        self.agent_id = None
        self.api_key = None

    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic"""
        session = requests.Session()
        retry = Retry(
            total=self.config.max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            max_retries=retry, pool_maxsize=self.config.connection_pool_size
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _get_headers(self) -> dict[str, str]:
        """Get common headers for requests"""
        headers = {
            "Content-Type": "application/json",
            "X-Constitutional-Hash": self.config.constitutional_hash,
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    # Agent Management

    def create_agent(self, name: str, agent_type: str, capabilities: list[str]) -> dict:
        """Create a new agent in the system"""
        url = f"{self.config.auth_service_url}/api/v1/agents"
        data = {
            "name": name,
            "type": agent_type,
            "capabilities": capabilities,
            "metadata": {
                "created_by": "gemini_cli",
                "purpose": "Constitutional AI agent managed by Gemini CLI",
            },
        }

        response = self.session.post(
            url,
            json=data,
            headers=self._get_headers(),
            timeout=self.config.request_timeout,
        )
        response.raise_for_status()
        result = response.json()

        # Store agent credentials
        self.agent_id = result["agent_id"]
        self.api_key = result["api_key"]

        logger.info(f"Created agent: {self.agent_id}")
        return result

    def list_agents(self) -> list[dict]:
        """List all agents"""
        url = f"{self.config.auth_service_url}/api/v1/agents"
        response = self.session.get(
            url, headers=self._get_headers(), timeout=self.config.request_timeout
        )
        response.raise_for_status()
        return response.json()

    def get_agent(self, agent_id: str) -> dict:
        """Get agent details"""
        url = f"{self.config.auth_service_url}/api/v1/agents/{agent_id}"
        response = self.session.get(
            url, headers=self._get_headers(), timeout=self.config.request_timeout
        )
        response.raise_for_status()
        return response.json()

    # Operation Management

    def submit_operation(
        self, operation_type: str, parameters: dict, agent_id: str | None = None
    ) -> dict:
        """Submit an operation to the ACGS coordinator"""
        url = f"{self.config.acgs_coordinator_url}/api/v1/operations"

        data = {
            "agent_id": agent_id or self.agent_id,
            "operation_type": operation_type,
            "parameters": parameters,
            "governance_params": {
                "require_constitutional_check": self.config.enforce_constitutional,
                "require_hitl_review": operation_type
                in ["code_generation", "system_modification"],
                "sandbox_execution": True,
            },
        }

        response = self.session.post(
            url,
            json=data,
            headers=self._get_headers(),
            timeout=self.config.request_timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_operation_status(self, operation_id: str) -> dict:
        """Get status of an operation"""
        url = f"{self.config.acgs_coordinator_url}/api/v1/operations/{operation_id}"
        response = self.session.get(
            url, headers=self._get_headers(), timeout=self.config.request_timeout
        )
        response.raise_for_status()
        return response.json()

    def list_agent_operations(self, agent_id: str | None = None) -> list[dict]:
        """List operations for an agent"""
        agent_id = agent_id or self.agent_id
        url = f"{self.config.acgs_coordinator_url}/api/v1/agents/{agent_id}/operations"
        response = self.session.get(
            url, headers=self._get_headers(), timeout=self.config.request_timeout
        )
        response.raise_for_status()
        return response.json()

    # Code Execution

    def execute_code(
        self, code: str, language: str = "python", environment: dict | None = None
    ) -> dict:
        """Execute code in sandbox environment"""
        return self.submit_operation(
            operation_type="code_execution",
            parameters={
                "code": code,
                "language": language,
                "environment": environment or {},
                "resource_limits": {
                    "cpu_limit": "2",
                    "memory_limit": "2G",
                    "timeout": 300,
                },
            },
        )

    # Policy Verification

    def verify_policy(self, policy: str, context: dict) -> dict:
        """Verify policy compliance"""
        url = f"{self.config.formal_verification_url}/api/v1/verify"
        data = {
            "policy": policy,
            "context": context,
            "constitutional_hash": self.config.constitutional_hash,
        }

        response = self.session.post(
            url,
            json=data,
            headers=self._get_headers(),
            timeout=self.config.request_timeout,
        )
        response.raise_for_status()
        return response.json()

    def check_constitutional_compliance(self, action: str, parameters: dict) -> dict:
        """Check if an action complies with constitutional principles"""
        url = f"{self.config.formal_verification_url}/api/v1/constitutional/check"
        data = {"action": action, "parameters": parameters, "agent_id": self.agent_id}

        response = self.session.post(
            url,
            json=data,
            headers=self._get_headers(),
            timeout=self.config.request_timeout,
        )
        response.raise_for_status()
        return response.json()

    # Audit Trail

    def get_audit_trail(
        self,
        operation_id: str | None = None,
        agent_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict]:
        """Get audit trail for operations"""
        url = f"{self.config.audit_service_url}/api/v1/audit/trail"
        params = {}

        if operation_id:
            params["operation_id"] = operation_id
        if agent_id:
            params["agent_id"] = agent_id
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = self.session.get(
            url,
            params=params,
            headers=self._get_headers(),
            timeout=self.config.request_timeout,
        )
        response.raise_for_status()
        return response.json()

    def verify_audit_entry(self, audit_id: str) -> dict:
        """Verify integrity of audit entry"""
        url = f"{self.config.audit_service_url}/api/v1/audit/{audit_id}/verify"
        response = self.session.get(
            url, headers=self._get_headers(), timeout=self.config.request_timeout
        )
        response.raise_for_status()
        return response.json()

    # HITL Integration

    def get_hitl_decision(self, operation_id: str) -> dict:
        """Get human-in-the-loop decision for an operation"""
        url = f"{self.config.hitl_service_url}/api/v1/decisions/{operation_id}"
        response = self.session.get(
            url, headers=self._get_headers(), timeout=self.config.request_timeout
        )
        response.raise_for_status()
        return response.json()

    def submit_hitl_feedback(
        self, operation_id: str, decision: str, feedback: str | None = None
    ) -> dict:
        """Submit HITL feedback for an operation"""
        url = f"{self.config.hitl_service_url}/api/v1/decisions/{operation_id}/feedback"
        data = {
            "decision": decision,  # approve, reject, modify
            "feedback": feedback,
            "reviewer": "gemini_cli_user",
        }

        response = self.session.post(
            url,
            json=data,
            headers=self._get_headers(),
            timeout=self.config.request_timeout,
        )
        response.raise_for_status()
        return response.json()

    # Health Checks

    def check_service_health(self) -> dict[str, bool]:
        """Check health of all ACGS services"""
        services = {
            "coordinator": self.config.acgs_coordinator_url,
            "auth": self.config.auth_service_url,
            "sandbox": self.config.sandbox_service_url,
            "formal_verification": self.config.formal_verification_url,
            "audit": self.config.audit_service_url,
            "hitl": self.config.hitl_service_url,
        }

        health_status = {}
        for service_name, url in services.items():
            try:
                response = self.session.get(f"{url}/health", timeout=5)
                health_status[service_name] = response.status_code == 200
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                health_status[service_name] = False

        return health_status
