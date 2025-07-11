"""
GitHub Webhook Integration Tests for ACGS Integrity Service
Constitutional Hash: cdd01ef066bc6cf2

Tests for GitHub webhook processing with constitutional compliance validation.
"""

import json
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestGitHubWebhookIntegration:
    """Test GitHub webhook integration with constitutional compliance."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        # This would normally import the actual FastAPI app
        # For now, we'll create a minimal test setup
        from fastapi import FastAPI
        app = FastAPI()
        
        # Add the GitHub router (would normally be imported)
        try:
            from services.platform_services.integrity.integrity_service.app.api.v1.github_webhooks import github_router
            app.include_router(github_router, prefix="/api/v1")
        except ImportError:
            pytest.skip("GitHub webhook router not available")
        
        return TestClient(app)
    
    def test_webhook_config_endpoint(self, client):
        """Test webhook configuration endpoint."""
        response = client.get("/api/v1/webhooks/github/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "supported_events" in data
        assert "constitutional_compliance" in data
        assert data["constitutional_compliance"]["hash"] == CONSTITUTIONAL_HASH
        assert "configuration_guide" in data
    
    def test_webhook_health_endpoint(self, client):
        """Test webhook health check endpoint."""
        response = client.get("/api/v1/webhooks/github/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "github-webhooks"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "supported_events" in data
    
    def test_push_event_processing(self, client):
        """Test GitHub push event processing."""
        push_payload = {
            "ref": "refs/heads/main",
            "repository": {
                "full_name": "test/repo"
            },
            "commits": [
                {
                    "id": "abc123",
                    "message": f"Test commit with constitutional hash {CONSTITUTIONAL_HASH}"
                },
                {
                    "id": "def456", 
                    "message": "Regular commit without constitutional context"
                }
            ]
        }
        
        headers = {
            "X-GitHub-Event": "push",
            "X-GitHub-Delivery": "test-delivery-123",
            "Content-Type": "application/json"
        }
        
        response = client.post(
            "/api/v1/webhooks/github",
            json=push_payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "processed"
        assert data["event_type"] == "push"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "processed_data" in data
        
        processed_data = data["processed_data"]
        assert processed_data["event_type"] == "push"
        assert processed_data["repository"] == "test/repo"
        assert processed_data["commit_count"] == 2
    
    def test_pull_request_event_processing(self, client):
        """Test GitHub pull request event processing."""
        pr_payload = {
            "action": "opened",
            "pull_request": {
                "number": 42,
                "title": "Constitutional compliance improvements",
                "body": f"This PR improves constitutional compliance with hash {CONSTITUTIONAL_HASH}"
            },
            "repository": {
                "full_name": "test/repo"
            }
        }
        
        headers = {
            "X-GitHub-Event": "pull_request", 
            "X-GitHub-Delivery": "test-delivery-124",
            "Content-Type": "application/json"
        }
        
        response = client.post(
            "/api/v1/webhooks/github",
            json=pr_payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "processed"
        assert data["event_type"] == "pull_request"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        processed_data = data["processed_data"]
        assert processed_data["action"] == "opened"
        assert processed_data["pr_number"] == 42
        assert "constitutional" in processed_data["governance_flags"]
        assert processed_data["requires_constitutional_validation"] == True
        assert processed_data["has_constitutional_hash"] == True
        assert processed_data["constitutional_compliance"] == True
    
    def test_security_advisory_event_processing(self, client):
        """Test GitHub security advisory event processing."""
        security_payload = {
            "action": "published",
            "security_advisory": {
                "ghsa_id": "GHSA-test-1234",
                "severity": "high",
                "summary": "High severity security vulnerability"
            },
            "repository": {
                "full_name": "test/repo"
            }
        }
        
        headers = {
            "X-GitHub-Event": "security_advisory",
            "X-GitHub-Delivery": "test-delivery-125", 
            "Content-Type": "application/json"
        }
        
        response = client.post(
            "/api/v1/webhooks/github",
            json=security_payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "processed"
        assert data["event_type"] == "security_advisory"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        processed_data = data["processed_data"]
        assert processed_data["event_type"] == "security_advisory"
        assert processed_data["severity"] == "high"
        assert processed_data["requires_immediate_attention"] == True
    
    def test_unsupported_event_handling(self, client):
        """Test handling of unsupported GitHub events."""
        unsupported_payload = {
            "repository": {"full_name": "test/repo"}
        }
        
        headers = {
            "X-GitHub-Event": "unsupported_event",
            "X-GitHub-Delivery": "test-delivery-126",
            "Content-Type": "application/json"
        }
        
        response = client.post(
            "/api/v1/webhooks/github",
            json=unsupported_payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "not supported" in data["message"]
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
    
    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON payload."""
        headers = {
            "X-GitHub-Event": "push",
            "X-GitHub-Delivery": "test-delivery-127",
            "Content-Type": "application/json"
        }
        
        response = client.post(
            "/api/v1/webhooks/github",
            data="invalid json",
            headers=headers
        )
        
        assert response.status_code == 400
        assert "Invalid JSON payload" in response.json()["detail"]
    
    def test_constitutional_compliance_validation(self, client):
        """Test constitutional compliance validation logic."""
        # Test PR without constitutional hash when constitutional changes are made
        pr_payload = {
            "action": "opened",
            "pull_request": {
                "number": 43,
                "title": "Constitutional policy updates",
                "body": "This PR updates constitutional policies but missing hash"
            },
            "repository": {
                "full_name": "test/repo"
            }
        }
        
        headers = {
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": "test-delivery-128",
            "Content-Type": "application/json"
        }
        
        response = client.post(
            "/api/v1/webhooks/github", 
            json=pr_payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        processed_data = data["processed_data"]
        assert processed_data["requires_constitutional_validation"] == True
        assert processed_data["has_constitutional_hash"] == False
        assert processed_data["constitutional_compliance"] == False
    
    def test_webhook_test_endpoint(self, client):
        """Test webhook test endpoint."""
        test_payload = {
            "test_field": "test_value"
        }
        
        response = client.post(
            "/api/v1/webhooks/github/test",
            json=test_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "test_processed"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "test_data" in data
    
    def test_signature_verification(self):
        """Test webhook signature verification logic."""
        from services.platform_services.integrity.integrity_service.app.api.v1.github_webhooks import GitHubWebhookProcessor
        
        processor = GitHubWebhookProcessor()
        
        # Test valid signature
        payload = b'{"test": "data"}'
        secret = "test-secret"
        
        # Calculate expected signature
        import hmac
        import hashlib
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        signature = f"sha256={expected_sig}"
        
        assert processor.verify_signature(payload, signature, secret) == True
        
        # Test invalid signature
        invalid_signature = "sha256=invalid"
        assert processor.verify_signature(payload, invalid_signature, secret) == False
        
        # Test missing signature
        assert processor.verify_signature(payload, "", secret) == False
    
    @pytest.mark.asyncio
    async def test_audit_trail_integration(self):
        """Test audit trail integration."""
        from services.platform_services.integrity.integrity_service.app.api.v1.github_webhooks import GitHubWebhookProcessor
        
        processor = GitHubWebhookProcessor()
        
        webhook_data = {
            "event_type": "test",
            "repository": "test/repo",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Test audit entry creation
        result = await processor.create_audit_entry(webhook_data)
        assert result == True  # Should succeed in test environment
    
    def test_constitutional_hash_validation_in_responses(self, client):
        """Test that all responses include constitutional hash."""
        endpoints = [
            "/api/v1/webhooks/github/config",
            "/api/v1/webhooks/github/health"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            assert data.get("constitutional_hash") == CONSTITUTIONAL_HASH
    
    def test_webhook_processing_performance(self, client):
        """Test webhook processing performance requirements."""
        import time
        
        push_payload = {
            "ref": "refs/heads/main", 
            "repository": {"full_name": "test/repo"},
            "commits": [{"id": "abc123", "message": "Test commit"}]
        }
        
        headers = {
            "X-GitHub-Event": "push",
            "X-GitHub-Delivery": "perf-test",
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        response = client.post(
            "/api/v1/webhooks/github",
            json=push_payload,
            headers=headers
        )
        processing_time = time.time() - start_time
        
        assert response.status_code == 200
        # Webhook processing should be fast (< 100ms for simple events)
        assert processing_time < 0.1, f"Processing took {processing_time:.3f}s, should be <0.1s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])