#!/usr/bin/env python3
"""
DeepSeek R1 Pilot Testing Script

Validates the DeepSeek R1 migration pilot implementation including:
- A/B testing functionality
- Constitutional compliance validation
- Cost tracking and analysis
- Performance monitoring
- Fallback mechanisms

Usage:
    python scripts/test_deepseek_r1_pilot.py
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.shared.ai_model_service import AIModelService
from services.shared.deepseek_r1_pilot import DeepSeekR1PilotManager, PilotConfiguration
from services.shared.deepseek_r1_monitoring import DeepSeekR1Monitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeepSeekR1PilotTester:
    """Test suite for DeepSeek R1 pilot implementation."""
    
    def __init__(self):
        self.test_results = []
        self.pilot_manager = None
        self.ai_service = None
        self.monitor = None
    
    async def setup(self):
        """Set up test environment."""
        logger.info("Setting up DeepSeek R1 pilot test environment...")
        
        # Set environment variables for testing
        os.environ["DEEPSEEK_R1_PILOT_ENABLED"] = "true"
        os.environ["DEEPSEEK_R1_TRAFFIC_PERCENTAGE"] = "50"  # Higher for testing
        os.environ["DEEPSEEK_R1_COMPLIANCE_THRESHOLD"] = "0.95"
        os.environ["DEEPSEEK_R1_RESPONSE_TIME_THRESHOLD"] = "2000"
        os.environ["DEEPSEEK_R1_COST_TRACKING"] = "true"
        os.environ["DEEPSEEK_R1_FALLBACK_ENABLED"] = "true"
        os.environ["ACGS_CONSTITUTIONAL_HASH"] = "cdd01ef066bc6cf2"
        
        # Mock OpenRouter API key for testing
        if not os.environ.get("OPENROUTER_API_KEY"):
            os.environ["OPENROUTER_API_KEY"] = "test_key_mock"
            logger.warning("Using mock OpenRouter API key for testing")
        
        # Initialize components
        self.pilot_manager = DeepSeekR1PilotManager()
        self.ai_service = AIModelService()
        self.monitor = DeepSeekR1Monitor()
        
        logger.info("Test environment setup complete")
    
    def record_test_result(self, test_name: str, passed: bool, message: str, details: dict = None):
        """Record test result."""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "details": details or {},
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "PASS" if passed else "FAIL"
        logger.info(f"[{status}] {test_name}: {message}")
    
    async def test_pilot_configuration(self):
        """Test pilot configuration loading."""
        test_name = "Pilot Configuration"
        
        try:
            config = self.pilot_manager.config
            
            # Verify configuration values
            assert config.enabled == True, "Pilot should be enabled"
            assert config.traffic_percentage == 50, f"Expected 50% traffic, got {config.traffic_percentage}%"
            assert config.constitutional_compliance_threshold == 0.95, "Compliance threshold should be 0.95"
            assert config.constitutional_hash == "cdd01ef066bc6cf2", "Constitutional hash mismatch"
            
            self.record_test_result(test_name, True, "Configuration loaded correctly", {
                "enabled": config.enabled,
                "traffic_percentage": config.traffic_percentage,
                "compliance_threshold": config.constitutional_compliance_threshold,
                "constitutional_hash": config.constitutional_hash
            })
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Configuration test failed: {e}")
    
    async def test_ab_testing_routing(self):
        """Test A/B testing traffic routing."""
        test_name = "A/B Testing Routing"
        
        try:
            # Test consistent routing with same request ID
            request_id = "test_request_123"
            
            # Call multiple times with same ID - should get consistent routing
            results = []
            for _ in range(10):
                use_deepseek = self.pilot_manager.should_use_deepseek_r1(request_id)
                results.append(use_deepseek)
            
            # All results should be the same (consistent hashing)
            assert all(r == results[0] for r in results), "Routing should be consistent for same request ID"
            
            # Test different request IDs - should get mixed results with 50% traffic
            different_ids = [f"test_request_{i}" for i in range(100)]
            deepseek_count = sum(1 for req_id in different_ids if self.pilot_manager.should_use_deepseek_r1(req_id))
            deepseek_percentage = deepseek_count / len(different_ids) * 100
            
            # Should be approximately 50% (allow 10% variance)
            assert 40 <= deepseek_percentage <= 60, f"Expected ~50% DeepSeek routing, got {deepseek_percentage}%"
            
            self.record_test_result(test_name, True, f"A/B routing working correctly ({deepseek_percentage:.1f}% DeepSeek)", {
                "consistent_routing": all(r == results[0] for r in results),
                "deepseek_percentage": deepseek_percentage,
                "sample_size": len(different_ids)
            })
            
        except Exception as e:
            self.record_test_result(test_name, False, f"A/B testing failed: {e}")
    
    async def test_constitutional_compliance_validation(self):
        """Test constitutional compliance validation."""
        test_name = "Constitutional Compliance Validation"
        
        try:
            validator = self.pilot_manager.constitutional_validator
            
            # Test compliant response
            compliant_response = {
                "choices": [{
                    "message": {
                        "content": "This is a helpful and constitutional response about AI governance."
                    }
                }]
            }
            
            result = await validator.validate_response(compliant_response, "cdd01ef066bc6cf2")
            
            assert result.compliant == True, "Compliant response should pass validation"
            assert result.confidence_score >= 0.95, f"Confidence score too low: {result.confidence_score}"
            assert result.constitutional_hash == "cdd01ef066bc6cf2", "Constitutional hash mismatch"
            
            # Test potentially harmful response
            harmful_response = {
                "choices": [{
                    "message": {
                        "content": "This response contains harmful and dangerous content that violates policies."
                    }
                }]
            }
            
            harmful_result = await validator.validate_response(harmful_response, "cdd01ef066bc6cf2")
            
            assert harmful_result.confidence_score < 0.95, "Harmful response should have low confidence"
            assert len(harmful_result.violations) > 0, "Violations should be detected"
            
            self.record_test_result(test_name, True, "Constitutional validation working correctly", {
                "compliant_score": result.confidence_score,
                "harmful_score": harmful_result.confidence_score,
                "violations_detected": len(harmful_result.violations)
            })
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Constitutional validation failed: {e}")
    
    async def test_cost_calculation(self):
        """Test cost calculation and tracking."""
        test_name = "Cost Calculation"
        
        try:
            # Test cost calculation for different models
            deepseek_cost = self.pilot_manager._calculate_cost("deepseek-r1", 1000)
            claude_cost = self.pilot_manager._calculate_cost("claude-3-7-sonnet", 1000)
            
            # DeepSeek should be significantly cheaper
            cost_reduction = ((claude_cost - deepseek_cost) / claude_cost) * 100
            
            assert deepseek_cost < claude_cost, "DeepSeek should be cheaper than Claude"
            assert cost_reduction > 90, f"Cost reduction should be >90%, got {cost_reduction:.1f}%"
            
            self.record_test_result(test_name, True, f"Cost calculation correct ({cost_reduction:.1f}% reduction)", {
                "deepseek_cost": deepseek_cost,
                "claude_cost": claude_cost,
                "cost_reduction_percent": cost_reduction
            })
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Cost calculation failed: {e}")
    
    async def test_ai_service_integration(self):
        """Test integration with AI model service."""
        test_name = "AI Service Integration"
        
        try:
            # Test pilot-enabled generation
            response = await self.ai_service.generate_with_pilot(
                "Test constitutional AI compliance validation",
                request_id="test_integration_001"
            )
            
            assert response is not None, "Response should not be None"
            assert response.content is not None, "Response content should not be None"
            assert len(response.content) > 0, "Response content should not be empty"
            
            # Check if pilot metadata is included
            metadata = response.metadata or {}
            pilot_enabled = metadata.get("pilot_enabled", False)
            constitutional_hash = metadata.get("constitutional_hash", "")
            
            self.record_test_result(test_name, True, "AI service integration working", {
                "response_length": len(response.content),
                "pilot_enabled": pilot_enabled,
                "constitutional_hash": constitutional_hash,
                "model_id": response.model_id,
                "provider": response.provider
            })
            
        except Exception as e:
            self.record_test_result(test_name, False, f"AI service integration failed: {e}")
    
    async def test_monitoring_system(self):
        """Test monitoring and metrics collection."""
        test_name = "Monitoring System"
        
        try:
            # Collect metrics
            metrics = await self.monitor.collect_metrics(self.ai_service)
            
            assert metrics is not None, "Metrics should not be None"
            assert metrics.constitutional_hash == "cdd01ef066bc6cf2", "Constitutional hash should match"
            
            # Test cost analysis
            cost_analysis = self.monitor.analyze_cost_savings(metrics)
            
            assert cost_analysis.cost_reduction_percentage > 90, "Cost reduction should be >90%"
            assert cost_analysis.projected_annual_savings > 1000000, "Annual savings should be >$1M"
            
            # Test dashboard data generation
            dashboard_data = self.monitor.generate_dashboard_data()
            
            assert "pilot_status" in dashboard_data, "Dashboard should include pilot status"
            assert "performance_metrics" in dashboard_data, "Dashboard should include performance metrics"
            assert "cost_analysis" in dashboard_data, "Dashboard should include cost analysis"
            
            self.record_test_result(test_name, True, "Monitoring system working correctly", {
                "cost_reduction_percent": cost_analysis.cost_reduction_percentage,
                "projected_annual_savings": cost_analysis.projected_annual_savings,
                "dashboard_sections": list(dashboard_data.keys())
            })
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Monitoring system failed: {e}")
    
    async def test_alert_system(self):
        """Test alert generation and thresholds."""
        test_name = "Alert System"
        
        try:
            # Create test metrics with low compliance to trigger alerts
            from services.shared.deepseek_r1_monitoring import PilotMetrics
            from datetime import datetime, timezone
            
            low_compliance_metrics = PilotMetrics(
                timestamp=datetime.now(timezone.utc),
                constitutional_compliance_rate=0.80,  # Below threshold
                response_time_p95_ms=3000,  # Above threshold
                response_time_p99_ms=4000,
                cost_reduction_percentage=96.0,
                success_rate=0.95,
                error_rate=0.05,
                fallback_rate=0.02,
                total_requests=100,
                deepseek_requests=50,
                control_requests=50,
                constitutional_hash="cdd01ef066bc6cf2",
                pilot_enabled=True
            )
            
            alerts = self.monitor.check_alerts(low_compliance_metrics)
            
            assert len(alerts) > 0, "Alerts should be generated for low compliance"
            
            # Check for high priority alerts
            high_alerts = [a for a in alerts if a["severity"] == "high"]
            assert len(high_alerts) > 0, "High priority alerts should be generated"
            
            self.record_test_result(test_name, True, f"Alert system working ({len(alerts)} alerts generated)", {
                "total_alerts": len(alerts),
                "high_priority_alerts": len(high_alerts),
                "alert_types": [a["type"] for a in alerts]
            })
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Alert system failed: {e}")
    
    async def run_all_tests(self):
        """Run all pilot tests."""
        logger.info("Starting DeepSeek R1 pilot test suite...")
        
        await self.setup()
        
        # Run individual tests
        await self.test_pilot_configuration()
        await self.test_ab_testing_routing()
        await self.test_constitutional_compliance_validation()
        await self.test_cost_calculation()
        await self.test_ai_service_integration()
        await self.test_monitoring_system()
        await self.test_alert_system()
        
        # Generate test report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("DEEPSEEK R1 PILOT TEST REPORT")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("="*80)
        
        # Detailed results
        for result in self.test_results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} {result['test_name']}: {result['message']}")
            
            if result["details"]:
                for key, value in result["details"].items():
                    print(f"    {key}: {value}")
        
        print("="*80)
        
        # Save detailed report
        report_file = "reports/deepseek_r1_pilot_test_report.json"
        os.makedirs("reports", exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate,
                    "timestamp": time.time()
                },
                "test_results": self.test_results
            }, f, indent=2)
        
        logger.info(f"Detailed test report saved to {report_file}")
        
        if success_rate >= 80:
            logger.info("🎉 DeepSeek R1 pilot implementation is ready for deployment!")
        else:
            logger.warning("⚠️  Some tests failed. Review issues before deployment.")


async def main():
    """Main test execution."""
    tester = DeepSeekR1PilotTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
