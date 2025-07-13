#!/usr/bin/env python3
"""
Real OPA (Open Policy Agent) Client for ACGS Governance System

Provides actual OPA integration to replace simulation methods,
enabling real policy evaluation through an OPA server instance.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import pathlib
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class OPAConfig:
    """Configuration for OPA client connection."""

    base_url: str = "http://opa-server:8181"
    timeout: float = 30.0
    max_retries: int = 3
    policy_bundle_path: str = "/v1/data"
    query_endpoint: str = "/v1/data/acgs"


class OPAClientError(Exception):
    """Base exception for OPA client errors."""


class OPAConnectionError(OPAClientError):
    """Raised when unable to connect to OPA server."""


class OPAPolicyError(OPAClientError):
    """Raised when policy evaluation fails."""


class RealOPAClient:
    """
    Real OPA client that connects to an actual OPA server instance.
    Replaces simulation methods with actual policy evaluation.
    """

    def __init__(self, config: OPAConfig | None = None):
        self.config = config or OPAConfig()
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={"Content-Type": "application/json"},
        )
        self._policies_loaded = False
        logger.info(f"Initialized OPA client for {self.config.base_url}")

    async def health_check(self) -> bool:
        """Check if OPA server is healthy and reachable."""
        try:
            response = await self.client.get("/health")
            is_healthy = response.status_code == 200
            if is_healthy:
                logger.info("OPA server health check passed")
            else:
                logger.warning(
                    f"OPA server health check failed: {response.status_code}"
                )
            return is_healthy
        except Exception as e:
            logger.exception(f"OPA health check failed: {e}")
            return False

    async def load_policy_bundle(self, bundle_path: str) -> bool:
        """
        Load policy bundle into OPA server.
        In production, this would typically be done via OPA's bundle system.
        """
        try:
            # Check if bundle file exists
            if not pathlib.Path(bundle_path).exists():
                logger.error(f"Policy bundle not found: {bundle_path}")
                return False

            # Load bundle content
            with open(bundle_path, encoding="utf-8") as f:
                bundle_content = f.read()

            # Upload to OPA
            response = await self.client.put(
                "/v1/policies/acgs",
                content=bundle_content,
                headers={"Content-Type": "text/plain"},
            )

            if response.status_code in {200, 201}:
                self._policies_loaded = True
                logger.info(f"Successfully loaded policy bundle: {bundle_path}")
                return True
            logger.error(
                f"Failed to load policy bundle: {response.status_code} -"
                f" {response.text}"
            )
            return False

        except Exception as e:
            logger.exception(f"Error loading policy bundle {bundle_path}: {e}")
            return False

    async def evaluate_policy(
        self, policy_path: str, input_data: dict[str, Any], retry_count: int = 0
    ) -> dict[str, Any]:
        """
        Evaluate a policy against input data using real OPA server.

        Args:
            policy_path: Path to the policy in OPA (e.g., "acgs/constitutional/human_dignity")
            input_data: Input data for policy evaluation
            retry_count: Current retry attempt

        Returns:
            OPA evaluation result
        """
        try:
            # Prepare request
            query_url = f"{self.config.query_endpoint}/{policy_path}"
            request_body = {"input": input_data}

            logger.debug(
                f"Evaluating policy {policy_path} with input:"
                f" {json.dumps(input_data, indent=2)}"
            )

            # Make request to OPA
            response = await self.client.post(query_url, json=request_body)

            if response.status_code == 200:
                result = response.json()
                logger.debug(f"Policy evaluation successful: {policy_path}")
                return result
            if response.status_code == 404:
                raise OPAPolicyError(f"Policy not found: {policy_path}")
            raise OPAConnectionError(
                f"OPA request failed: {response.status_code} - {response.text}"
            )

        except httpx.RequestError as e:
            if retry_count < self.config.max_retries:
                logger.warning(
                    "OPA request failed, retrying"
                    f" ({retry_count + 1}/{self.config.max_retries}): {e}"
                )
                await asyncio.sleep(1 * (retry_count + 1))  # Exponential backoff
                return await self.evaluate_policy(
                    policy_path, input_data, retry_count + 1
                )
            raise OPAConnectionError(
                "OPA connection failed after" f" {self.config.max_retries} retries: {e}"
            )
        except Exception as e:
            logger.exception(f"Unexpected error evaluating policy {policy_path}: {e}")
            raise OPAPolicyError(f"Policy evaluation failed: {e}")

    async def evaluate_constitutional_policy(
        self, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Evaluate constitutional compliance policies.
        Uses real OPA policies for constitutional AI principles.
        """
        try:
            # Evaluate core constitutional principles
            principles = [
                "human_dignity",
                "fairness",
                "transparency",
                "accountability",
                "privacy",
            ]

            results = {}
            overall_compliance = 0.0

            for principle in principles:
                policy_path = f"constitutional/{principle}"
                principle_result = await self.evaluate_policy(policy_path, input_data)

                # Extract score from OPA result
                principle_score = principle_result.get("result", {}).get("score", 0.0)
                results[principle] = {
                    "score": principle_score,
                    "details": principle_result.get("result", {}),
                }

                # Weight the scores (same as simulation for consistency)
                weights = {
                    "human_dignity": 0.25,
                    "fairness": 0.20,
                    "transparency": 0.15,
                    "accountability": 0.20,
                    "privacy": 0.20,
                }
                overall_compliance += principle_score * weights.get(principle, 0.2)

            # Make final decision
            decision = "allow" if overall_compliance >= 0.8 else "deny"

            return {
                "decision": decision,
                "compliance_score": overall_compliance,
                "principle_scores": results,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "evaluation_method": "real_opa",
            }

        except Exception as e:
            logger.exception(f"Constitutional policy evaluation failed: {e}")
            # Fallback to deny for safety
            return {
                "decision": "deny",
                "compliance_score": 0.0,
                "error": str(e),
                "evaluation_method": "real_opa_error",
            }

    async def evaluate_security_policy(
        self, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate security policies using real OPA."""
        try:
            result = await self.evaluate_policy("security/main", input_data)

            return {
                "decision": result.get("result", {}).get("decision", "deny"),
                "security_level": result.get("result", {}).get(
                    "security_level", "high"
                ),
                "threats_detected": result.get("result", {}).get("threats", []),
                "evaluation_method": "real_opa",
            }
        except Exception as e:
            logger.exception(f"Security policy evaluation failed: {e}")
            return {
                "decision": "deny",
                "security_level": "high",
                "error": str(e),
                "evaluation_method": "real_opa_error",
            }

    async def evaluate_multi_tenant_policy(
        self, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate multi-tenant isolation policies using real OPA."""
        try:
            result = await self.evaluate_policy("multi_tenant/isolation", input_data)

            return {
                "decision": result.get("result", {}).get("decision", "deny"),
                "tenant_access": result.get("result", {}).get("tenant_access", False),
                "resource_scope": result.get("result", {}).get("resource_scope", []),
                "evaluation_method": "real_opa",
            }
        except Exception as e:
            logger.exception(f"Multi-tenant policy evaluation failed: {e}")
            return {
                "decision": "deny",
                "tenant_access": False,
                "error": str(e),
                "evaluation_method": "real_opa_error",
            }

    async def evaluate_evolutionary_policy(
        self, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate evolutionary computation policies using real OPA."""
        try:
            result = await self.evaluate_policy("evolutionary/optimization", input_data)

            return {
                "decision": result.get("result", {}).get("decision", "allow"),
                "optimization_allowed": result.get("result", {}).get(
                    "optimization_allowed", True
                ),
                "parameters": result.get("result", {}).get("parameters", {}),
                "evaluation_method": "real_opa",
            }
        except Exception as e:
            logger.exception(f"Evolutionary policy evaluation failed: {e}")
            return {
                "decision": "allow",  # Default allow for evolutionary policies
                "optimization_allowed": True,
                "error": str(e),
                "evaluation_method": "real_opa_error",
            }

    async def list_policies(self) -> list[str]:
        """List all available policies in OPA."""
        try:
            response = await self.client.get("/v1/policies")
            if response.status_code == 200:
                policies = response.json().get("result", [])
                return list(policies.keys()) if isinstance(policies, dict) else []
            return []
        except Exception as e:
            logger.exception(f"Failed to list policies: {e}")
            return []

    async def get_policy_data(self, path: str) -> dict[str, Any] | None:
        """Get data from a specific policy path."""
        try:
            response = await self.client.get(f"/v1/data/{path}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.exception(f"Failed to get policy data for {path}: {e}")
            return None

    async def close(self):
        """Close the HTTP client connection."""
        await self.client.aclose()
        logger.info("OPA client connection closed")


class OPAPolicyManager:
    """
    Manages OPA policy definitions and loading.
    Provides utilities for policy management.
    """

    def __init__(self, opa_client: RealOPAClient):
        self.opa_client = opa_client

    async def create_default_policies(self) -> bool:
        """
        Create default ACGS policies in OPA server.
        This replaces simulation with actual policy definitions.
        """
        policies = {
            "constitutional/human_dignity": self._get_human_dignity_policy(),
            "constitutional/fairness": self._get_fairness_policy(),
            "constitutional/transparency": self._get_transparency_policy(),
            "constitutional/accountability": self._get_accountability_policy(),
            "constitutional/privacy": self._get_privacy_policy(),
            "security/main": self._get_security_policy(),
            "multi_tenant/isolation": self._get_multi_tenant_policy(),
            "evolutionary/optimization": self._get_evolutionary_policy(),
        }

        success_count = 0
        for policy_name, policy_content in policies.items():
            try:
                response = await self.opa_client.client.put(
                    f"/v1/policies/{policy_name}",
                    content=policy_content,
                    headers={"Content-Type": "text/plain"},
                )
                if response.status_code in {200, 201}:
                    success_count += 1
                    logger.info(f"Successfully created policy: {policy_name}")
                else:
                    logger.error(
                        f"Failed to create policy {policy_name}: {response.status_code}"
                    )
            except Exception as e:
                logger.exception(f"Error creating policy {policy_name}: {e}")

        logger.info(f"Successfully created {success_count}/{len(policies)} policies")
        return success_count == len(policies)

    def _get_human_dignity_policy(self) -> str:
        """Get human dignity policy definition."""
        return """
package acgs.constitutional.human_dignity

import rego.v1

default score := 0.0
default allow := false

# Human dignity compliance scoring
score := calculated_score if {
    calculated_score := _calculate_dignity_score(input)
}

allow if score >= 0.8

_calculate_dignity_score(input_data) := score if {
    # Check for dignity violations
    dignity_factors := [
        _check_autonomy(input_data),
        _check_respect(input_data),
        _check_human_oversight(input_data),
        _check_non_discrimination(input_data)
    ]

    score := (sum(dignity_factors) / count(dignity_factors))
}

_check_autonomy(input_data) := 1.0 if {
    input_data.action != "override_user_choice"
    not input_data.environment.forced_decision
} else := 0.0

_check_respect(input_data) := 1.0 if {
    not _contains_disrespectful_content(input_data)
} else := 0.0

_check_human_oversight(input_data) := 1.0 if {
    input_data.environment.human_oversight == true
} else := 0.5

_check_non_discrimination(input_data) := 1.0 if {
    not _contains_discriminatory_factors(input_data)
} else := 0.0

_contains_disrespectful_content(input_data) if {
    some content in input_data.resource.content
    contains(lower(content), "dehumanize")
}

_contains_discriminatory_factors(input_data) if {
    protected_attributes := ["race", "gender", "religion", "age"]
    some attr in protected_attributes
    input_data.principal.attributes[attr]
    input_data.action == "discriminate_based_on_attribute"
}
"""

    def _get_fairness_policy(self) -> str:
        """Get fairness policy definition."""
        return """
package acgs.constitutional.fairness

import rego.v1

default score := 0.0

score := calculated_score if {
    calculated_score := _calculate_fairness_score(input)
}

_calculate_fairness_score(input_data) := score if {
    fairness_factors := [
        _check_equal_treatment(input_data),
        _check_bias_mitigation(input_data),
        _check_equitable_access(input_data)
    ]

    score := (sum(fairness_factors) / count(fairness_factors))
}

_check_equal_treatment(input_data) := 1.0 if {
    input_data.environment.equal_treatment_ensured == true
} else := 0.0

_check_bias_mitigation(input_data) := 1.0 if {
    input_data.environment.bias_checked == true
} else := 0.0

_check_equitable_access(input_data) := 1.0 if {
    input_data.resource.access_level == "equitable"
} else := 0.5
"""

    def _get_transparency_policy(self) -> str:
        """Get transparency policy definition."""
        return """
package acgs.constitutional.transparency

import rego.v1

default score := 0.0

score := calculated_score if {
    calculated_score := _calculate_transparency_score(input)
}

_calculate_transparency_score(input_data) := score if {
    transparency_factors := [
        _check_explainability(input_data),
        _check_audit_trail(input_data),
        _check_disclosure(input_data)
    ]

    score := (sum(transparency_factors) / count(transparency_factors))
}

_check_explainability(input_data) := 1.0 if {
    input_data.environment.explanation_available == true
} else := 0.0

_check_audit_trail(input_data) := 1.0 if {
    input_data.environment.audit_logged == true
} else := 0.0

_check_disclosure(input_data) := 1.0 if {
    input_data.environment.ai_disclosure == true
} else := 0.0
"""

    def _get_accountability_policy(self) -> str:
        """Get accountability policy definition."""
        return """
package acgs.constitutional.accountability

import rego.v1

default score := 0.0

score := calculated_score if {
    calculated_score := _calculate_accountability_score(input)
}

_calculate_accountability_score(input_data) := score if {
    accountability_factors := [
        _check_responsibility_chain(input_data),
        _check_monitoring(input_data),
        _check_remediation(input_data)
    ]

    score := (sum(accountability_factors) / count(accountability_factors))
}

_check_responsibility_chain(input_data) := 1.0 if {
    input_data.environment.responsible_party_identified == true
} else := 0.0

_check_monitoring(input_data) := 1.0 if {
    input_data.environment.monitoring_active == true
} else := 0.0

_check_remediation(input_data) := 1.0 if {
    input_data.environment.remediation_available == true
} else := 0.0
"""

    def _get_privacy_policy(self) -> str:
        """Get privacy policy definition."""
        return """
package acgs.constitutional.privacy

import rego.v1

default score := 0.0

score := calculated_score if {
    calculated_score := _calculate_privacy_score(input)
}

_calculate_privacy_score(input_data) := score if {
    privacy_factors := [
        _check_data_minimization(input_data),
        _check_consent(input_data),
        _check_encryption(input_data)
    ]

    score := (sum(privacy_factors) / count(privacy_factors))
}

_check_data_minimization(input_data) := 1.0 if {
    input_data.resource.data_scope == "minimal"
} else := 0.0

_check_consent(input_data) := 1.0 if {
    input_data.environment.user_consent == true
} else := 0.0

_check_encryption(input_data) := 1.0 if {
    input_data.environment.data_encrypted == true
} else := 0.0
"""

    def _get_security_policy(self) -> str:
        """Get security policy definition."""
        return """
package acgs.security.main

import rego.v1

default decision := "deny"
default security_level := "high"

decision := "allow" if {
    _security_checks_passed(input)
}

security_level := "low" if {
    input.environment.threat_level == "low"
    _basic_security_met(input)
}

security_level := "medium" if {
    input.environment.threat_level == "medium"
    _enhanced_security_met(input)
}

_security_checks_passed(input_data) if {
    _authentication_valid(input_data)
    _authorization_granted(input_data)
    not _threats_detected(input_data)
}

_authentication_valid(input_data) if {
    input_data.principal.authenticated == true
    input_data.principal.mfa_verified == true
}

_authorization_granted(input_data) if {
    required_role := input_data.resource.required_role
    user_roles := input_data.principal.roles
    required_role in user_roles
}

_threats_detected(input_data) if {
    input_data.environment.malicious_activity == true
}

_basic_security_met(input_data) if {
    input_data.environment.ssl_enabled == true
    input_data.environment.rate_limited == true
}

_enhanced_security_met(input_data) if {
    _basic_security_met(input_data)
    input_data.environment.anomaly_detection == true
}
"""

    def _get_multi_tenant_policy(self) -> str:
        """Get multi-tenant isolation policy definition."""
        return """
package acgs.multi_tenant.isolation

import rego.v1

default decision := "deny"
default tenant_access := false

decision := "allow" if {
    _tenant_isolation_validated(input)
}

tenant_access := true if {
    _tenant_access_granted(input)
}

_tenant_isolation_validated(input_data) if {
    _correct_tenant_scope(input_data)
    _data_isolation_enforced(input_data)
    _resource_boundaries_respected(input_data)
}

_correct_tenant_scope(input_data) if {
    user_tenant := input_data.principal.tenant_id
    resource_tenant := input_data.resource.tenant_id
    user_tenant == resource_tenant
}

_data_isolation_enforced(input_data) if {
    input_data.environment.data_isolation == true
}

_resource_boundaries_respected(input_data) if {
    input_data.environment.resource_quotas_enforced == true
}

_tenant_access_granted(input_data) if {
    input_data.principal.tenant_permissions[input_data.action] == true
}
"""

    def _get_evolutionary_policy(self) -> str:
        """Get evolutionary computation policy definition."""
        return """
package acgs.evolutionary.optimization

import rego.v1

default decision := "allow"
default optimization_allowed := true

decision := "deny" if {
    _optimization_risks_detected(input)
}

optimization_allowed := false if {
    input.environment.computational_budget_exceeded == true
}

optimization_allowed := false if {
    input.resource.safety_critical == true
    not input.environment.safety_validation_passed
}

_optimization_risks_detected(input_data) if {
    input_data.environment.convergence_failure == true
}

_optimization_risks_detected(input_data) if {
    input_data.environment.parameter_drift_detected == true
    input_data.environment.drift_severity == "high"
}
"""


# Factory function
def get_opa_client(config: OPAConfig | None = None) -> RealOPAClient:
    """Factory function to create an OPA client."""
    return RealOPAClient(config)


# Global client instance for backward compatibility
_default_config = OPAConfig(
    base_url=os.getenv("OPA_SERVER_URL", "http://opa-server:8181")
)
default_opa_client = get_opa_client(_default_config)
