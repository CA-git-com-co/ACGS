#!/usr/bin/env python3
"""
Test suite for the Comprehensive Load Testing Suite
Validates the load testing framework functionality
"""

import asyncio
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from tests.performance.comprehensive_load_testing_suite import (
    ComprehensiveLoadTestSuite,
    LoadTestMetrics,
    ServiceEndpoint,
    ChaosScenario
)

class TestComprehensiveLoadTestSuite:
    """Test cases for the comprehensive load testing suite."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary configuration file for testing."""
        config = {
            "max_concurrent_users": 10,
            "test_duration_seconds": 5,
            "chaos_enabled": False,
            "monitoring_enabled": False
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            yield f.name
        
        # Cleanup
        os.unlink(f.name)
    
    @pytest.fixture
    def load_test_suite(self, temp_config_file):
        """Create a load test suite instance for testing."""
        return ComprehensiveLoadTestSuite(temp_config_file)
    
    def test_initialization(self, load_test_suite):
        """Test that the load test suite initializes correctly."""
        assert load_test_suite.config['max_concurrent_users'] == 10
        assert load_test_suite.config['test_duration_seconds'] == 5
        assert load_test_suite.config['chaos_enabled'] is False
        
        # Check service endpoints are initialized
        assert len(load_test_suite.service_endpoints) > 0
        assert all(isinstance(ep, ServiceEndpoint) for ep in load_test_suite.service_endpoints)
        
        # Check chaos scenarios are initialized
        assert len(load_test_suite.chaos_scenarios) > 0
        assert all(isinstance(scenario, ChaosScenario) for scenario in load_test_suite.chaos_scenarios)
        
        # Check performance targets
        assert 'policy_generation_latency_ms' in load_test_suite.performance_targets
        assert 'throughput_rps' in load_test_suite.performance_targets
    
    def test_service_endpoints_configuration(self, load_test_suite):
        """Test that service endpoints are properly configured."""
        endpoints = load_test_suite.service_endpoints
        
        # Check required services are present
        service_names = [ep.name for ep in endpoints]
        required_services = [
            'policy_governance_controller',
            'constitutional_trainer',
            'quantum_error_correction',
            'democratic_governance_module',
            'appeals_logging_service'
        ]
        
        for service in required_services:
            assert service in service_names, f"Required service {service} not found"
        
        # Check endpoint properties
        for endpoint in endpoints:
            assert endpoint.name
            assert endpoint.url
            assert endpoint.method in ['GET', 'POST']
            assert endpoint.expected_status > 0
            assert endpoint.weight > 0
    
    def test_chaos_scenarios_configuration(self, load_test_suite):
        """Test that chaos scenarios are properly configured."""
        scenarios = load_test_suite.chaos_scenarios
        
        # Check scenario properties
        for scenario in scenarios:
            assert scenario.name
            assert scenario.description
            assert scenario.duration_seconds > 0
            assert 0 <= scenario.failure_rate <= 1
            assert len(scenario.target_services) > 0
            assert len(scenario.failure_types) > 0
    
    @pytest.mark.asyncio
    async def test_single_service_test(self, load_test_suite):
        """Test single service testing functionality."""
        # Create a mock endpoint
        endpoint = ServiceEndpoint(
            name="test_service",
            url="http://httpbin.org/status/200",
            method="GET",
            expected_status=200
        )
        
        # Run a very short test
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock the response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="OK")
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            # Run test for 1 second
            metrics = await load_test_suite._test_single_service(endpoint, duration=1)
            
            # Validate metrics
            assert isinstance(metrics, LoadTestMetrics)
            assert metrics.scenario_name == "baseline_test_service"
            assert metrics.total_requests >= 0
            assert metrics.end_time is not None
    
    @pytest.mark.asyncio
    async def test_chaos_injection(self, load_test_suite):
        """Test chaos injection functionality."""
        scenario = ChaosScenario(
            name="test_chaos",
            description="Test chaos scenario",
            duration_seconds=2,
            failure_rate=0.5,
            target_services=["test_service"],
            failure_types=["latency"]
        )
        
        # Run chaos injection
        chaos_events = await load_test_suite._inject_chaos(scenario)
        
        # Validate chaos events
        assert isinstance(chaos_events, int)
        assert chaos_events >= 0
    
    def test_metrics_calculation(self, load_test_suite):
        """Test metrics calculation functionality."""
        # Create sample test results
        baseline_results = {
            "test_service": {
                "total_requests": 100,
                "failed_requests": 5,
                "avg_response_time_ms": 150.0,
                "throughput_rps": 10.0,
                "error_rate": 0.05
            }
        }
        
        chaos_results = {
            "chaos_test": {
                "total_requests": 80,
                "failed_requests": 8,
                "error_rate": 0.1
            }
        }
        
        stress_results = {
            "stress_100_users": {
                "total_requests": 200,
                "failed_requests": 2,
                "error_rate": 0.01
            }
        }
        
        # Calculate summary metrics
        summary = load_test_suite._calculate_summary_metrics(
            baseline_results, chaos_results, stress_results
        )
        
        # Validate summary
        assert 'total_requests' in summary
        assert 'total_errors' in summary
        assert 'avg_response_time_ms' in summary
        assert 'chaos_resilience_score' in summary
        assert 'performance_targets_met' in summary
        
        # Check calculations
        assert summary['total_requests'] == 100  # Only baseline counted
        assert summary['total_errors'] == 5
        assert summary['avg_response_time_ms'] == 150.0
    
    def test_recommendations_generation(self, load_test_suite):
        """Test recommendations generation."""
        # Create sample results with issues
        baseline_results = {
            "slow_service": {
                "avg_response_time_ms": 500.0,  # High latency
                "error_rate": 0.02  # High error rate
            }
        }
        
        chaos_results = {
            "high_impact_chaos": {
                "error_rate": 0.15  # High chaos impact
            }
        }
        
        stress_results = {
            "stress_degradation": {
                "error_rate": 0.08  # Performance degradation
            }
        }
        
        # Generate recommendations
        recommendations = load_test_suite._generate_recommendations(
            baseline_results, chaos_results, stress_results
        )
        
        # Validate recommendations
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check for specific recommendations based on the issues
        rec_text = ' '.join(recommendations)
        assert 'latency' in rec_text.lower() or 'optimize' in rec_text.lower()
        assert 'error' in rec_text.lower() or 'reliability' in rec_text.lower()
    
    def test_report_generation(self, load_test_suite):
        """Test comprehensive report generation."""
        baseline_results = {"test": {"total_requests": 100}}
        chaos_results = {"chaos": {"total_requests": 50}}
        stress_results = {"stress": {"total_requests": 200}}
        suite_duration = 300.0
        
        # Generate report
        report = load_test_suite._generate_comprehensive_report(
            baseline_results, chaos_results, stress_results, suite_duration
        )
        
        # Validate report structure
        assert 'test_suite' in report
        assert 'timestamp' in report
        assert 'suite_duration_seconds' in report
        assert 'configuration' in report
        assert 'performance_targets' in report
        assert 'results' in report
        assert 'summary' in report
        assert 'recommendations' in report
        
        # Check results structure
        results = report['results']
        assert 'baseline' in results
        assert 'chaos_engineering' in results
        assert 'stress_testing' in results
    
    @pytest.mark.asyncio
    async def test_load_test_config_loading(self):
        """Test loading configuration from file."""
        # Test with non-existent file (should use defaults)
        suite1 = ComprehensiveLoadTestSuite("non_existent_file.json")
        assert suite1.config['max_concurrent_users'] == 1000  # Default value
        
        # Test with valid config file
        config = {"max_concurrent_users": 500, "test_duration_seconds": 120}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_file = f.name
        
        try:
            suite2 = ComprehensiveLoadTestSuite(config_file)
            assert suite2.config['max_concurrent_users'] == 500
            assert suite2.config['test_duration_seconds'] == 120
        finally:
            os.unlink(config_file)
    
    def test_performance_targets_validation(self, load_test_suite):
        """Test that performance targets are properly defined."""
        targets = load_test_suite.performance_targets
        
        required_targets = [
            'policy_generation_latency_ms',
            'throughput_rps',
            'uptime_percent',
            'false_positive_reduction_percent',
            'detection_accuracy_percent'
        ]
        
        for target in required_targets:
            assert target in targets, f"Required performance target {target} not found"
            assert isinstance(targets[target], (int, float)), f"Target {target} should be numeric"
            assert targets[target] > 0, f"Target {target} should be positive"


@pytest.mark.asyncio
async def test_integration_with_mock_services():
    """Integration test with mocked services."""
    # Create a minimal test suite
    suite = ComprehensiveLoadTestSuite()
    suite.config['max_concurrent_users'] = 5
    suite.config['test_duration_seconds'] = 2
    suite.config['chaos_enabled'] = False
    
    # Mock all HTTP requests to return success
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="OK")
        
        # Mock both GET and POST methods
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
        
        # Run baseline tests only
        baseline_results = await suite._run_baseline_tests()
        
        # Validate results
        assert isinstance(baseline_results, dict)
        assert len(baseline_results) > 0
        
        # Check that each service was tested
        service_names = [ep.name for ep in suite.service_endpoints]
        for service_name in service_names:
            assert service_name in baseline_results


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
