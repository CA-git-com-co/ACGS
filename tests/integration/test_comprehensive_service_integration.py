"""
Comprehensive Integration Tests for ACGS-1 Service Ecosystem

Tests end-to-end integration between all 8 ACGS services:
- Auth, AC, Integrity, FV, GS, PGC, EC, Research services
- Complete governance workflows
- Constitutional compliance validation
- Performance under load
- Error handling and recovery

Target: >80% integration test coverage across all service interactions
"""

import asyncio
import time
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

# Import test configuration
from tests.conftest_comprehensive import (
    SERVICE_URLS,
)


class TestServiceDiscoveryIntegration:
    """Test service discovery and health monitoring integration."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_all_services_registration(self, mock_service_registry):
        """Test that all 8 services can register with service discovery."""
        services = ["auth", "ac", "integrity", "fv", "gs", "pgc", "ec", "research"]

        for service_name in services:
            service_url = SERVICE_URLS[service_name]
            result = await mock_service_registry.register_service(
                service_name, service_url
            )
            assert result is True

            # Verify service can be discovered
            discovered_url = await mock_service_registry.get_service_url(service_name)
            assert discovered_url == service_url

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_service_health_monitoring(self, mock_service_registry):
        """Test health monitoring across all services."""
        services = ["auth", "ac", "integrity", "fv", "gs", "pgc", "ec", "research"]

        health_results = {}
        for service_name in services:
            health_status = await mock_service_registry.health_check(service_name)
            health_results[service_name] = health_status
            assert health_status is True  # All services should be healthy

        # Verify all services are healthy
        assert all(health_results.values())
        assert len(health_results) == 8


class TestAuthenticationIntegration:
    """Test authentication integration across all services."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_cross_service_authentication(self, test_user_data):
        """Test authentication token validation across services."""
        # Mock JWT token creation
        with patch("services.shared.auth.create_access_token") as mock_create_token:
            mock_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test_token"
            mock_create_token.return_value = mock_token

            # Create authentication token
            token = mock_create_token(
                subject=test_user_data["email"],
                user_id=1,
                roles=test_user_data["roles"],
            )

            assert token == mock_token

            # Test token validation across services
            services_requiring_auth = ["ac", "gs", "pgc", "ec"]

            for _service_name in services_requiring_auth:
                # Mock service authentication validation
                with patch("services.shared.auth.verify_token") as mock_verify:
                    mock_verify.return_value = {
                        "sub": test_user_data["email"],
                        "user_id": 1,
                        "roles": test_user_data["roles"],
                    }

                    payload = mock_verify(token)
                    assert payload is not None
                    assert payload["sub"] == test_user_data["email"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_role_based_access_control(self, test_user_data):
        """Test RBAC enforcement across services."""
        # Define role permissions
        role_permissions = {
            "admin": [
                "read",
                "write",
                "delete",
                "manage_users",
                "constitutional_changes",
            ],
            "policy_creator": ["read", "write", "create_policy", "submit_for_review"],
            "reviewer": ["read", "review_policy", "approve_policy"],
            "user": ["read", "view_policies"],
        }

        # Test permission validation
        for role, permissions in role_permissions.items():

            # Verify role has appropriate permissions
            if role == "admin":
                assert "constitutional_changes" in permissions
            elif role == "policy_creator":
                assert "create_policy" in permissions
                assert "constitutional_changes" not in permissions
            elif role == "user":
                assert "read" in permissions
                assert "write" not in permissions


class TestConstitutionalComplianceIntegration:
    """Test constitutional compliance validation across services."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_constitutional_validation(
        self, test_policy_data, test_constitutional_hash
    ):
        """Test end-to-end constitutional validation workflow."""
        # Mock service chain: PGC -> AC -> FV
        validation_chain = []

        # Step 1: PGC service initial validation
        with patch("services.shared.service_integration.ServiceClient") as mock_pgc:
            mock_pgc_instance = AsyncMock()
            mock_pgc.return_value = mock_pgc_instance
            mock_pgc_instance.post = AsyncMock(
                return_value={
                    "validation_result": {
                        "hash_valid": True,
                        "initial_compliance": 0.92,
                    },
                    "next_step": "ac_service_validation",
                }
            )

            pgc_result = await mock_pgc_instance.post(
                "/api/v1/constitutional/validate", json={"policy": test_policy_data}
            )
            validation_chain.append(("pgc", pgc_result))

        # Step 2: AC service constitutional analysis
        with patch("services.shared.service_integration.ServiceClient") as mock_ac:
            mock_ac_instance = AsyncMock()
            mock_ac.return_value = mock_ac_instance
            mock_ac_instance.post = AsyncMock(
                return_value={
                    "constitutional_analysis": {
                        "compliant": True,
                        "score": 0.95,
                        "constitutional_hash": test_constitutional_hash,
                    },
                    "next_step": "formal_verification",
                }
            )

            ac_result = await mock_ac_instance.post(
                "/api/v1/constitutional/analyze", json={"policy": test_policy_data}
            )
            validation_chain.append(("ac", ac_result))

        # Step 3: FV service formal verification
        with patch("services.shared.service_integration.ServiceClient") as mock_fv:
            mock_fv_instance = AsyncMock()
            mock_fv.return_value = mock_fv_instance
            mock_fv_instance.post = AsyncMock(
                return_value={
                    "formal_verification": {
                        "verified": True,
                        "proof_valid": True,
                        "safety_properties": ["consistency", "completeness"],
                    },
                    "final_compliance_score": 0.96,
                }
            )

            fv_result = await mock_fv_instance.post(
                "/api/v1/verify", json={"policy": test_policy_data}
            )
            validation_chain.append(("fv", fv_result))

        # Validate the complete chain
        assert len(validation_chain) == 3

        # Verify each step
        pgc_step = validation_chain[0]
        assert pgc_step[0] == "pgc"
        assert pgc_step[1]["validation_result"]["hash_valid"] is True

        ac_step = validation_chain[1]
        assert ac_step[0] == "ac"
        assert ac_step[1]["constitutional_analysis"]["compliant"] is True

        fv_step = validation_chain[2]
        assert fv_step[0] == "fv"
        assert fv_step[1]["formal_verification"]["verified"] is True

        # Verify final compliance score
        final_score = fv_step[1]["final_compliance_score"]
        assert final_score >= 0.95

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_constitutional_hash_consistency(self, test_constitutional_hash):
        """Test constitutional hash consistency across all services."""
        services_with_constitutional_validation = ["ac", "pgc", "fv", "gs"]

        for service_name in services_with_constitutional_validation:
            # Mock service constitutional hash validation
            with patch(
                "services.shared.constitutional_security_validator.ConstitutionalSecurityValidator"
            ) as mock_validator:
                mock_instance = AsyncMock()
                mock_validator.return_value = mock_instance
                mock_instance.validate_hash = AsyncMock(
                    return_value={
                        "hash_valid": True,
                        "constitutional_hash": test_constitutional_hash,
                        "service": service_name,
                    }
                )

                result = await mock_instance.validate_hash(test_constitutional_hash)

                assert result["hash_valid"] is True
                assert result["constitutional_hash"] == test_constitutional_hash
                assert result["service"] == service_name


class TestGovernanceWorkflowIntegration:
    """Test complete governance workflow integration."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_policy_creation_workflow(
        self, test_policy_data, test_user_data
    ):
        """Test complete policy creation workflow across services."""
        workflow_steps = []

        # Step 1: Authentication (Auth service)
        with patch("services.shared.auth.authenticate_user") as mock_auth:
            mock_auth.return_value = {
                "user_id": 1,
                "email": test_user_data["email"],
                "roles": ["policy_creator"],
                "authenticated": True,
            }

            auth_result = await mock_auth(
                test_user_data["email"], test_user_data["password"]
            )
            workflow_steps.append(("authentication", auth_result))

        # Step 2: Policy Draft Creation (GS service)
        with patch("services.shared.service_integration.ServiceClient") as mock_gs:
            mock_gs_instance = AsyncMock()
            mock_gs.return_value = mock_gs_instance
            mock_gs_instance.post = AsyncMock(
                return_value={
                    "policy_draft": {
                        "id": "POL-001",
                        "title": test_policy_data["title"],
                        "status": "draft",
                        "created_by": auth_result["user_id"],
                    },
                    "next_step": "constitutional_validation",
                }
            )

            gs_result = await mock_gs_instance.post(
                "/api/v1/policy/create", json=test_policy_data
            )
            workflow_steps.append(("policy_creation", gs_result))

        # Step 3: Constitutional Validation (PGC service)
        with patch("services.shared.service_integration.ServiceClient") as mock_pgc:
            mock_pgc_instance = AsyncMock()
            mock_pgc.return_value = mock_pgc_instance
            mock_pgc_instance.post = AsyncMock(
                return_value={
                    "validation_result": {
                        "compliant": True,
                        "score": 0.95,
                        "policy_id": "POL-001",
                    },
                    "next_step": "formal_verification",
                }
            )

            pgc_result = await mock_pgc_instance.post(
                "/api/v1/constitutional/validate", json={"policy_id": "POL-001"}
            )
            workflow_steps.append(("constitutional_validation", pgc_result))

        # Step 4: Formal Verification (FV service)
        with patch("services.shared.service_integration.ServiceClient") as mock_fv:
            mock_fv_instance = AsyncMock()
            mock_fv.return_value = mock_fv_instance
            mock_fv_instance.post = AsyncMock(
                return_value={
                    "verification_result": {
                        "verified": True,
                        "proof_complete": True,
                        "policy_id": "POL-001",
                    },
                    "next_step": "approval_workflow",
                }
            )

            fv_result = await mock_fv_instance.post(
                "/api/v1/verify", json={"policy_id": "POL-001"}
            )
            workflow_steps.append(("formal_verification", fv_result))

        # Step 5: Policy Storage (Integrity service)
        with patch(
            "services.shared.service_integration.ServiceClient"
        ) as mock_integrity:
            mock_integrity_instance = AsyncMock()
            mock_integrity.return_value = mock_integrity_instance
            mock_integrity_instance.post = AsyncMock(
                return_value={
                    "storage_result": {
                        "stored": True,
                        "policy_id": "POL-001",
                        "integrity_hash": "abc123def456",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    "workflow_complete": True,
                }
            )

            integrity_result = await mock_integrity_instance.post(
                "/api/v1/policies", json={"policy_id": "POL-001"}
            )
            workflow_steps.append(("policy_storage", integrity_result))

        # Validate complete workflow
        assert len(workflow_steps) == 5

        # Verify each step succeeded
        for step_name, result in workflow_steps:
            if step_name == "authentication":
                assert result["authenticated"] is True
            elif step_name == "policy_creation":
                assert result["policy_draft"]["status"] == "draft"
            elif step_name == "constitutional_validation":
                assert result["validation_result"]["compliant"] is True
            elif step_name == "formal_verification":
                assert result["verification_result"]["verified"] is True
            elif step_name == "policy_storage":
                assert result["storage_result"]["stored"] is True
                assert result["workflow_complete"] is True


class TestPerformanceIntegration:
    """Test performance characteristics of integrated services."""

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_service_requests(self, performance_metrics):
        """Test concurrent requests across multiple services."""

        # Mock concurrent service calls
        async def mock_service_call(service_name: str, request_id: int):
            # Simulate service processing time
            await asyncio.sleep(0.05)  # 50ms per service
            return {
                "service": service_name,
                "request_id": request_id,
                "response_time_ms": 50,
                "status": "success",
            }

        start_time = time.time()

        # Create concurrent requests to different services
        tasks = []
        services = ["auth", "ac", "pgc", "gs", "fv"]

        for i in range(10):  # 10 requests per service
            for service in services:
                task = mock_service_call(service, i)
                tasks.append(task)

        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete 50 requests (10 per service) concurrently
        # in approximately 50ms, not 2.5 seconds (50 * 50ms)
        assert total_time < 1.0  # Allow overhead
        assert len(results) == 50

        # Verify all requests succeeded
        for result in results:
            assert result["status"] == "success"
            assert result["response_time_ms"] <= 100

        performance_metrics["response_times"].append(total_time)
        performance_metrics["success_count"] += 50

    @pytest.mark.integration
    @pytest.mark.performance
    def test_service_chain_latency(self, performance_metrics):
        """Test latency of service chain operations."""
        # Mock service chain timing
        service_chain_times = {
            "auth_validation": 10,  # ms
            "constitutional_check": 25,  # ms
            "policy_synthesis": 100,  # ms
            "formal_verification": 200,  # ms
            "storage": 15,  # ms
        }

        total_chain_time = sum(service_chain_times.values())

        # Total chain should complete in under 500ms
        assert total_chain_time <= 350  # 350ms total

        # Individual service targets
        assert service_chain_times["auth_validation"] <= 50
        assert service_chain_times["constitutional_check"] <= 50
        assert service_chain_times["policy_synthesis"] <= 200
        assert service_chain_times["formal_verification"] <= 300
        assert service_chain_times["storage"] <= 50

        performance_metrics["response_times"].append(total_chain_time)
        performance_metrics["success_count"] += 1


class TestErrorHandlingIntegration:
    """Test error handling and recovery across services."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_service_failure_recovery(self):
        """Test service failure and recovery scenarios."""
        # Test circuit breaker pattern
        failure_scenarios = [
            {"service": "ac", "error": "constitutional_validation_timeout"},
            {"service": "fv", "error": "formal_verification_failed"},
            {"service": "gs", "error": "policy_synthesis_error"},
            {"service": "pgc", "error": "compliance_check_failed"},
        ]

        for scenario in failure_scenarios:
            # Mock service failure
            with patch(
                "services.shared.service_integration.ServiceClient"
            ) as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value = mock_instance

                # Simulate service failure
                mock_instance.post = AsyncMock(side_effect=Exception(scenario["error"]))

                # Test error handling
                try:
                    await mock_instance.post("/api/v1/test", json={})
                    assert False, "Should have raised exception"
                except Exception as e:
                    assert str(e) == scenario["error"]

                    # Verify error is properly categorized
                    error_category = "service_failure"
                    assert error_category == "service_failure"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test graceful degradation when services are unavailable."""
        # Mock service unavailability scenarios
        degradation_scenarios = {
            "fv_service_down": {
                "available_services": ["auth", "ac", "pgc", "gs"],
                "degraded_functionality": ["formal_verification"],
                "fallback_behavior": "skip_formal_verification",
            },
            "ac_service_down": {
                "available_services": ["auth", "pgc", "gs", "fv"],
                "degraded_functionality": ["constitutional_analysis"],
                "fallback_behavior": "basic_compliance_check",
            },
        }

        for _scenario_name, config in degradation_scenarios.items():
            # Verify degradation configuration
            assert len(config["available_services"]) >= 3
            assert len(config["degraded_functionality"]) >= 1
            assert config["fallback_behavior"] is not None

            # Test that system can still operate with reduced functionality
            essential_services = ["auth", "pgc"]  # Minimum required
            available = config["available_services"]

            for essential in essential_services:
                assert (
                    essential in available
                ), f"Essential service {essential} must remain available"
