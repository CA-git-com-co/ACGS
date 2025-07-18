"""
Unit Tests for Service Integration Validator
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive test suite for the ServiceIntegrationValidator
covering all integration validation functionality.

Test Coverage:
- Service registration and health validation
- Constitutional compliance across services
- Dependency validation and resolution
- Cross-service communication testing
- Performance integration validation
- Error handling and recovery
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any
import aiohttp

from services.shared.integration.service_integration_validator import (
    ServiceIntegrationValidator,
    ServiceEndpoint,
    IntegrationMetrics,
    INTEGRATION_TARGETS,
    CONSTITUTIONAL_HASH
)


class TestIntegrationMetrics:
    """Test suite for IntegrationMetrics."""

    def test_initialization(self):
        """Test metrics initialization."""
        metrics = IntegrationMetrics()
        
        assert metrics.total_validations == 0
        assert metrics.successful_validations == 0
        assert metrics.failed_validations == 0
        assert metrics.constitutional_violations == 0

    def test_add_validation_success(self):
        """Test adding successful validation."""
        metrics = IntegrationMetrics()
        
        metrics.add_validation(0.05, success=True, constitutional_compliant=True)
        
        assert metrics.total_validations == 1
        assert metrics.successful_validations == 1
        assert metrics.failed_validations == 0
        assert metrics.constitutional_violations == 0

    def test_add_validation_failure(self):
        """Test adding failed validation."""
        metrics = IntegrationMetrics()
        
        metrics.add_validation(0.1, success=False, constitutional_compliant=False)
        
        assert metrics.total_validations == 1
        assert metrics.successful_validations == 0
        assert metrics.failed_validations == 1
        assert metrics.constitutional_violations == 1

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        metrics = IntegrationMetrics()
        
        # No validations
        assert metrics.get_success_rate() == 1.0
        
        # Add mixed validations
        metrics.add_validation(0.05, success=True)
        metrics.add_validation(0.1, success=True)
        metrics.add_validation(0.15, success=False)
        
        assert metrics.get_success_rate() == 2/3

    def test_avg_response_time(self):
        """Test average response time calculation."""
        metrics = IntegrationMetrics()
        
        # No validations
        assert metrics.get_avg_response_time_ms() == 0.0
        
        # Add validations
        metrics.add_validation(0.002)  # 2ms
        metrics.add_validation(0.004)  # 4ms
        
        assert metrics.get_avg_response_time_ms() == 3.0

    def test_constitutional_compliance_rate(self):
        """Test constitutional compliance rate calculation."""
        metrics = IntegrationMetrics()
        
        # No validations
        assert metrics.get_constitutional_compliance_rate() == 1.0
        
        # Add mixed compliance
        metrics.add_validation(0.05, constitutional_compliant=True)
        metrics.add_validation(0.05, constitutional_compliant=True)
        metrics.add_validation(0.05, constitutional_compliant=False)
        
        assert metrics.get_constitutional_compliance_rate() == 2/3


class TestServiceEndpoint:
    """Test suite for ServiceEndpoint."""

    def test_initialization(self):
        """Test service endpoint initialization."""
        endpoint = ServiceEndpoint(
            name="test_service",
            url="http://localhost",
            port=8080,
            dependencies=["dependency1", "dependency2"]
        )
        
        assert endpoint.name == "test_service"
        assert endpoint.url == "http://localhost"
        assert endpoint.port == 8080
        assert endpoint.dependencies == ["dependency1", "dependency2"]
        assert endpoint.required is True
        assert endpoint.health_path == "/health"


class TestServiceIntegrationValidator:
    """Test suite for ServiceIntegrationValidator."""

    @pytest.fixture
    def validator(self):
        """Create a service integration validator."""
        return ServiceIntegrationValidator()

    @pytest.fixture
    def mock_session(self):
        """Create a mock HTTP session."""
        session = AsyncMock(spec=aiohttp.ClientSession)
        return session

    @pytest.fixture
    def sample_service(self):
        """Create a sample service endpoint."""
        return ServiceEndpoint(
            name="test_service",
            url="http://localhost",
            port=8080,
            dependencies=["dependency_service"]
        )

    def test_initialization(self, validator):
        """Test validator initialization."""
        assert validator.constitutional_hash == CONSTITUTIONAL_HASH
        assert len(validator.services) == 0
        assert len(validator.service_dependencies) == 0
        assert validator.session is None

    @pytest.mark.asyncio
    async def test_initialize_success(self, validator):
        """Test successful validator initialization."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            await validator.initialize()
            
            assert validator.session is not None
            assert len(validator.services) > 0  # Default services registered

    @pytest.mark.asyncio
    async def test_initialize_constitutional_failure(self, validator):
        """Test initialization failure due to constitutional compliance."""
        # Mock validator to fail
        validator.constitutional_validator.validate_hash.return_value = False
        
        with pytest.raises(RuntimeError, match="Constitutional compliance violation"):
            await validator.initialize()

    @pytest.mark.asyncio
    async def test_register_service(self, validator, sample_service):
        """Test service registration."""
        await validator.register_service(sample_service)
        
        assert "test_service" in validator.services
        assert validator.services["test_service"] == sample_service
        assert "test_service" in validator.service_dependencies
        assert "dependency_service" in validator.service_dependencies["test_service"]

    @pytest.mark.asyncio
    async def test_validate_service_health_success(self, validator, sample_service, mock_session):
        """Test successful service health validation."""
        validator.session = mock_session
        await validator.register_service(sample_service)
        
        # Mock successful health response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "healthy": True,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await validator.validate_service_health("test_service")
        
        assert result["healthy"] is True
        assert result["service"] == "test_service"
        assert result["constitutional_compliant"] is True
        assert "response_time_ms" in result

    @pytest.mark.asyncio
    async def test_validate_service_health_failure(self, validator, sample_service, mock_session):
        """Test failed service health validation."""
        validator.session = mock_session
        await validator.register_service(sample_service)
        
        # Mock failed health response
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await validator.validate_service_health("test_service")
        
        assert result["healthy"] is False
        assert result["service"] == "test_service"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_validate_service_health_nonexistent(self, validator):
        """Test health validation for non-existent service."""
        result = await validator.validate_service_health("nonexistent_service")
        
        assert result["healthy"] is False
        assert "not registered" in result["error"]

    @pytest.mark.asyncio
    async def test_validate_constitutional_compliance_success(self, validator, sample_service, mock_session):
        """Test successful constitutional compliance validation."""
        validator.session = mock_session
        await validator.register_service(sample_service)
        
        # Mock successful constitutional response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "compliant": True
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await validator.validate_constitutional_compliance("test_service")
        
        assert result["compliant"] is True
        assert result["service"] == "test_service"
        assert result["service_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_validate_constitutional_compliance_violation(self, validator, sample_service, mock_session):
        """Test constitutional compliance violation."""
        validator.session = mock_session
        await validator.register_service(sample_service)
        
        # Mock non-compliant response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "constitutional_hash": "invalid_hash",
            "compliant": False
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await validator.validate_constitutional_compliance("test_service")
        
        assert result["compliant"] is False
        assert result["service_hash"] == "invalid_hash"
        assert validator.metrics.constitutional_violations > 0

    @pytest.mark.asyncio
    async def test_validate_service_dependencies_success(self, validator, mock_session):
        """Test successful dependency validation."""
        validator.session = mock_session
        
        # Register services with dependencies
        dependency_service = ServiceEndpoint("dependency_service", "http://localhost", 8081)
        main_service = ServiceEndpoint("main_service", "http://localhost", 8082, dependencies=["dependency_service"])
        
        await validator.register_service(dependency_service)
        await validator.register_service(main_service)
        
        # Mock successful health responses
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"healthy": True, "constitutional_hash": CONSTITUTIONAL_HASH}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await validator.validate_service_dependencies("main_service")
        
        assert result["dependencies_healthy"] is True
        assert "dependency_service" in result["dependencies"]
        assert result["dependencies"]["dependency_service"]["healthy"] is True

    @pytest.mark.asyncio
    async def test_validate_service_dependencies_failure(self, validator, mock_session):
        """Test dependency validation with unhealthy dependency."""
        validator.session = mock_session
        
        # Register services with dependencies
        dependency_service = ServiceEndpoint("dependency_service", "http://localhost", 8081)
        main_service = ServiceEndpoint("main_service", "http://localhost", 8082, dependencies=["dependency_service"])
        
        await validator.register_service(dependency_service)
        await validator.register_service(main_service)
        
        # Mock failed health response for dependency
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await validator.validate_service_dependencies("main_service")
        
        assert result["dependencies_healthy"] is False
        assert result["dependencies"]["dependency_service"]["healthy"] is False
        assert validator.metrics.dependency_failures > 0

    @pytest.mark.asyncio
    async def test_validate_cross_service_communication(self, validator, mock_session):
        """Test cross-service communication validation."""
        validator.session = mock_session
        
        # Register services
        service1 = ServiceEndpoint("service1", "http://localhost", 8081)
        service2 = ServiceEndpoint("service2", "http://localhost", 8082)
        
        await validator.register_service(service1)
        await validator.register_service(service2)
        
        # Mock successful communication
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await validator.validate_cross_service_communication("service1", "service2")
        
        assert result["communication_healthy"] is True
        assert result["from_service"] == "service1"
        assert result["to_service"] == "service2"
        assert "latency_ms" in result

    @pytest.mark.asyncio
    async def test_validate_all_services(self, validator, mock_session):
        """Test comprehensive validation of all services."""
        validator.session = mock_session
        
        # Register a simple service
        service = ServiceEndpoint("test_service", "http://localhost", 8080)
        await validator.register_service(service)
        
        # Mock successful responses
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"healthy": True, "constitutional_hash": CONSTITUTIONAL_HASH}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await validator.validate_all_services()
        
        assert "overall_healthy" in result
        assert "services" in result
        assert "constitutional_compliance" in result
        assert "dependencies" in result
        assert "summary" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    def test_get_integration_metrics(self, validator):
        """Test integration metrics collection."""
        # Add some test data
        validator.metrics.total_validations = 100
        validator.metrics.successful_validations = 95
        validator.metrics.constitutional_violations = 2
        
        metrics = validator.get_integration_metrics()
        
        assert "validation_metrics" in metrics
        assert "service_registry" in metrics
        assert "dependency_graph" in metrics
        assert "error_statistics" in metrics
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_optimize_integration(self, validator):
        """Test integration optimization."""
        # Set up some metrics that need optimization
        validator.metrics.total_validations = 100
        validator.metrics.successful_validations = 80  # 80% success rate
        validator.metrics.constitutional_violations = 10
        
        optimization_result = await validator.optimize_integration()
        
        assert "optimizations_applied" in optimization_result
        assert "recommendations" in optimization_result
        assert "current_metrics" in optimization_result

    @pytest.mark.asyncio
    async def test_performance_integration_validation(self, validator):
        """Test performance integration validation."""
        # Mock performance service
        mock_performance_service = AsyncMock()
        mock_performance_service.get_performance_summary.return_value = {
            "targets_met": {
                "response_time": True,
                "success_rate": True,
                "cache_hit_rate": True
            },
            "integration_metrics": {
                "avg_response_time_ms": 2.0,
                "success_rate": 0.99
            }
        }
        validator.performance_service = mock_performance_service
        
        result = await validator.validate_performance_integration()
        
        assert result["performance_integration_healthy"] is True
        assert "targets_met" in result
        assert "integration_metrics" in result

    @pytest.mark.asyncio
    async def test_concurrent_validations(self, validator, mock_session):
        """Test concurrent service validations."""
        validator.session = mock_session
        
        # Register multiple services
        services = [
            ServiceEndpoint(f"service_{i}", "http://localhost", 8080 + i)
            for i in range(5)
        ]
        
        for service in services:
            await validator.register_service(service)
        
        # Mock successful responses
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"healthy": True, "constitutional_hash": CONSTITUTIONAL_HASH}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        # Validate all services concurrently
        tasks = [
            validator.validate_service_health(service.name)
            for service in services
        ]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(result["healthy"] for result in results)

    @pytest.mark.asyncio
    async def test_error_handling(self, validator, mock_session):
        """Test error handling in validation."""
        validator.session = mock_session
        
        service = ServiceEndpoint("error_service", "http://localhost", 8080)
        await validator.register_service(service)
        
        # Mock connection error
        mock_session.get.side_effect = aiohttp.ClientError("Connection failed")
        
        result = await validator.validate_service_health("error_service")
        
        assert result["healthy"] is False
        assert "error" in result
        assert validator.metrics.health_check_failures > 0

    @pytest.mark.asyncio
    async def test_close(self, validator, mock_session):
        """Test validator closure."""
        validator.session = mock_session
        validator._monitoring_enabled = True
        validator._monitoring_task = AsyncMock()
        
        await validator.close()
        
        assert validator._monitoring_enabled is False
        validator._monitoring_task.cancel.assert_called_once()
        mock_session.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
