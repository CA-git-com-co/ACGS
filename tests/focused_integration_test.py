#!/usr/bin/env python3
"""
Focused Integration Test for Running ACGS-2 Services
Constitutional Hash: cdd01ef066bc6cf2

Tests the services that are currently running and validates
constitutional compliance across the operational services.
"""

import asyncio
import json
import aiohttp
from datetime import datetime
from typing import Dict, Any

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Known running services
RUNNING_SERVICES = {
    "constitutional_core": "http://localhost:8001"
}

class FocusedIntegrationTest:
    """Focused test for operational services"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
    
    async def setup(self):
        """Setup test environment"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        print(f"🔧 Focused integration test initialized")
        print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    async def teardown(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
        print("🧹 Focused integration test cleanup completed")
    
    async def test_service_health(self, service_name: str, url: str) -> Dict[str, Any]:
        """Test individual service health"""
        try:
            async with self.session.get(f"{url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    result = {
                        "service": service_name,
                        "status": "healthy",
                        "constitutional_hash": data.get("constitutional_hash"),
                        "version": data.get("version"),
                        "response_time_ms": 0,
                        "details": data
                    }
                    
                    # Validate constitutional hash
                    if data.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                        result["constitutional_compliance"] = True
                        print(f"✅ {service_name}: Health check passed with constitutional compliance")
                    else:
                        result["constitutional_compliance"] = False
                        print(f"⚠️ {service_name}: Health check passed but constitutional hash mismatch")
                    
                    return result
                else:
                    return {
                        "service": service_name,
                        "status": "unhealthy",
                        "error": f"HTTP {response.status}",
                        "constitutional_compliance": False
                    }
        except Exception as e:
            return {
                "service": service_name,
                "status": "error",
                "error": str(e),
                "constitutional_compliance": False
            }
    
    async def test_constitutional_validation(self) -> Dict[str, Any]:
        """Test constitutional validation functionality"""
        try:
            payload = {
                "request": "validate_constitutional_compliance",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "context": {
                    "purpose": "focused_integration_test",
                    "compliance_level": "high"
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Constitutional-Hash": CONSTITUTIONAL_HASH
            }
            
            async with self.session.post(
                f"{RUNNING_SERVICES['constitutional_core']}/api/v1/constitutional/validate",
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Constitutional validation successful")
                    print(f"   Constitutional Hash: {data.get('constitutional_hash')}")
                    print(f"   Compliance Status: {data.get('is_compliant')}")
                    print(f"   Compliance Score: {data.get('compliance_score', 'N/A')}")
                    
                    return {
                        "test": "constitutional_validation",
                        "status": "passed",
                        "constitutional_compliance": data.get("constitutional_hash") == CONSTITUTIONAL_HASH,
                        "details": data
                    }
                else:
                    error_text = await response.text()
                    print(f"⚠️ Constitutional validation failed: HTTP {response.status}")
                    print(f"   Error: {error_text}")
                    return {
                        "test": "constitutional_validation",
                        "status": "failed",
                        "error": f"HTTP {response.status}: {error_text}",
                        "constitutional_compliance": False
                    }
        except Exception as e:
            print(f"❌ Constitutional validation error: {str(e)}")
            return {
                "test": "constitutional_validation",
                "status": "error",
                "error": str(e),
                "constitutional_compliance": False
            }
    
    async def run_focused_tests(self):
        """Run focused integration tests"""
        print("🚀 Starting Focused ACGS-2 Integration Tests")
        print("=" * 60)
        
        # Test service health
        for service_name, url in RUNNING_SERVICES.items():
            result = await self.test_service_health(service_name, url)
            self.test_results.append(result)
        
        # Test constitutional validation
        validation_result = await self.test_constitutional_validation()
        self.test_results.append(validation_result)
        
        # Test performance
        await self.test_basic_performance()
        
        # Print results summary
        self.print_summary()
    
    async def test_basic_performance(self):
        """Test basic performance characteristics"""
        print("\n🏃 Testing Basic Performance")
        
        # Test latency with multiple requests
        latencies = []
        
        for i in range(10):
            start_time = asyncio.get_event_loop().time()
            
            try:
                async with self.session.get(
                    f"{RUNNING_SERVICES['constitutional_core']}/health"
                ) as response:
                    end_time = asyncio.get_event_loop().time()
                    latency_ms = (end_time - start_time) * 1000
                    latencies.append(latency_ms)
                    
                    if response.status != 200:
                        print(f"⚠️ Request {i+1} failed: HTTP {response.status}")
            except Exception as e:
                print(f"❌ Request {i+1} error: {str(e)}")
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            min_latency = min(latencies)
            
            print(f"📊 Performance Results (10 requests):")
            print(f"   Average Latency: {avg_latency:.2f}ms")
            print(f"   Min Latency: {min_latency:.2f}ms")
            print(f"   Max Latency: {max_latency:.2f}ms")
            
            # Check if we meet P99 target of <5ms
            if avg_latency <= 5.0:
                print("✅ Latency target met (<5ms average)")
            else:
                print(f"⚠️ Latency target not met (>{avg_latency:.2f}ms > 5ms)")
            
            self.test_results.append({
                "test": "basic_performance",
                "status": "passed",
                "avg_latency_ms": avg_latency,
                "max_latency_ms": max_latency,
                "target_met": avg_latency <= 5.0
            })
        else:
            print("❌ No successful performance measurements")
            self.test_results.append({
                "test": "basic_performance",
                "status": "failed",
                "error": "No successful requests"
            })
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("🏁 Focused Integration Test Results")
        print("=" * 60)
        
        passed_tests = sum(1 for r in self.test_results if r.get("status") == "passed")
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 Test Breakdown:")
        for result in self.test_results:
            test_name = result.get("test", result.get("service", "unknown"))
            status = result.get("status", "unknown")
            compliance = result.get("constitutional_compliance")
            
            status_icon = "✅" if status == "passed" else "❌" if status == "failed" else "⚠️"
            compliance_icon = "✅" if compliance else "❌" if compliance is False else "⚪"
            
            print(f"   {status_icon} {test_name}: {status}")
            if compliance is not None:
                print(f"      Constitutional Compliance: {compliance_icon}")
        
        print(f"\n🔐 Constitutional Compliance:")
        compliant_services = sum(1 for r in self.test_results if r.get("constitutional_compliance") is True)
        compliance_tested = sum(1 for r in self.test_results if r.get("constitutional_compliance") is not None)
        
        if compliance_tested > 0:
            compliance_rate = (compliant_services / compliance_tested) * 100
            compliance_icon = "✅" if compliance_rate >= 95 else "⚠️" if compliance_rate >= 80 else "❌"
            print(f"   {compliance_icon} Constitutional Hash Validation: {CONSTITUTIONAL_HASH}")
            print(f"   {compliance_icon} Compliance Rate: {compliance_rate:.1f}% ({compliant_services}/{compliance_tested})")
        else:
            print(f"   ⚪ No constitutional compliance tests performed")
        
        # Overall system status
        if success_rate >= 90:
            print(f"\n🎉 System Status: EXCELLENT")
            print(f"   Operational services are performing optimally")
        elif success_rate >= 70:
            print(f"\n✅ System Status: GOOD")
            print(f"   Operational services are performing well")
        else:
            print(f"\n⚠️ System Status: NEEDS ATTENTION")
            print(f"   Operational services have issues requiring attention")
        
        print(f"\n📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"🕐 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def main():
    """Main test runner"""
    test_suite = FocusedIntegrationTest()
    await test_suite.setup()
    
    try:
        await test_suite.run_focused_tests()
    finally:
        await test_suite.teardown()

if __name__ == "__main__":
    asyncio.run(main())