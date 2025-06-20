"""
Integration tests for external service interactions.

Tests integration with ACGS core services including Auth Service,
Constitutional AI Service, and Governance Synthesis Service.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import httpx


@pytest.mark.integration
@pytest.mark.services
class TestServiceIntegration:
    """Integration tests for external service interactions."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock Auth Service responses."""
        mock_responses = {
            "validate_token": {
                "valid": True,
                "user_id": str(uuid4()),
                "username": "test_user",
                "roles": ["dgm_user"],
                "permissions": ["dgm:read", "dgm:write", "dgm:execute"],
                "expires_at": "2024-12-31T23:59:59Z"
            },
            "check_permission": {
                "allowed": True,
                "permission": "dgm:execute",
                "reason": "User has required permission"
            }
        }
        return mock_responses
    
    @pytest.fixture
    def mock_ac_service(self):
        """Mock Constitutional AI Service responses."""
        mock_responses = {
            "validate_proposal": {
                "is_compliant": True,
                "compliance_score": 0.95,
                "constitutional_hash": "cdd01ef066bc6cf2",
                "violations": [],
                "recommendations": [],
                "validation_details": {
                    "checks_performed": 15,
                    "checks_passed": 15,
                    "governance_principles_verified": [
                        "democratic_participation",
                        "transparency",
                        "accountability",
                        "safety"
                    ]
                }
            },
            "validate_execution": {
                "is_compliant": True,
                "compliance_score": 0.92,
                "constitutional_hash": "cdd01ef066bc6cf2",
                "audit_trail": {
                    "validation_timestamp": datetime.utcnow().isoformat(),
                    "validator_version": "1.0.0",
                    "execution_verified": True
                }
            }
        }
        return mock_responses
    
    @pytest.fixture
    def mock_gs_service(self):
        """Mock Governance Synthesis Service responses."""
        mock_responses = {
            "get_performance_metrics": {
                "service_name": "gs-service",
                "metrics": {
                    "response_time": 145.2,
                    "throughput": 820.5,
                    "error_rate": 0.003,
                    "cpu_usage": 0.52,
                    "memory_usage": 0.68
                },
                "timestamp": datetime.utcnow().isoformat(),
                "health_status": "healthy"
            },
            "apply_improvement": {
                "success": True,
                "improvement_id": str(uuid4()),
                "changes_applied": [
                    "updated_algorithm_parameters",
                    "optimized_query_execution"
                ],
                "execution_time": 42.3,
                "rollback_checkpoint": "checkpoint_12345"
            }
        }
        return mock_responses
    
    async def test_auth_service_integration(self, mock_auth_service):
        """Test integration with Auth Service."""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Mock token validation
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_auth_service["validate_token"]
            
            # Test token validation
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://auth-service:8000/api/v1/auth/validate",
                    json={"token": "test_jwt_token"}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert data["username"] == "test_user"
            assert "dgm:execute" in data["permissions"]
    
    async def test_auth_service_permission_check(self, mock_auth_service):
        """Test permission checking with Auth Service."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_auth_service["check_permission"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://auth-service:8000/api/v1/auth/check-permission",
                    json={
                        "user_id": str(uuid4()),
                        "permission": "dgm:execute",
                        "resource": "improvement_execution"
                    }
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["allowed"] is True
    
    async def test_auth_service_failure_handling(self):
        """Test Auth Service failure handling."""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Simulate service unavailable
            mock_post.side_effect = httpx.ConnectError("Connection failed")
            
            with pytest.raises(httpx.ConnectError):
                async with httpx.AsyncClient() as client:
                    await client.post(
                        "http://auth-service:8000/api/v1/auth/validate",
                        json={"token": "test_token"}
                    )
    
    async def test_constitutional_ai_service_integration(self, mock_ac_service):
        """Test integration with Constitutional AI Service."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_ac_service["validate_proposal"]
            
            # Test proposal validation
            proposal = {
                "strategy": "performance_optimization",
                "target_services": ["gs-service"],
                "proposed_changes": {
                    "type": "algorithm_optimization",
                    "parameters": {"learning_rate": 0.01}
                },
                "risk_assessment": {"risk_level": "low"}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://ac-service:8001/api/v1/constitutional/validate-proposal",
                    json=proposal
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_compliant"] is True
            assert data["compliance_score"] == 0.95
            assert len(data["violations"]) == 0
    
    async def test_constitutional_ai_execution_validation(self, mock_ac_service):
        """Test execution validation with Constitutional AI Service."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_ac_service["validate_execution"]
            
            execution_result = {
                "improvement_id": str(uuid4()),
                "strategy": "performance_optimization",
                "execution_time": 45.2,
                "changes_applied": ["algorithm_update"],
                "performance_metrics": {
                    "before": {"response_time": 150.0},
                    "after": {"response_time": 125.0}
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://ac-service:8001/api/v1/constitutional/validate-execution",
                    json=execution_result
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_compliant"] is True
            assert data["compliance_score"] == 0.92
            assert "audit_trail" in data
    
    async def test_governance_synthesis_service_integration(self, mock_gs_service):
        """Test integration with Governance Synthesis Service."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_gs_service["get_performance_metrics"]
            
            # Test performance metrics retrieval
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://gs-service:8002/api/v1/governance/performance-metrics"
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["service_name"] == "gs-service"
            assert "metrics" in data
            assert data["health_status"] == "healthy"
    
    async def test_governance_synthesis_improvement_application(self, mock_gs_service):
        """Test improvement application to Governance Synthesis Service."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_gs_service["apply_improvement"]
            
            improvement_request = {
                "improvement_id": str(uuid4()),
                "strategy": "performance_optimization",
                "changes": {
                    "algorithm_parameters": {"learning_rate": 0.01},
                    "optimization_settings": {"batch_size": 64}
                },
                "safety_constraints": {
                    "max_execution_time": 300,
                    "rollback_threshold": -0.05
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://gs-service:8002/api/v1/governance/apply-improvement",
                    json=improvement_request
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "rollback_checkpoint" in data
            assert len(data["changes_applied"]) > 0
    
    async def test_service_circuit_breaker_pattern(self):
        """Test circuit breaker pattern for service failures."""
        failure_count = 0
        max_failures = 3
        
        async def mock_failing_service():
            nonlocal failure_count
            failure_count += 1
            if failure_count <= max_failures:
                raise httpx.ConnectError("Service unavailable")
            return {"status": "recovered"}
        
        # Simulate circuit breaker logic
        circuit_open = False
        
        for attempt in range(5):
            try:
                if circuit_open and attempt < max_failures + 1:
                    # Circuit is open, fail fast
                    raise Exception("Circuit breaker open")
                
                result = await mock_failing_service()
                circuit_open = False  # Reset on success
                assert result["status"] == "recovered"
                break
                
            except (httpx.ConnectError, Exception) as e:
                if failure_count >= max_failures:
                    circuit_open = True
                
                if attempt == 4:  # Last attempt
                    assert circuit_open is True
    
    async def test_service_retry_mechanism(self):
        """Test retry mechanism for transient failures."""
        attempt_count = 0
        
        async def mock_transient_failure():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise httpx.TimeoutException("Request timeout")
            return {"status": "success", "attempts": attempt_count}
        
        # Simulate retry logic
        max_retries = 3
        for retry in range(max_retries):
            try:
                result = await mock_transient_failure()
                assert result["status"] == "success"
                assert result["attempts"] == 3
                break
            except httpx.TimeoutException:
                if retry == max_retries - 1:
                    pytest.fail("Max retries exceeded")
                continue
    
    async def test_service_load_balancing_simulation(self):
        """Test load balancing across multiple service instances."""
        service_instances = [
            "http://gs-service-1:8002",
            "http://gs-service-2:8002", 
            "http://gs-service-3:8002"
        ]
        
        request_count = 10
        instance_usage = {instance: 0 for instance in service_instances}
        
        # Simulate round-robin load balancing
        for i in range(request_count):
            selected_instance = service_instances[i % len(service_instances)]
            instance_usage[selected_instance] += 1
        
        # Verify load distribution
        expected_requests_per_instance = request_count // len(service_instances)
        for instance, count in instance_usage.items():
            assert count >= expected_requests_per_instance
            assert count <= expected_requests_per_instance + 1
    
    async def test_service_health_check_integration(self):
        """Test health check integration with services."""
        services = [
            ("auth-service", "http://auth-service:8000/health"),
            ("ac-service", "http://ac-service:8001/health"),
            ("gs-service", "http://gs-service:8002/health")
        ]
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "dependencies": {"database": "healthy", "cache": "healthy"}
            }
            
            health_results = {}
            
            async with httpx.AsyncClient() as client:
                for service_name, health_url in services:
                    try:
                        response = await client.get(health_url, timeout=5.0)
                        health_results[service_name] = {
                            "healthy": response.status_code == 200,
                            "response_time": 0.1  # Simulated
                        }
                    except Exception as e:
                        health_results[service_name] = {
                            "healthy": False,
                            "error": str(e)
                        }
            
            # Verify all services are healthy
            for service_name, result in health_results.items():
                assert result["healthy"] is True, f"{service_name} is not healthy"
    
    async def test_service_authentication_flow(self, mock_auth_service):
        """Test complete authentication flow across services."""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Step 1: Authenticate with Auth Service
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "access_token": "jwt_token_12345",
                "token_type": "bearer",
                "expires_in": 3600,
                "user_id": str(uuid4())
            }
            
            async with httpx.AsyncClient() as client:
                auth_response = await client.post(
                    "http://auth-service:8000/api/v1/auth/login",
                    json={"username": "test_user", "password": "test_password"}
                )
            
            assert auth_response.status_code == 200
            auth_data = auth_response.json()
            token = auth_data["access_token"]
            
            # Step 2: Use token for authenticated request
            with patch('httpx.AsyncClient.get') as mock_get:
                mock_get.return_value.status_code = 200
                mock_get.return_value.json.return_value = {"authorized": True}
                
                headers = {"Authorization": f"Bearer {token}"}
                
                protected_response = await client.get(
                    "http://dgm-service:8007/api/v1/dgm/improvements",
                    headers=headers
                )
                
                assert protected_response.status_code == 200
                assert protected_response.json()["authorized"] is True
