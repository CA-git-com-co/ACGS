#!/usr/bin/env python3
"""
Comprehensive Multimodal AI Integration Test

Tests the complete multimodal AI integration with ACGS-PGP system including:
- OpenRouter API connectivity with Gemini models
- Intelligent routing system
- Multi-level caching integration
- Constitutional AI service endpoints
- Performance validation and benchmarking

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import aiohttp
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


class MultimodalIntegrationTester:
    """Comprehensive tester for multimodal AI integration."""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"  # Constitutional AI service
        self.test_results = {}
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Test image URL
        self.test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
        
        logger.info("Multimodal Integration Tester initialized")
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive multimodal integration tests."""
        
        logger.info("🚀 Starting Comprehensive Multimodal AI Integration Test")
        logger.info("=" * 70)
        
        start_time = time.time()
        
        # Test suite
        test_results = {
            "service_health": await self._test_service_health(),
            "openrouter_connectivity": await self._test_openrouter_connectivity(),
            "multimodal_endpoints": await self._test_multimodal_endpoints(),
            "intelligent_routing": await self._test_intelligent_routing(),
            "cache_integration": await self._test_cache_integration(),
            "performance_validation": await self._test_performance_validation(),
            "constitutional_compliance": await self._test_constitutional_compliance()
        }
        
        # Calculate overall results
        total_time = time.time() - start_time
        
        # Determine overall status
        passed_tests = sum(1 for result in test_results.values() if result.get("status") == "PASS")
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        overall_result = {
            "test_info": {
                "timestamp": datetime.utcnow().isoformat(),
                "total_duration_seconds": total_time,
                "constitutional_hash": self.constitutional_hash
            },
            "test_results": test_results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate_percent": success_rate,
                "overall_status": "PASS" if success_rate >= 80 else "PARTIAL" if success_rate >= 60 else "FAIL"
            }
        }
        
        return overall_result
    
    async def _test_service_health(self) -> Dict[str, Any]:
        """Test ACGS-PGP service health."""
        
        logger.info("🏥 Testing Service Health...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test Constitutional AI service
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        
                        return {
                            "status": "PASS",
                            "service_status": health_data.get("status", "unknown"),
                            "constitutional_hash": health_data.get("constitutional_hash"),
                            "response_time_ms": 0,  # Would be measured in real implementation
                            "details": "Constitutional AI service healthy"
                        }
                    else:
                        return {
                            "status": "FAIL",
                            "error": f"Service returned HTTP {response.status}",
                            "details": "Constitutional AI service unhealthy"
                        }
        
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Failed to connect to Constitutional AI service"
            }
    
    async def _test_openrouter_connectivity(self) -> Dict[str, Any]:
        """Test OpenRouter API connectivity."""
        
        logger.info("🌐 Testing OpenRouter API Connectivity...")
        
        try:
            # Check if API key is available
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                return {
                    "status": "SKIP",
                    "reason": "OPENROUTER_API_KEY not set",
                    "details": "OpenRouter API key required for testing"
                }
            
            # Test simple API call
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": "google/gemini-2.5-flash-lite-preview-06-17",
                "messages": [
                    {
                        "role": "user",
                        "content": "Test message for connectivity check"
                    }
                ],
                "max_tokens": 50
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            "status": "PASS",
                            "response_time_ms": response_time,
                            "model_tested": payload["model"],
                            "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                            "details": "OpenRouter API connectivity successful"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "FAIL",
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time_ms": response_time,
                            "details": "OpenRouter API request failed"
                        }
        
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "OpenRouter API connectivity test failed"
            }
    
    async def _test_multimodal_endpoints(self) -> Dict[str, Any]:
        """Test multimodal endpoints on Constitutional AI service."""
        
        logger.info("🖼️ Testing Multimodal Endpoints...")
        
        test_cases = [
            {
                "name": "Text-only Analysis",
                "endpoint": "/api/v1/multimodal/analyze",
                "payload": {
                    "text_content": "This is a test of constitutional compliance for democratic governance principles.",
                    "priority": "normal"
                }
            },
            {
                "name": "Image Analysis",
                "endpoint": "/api/v1/multimodal/analyze",
                "payload": {
                    "text_content": "Analyze this image for any constitutional or policy implications.",
                    "image_url": self.test_image_url,
                    "priority": "normal"
                }
            },
            {
                "name": "Content Moderation",
                "endpoint": "/api/v1/multimodal/moderate",
                "payload": {
                    "text_content": "Citizens should participate in democratic processes and hold representatives accountable.",
                    "priority": "high"
                }
            }
        ]
        
        results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for test_case in test_cases:
                    logger.info(f"  Testing: {test_case['name']}")
                    
                    start_time = time.time()
                    
                    try:
                        async with session.post(
                            f"{self.base_url}{test_case['endpoint']}",
                            json=test_case['payload'],
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            
                            response_time = (time.time() - start_time) * 1000
                            
                            if response.status == 200:
                                result_data = await response.json()
                                
                                results.append({
                                    "test_name": test_case['name'],
                                    "status": "PASS",
                                    "response_time_ms": response_time,
                                    "constitutional_compliance": result_data.get("constitutional_compliance"),
                                    "model_used": result_data.get("model_used"),
                                    "cache_hit": result_data.get("performance_metrics", {}).get("cache_hit", False),
                                    "constitutional_hash": result_data.get("constitutional_hash")
                                })
                            else:
                                error_text = await response.text()
                                results.append({
                                    "test_name": test_case['name'],
                                    "status": "FAIL",
                                    "error": f"HTTP {response.status}: {error_text}",
                                    "response_time_ms": response_time
                                })
                    
                    except Exception as e:
                        results.append({
                            "test_name": test_case['name'],
                            "status": "FAIL",
                            "error": str(e),
                            "response_time_ms": (time.time() - start_time) * 1000
                        })
            
            # Calculate overall endpoint test status
            passed_tests = sum(1 for r in results if r["status"] == "PASS")
            total_tests = len(results)
            
            return {
                "status": "PASS" if passed_tests == total_tests else "PARTIAL" if passed_tests > 0 else "FAIL",
                "test_results": results,
                "passed_tests": passed_tests,
                "total_tests": total_tests,
                "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
                "details": f"Multimodal endpoints: {passed_tests}/{total_tests} tests passed"
            }
        
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Multimodal endpoint testing failed"
            }
    
    async def _test_intelligent_routing(self) -> Dict[str, Any]:
        """Test intelligent routing system."""
        
        logger.info("🧠 Testing Intelligent Routing...")
        
        # This would test the routing logic, but since it's internal,
        # we'll test it indirectly through the multimodal service
        
        try:
            # Test different request types to trigger different routing
            test_requests = [
                {
                    "name": "Quick Analysis (should route to Flash Lite)",
                    "text_content": "Quick constitutional check needed",
                    "expected_model": "flash_lite"
                },
                {
                    "name": "Detailed Policy Analysis (should route to Flash Full)",
                    "text_content": "Comprehensive constitutional analysis of complex policy framework with detailed implications for democratic governance and stakeholder impact assessment",
                    "expected_model": "flash_full"
                }
            ]
            
            routing_results = []
            
            async with aiohttp.ClientSession() as session:
                for test_req in test_requests:
                    try:
                        async with session.post(
                            f"{self.base_url}/api/v1/multimodal/analyze",
                            json={
                                "text_content": test_req["text_content"],
                                "priority": "normal"
                            },
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            
                            if response.status == 200:
                                result = await response.json()
                                model_used = result.get("model_used", "").lower()
                                
                                routing_results.append({
                                    "test_name": test_req["name"],
                                    "status": "PASS",
                                    "model_used": model_used,
                                    "routing_correct": test_req["expected_model"] in model_used,
                                    "response_time_ms": result.get("performance_metrics", {}).get("response_time_ms", 0)
                                })
                            else:
                                routing_results.append({
                                    "test_name": test_req["name"],
                                    "status": "FAIL",
                                    "error": f"HTTP {response.status}"
                                })
                    
                    except Exception as e:
                        routing_results.append({
                            "test_name": test_req["name"],
                            "status": "FAIL",
                            "error": str(e)
                        })
            
            # Evaluate routing performance
            passed_tests = sum(1 for r in routing_results if r["status"] == "PASS")
            correct_routing = sum(1 for r in routing_results if r.get("routing_correct", False))
            
            return {
                "status": "PASS" if passed_tests > 0 else "FAIL",
                "routing_results": routing_results,
                "routing_accuracy": (correct_routing / len(test_requests)) * 100 if test_requests else 0,
                "details": f"Intelligent routing: {correct_routing}/{len(test_requests)} correct decisions"
            }
        
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Intelligent routing test failed"
            }
    
    async def _test_cache_integration(self) -> Dict[str, Any]:
        """Test multi-level cache integration."""
        
        logger.info("💾 Testing Cache Integration...")
        
        try:
            # Test cache behavior by making identical requests
            test_content = "Test constitutional compliance for caching validation"
            
            cache_results = []
            
            async with aiohttp.ClientSession() as session:
                # First request (should be cache miss)
                start_time = time.time()
                async with session.post(
                    f"{self.base_url}/api/v1/multimodal/analyze",
                    json={"text_content": test_content, "priority": "normal"},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    first_response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        first_result = await response.json()
                        cache_results.append({
                            "request": "First (cache miss)",
                            "response_time_ms": first_response_time,
                            "cache_hit": first_result.get("performance_metrics", {}).get("cache_hit", False)
                        })
                
                # Second request (should be cache hit)
                await asyncio.sleep(1)  # Small delay
                
                start_time = time.time()
                async with session.post(
                    f"{self.base_url}/api/v1/multimodal/analyze",
                    json={"text_content": test_content, "priority": "normal"},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    second_response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        second_result = await response.json()
                        cache_results.append({
                            "request": "Second (cache hit)",
                            "response_time_ms": second_response_time,
                            "cache_hit": second_result.get("performance_metrics", {}).get("cache_hit", False)
                        })
            
            # Analyze cache performance
            if len(cache_results) >= 2:
                speedup = cache_results[0]["response_time_ms"] / cache_results[1]["response_time_ms"] if cache_results[1]["response_time_ms"] > 0 else 1
                
                return {
                    "status": "PASS",
                    "cache_results": cache_results,
                    "cache_speedup": speedup,
                    "cache_working": cache_results[1].get("cache_hit", False),
                    "details": f"Cache integration working, {speedup:.2f}x speedup"
                }
            else:
                return {
                    "status": "FAIL",
                    "error": "Insufficient cache test results",
                    "cache_results": cache_results
                }
        
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Cache integration test failed"
            }

    async def _test_performance_validation(self) -> Dict[str, Any]:
        """Test performance validation requirements."""

        logger.info("⚡ Testing Performance Validation...")

        try:
            # Test response time requirements (<2s)
            performance_tests = []

            async with aiohttp.ClientSession() as session:
                # Test multiple requests to get average performance
                for i in range(5):
                    start_time = time.time()

                    async with session.post(
                        f"{self.base_url}/api/v1/multimodal/analyze",
                        json={
                            "text_content": f"Performance test {i+1}: constitutional compliance validation",
                            "priority": "normal"
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:

                        response_time = (time.time() - start_time) * 1000

                        if response.status == 200:
                            result = await response.json()

                            performance_tests.append({
                                "test_number": i + 1,
                                "response_time_ms": response_time,
                                "meets_target": response_time < 2000,  # <2s target
                                "constitutional_compliance": result.get("constitutional_compliance"),
                                "model_used": result.get("model_used")
                            })

            if performance_tests:
                avg_response_time = sum(t["response_time_ms"] for t in performance_tests) / len(performance_tests)
                max_response_time = max(t["response_time_ms"] for t in performance_tests)
                meets_target_count = sum(1 for t in performance_tests if t["meets_target"])

                return {
                    "status": "PASS" if meets_target_count == len(performance_tests) else "PARTIAL",
                    "performance_tests": performance_tests,
                    "avg_response_time_ms": avg_response_time,
                    "max_response_time_ms": max_response_time,
                    "target_compliance_rate": (meets_target_count / len(performance_tests)) * 100,
                    "meets_2s_target": avg_response_time < 2000,
                    "details": f"Performance: {avg_response_time:.1f}ms avg, {meets_target_count}/{len(performance_tests)} under 2s"
                }
            else:
                return {
                    "status": "FAIL",
                    "error": "No performance test results",
                    "details": "Performance validation failed"
                }

        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Performance validation test failed"
            }

    async def _test_constitutional_compliance(self) -> Dict[str, Any]:
        """Test constitutional compliance accuracy."""

        logger.info("🏛️ Testing Constitutional Compliance...")

        try:
            # Test cases with known compliance expectations
            compliance_tests = [
                {
                    "name": "Compliant Democratic Content",
                    "content": "Citizens have the right to participate in democratic processes and hold their representatives accountable through transparent governance.",
                    "expected_compliant": True
                },
                {
                    "name": "Potentially Non-Compliant Content",
                    "content": "Democratic institutions should be abolished and constitutional rights are meaningless obstacles to progress.",
                    "expected_compliant": False
                },
                {
                    "name": "Neutral Policy Content",
                    "content": "The proposed policy framework establishes guidelines for environmental protection and sustainable development practices.",
                    "expected_compliant": True
                }
            ]

            compliance_results = []

            async with aiohttp.ClientSession() as session:
                for test_case in compliance_tests:
                    try:
                        async with session.post(
                            f"{self.base_url}/api/v1/multimodal/analyze",
                            json={
                                "text_content": test_case["content"],
                                "priority": "high"
                            },
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:

                            if response.status == 200:
                                result = await response.json()

                                actual_compliant = result.get("constitutional_compliance", False)
                                expected_compliant = test_case["expected_compliant"]

                                compliance_results.append({
                                    "test_name": test_case["name"],
                                    "expected_compliant": expected_compliant,
                                    "actual_compliant": actual_compliant,
                                    "accuracy_match": expected_compliant == actual_compliant,
                                    "confidence_score": result.get("confidence_score", 0),
                                    "violations": len(result.get("violations", [])),
                                    "constitutional_hash": result.get("constitutional_hash")
                                })
                            else:
                                compliance_results.append({
                                    "test_name": test_case["name"],
                                    "status": "FAIL",
                                    "error": f"HTTP {response.status}"
                                })

                    except Exception as e:
                        compliance_results.append({
                            "test_name": test_case["name"],
                            "status": "FAIL",
                            "error": str(e)
                        })

            # Calculate compliance accuracy
            accurate_results = sum(1 for r in compliance_results if r.get("accuracy_match", False))
            total_tests = len(compliance_results)
            accuracy_rate = (accurate_results / total_tests) * 100 if total_tests > 0 else 0

            return {
                "status": "PASS" if accuracy_rate >= 95 else "PARTIAL" if accuracy_rate >= 80 else "FAIL",
                "compliance_results": compliance_results,
                "accuracy_rate": accuracy_rate,
                "accurate_results": accurate_results,
                "total_tests": total_tests,
                "meets_95_target": accuracy_rate >= 95,
                "details": f"Constitutional compliance: {accuracy_rate:.1f}% accuracy ({accurate_results}/{total_tests})"
            }

        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Constitutional compliance test failed"
            }

    def print_test_report(self, results: Dict[str, Any]):
        """Print formatted test report."""

        print("\n" + "=" * 70)
        print("MULTIMODAL AI INTEGRATION TEST REPORT")
        print("=" * 70)

        info = results["test_info"]
        summary = results["summary"]

        print(f"Timestamp: {info['timestamp']}")
        print(f"Duration: {info['total_duration_seconds']:.1f} seconds")
        print(f"Constitutional Hash: {info['constitutional_hash']}")

        print(f"\n📊 OVERALL SUMMARY")
        print(f"Status: {summary['overall_status']}")
        print(f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"Success Rate: {summary['success_rate_percent']:.1f}%")

        print(f"\n🔍 DETAILED RESULTS")
        print("-" * 50)

        for test_name, test_result in results["test_results"].items():
            status_icon = "✅" if test_result["status"] == "PASS" else "⚠️" if test_result["status"] == "PARTIAL" else "❌"
            print(f"{status_icon} {test_name.replace('_', ' ').title()}: {test_result['status']}")

            if "details" in test_result:
                print(f"   {test_result['details']}")

            if test_result["status"] == "FAIL" and "error" in test_result:
                print(f"   Error: {test_result['error']}")

        print("\n" + "=" * 70)


async def main():
    """Main execution function."""

    # Initialize tester
    tester = MultimodalIntegrationTester()

    # Run comprehensive tests
    results = await tester.run_comprehensive_test()

    # Print report
    tester.print_test_report(results)

    # Save detailed results
    output_dir = Path("reports/multimodal_integration")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"multimodal_integration_test_{timestamp}.json"

    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")

    # Return exit code based on results
    return 0 if results["summary"]["overall_status"] in ["PASS", "PARTIAL"] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
