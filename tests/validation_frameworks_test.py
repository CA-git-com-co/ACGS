"""
Comprehensive test suite for validation frameworks.
Tests constitutional compliance, performance accuracy, and authentication security.
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from services.shared.middleware.constitutional_validation import (
    ConstitutionalComplianceChecker,
    ConstitutionalValidationMiddleware,
    setup_constitutional_validation,
)
from services.shared.middleware.enhanced_auth_middleware import (
    AuthHeaders,
    EnhancedAuthMiddleware,
    ServiceTokenManager,
)
from services.shared.performance.performance_monitoring import (
    alert_performance_breach,
    monitor_cache_performance,
    track_performance_metrics,
)

# Import validation frameworks
from services.shared.validation.constitutional_validator import (
    ConstitutionalBaseModel,
    ConstitutionalRequest,
    ConstitutionalResponse,
    ValidationContext,
)

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestConstitutionalValidation:
    """Test constitutional validation framework."""

    def test_constitutional_base_model_validation(self):
        """Test constitutional hash validation in base model."""

        # Valid constitutional hash
        valid_data = {"constitutional_hash": CONSTITUTIONAL_HASH}
        model = ConstitutionalBaseModel(**valid_data)
        assert model.constitutional_hash == CONSTITUTIONAL_HASH

        # Invalid constitutional hash
        with pytest.raises(ValueError):
            invalid_data = {"constitutional_hash": "invalid_hash"}
            ConstitutionalBaseModel(**invalid_data)

    def test_constitutional_request_validation(self):
        """Test constitutional request model validation."""

        # Valid request
        valid_request = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "data": {"test": "value"},
        }
        request = ConstitutionalRequest(**valid_request)
        assert request.constitutional_hash == CONSTITUTIONAL_HASH
        assert request.data == {"test": "value"}

        # Invalid request
        with pytest.raises(ValueError):
            invalid_request = {
                "constitutional_hash": "wrong_hash",
                "data": {"test": "value"},
            }
            ConstitutionalRequest(**invalid_request)

    def test_constitutional_response_generation(self):
        """Test constitutional response model generation."""

        response_data = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "success": True,
            "data": {"result": "processed"},
        }
        response = ConstitutionalResponse(**response_data)

        assert response.constitutional_hash == CONSTITUTIONAL_HASH
        assert response.success is True
        assert response.data == {"result": "processed"}

        # Ensure timestamp is set
        assert response.timestamp is not None


class TestConstitutionalMiddleware:
    """Test constitutional validation middleware."""

    @pytest.fixture
    def test_app(self):
        """Create test FastAPI application with constitutional middleware."""
        app = FastAPI()

        app.add_middleware(
            ConstitutionalValidationMiddleware,
            constitutional_hash=CONSTITUTIONAL_HASH,
            performance_target_ms=5.0,
            enable_strict_validation=True,
        )

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        @app.post("/test-json")
        async def test_json_endpoint(request_data: dict):
            return {"received": request_data}

        return app

    def test_constitutional_headers_added(self, test_app):
        """Test that constitutional headers are added to responses."""
        client = TestClient(test_app)

        response = client.get("/test")

        assert response.status_code == 200
        assert response.headers.get("X-Constitutional-Hash") == CONSTITUTIONAL_HASH
        assert response.headers.get("X-Constitutional-Compliance") == "validated"
        assert "X-Processing-Time-Ms" in response.headers
        assert "X-Performance-Target-Ms" in response.headers
        assert "X-Performance-Compliant" in response.headers

    def test_constitutional_hash_validation_in_headers(self, test_app):
        """Test constitutional hash validation in request headers."""
        client = TestClient(test_app)

        # Valid constitutional hash
        valid_headers = {"X-Constitutional-Hash": CONSTITUTIONAL_HASH}
        response = client.get("/test", headers=valid_headers)
        assert response.status_code == 200

        # Invalid constitutional hash (should be rejected in strict mode)
        invalid_headers = {"X-Constitutional-Hash": "invalid_hash"}
        response = client.get("/test", headers=invalid_headers)
        assert response.status_code == 400

    def test_constitutional_hash_validation_in_body(self, test_app):
        """Test constitutional hash validation in request body."""
        client = TestClient(test_app)

        # Valid constitutional hash in body
        valid_body = {"constitutional_hash": CONSTITUTIONAL_HASH, "data": "test"}
        response = client.post("/test-json", json=valid_body)
        assert response.status_code == 200

        # Invalid constitutional hash in body
        invalid_body = {"constitutional_hash": "invalid_hash", "data": "test"}
        response = client.post("/test-json", json=invalid_body)
        assert response.status_code == 400

    def test_performance_monitoring(self, test_app):
        """Test performance monitoring in constitutional middleware."""
        client = TestClient(test_app)

        response = client.get("/test")

        processing_time = float(response.headers.get("X-Processing-Time-Ms", "0"))
        target_time = float(response.headers.get("X-Performance-Target-Ms", "5"))
        compliant = response.headers.get("X-Performance-Compliant")

        assert processing_time >= 0
        assert target_time == 5.0
        assert compliant in ["true", "false"]


class TestConstitutionalComplianceChecker:
    """Test constitutional compliance checker utility."""

    def test_hash_validation(self):
        """Test constitutional hash validation."""
        checker = ConstitutionalComplianceChecker()

        assert checker.validate_hash(CONSTITUTIONAL_HASH) is True
        assert checker.validate_hash("invalid_hash") is False

    def test_request_data_validation(self):
        """Test request data validation."""
        checker = ConstitutionalComplianceChecker()

        # Valid request data
        valid_data = {"constitutional_hash": CONSTITUTIONAL_HASH, "test": "value"}
        assert checker.validate_request_data(valid_data) is True

        # Invalid request data
        invalid_data = {"constitutional_hash": "wrong_hash", "test": "value"}
        assert checker.validate_request_data(invalid_data) is False

        # No hash (should be valid for requests)
        no_hash_data = {"test": "value"}
        assert checker.validate_request_data(no_hash_data) is True

    def test_response_data_validation(self):
        """Test response data validation."""
        checker = ConstitutionalComplianceChecker()

        # Valid response data
        valid_data = {"constitutional_hash": CONSTITUTIONAL_HASH, "result": "success"}
        assert checker.validate_response_data(valid_data) is True

        # Invalid response data
        invalid_data = {"constitutional_hash": "wrong_hash", "result": "success"}
        assert checker.validate_response_data(invalid_data) is False

        # No hash (should be invalid for responses)
        no_hash_data = {"result": "success"}
        assert checker.validate_response_data(no_hash_data) is False

    def test_ensure_compliance(self):
        """Test compliance enforcement."""
        checker = ConstitutionalComplianceChecker()

        data = {"test": "value"}
        compliant_data = checker.ensure_compliance(data)

        assert compliant_data["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert compliant_data["test"] == "value"


class TestEnhancedAuthMiddleware:
    """Test enhanced authentication middleware."""

    @pytest.fixture
    def test_app_with_auth(self):
        """Create test FastAPI application with authentication middleware."""
        app = FastAPI()

        app.add_middleware(
            EnhancedAuthMiddleware,
            service_name="test_service",
service_secret=os.getenv("ACGS_TEST_SECRET", "test_secret_key"),
            public_paths=["/public", "/health"],
            service_only_paths=["/internal"],
        )

        @app.get("/public")
        async def public_endpoint():
            return {"message": "public"}

        @app.get("/protected")
        async def protected_endpoint():
            return {"message": "protected"}

        @app.get("/internal")
        async def internal_endpoint():
            return {"message": "internal"}

        return app

    def test_public_path_access(self, test_app_with_auth):
        """Test access to public paths without authentication."""
        client = TestClient(test_app_with_auth)

        response = client.get("/public")
        assert response.status_code == 200
        assert response.json()["message"] == "public"

    @patch("httpx.AsyncClient.post")
    def test_valid_user_token(self, mock_post, test_app_with_auth):
        """Test access with valid user JWT token."""
        # Mock successful token validation
        mock_post.return_value = AsyncMock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "valid": True,
            "user_id": "test_user",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        client = TestClient(test_app_with_auth)

        # Create valid JWT token
        token_payload = {
            "user_id": "test_user",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }
        token = jwt.encode(token_payload, "test_secret", algorithm="HS256")

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/protected", headers=headers)

        assert response.status_code == 200
        assert response.json()["message"] == "protected"

    def test_service_token_generation(self):
        """Test service token generation and validation."""
        manager = ServiceTokenManager("test_service", "test_secret")

        token = manager.generate_service_token()
        assert token is not None

        # Decode and validate token
        decoded = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert decoded["service_name"] == "test_service"
        assert decoded["constitutional_hash"] == CONSTITUTIONAL_HASH

    def test_auth_headers_utility(self):
        """Test auth headers utility class."""
        headers = AuthHeaders.create_service_headers("test_service", "test_secret")

        assert "Authorization" in headers
        assert "X-Service-Name" in headers
        assert "X-Constitutional-Hash" in headers
        assert headers["X-Service-Name"] == "test_service"
        assert headers["X-Constitutional-Hash"] == CONSTITUTIONAL_HASH


class TestPerformanceMonitoring:
    """Test performance monitoring framework."""

    @pytest.mark.asyncio
    async def test_performance_tracking_decorator(self):
        """Test performance tracking decorator."""

        @track_performance_metrics("test_service", "test_endpoint", "GET")
        async def test_function():
            await asyncio.sleep(0.001)  # Simulate work
            return {"result": "success"}

        # Mock Prometheus metrics
        with patch(
            "services.shared.performance.performance_monitoring.REQUEST_DURATION"
        ) as mock_duration:
            with patch(
                "services.shared.performance.performance_monitoring.REQUEST_COUNT"
            ) as mock_count:
                result = await test_function()

                assert result["result"] == "success"
                mock_duration.labels.assert_called_with(
                    "test_service", "test_endpoint", "GET"
                )
                mock_count.labels.assert_called_with(
                    "test_service", "test_endpoint", "GET", "success"
                )

    @pytest.mark.asyncio
    async def test_cache_performance_monitoring(self):
        """Test cache performance monitoring."""

        @monitor_cache_performance("test_cache")
        async def cached_function(cache_hit=True):
            if cache_hit:
                return {"data": "cached", "cache_hit": True}
            else:
                await asyncio.sleep(0.001)  # Simulate cache miss work
                return {"data": "fresh", "cache_hit": False}

        # Test cache hit
        with patch(
            "services.shared.performance.performance_monitoring.CACHE_HIT_RATE"
        ) as mock_hit_rate:
            result = await cached_function(cache_hit=True)
            assert result["cache_hit"] is True
            mock_hit_rate.labels.assert_called_with("test_cache", "hit")

        # Test cache miss
        with patch(
            "services.shared.performance.performance_monitoring.CACHE_HIT_RATE"
        ) as mock_hit_rate:
            result = await cached_function(cache_hit=False)
            assert result["cache_hit"] is False
            mock_hit_rate.labels.assert_called_with("test_cache", "miss")

    @pytest.mark.asyncio
    async def test_performance_breach_alerting(self):
        """Test performance breach alerting."""

        with patch(
            "services.shared.performance.performance_monitoring.PERFORMANCE_ALERTS"
        ) as mock_alerts:
            # Test P99 latency breach
            await alert_performance_breach(
                service_name="test_service",
                metric_type="p99_latency",
                current_value=10.0,
                threshold=5.0,
            )

            mock_alerts.labels.assert_called_with(
                "test_service", "p99_latency", "breach"
            )


class TestIntegration:
    """Integration tests for all validation frameworks."""

    @pytest.fixture
    def full_test_app(self):
        """Create test app with all middleware integrated."""
        app = FastAPI()

        # Add all middleware
        app.add_middleware(
            EnhancedAuthMiddleware,
            service_name="integration_test",
service_secret=os.getenv("ACGS_TEST_SECRET", "test_secret_key"),
            public_paths=["/health", "/public"],
            service_only_paths=["/internal"],
        )

        app.add_middleware(
            ConstitutionalValidationMiddleware,
            constitutional_hash=CONSTITUTIONAL_HASH,
            performance_target_ms=5.0,
            enable_strict_validation=True,
        )

        @app.get("/health")
        async def health():
            return {"status": "healthy", "constitutional_hash": CONSTITUTIONAL_HASH}

        @app.post("/api/validate")
        @track_performance_metrics("integration_test", "validate", "POST")
        async def validate_endpoint(request_data: ConstitutionalRequest):
            response_data = {
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "success": True,
                "data": {"validated": True},
            }
            return ConstitutionalResponse(**response_data)

        return app

    def test_full_integration_health_check(self, full_test_app):
        """Test health check with all middleware."""
        client = TestClient(full_test_app)

        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["constitutional_hash"] == CONSTITUTIONAL_HASH

        # Check constitutional validation headers
        assert response.headers.get("X-Constitutional-Hash") == CONSTITUTIONAL_HASH
        assert response.headers.get("X-Constitutional-Compliance") == "validated"

    @patch("httpx.AsyncClient.post")
    def test_full_integration_authenticated_request(self, mock_post, full_test_app):
        """Test authenticated request with constitutional validation."""
        # Mock successful token validation
        mock_post.return_value = AsyncMock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "valid": True,
            "user_id": "test_user",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        client = TestClient(full_test_app)

        # Create valid JWT token
        token_payload = {
            "user_id": "test_user",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }
        token = jwt.encode(token_payload, "test_secret", algorithm="HS256")

        # Valid request with constitutional compliance
        request_data = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "data": {"test": "validation"},
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
        }

        response = client.post("/api/validate", json=request_data, headers=headers)

        assert response.status_code == 200

        response_json = response.json()
        assert response_json["success"] is True
        assert response_json["constitutional_hash"] == CONSTITUTIONAL_HASH

        # Check constitutional validation headers
        assert response.headers.get("X-Constitutional-Hash") == CONSTITUTIONAL_HASH
        assert response.headers.get("X-Constitutional-Compliance") == "validated"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
