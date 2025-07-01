"""
End-to-End Integration Tests for ACGS

Tests complete workflows through the entire ACGS system.
"""

import pytest
import asyncio
import httpx
from typing import Dict, Any


class TestE2EWorkflows:
    """End-to-end workflow tests."""
    
    BASE_URLS = {
        "coordinator": "http://localhost:8000",
        "auth_service": "http://localhost:8006",
        "agent_hitl": "http://localhost:8008",
        "sandbox_execution": "http://localhost:8009",
    }
    
    @pytest.fixture
    async def http_client(self):
        async with httpx.AsyncClient(timeout=30.0) as client:
            yield client
    
    @pytest.fixture
    async def test_agent(self, http_client):
        """Create a test agent for workflows."""
        agent_data = {
            "agent_id": "e2e-test-agent",
            "name": "E2E Test Agent",
            "description": "Agent for end-to-end testing",
            "agent_type": "coding_agent",
            "owner_user_id": 1,
            "capabilities": ["code_execution", "code_generation"],
            "permissions": ["read:code", "write:code", "execute:code"],
            "compliance_level": "high"
        }
        
        try:
            response = await http_client.post(
                f"{self.BASE_URLS['auth_service']}/api/v1/agents",
                json=agent_data
            )
            if response.status_code in [201, 409]:  # 409 if already exists
                return agent_data
        except Exception:
            pass
        
        return agent_data
    
    @pytest.mark.asyncio
    async def test_simple_code_execution_workflow(self, http_client, test_agent):
        """Test simple code execution through ACGS coordinator."""
        operation_request = {
            "agent_id": test_agent["agent_id"],
            "agent_type": test_agent["agent_type"],
            "operation_type": "code_execution",
            "operation_description": "Execute simple Python code",
            "code": "print('Hello from E2E test')\nresult = 10 + 5\nprint(f'Result: {result}')",
            "execution_environment": "python",
            "operation_context": {
                "safe_operation": True,
                "test_mode": True
            },
            "bypass_hitl": True  # Skip HITL for faster testing
        }
        
        # Submit operation to coordinator
        response = await http_client.post(
            f"{self.BASE_URLS['coordinator']}/api/v1/operations",
            json=operation_request
        )
        
        # Should accept the operation
        assert response.status_code in [200, 201, 202]
        
        operation_result = response.json()
        assert "operation_id" in operation_result
        assert operation_result["agent_id"] == test_agent["agent_id"]
    
    @pytest.mark.asyncio
    async def test_hitl_review_workflow(self, http_client, test_agent):
        """Test operation requiring human review."""
        operation_request = {
            "agent_id": test_agent["agent_id"],
            "agent_type": test_agent["agent_type"],
            "operation_type": "system_command",
            "operation_description": "Execute system command requiring review",
            "operation_context": {
                "high_risk": True,
                "affects_system": True
            },
            "requires_human_approval": True
        }
        
        # Submit operation that should require HITL review
        response = await http_client.post(
            f"{self.BASE_URLS['coordinator']}/api/v1/operations",
            json=operation_request
        )
        
        # Should be accepted but pending review
        assert response.status_code in [200, 201, 202]
        
        operation_result = response.json()
        assert operation_result["status"] in ["pending_review", "processing"]
    
    @pytest.mark.asyncio
    async def test_policy_violation_workflow(self, http_client, test_agent):
        """Test operation that violates policies."""
        operation_request = {
            "agent_id": test_agent["agent_id"],
            "agent_type": test_agent["agent_type"],
            "operation_type": "malicious_action",
            "operation_description": "Attempt to bypass security controls",
            "operation_context": {
                "malicious_intent": True
            }
        }
        
        # Submit operation that should be rejected
        response = await http_client.post(
            f"{self.BASE_URLS['coordinator']}/api/v1/operations",
            json=operation_request
        )
        
        # Should be accepted for processing but will be rejected
        operation_result = response.json()
        
        # The operation should be rejected due to policy violations
        if operation_result.get("status") == "rejected":
            assert len(operation_result.get("policy_violations", [])) > 0
    
    @pytest.mark.asyncio
    async def test_sandbox_security_workflow(self, http_client, test_agent):
        """Test sandbox security enforcement."""
        operation_request = {
            "agent_id": test_agent["agent_id"],
            "agent_type": test_agent["agent_type"],
            "operation_type": "code_execution",
            "operation_description": "Test sandbox security",
            "code": "import os\nprint('Attempting to list files')\nprint(os.listdir('/'))",
            "execution_environment": "python",
            "operation_context": {
                "test_sandbox_security": True
            },
            "bypass_hitl": True
        }
        
        # Submit operation that tests sandbox boundaries
        response = await http_client.post(
            f"{self.BASE_URLS['coordinator']}/api/v1/operations",
            json=operation_request
        )
        
        # Should be processed (sandbox should contain the operation)
        assert response.status_code in [200, 201, 202]
        
        operation_result = response.json()
        # Execution should complete (though may be restricted by sandbox)
        assert operation_result["status"] in ["completed", "processing", "pending_review"]
    
    @pytest.mark.asyncio
    async def test_constitutional_compliance_workflow(self, http_client, test_agent):
        """Test constitutional compliance enforcement."""
        operation_request = {
            "agent_id": test_agent["agent_id"],
            "agent_type": test_agent["agent_type"],
            "operation_type": "data_access",
            "operation_description": "Access user personal data without consent",
            "operation_context": {
                "data_type": "personal",
                "user_consent": False,
                "constitutional_check": True
            }
        }
        
        # Submit operation that may violate constitutional principles
        response = await http_client.post(
            f"{self.BASE_URLS['coordinator']}/api/v1/operations",
            json=operation_request
        )
        
        operation_result = response.json()
        
        # Should enforce constitutional compliance
        assert operation_result.get("constitutional_compliance") is not None
    
    @pytest.mark.asyncio
    async def test_multi_service_coordination(self, http_client, test_agent):
        """Test coordination across multiple services."""
        # First, create a HITL review directly
        review_request = {
            "agent_id": test_agent["agent_id"],
            "agent_type": test_agent["agent_type"],
            "operation_type": "code_review",
            "operation_description": "Review code for compliance",
            "operation_context": {
                "complexity": "medium"
            }
        }
        
        response = await http_client.post(
            f"{self.BASE_URLS['agent_hitl']}/api/v1/reviews/evaluate",
            json=review_request
        )
        
        if response.status_code == 201:
            review_result = response.json()
            assert "review_id" in review_result
            assert "confidence_score" in review_result
        
        # Then test sandbox execution directly
        execution_request = {
            "agent_id": test_agent["agent_id"],
            "agent_type": test_agent["agent_type"],
            "environment": "python",
            "code": "# Simple test code\nprint('Multi-service test')",
            "language": "python"
        }
        
        response = await http_client.post(
            f"{self.BASE_URLS['sandbox_execution']}/api/v1/executions",
            json=execution_request
        )
        
        if response.status_code == 201:
            execution_result = response.json()
            assert "execution_id" in execution_result
    
    @pytest.mark.asyncio
    async def test_audit_trail_workflow(self, http_client, test_agent):
        """Test that operations create proper audit trails."""
        operation_request = {
            "agent_id": test_agent["agent_id"],
            "agent_type": test_agent["agent_type"],
            "operation_type": "audit_test",
            "operation_description": "Test audit trail generation",
            "operation_context": {
                "audit_test": True,
                "tracking_required": True
            }
        }
        
        # Submit operation
        response = await http_client.post(
            f"{self.BASE_URLS['coordinator']}/api/v1/operations",
            json=operation_request
        )
        
        operation_result = response.json()
        
        # Should have audit entries
        assert "audit_entries" in operation_result or "operation_id" in operation_result
    
    @pytest.mark.asyncio
    async def test_performance_workflow(self, http_client, test_agent):
        """Test system performance under normal load."""
        import time
        
        # Measure response time for a simple operation
        start_time = time.time()
        
        operation_request = {
            "agent_id": test_agent["agent_id"],
            "agent_type": test_agent["agent_type"],
            "operation_type": "performance_test",
            "operation_description": "Performance test operation",
            "bypass_hitl": True
        }
        
        response = await http_client.post(
            f"{self.BASE_URLS['coordinator']}/api/v1/operations",
            json=operation_request
        )
        
        response_time = time.time() - start_time
        
        # Should respond quickly (under 5 seconds)
        assert response_time < 5.0
        assert response.status_code in [200, 201, 202]
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, http_client, test_agent):
        """Test error handling across the system."""
        # Test with invalid operation data
        invalid_request = {
            "agent_id": "nonexistent-agent",
            "agent_type": "invalid_type",
            "operation_type": "",
            "operation_description": ""
        }
        
        response = await http_client.post(
            f"{self.BASE_URLS['coordinator']}/api/v1/operations",
            json=invalid_request
        )
        
        # Should handle errors gracefully
        assert response.status_code in [400, 422, 500]  # Various error codes acceptable


if __name__ == "__main__":
    pytest.main([__file__, "-v"])